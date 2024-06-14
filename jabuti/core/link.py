from jabuti.core.anchor import Input, Output



class Link:
    def __init__(self, output: Output, _input: Input) -> None:
        assert isinstance(output, Output)
        assert isinstance(_input, Input)
        
        self.backref: Output = output
        self.nextref: Input = _input
        
        self.backref.add_link(self)
        self.nextref.add_link(self)
        
        # If the output is ready, tells the input to check
        if self.backref.status:
            self.propagate()
        
        self.healthy: bool = True
        bvt = self.backref.vtype
        nvt = self.nextref.vtype
        if bvt is not None and nvt is not None and bvt != nvt:
            self.healthy = False
            # print(f"Link is bad: {bvt} -> {nvt}")
    
    def __repr__(self) -> str:
        a0 = f"{self.backref.block.name}.{self.backref.name}"
        a1 = f"{self.nextref.block.name}.{self.nextref.name}"
        return f"<link::Link {a0}-->{a1}>"
    
    def _export(self) -> str:
        a0 = f"{self.backref.block.idf}<{self.backref.name}"
        a1 = f"{self.nextref.block.idf}>{self.nextref.name}"
        return f"{a0}-{a1}"
    
    def get_value(self) -> any:
        return self.backref.value
    
    def get_status(self) -> bool:
        return self.backref.status
    
    def unlink(self) -> None:
        self.backref.rmv_link(self)
        self.nextref.rmv_link(self)
    
    def propagate(self) -> None:
        self.nextref.check()
