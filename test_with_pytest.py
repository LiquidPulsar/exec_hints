import exec_hints
from exec_hints import _UnionType, Literal

def test_exec_hints1():
    @exec_hints
    def foo(arg:int):
        return arg**2

    assert foo('12') == 144

def test_exec_hints2():
    @exec_hints
    def foo(arg:set):
        return arg, arg.issubset('123')

    assert foo('12') == ({'2', '1'}, True)

def test_exec_hints3():
    @exec_hints
    def foo(arg:set[int]):
        return arg, arg.issubset(range(10))

    assert foo('12') == ({1, 2}, True)

def test_exec_hints4():
    @exec_hints
    def foo(arg:dict[int]):
        return arg, arg.keys()

    assert foo({'a':'123',12:13.2}) == \
        ({'a': 123, 12: 13}, {'a': 123, 12: 13}.keys())

def test_exec_hints5():
    @exec_hints
    def foo(arg:set[int|str]):
        return arg, arg.issubset(range(10))

    assert foo('1a2') == ({1, 'a', 2}, False)

def test_exec_hints6():
    @exec_hints
    def foo(arg:list[int,str,int]):
        return arg, arg[::-1]

    assert foo('1a2') == ([1, 'a', 2], [2, 'a', 1])

def test_exec_hints7():
    @exec_hints
    def foo(arg:list[int,int|str,tuple[int|float|str]]):
        return arg

    assert foo(('1','a',['1','2.67','b'])) == [1, 'a', (1, 2.67, 'b')]

def test_exec_hints8():
    @exec_hints
    def foo(arg:list[int,int|str]|tuple[int|float|str]):
        return arg

    assert foo(['1','2.67','b']) == (1, 2.67, 'b')
    assert foo(['1','2.67']) == [1, '2.67']

def test_exec_hints9():
    @exec_hints
    def foo(arg:lambda x: x[::2]):
        return arg

    assert foo('banana') == 'bnn'

def test_exec_hints10():
    @exec_hints
    def foo(arg:int|Literal(0)):
        return arg

    assert foo('banana') == 0
    assert foo('123') == 123

def test_exec_hints11():
    @exec_hints
    def foo(arg:int|Literal[str.upper]):
        return arg

    assert foo('banana') == 'BANANA'
    assert foo(123.567) == 123

def test_exec_hints12():
    @exec_hints
    def foo(message:int|tuple[int]|list[0], dct:dict[int,tuple[str.lower]]):
        return message, dct

    assert foo('a1',{'213':'BaNaNa','444':'BoBa'}) == ([0, 0], {213: ('b', 'a', 'n', 'a', 'n', 'a'), 444: ('b', 'o', 'b', 'a')})
    assert foo(12.001,{}) == (12, {})

def test_exec_hints13():
    @exec_hints
    def foo(a,b:str.upper,c:tuple[int],d=12,*e:lambda x:map(str,x),f:int|Literal(-3)=3,**g:dict[str]):
        return a,b,c,d,e,f,g

    assert foo(1,'bb',['2','3'],4,5,banana=1,apple=2) == (1, 'BB', (2, 3), 4, ('5',), 3, {'banana': '1', 'apple': '2'})

def test_exec_hints14():
    @exec_hints
    def foo(arg:int|Literal(str.upper)) -> lambda x:tuple(reversed(x)):
        return arg

    assert foo('banana') == ('A', 'N', 'A', 'N', 'A', 'B')