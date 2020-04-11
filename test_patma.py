import array
import dataclasses

from patma import *


@dataclasses.dataclass
class MyClass:
    x: int
    y: str


def test_constant_pattern():
    # case 42:
    pat = ConstantPattern(42)
    assert pat.match(42) == {}
    assert pat.match(0) is None
    assert pat.match(42.0) is None
    assert pat.match("42") is None


def test_constant_float_pattern():
    # case 42.0:
    pat = ConstantPattern(42.0)
    assert pat.match(42.0) == {}
    assert pat.match(42) == {}
    assert pat.match(0.0) is None
    assert pat.match(0) is None


def test_alternatives_pattern():
    # case 1|2|3:
    pat = AlternativesPattern([ConstantPattern(i) for i in [1, 2, 3]])
    assert pat.match(1) == {}
    assert pat.match(2) == {}
    assert pat.match(3) == {}
    assert pat.match(3.0) is None
    assert pat.match(0) is None
    assert pat.match(4) is None
    assert pat.match("1") is None


def test_fancy_alternatives_pattern():
    # case [1, 2] | [3, 4]:
    pat = AlternativesPattern(
        [
            SequencePattern([ConstantPattern(1), ConstantPattern(2)]),
            SequencePattern([ConstantPattern(3), ConstantPattern(4)]),
        ]
    )
    assert pat.match([1, 2]) == {}
    assert pat.match([3, 4]) == {}
    assert pat.match(42) is None
    assert pat.match([2, 3]) is None
    assert pat.match([1, 2, 3]) is None
    assert pat.match([1, 2.0]) is None


def test_variable_pattern():
    # case x:
    pat = VariablePattern("x")
    assert pat.match(42) == {"x": 42}
    assert pat.match((1, 2)) == {"x": (1, 2)}
    assert pat.match(None) == {"x": None}


def test_annotated_pattern():
    # case (x: int):
    pat = AnnotatedPattern(VariablePattern("x"), int)
    assert pat.match(42) == {"x": 42}
    assert pat.match("hello") is None


def test_int_matches_float():
    # case (x: float):  # Should match int
    pat = AnnotatedPattern(VariablePattern("x"), float)
    assert pat.match(42) == {"x": 42}
    assert type(pat.match(42)["x"]) == int


def test_float_doesnt_match_int():
    # case (x: int):  # Shouldn't match 1.0
    pat = AnnotatedPattern(VariablePattern("x"), int)
    assert pat.match(1.0) is None


def test_sequence_pattern():
    # case (x, y, z):
    pat = SequencePattern([VariablePattern(s) for s in "xyz"])
    assert pat.match((1, 2, 3)) == {"x": 1, "y": 2, "z": 3}
    assert pat.match((1, 2)) is None
    assert pat.match((1, 2, 3, 4)) is None
    assert pat.match(123) is None
    # Check that character/byte strings don't match sequences
    assert pat.match("abc") is None
    assert pat.match(b"abc") is None
    assert pat.match(array.array("b", b"abc")) is None
    ## assert pat.match(memoryview(b'abc')) is None
    ## assert pat.match(bytearray(b'abc')) is None


def test_instance_pattern():
    # case MyClass(xx: int, y='hello'):
    vxx = AnnotatedPattern(VariablePattern("xx"), int)
    hello = ConstantPattern("hello")
    pat = InstancePattern(MyClass, [vxx], {"y": hello})
    match = pat.match(MyClass(42, "hello"))
    assert match == {"xx": 42}


def test_walrus_pattern():
    # case x := (p, q):
    pat = WalrusPattern("x", SequencePattern([VariablePattern(s) for s in "pq"]))
    assert pat.match((1, 2)) == {"p": 1, "q": 2, "x": (1, 2)}
    assert pat.match([1, 2]) == {"p": 1, "q": 2, "x": [1, 2]}
    assert pat.match(12) is None
    assert pat.match((1, 2, 3)) is None
