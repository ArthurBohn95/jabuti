from typing import Any

from jabuti.core.anchor import Input, Output

class Link:
    def __init__(self, name: str, output: Output, _input: Input) -> None:
        assert isinstance(output, Output)
        assert isinstance(_input, Input)
        
        self.name: str = name
        self.backref: Output = output
        self.nextref: Input = _input
        
        self.backref.add_link(self)
        self.nextref.add_link(self)
        
        # If the output is ready, tells the input to check
        if self.backref.status:
            self.propagate()
        
        bvt = self.backref.vtype
        nvt = self.nextref.vtype
        if (bvt is not None and nvt is not None
            and bvt != nvt and nvt != "sequence"):
            print(f"Link '{self.name}' is bad: {bvt} -> {nvt}")
    
    def __repr__(self) -> str:
        return f"<link> name:{self.name} conn:{self.backref.name}<>{self.nextref.name}"
    
    def get_value(self) -> Any:
        return self.backref.value
    
    def get_status(self) -> bool:
        return self.backref.status
    
    def unlink(self) -> None:
        self.backref.rmv_link(self)
        self.nextref.rmv_link(self)
    
    def propagate(self) -> None:
        self.nextref.check()
