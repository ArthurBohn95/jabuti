import inspect
from typing import Callable

from jabuti.core.anchor import Input, Output



class Block:
    def __init__(self,function: Callable = None, inputs: list[Input] = None, outputs: list[Output] = None) -> None:
        # self.name: str = name
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
        self.enabler: Input = Input("enable", bool, True)
        self.runflag: Output = Output("status", bool, False)
    
    def __repr__(self) -> str:
        return f"[block] function:{self.function.__name__} status:{self.status} enabled:{self.enabler.value}"
    
    def __getitem__(self, item: str) -> Input | Output:
        if len(item) < 2:
            return
        
        io, name = item[0], item[1:]
        if io == '>':
            return self.inputs.get(name, None)
        if io == '<':
            return self.outputs.get(name, None)
        
        # print(f"Anchor {name} does not exist")
    
    def reset(self) -> None:
        self.status = False
        self.result = None
        for _in in self.inputs.values():
            _in.reset()
        for _out in self.outputs.values():
            _out.reset()
        self.runflag.reset()
    
    def is_ready(self) -> bool:
        return self.check_inputs() and self.enabler
    
    def register_inputs(self, inputs: list[Input]) -> None:
        for _input in inputs:
            # print(f"Block '{self.name}' registered Input '{_input.name}'")
            self.inputs[_input.name] = _input
    
    def register_outputs(self, outputs: list[Output]) -> None:
        for _output in outputs:
            # print(f"Block '{self.name}' registered Output '{_output.name}'")
            self.outputs[_output.name] = _output
    
    def check_inputs(self) -> None:
        for _input in self.inputs.values():
            _input.check()
            if not _input.status:
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
        
        # The result is ordered: a tuple matching the outputs order # HELL NO
        # print(f"For some reason could not map the result to the outputs.")
    
    def run(self) -> None:
        self.enabler.check()
        if not self.enabler.value:
            # print(f"The block '{self.name}' is disabled")
            return
        
        if self.function is None:
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
    def __init__(self, values: dict[str, any]) -> None:
        super().__init__()
        for k, v in values.items():
            _output = Output(k, type(v))
            _output.set(v)
            self.outputs[k] = _output
        self.status: bool = True

class AutoBlock(Block):
    def __init__(self, function: Callable, outputs: dict[str, type] = None) -> None:
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
            self.inputs[name] = Input(name, _type)
        
        if outputs is not None:
            for name, _type in outputs.items():
                self.outputs[name] = Output(name, _type)
