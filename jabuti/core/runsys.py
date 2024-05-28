from jabuti.core.block import Block



class RunSystem:
    def __init__(self, blocks: list[Block] = None) -> None:
        self.blocks: list[Block] = []
        self.awaiting: list[Block] = []
        self.finished: bool = False
        if blocks is not None:
            self.blocks.extend(blocks)
    
    def register_block(self, block: Block) -> None:
        if block in self.blocks:
            return
        self.blocks.append(block)
    
    def reset_blocks(self) -> None:
        self.finished = False
        for block in self.blocks:
            block.reset()
        self.awaiting = self.blocks.copy()
    
    def run_next(self) -> None:
        if not self.awaiting or self.finished:
            print(f"Nothing to run")
            return
        
        for block in self.awaiting:
            if block.is_ready() and not block.status:
                # print(f"Running block {block}")
                block.run()
                return
        
        self.finished = True
        # print(f"No blocks left to run")
    
    def run_loop(self) -> None:
        self.reset_blocks()
        while not self.finished:
            self.run_next()
