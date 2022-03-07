# exec_hints
Pretty comprehensive typehint evaluator to give you code that extra bit of zazz and illegibility it always needed


For all examples, here's the obvious prerequisite
```py
from exec_hints import _UnionType, exec_hints, Literal
```
Let's start off small: you can specify a hint on an argument and it'll convert it
```py
@exec_hints
def foo(arg:int):
    print(arg*arg)

foo('12')
>>> 144
```

```py
@exec_hints
def foo(arg:set):
    print(arg, arg.issubset('123'))

foo('12')
>>> {'2', '1'} True
```

```py
@exec_hints
def foo(arg:set[int]):
    print(arg, arg.issubset(range(10)))

foo('12')
>>> {1, 2} True
```
A single argument to dict will modify all values, 2 arguments means the first applies to keys, 2nd to values
```py
@exec_hints
def foo(arg:dict[int]):
    print(arg, arg.keys())

foo({'a':'123',12:13.2})
>>> {'a': 123, 12: 13} dict_keys(['a', 12])
```
Works with Unions (more on that later)
```py
@exec_hints
def foo(arg:set[int|str]):
    print(arg, arg.issubset(range(10)))

foo('1a2')
>>> {1, 'a', 2} False
```
If an iterable hint is provided with a number of arguments matching what was passed, each subhint will be applied to corresponding arguments
```py
@exec_hints
def foo(arg:list[int,str,int]):
    print(arg, arg[::-1])

foo('1a2')
>>> [1, 'a', 2] [2, 'a', 1]
```
...and of course, we can nest these 😎
```py
@exec_hints
def foo(arg:list[int,int|str,tuple[int|float|str]]):
    print(arg)

foo(('1','a',['1','2.67','b']))
>>> [1, 'a', (1, 2.67, 'b')]
```
If several options are given, it tries each in turn
```py
@exec_hints
def foo(arg:list[int,int|str]|tuple[int|float|str]):
    print(arg)

#first fails because there are 2 subhints and 3 args provided
foo(['1','2.67','b'])
>>> (1, 2.67, 'b')
#first works!
foo(['1','2.67'])
>>> [1, '2.67']
```
You can pass your own functions in here, but they cant directly be used with |
Blame Python, not me.
```py
@exec_hints
def foo(arg:lambda x: x[::2]):
    print(arg)

foo('banana')
>>> bnn
```
There's a workaround for that tho!
`list|1` isnt supported by Python, so we have a class for that: `Literal`
Accepts a callable or a literal (ok the class name isnt the best, accepting any suggestions)
If it's callable, will try call on the arg, otherwise will just return itself
```py
@exec_hints
def foo(arg:int|Literal(0)):
    print(arg)

foo('banana')
>>> 0
```
We can use it to chain builtins that wouldnt normally be allowed.
Also note you can use it with `[]` syntax too
```py
@exec_hints
def foo(arg:int|Literal[str.upper]):
    print(arg)

foo('banana')
>>> BANANA
```
This documentation would have to be a few miles long to cover all of this
So here's a few examples:
```py
@exec_hints
def foo(message:int|tuple[int]|list[0], dct:dict[int,tuple[str.lower]]):
    print(message)
    print(dct)

foo('a1',{'213':'BaNaNa','444':'BoBa'})
>>> [0, 0]
>>> {213: ('b', 'a', 'n', 'a', 'n', 'a'), 444: ('b', 'o', 'b', 'a')}
```
Uhh, it works on a lot of stuff :)
Notably you can manipulate `*args` and `**kwargs` as normal.
Works with defaults too, but it will try to apply the hint to the default provided
```py
@exec_hints
def a(a,b:str.upper,c:tuple[int],d=12,*e:lambda x:map(str,x),f:int|Literal(-3)=3,**g:dict[str]):
    print(a,b,c,d,e,f,g)

a(1,'bb',['2','3'],4,5,banana=1,apple=2)
>>> 1 BB (2, 3) 4 ('5',) 3 {'banana': '1', 'apple': '2'}
```
You can typehint return values too 🎉
```py
@exec_hints
def foo(arg:int|Literal(str.upper)) -> lambda x:tuple(reversed(x)):
    print(arg)
    return arg

print(foo('banana'))
>>> BANANA
>>> ('A', 'N', 'A', 'N', 'A', 'B')
```
