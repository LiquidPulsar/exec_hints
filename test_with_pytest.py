from exec_hints import Literal, exec_hints, check_hints
from pytest import raises

def test_exec_hints1():
    @exec_hints
    def foo(arg: int):
        return arg**2

    assert foo("12") == 144


def test_exec_hints2():
    @exec_hints
    def foo(arg: set):
        return arg, arg.issubset("123")

    assert foo("12") == ({"2", "1"}, True)


def test_exec_hints3():
    @exec_hints
    def foo(arg: set[int]):
        return arg, arg.issubset(range(10))

    assert foo("12") == ({1, 2}, True)


def test_exec_hints4():
    @exec_hints
    def foo(arg: dict[int]):
        return arg, arg.keys()

    assert foo({"a": "123", 12: 13.2}) == (
        {"a": 123, 12: 13},
        {"a": 123, 12: 13}.keys(),
    )


def test_exec_hints5():
    @exec_hints
    def foo(arg: set[int | str]):
        return arg, arg.issubset(range(10))

    assert foo("1a2") == ({1, "a", 2}, False)


def test_exec_hints6():
    @exec_hints
    def foo(arg: list[int, str, int]):
        return arg, arg[::-1]

    assert foo("1a2") == ([1, "a", 2], [2, "a", 1])


def test_exec_hints7():
    @exec_hints
    def foo(arg: list[int, int | str, tuple[int | float | str]]):
        return arg

    assert foo(("1", "a", ["1", "2.67", "b"])) == [1, "a", (1, 2.67, "b")]


def test_exec_hints8():
    @exec_hints
    def foo(arg: list[int, int | str] | tuple[int | float | str]):
        return arg

    assert foo(["1", "2.67", "b"]) == (1, 2.67, "b")
    assert foo(["1", "2.67"]) == [1, "2.67"]


def test_exec_hints9():
    @exec_hints
    def foo(arg: lambda x: x[::2]):
        return arg

    assert foo("banana") == "bnn"


def test_exec_hints10():
    @exec_hints
    def foo(arg: int | Literal(0)):
        return arg

    assert foo("banana") == 0
    assert foo("123") == 123


def test_exec_hints11():
    @exec_hints
    def foo(arg: int | Literal[str.upper]):
        return arg

    assert foo("banana") == "BANANA"
    assert foo(123.567) == 123


def test_exec_hints12():
    @exec_hints
    def foo(message: int | tuple[int] | list[0], dct: dict[int, tuple[str.lower]]):
        return message, dct

    assert foo("a1", {"213": "BaNaNa", "444": "BoBa"}) == (
        [0, 0],
        {213: ("b", "a", "n", "a", "n", "a"), 444: ("b", "o", "b", "a")},
    )
    assert foo(12.001, {}) == (12, {})


def test_exec_hints13():
    @exec_hints
    def foo(
        a,
        b: str.upper,
        c: tuple[int],
        d=12,
        *e: lambda x: map(str, x),
        f: int | Literal(-3) = 3,
        **g: dict[str]
    ):
        return a, b, c, d, e, f, g

    assert foo(1, "bb", ["2", "3"], 4, 5, banana=1, apple=2) == (
        1,
        "BB",
        (2, 3),
        4,
        ("5",),
        3,
        {"banana": "1", "apple": "2"},
    )


def test_exec_hints14():
    @exec_hints
    def foo(arg: int | Literal(str.upper)) -> lambda x: tuple(reversed(x)):
        return arg

    assert foo("banana") == ("A", "N", "A", "N", "A", "B")


def test_exec_hints15():
    from dataclasses import dataclass

    @exec_hints
    @dataclass
    class Bot:
        alignment: bool
        serial: int
        name: str

    b = Bot(123123, "12", 2)
    assert b.alignment == True
    assert b.serial == 12
    assert b.name == "2"


def test_check_hints1():
    @check_hints
    def foo(arg: int):
        return arg**2

    foo(12)
    with raises(TypeError):
        foo("12")


def test_check_hints2():
    @check_hints
    def foo(arg: set):
        return arg, arg.issubset("123")

    foo({1,2})
    with raises(TypeError):
        foo("12")


def test_check_hints3():
    @check_hints
    def foo(arg: set[int]):
        return arg, arg.issubset(range(10))

    foo({1,2})
    with raises(TypeError):
        foo("12")


def test_check_hints4():
    @check_hints
    def foo(arg: dict[int]):
        return arg, arg.keys()

    foo({12: 13})
    with raises(TypeError):
        foo({"a": "123", 12: 13.2})


def test_check_hints5():
    @check_hints
    def foo(arg: set[int | str]):
        return arg, arg.issubset(range(10))

    foo(set())
    foo({12,"13"})
    with raises(TypeError):
        foo("1a2")
    with raises(TypeError):
        foo({12,"13",0.2})


def test_check_hints6():
    @check_hints
    def foo(arg: list[int, str, int]):
        return arg, arg[::-1]

    foo([1, "a", 2])
    with raises(TypeError):
        foo([])
    with raises(TypeError):
        foo((1, "a", .2))
    with raises(TypeError):
        foo([1, "a", 2, 3])


def test_check_hints7():
    @check_hints
    def foo(arg: list[int, int | str, tuple[int | float | str]]):
        return arg

    foo([1, "a", (1, 2.67, "b")])
    with raises(TypeError):
        foo(("1", "a", ["1", "2.67", "b"]))
    with raises(TypeError):
        foo([1, "a", ("1", "2.67", {})])


def test_check_hints8():
    @check_hints
    def foo(arg: list[int, int | str] | tuple[int | float | str]):
        return arg

    foo([1, "a"])
    foo((1, 2.67, "b"))
    with raises(TypeError):
        foo([1])
    with raises(TypeError):
        foo(((),))


def test_check_hints9():
    @check_hints
    def foo(arg: tuple | Literal[0]):
        return arg

    foo(0)
    with raises(TypeError):
        foo("banana")
    with raises(TypeError):
        foo(1)


def test_check_hints10():
    @check_hints
    def foo(arg: int | Literal[str.isupper]):
        return arg

    with raises(TypeError):
        foo("banana")


def test_check_hints11():
    @check_hints
    def foo(message: int | tuple[int] | list[0], dct: dict[int, tuple[str.islower]]):
        return message, dct

    foo([0,0,0], {1: tuple("banana"), 444: tuple("boba")})
    with raises(TypeError):
        foo("a1", {"213": "BaNaNa", "444": "BoBa"})


def test_check_hints12():
    @check_hints
    def foo(
        a,
        b: str.isupper,
        c: tuple[int],
        d=12,
        *e: lambda x: "".join(map(str, x)) == "".join(map(str, x[::-1])), # palindrome check :)
        f: int | Literal(3) = 3,
        **g: dict[str]
    ):
        return a, b, c, d, e, f, g

    foo(1, "BB", (1, 1), 4, 5, 6, 5, banana="1", apple="2")
    with raises(TypeError):
        foo(1, "bb", ["2", "3"], 4, 5, banana=1, apple=2)


def test_check_hints13():
    @check_hints
    def foo(arg: int | Literal(str.isupper)) -> int:
        return arg

    foo(12)
    with raises(TypeError): 
        foo("BANANA")


def test_check_hints14():
    from dataclasses import dataclass

    @check_hints
    @dataclass
    class Bot:
        alignment: bool
        serial: int
        name: str
    Bot(False, 12, "2")