import inspect
from typing import Callable

from jabuti.core.anchor import Anchor, Input, Output



class Block:
    def __init__(self,
            function: Callable = None,
            inputs: list[Input] = None,
            outputs: list[Output] = None,
        ) -> None:
        self.idf: str = None
        self.name: str = self.__class__.__name__
        self.status: bool = False
        self.result: any = None
        self.function: Callable = function
        
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}
        
        if inputs is not None:
            self.register_inputs(inputs)
        
        if outputs is not None:
            self.register_outputs(outputs)
        
        # Creates the specific flow controlling IOs
        self.enabler: Input = Input(self, "enabler", bool, True, "flag")
        self.runflag: Output = Output(self, "runflag", bool, False, "flag")
    
    def __repr__(self) -> str:
        info = [
            f"[block::{self.name}",
            f"enabled:{self.enabler.value}" if self.enabler is not None else None,
            f"status:{self.status}" if self.status is not None else None,
        ]
        return ' '.join([i for i in info if i is not None]) + ']'
    
    def __getitem__(self, item: str) -> Input | Output:
        if len(item) < 2:
            return
        
        io, name = item[0], item[1:]
        if io == '>': return self.inputs.get(name, None)
        if io == '<': return self.outputs.get(name, None)
        
        print(f"Anchor {name} does not exist")
    
    def _size(self) -> int:
        return max(len(self.inputs), len(self.outputs))
    
    def _export(self) -> dict[str, any]:
        return {
            "name": f"{self.__module__}.{self.name}"
        }
    
    def _export_anchors(self) -> list[tuple[Anchor, str, str, tuple]]:
        ainfo = []
        for y, input in enumerate(self.inputs.values()):
            ainfo.append((input, "in", "h", (0, y+1)))
        for y, output in enumerate(self.outputs.values()):
            ainfo.append((output, "out", "h", (1, y+1)))
        if self.enabler is not None:
            ainfo.append((self.enabler, "in", "v", (0.5, 0)))
        if self.runflag is not None:
            ainfo.append((self.runflag, "out", "v", (0.5, self._size()+1)))
        return ainfo
    
    def reset(self) -> None:
        self.status = False
        self.result = None
        for input in self.inputs.values():
            input.reset()
        for output in self.outputs.values():
            output.reset()
        self.runflag.reset()
    
    def is_ready(self) -> bool:
        self.enabler.check()
        return self.check_inputs() and self.enabler.value
    
    def register_inputs(self, inputs: list[Input]) -> None:
        for input in inputs:
            # print(f"Block '{self.name}' registered Input '{_input.name}'")
            self.inputs[input.name] = input
    
    def register_outputs(self, outputs: list[Output]) -> None:
        for output in outputs:
            # print(f"Block '{self.name}' registered Output '{_output.name}'")
            self.outputs[output.name] = output
    
    def check_inputs(self) -> None:
        if not self.inputs: # ConfigBlock
            return True
        for input in self.inputs.values():
            input.check()
            if not input.status:
                # print(f"Input '{_input.name}' is not ready")
                return False
        return True
    
    def check_outputs(self) -> None:
        if not self.status:
            # print(f"Block did not run")
            return
        
        if not len(self.outputs):
            # print(f"No outputs to set")
            return
        
        # The result is simple: a scalar with only one output
        if not isinstance(self.result, (dict, tuple)) and len(self.outputs) == 1:
            list(self.outputs.values())[0].set(self.result)
            return
        
        # The result is named: a dict matching the outputs 
        if isinstance(self.result, (dict)):
            for k, v in self.result.items():
                # print(f"Matching {k=} ... ", end='')
                if k not in self.outputs:
                    # print(f"does not exist in the outputs")
                    continue
                self.outputs[k].set(v)
                # print(f"matched!")
            return
        
        # The result is ordered: a tuple matching the outputs order
        if isinstance(self.result, (tuple)):
            for value, output in zip(self.result, self.outputs.values()):
                output.set(value)
            return
        
        print(f"For some reason could not map the result to the outputs.")
    
    def run(self) -> None:
        self.reset()
        self.enabler.check()
        if not self.enabler.value:
            # print(f"The block '{self.name}' is disabled")
            return
        
        if self.function is None:
            # print(f"There is no function")
            return
        
        if not self.check_inputs():
            # print(f"Not all inputs are ready")
            return
        
        params = {i.name: i.value for i in self.inputs.values()}
        self.result = self.function(**params)
        self.status = True
        self.check_outputs()
        self.runflag.set(True)


class BlockConfig(Block):
    """Special block that only has outputs"""
    def __init__(self, values: dict[str, any]) -> None:
        super().__init__()
        self.result = values
        for k, v in values.items():
            output = Output(self, k, type(v))
            output.set(v)
            self.outputs[k] = output
        self.status: bool = True
        self.enabler = None
        self.runflag = None
    
    def __repr__(self) -> str:
        vals = ','.join(self.outputs.keys())
        return super().__repr__().replace(']', '') + f" values:{vals}]"
    
    def _export(self) -> dict[str, any]:
        exp = super()._export()
        exp.update({"params": {"values": self.result}})
        return exp
    
    def reset(self) -> None:
        pass
    
    def run(self) -> None:
        self.status = True
        self.check_outputs()
        self.runflag.set(True)


class AutoBlock(Block):
    """Uses the inspect.signature to fill out necessary parameters."""
    def __init__(self,
            function: Callable,
            outputs: dict[str, type] | list[str] = None,
            flag: bool = False,
        ) -> None:
        super().__init__(function)
        
        for param in inspect.signature(function).parameters.values():
            name = param.name
            _type = _type = param.annotation
            if _type == inspect._empty:
                if param.kind == inspect._ParameterKind.VAR_POSITIONAL:
                    _type = list
                elif param.kind == inspect._ParameterKind.VAR_KEYWORD:
                    _type = dict
                else:
                    _type = any
            self.inputs[name] = Input(self, name, _type)
        
        if outputs is not None:
            if flag:
                for name in outputs:
                    self.outputs[name] = Output(self, name, bool, False, "flag")
            else:
                for name, _type in outputs.items():
                    self.outputs[name] = Output(self, name, _type, vtype="value")
