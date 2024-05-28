from jabuti.core.block import AutoBlock



class BlockSum(AutoBlock):
    def __init__(self, name: str) -> None:
        def func(nums: list):
            return sum(nums)
        super().__init__(name, func, {"sum": float})

class BlockAdd(AutoBlock):
    def __init__(self, name: str) -> None:
        def func(num1: float, num2: float):
            return num1 + num2
        super().__init__(name, func, {"sum": float})

class BlockDiv(AutoBlock):
    def __init__(self, name: str) -> None:
        def func(num: float, div: float):
            return num / div
        super().__init__(name, func, {"result": float})

class BlockInv(AutoBlock):
    def __init__(self, name: str) -> None:
        def func(num: float):
            return -num
        super().__init__(name, func, {"inv": float})
