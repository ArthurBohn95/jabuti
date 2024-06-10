from jabuti.core.block import AutoBlock



class If(AutoBlock):
    """A -> True, False"""
    def __init__(self) -> None:
        def func(flag: bool):
            return flag, not flag
        super().__init__(func, ["t, f"], flag=True)

class Cmp(AutoBlock):
    """A, B -> A==B, A!=B, A<B, A<=B, A>B, A>=B"""
    def __init__(self) -> None:
        def func(x: float, y: float):
            return x==y, x!=y, x<y, x<=y, x>y, x>=y
        super().__init__(func, ["eq", "neq", "lt", "lte", "gt", "gte"], flag=True)
