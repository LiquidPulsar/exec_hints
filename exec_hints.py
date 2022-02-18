import inspect, types, typing

def apply_hint(arg,hint):
    if isinstance(hint,types.GenericAlias):
        b = hint.__args__
        t = hint.__mro__[0]
        if b:
            if isinstance(arg,dict):
                if len(b) == 1:
                    return {k:apply_hint(v,b[0]) for k,v in arg.items()}
                elif len(b) == 2:
                    return {apply_hint(k,b[0]):apply_hint(v,b[1]) for k,v in arg.items()}
		raise ValueError(f'Invalid number of subhints specified for arg of type dict: {len(b)} not in (1, 2), no hint application method found')
            elif hasattr(t, '__iter__'):
                if len(b) == 1:
                    return t(apply_hint(v,b[0]) for v in arg)
                elif len(b) == len(arg):
                    return t(apply_hint(g,f) for f,g in zip(b,arg))
		raise ValueError(f'Invalid number of subhints specified for iterable type {t}: {len(b)} not in (1, {len(arg)}), no hint application method found')
        else:
            return t(arg)
    elif isinstance(hint,(types.UnionType,_UnionType)):
        b = hint.__args__
        for opt in b:
            try:
                return apply_hint(arg,opt)
            except (TypeError, ValueError):
                pass
        raise ValueError(f'Things didn\'t work out, all of {b} errored on {arg}')
    else:
        return hint(arg) if callable(hint) else hint

def exec_hints(func):
  def inner(*args, **kwargs):
    ann = typing.get_type_hints(func)
    spec = inspect.getfullargspec(func)

    args, vargs = args[:len(spec.args)],args[len(spec.args):]

    args = [apply_hint(value,ann[name]) if name in ann else value
			for name,value in zip(spec.args,args)]

    if spec.varargs:
        if spec.varargs in ann:
            args += [*apply_hint(vargs,ann[spec.varargs])]
        else:
            args += [vargs]


    kwargs = {name:apply_hint(value,ann[name]) if name in ann else value
            for name,value in list(kwargs.items())}
    
    if spec.kwonlyargs:
        kwonlyvals = [kwargs.pop(k) if k in kwargs else 
                    spec.kwonlydefaults[k] for k in spec.kwonlyargs]

    if spec.varkw and spec.varkw in ann:
        kwargs = apply_hint(kwargs,ann[spec.varkw])

    if spec.kwonlyargs:
        for k,v in zip(spec.kwonlyargs,kwonlyvals):
            kwargs[k] = apply_hint(v,ann[k]) if k in ann else v
    x = func(*args,**kwargs)
    return apply_hint(x,ann['return']) if 'return' in ann else x
  return inner

class _UnionType:
    def  __init__(self,*args):
        self.__args__ = list(args)
    def __or__(self, other):
        if isinstance(other, (types.UnionType,_UnionType)):
            print(self,other)
            return _UnionType(*self.__args__,*other.__args__)
        return _UnionType(*self.__args__,other)
    def __ror__(self, other):
        if isinstance(other, (types.UnionType,_UnionType)):
            print(self,other)
            return _UnionType(*other.__args__,*self.__args__)
        return _UnionType(other,*self.__args__)

class Literal:
    def __init__(self,v):
        self.v = v
    def __or__(self, other):
        if isinstance(other, (types.UnionType,_UnionType)):
            return _UnionType(self.v,*other.__args__)

        return _UnionType(self.v,other)
    def __ror__(self, other):
        if isinstance(other, (types.UnionType,_UnionType)):
            print(other.__args__)
            return _UnionType(*other.__args__,self.v)
        return _UnionType(other,self.v)

    def __call__(self,arg):
        if callable(arg):
            return self.v(arg)
        else:
            return self.v
