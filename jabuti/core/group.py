from jabuti.core.block import Block



class Group:
    def __init__(self, blocks: list[Block] = None, status: bool = True) -> None:
        self.status: bool = status
        self.blocks: list[Block] = []
        if blocks is not None:
            self.blocks.extend(set(blocks))
        
        self.update()
    
    def update(self, status: bool = None) -> None:
        if status is not None:
            self.status = status
        
        for block in self.blocks:
            block.enabler.value = self.status
