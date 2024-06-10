from jabuti.core.block import AutoBlock



# region arithmetics
# sum: nums -> sum
# mult: nums -> mult
# div: num, den -> div, quo, rem
# inv: num -> inv

class Sum(AutoBlock):
    """A... -> A1+A2+..."""
    def __init__(self) -> None:
        def func(nums: list[float]):
            return sum(nums)
        super().__init__(func, {"sum": float})

class Mult(AutoBlock):
    """A... -> A1*A2*..."""
    def __init__(self) -> None:
        def func(nums: list[float]):
            res = 1
            for num in nums:
                res *= num
            return res
        super().__init__(func, {"mult": float})

class Div(AutoBlock):
    """A, B -> A/B, A//B, A%B"""
    def __init__(self) -> None:
        def func(num: float, den: float):
            return num / den, num // den, num % den
        super().__init__(func, {"div": float, "quo": float, "rem": float})

class Inv(AutoBlock):
    """A -> 1/A"""
    def __init__(self) -> None:
        def func(num: float):
            return 1 / num
        super().__init__(func, {"inv": float})

# region operations
# abs: num -> abs, neg
# pow: num, exp -> pow
# sqrt: num -> sqrt

class Abs(AutoBlock):
    """A -> |A|, -|A|"""
    def __init__(self) -> None:
        def func(num: float):
            abs_num = abs(num)
            return abs_num, -abs_num
        super().__init__(func, {"abs": float, "neg": float})

class Pow(AutoBlock):
    """A, B -> A^B"""
    def __init__(self) -> None:
        def func(num: float, exp: float):
            return num ** exp
        super().__init__(func, {"pow": float})

class Sqrt(AutoBlock):
    """A -> sqrt(A)"""
    def __init__(self) -> None:
        def func(num: float):
            return num ** 0.5
        super().__init__(func, {"sqrt": float})

# region statistics
# min
# max
# avg


