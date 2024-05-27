from jabuti.core.block import AutoBlock
import pandas as pd

class BlockUnion(AutoBlock):
    def __init__(self, name: str) -> None:
        def func(df1: pd.DataFrame, df2: pd.DataFrame):
            return pd.concat((df1, df2), ignore_index=True)
        super().__init__(name, func, {"sum": float})
