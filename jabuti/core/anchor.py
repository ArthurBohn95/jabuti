from typing import Any, Literal, TYPE_CHECKING
if TYPE_CHECKING:
    from jabuti.core.link import Link
    from jabuti.core.block import Block



class Anchor:
    def __init__(self,
            block: "Block",
            name: str,
            _type: type,
            value: Any = None,
            vtype: Literal["value", "flag"] = "value",
        ) -> None:
        self.name: str = name
        self.type: type = _type
        self.vtype: str = vtype
        self.value: Any = value
        self.block: "Block" = block
        self.links: list["Link"] = []
        self.status: bool = False
        
        if value is not None:
            self.status = True
    
    def __repr__(self) -> str:
        _type = f"type:{self.vtype}({self.type.__name__})"
        _vals = f"value:{self.value} status:{self.status} links:{self.links}"
        return f"(anchor) name:{self.name} {_type} {_vals}"
    
    def rmv(self) -> None:
        self.block = None
    
    def reset(self) -> None:
        self.value = None
        self.status = False
    
    def add_link(self, link: "Link") -> None:
        if link in self.links:
            return
        self.links.append(link)
    
    def rmv_link(self, link: "Link") -> None:
        if link not in self.links:
            return
        self.links.remove(link)


class Input(Anchor):
    def check(self):
        if not self.links:
            self.status = False
            return
        
        for link in self.links:
            if not link.get_status():
                return
        
        if len(self.links) == 1:
            self.value = self.links[0].get_value()
        
        else:
            self.type = list
            values = []
            for link in self.links:
                value = link.get_value()
                if not isinstance(value, (list, set, tuple)):
                    value = [value]
                values.extend(value)
            self.value = values
            
            if self.vtype == "flag":
                self.value = all(self.value)
        
        self.status = True


class Output(Anchor):
    def set(self, value: Any) -> None:
        self.value = value
        self.status = True
        for link in self.links:
            link.propagate()
    
    def link_with(self, _input: Input) -> "Link":
        from jabuti.core.link import Link
        return Link(self, _input)
