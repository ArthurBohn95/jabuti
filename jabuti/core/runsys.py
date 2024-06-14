import typing
from jabuti.core.link import Link
from jabuti.core.block import Block
from jabuti.core.anchor import Anchor



class RunSystem:
    def __init__(self) -> None:
        self.links: dict[str, Link] = {}
        self.blocks: dict[str, Block] = {}
        self.counts: dict[str, int] = {"block": 0, "link": 0}
        
        self.block_maps: dict[str, dict[str, str | typing.Type]] = {}
        self._load_blocks()
        
        self.finished: bool = False
        self.awaiting: dict[int, Block] = {}
    
    def setup(self,
            blocks: dict[str, dict[str, str]] = None,
            links: dict[str, dict[str, str]] = None,
        ) -> None:
        
        if blocks is not None:
            maxb = 0
            for block_key, block_data in blocks.items():
                maxb = max(maxb, int(block_key.removeprefix('b')))
                block_class = block_data.get("class")
                args = block_data.get("args", [])
                params = block_data.get("params", {})
                self._build_block(block_class, block_key, *args, **params)
            self.counts["block"] = maxb
        
        if links is not None:
            maxl = 0
            for link_key, link_data in links.items():
                maxl = max(maxl, int(link_key.removeprefix('l')))
                self._build_link(link_data, link_key)
            self.counts["link"] = maxl
    
    @staticmethod
    def from_file(config_path: str) -> "RunSystem":
        import json
        
        conf: dict[str, dict[str, dict]]
        
        ext = config_path.split('.')[-1].lower()
        match ext:
            case 'json':
                import json
                with open(config_path, "r") as injson:
                    conf = json.load(injson)
            
            case 'toml':
                import tomllib
                with open("./tests/runsys/rs1.toml", 'rb') as intoml:
                    conf = tomllib.load(intoml)
            
            case _:
                print(f"Unsuported extension: '{ext}'")
                return None
        print(f"conf {ext}     = {conf}")
        
        rs = RunSystem()
        rs.setup(
            blocks=conf["blocks"],
            links=conf["links"],
        )
        
        return rs
    
    def __getitem__(self, item: str) -> Link | Block | Anchor:
        if len(item) < 2:
            return
        
        tag = item[0].lower()
        if tag == 'l':
            return self.links.get(item, None)                  # LINK
        
        if tag == 'b':
            if item in self.blocks:
                return self.blocks[item]                       # BLOCK
            
            if   '>' in item: idx = item.index('>')
            elif '<' in item: idx = item.index('<')
            else            : return None
            
            bk, ak = item[:idx], item[idx:]
            if bk not in self.blocks:
                return None
            
            block = self.blocks.get(bk)
            anchor = block[ak]
            return anchor                                      # ANCHOR
    
    def _build_block(self,
            block_class: str,
            block_key: str = None,
            *args,
            **params,
        ) -> None:
        if block_class not in self.block_maps:
            raise Exception(f"Block '{block_class}' not found")
        
        if block_key is None:
            block_key = f"b{self.__get_count('block', True)}"
        
        const = self.block_maps.get(block_class)["class"]
        block: Block = const(*args, **params)
        block.idf = block_key
        self.blocks[block_key] = block
    
    def _build_link(self, link_data: str, link_key: str = None) -> None:
        if link_key is None:
            link_key = f"l{self.__get_count('link', True)}"
        
        ak0, ak1 = link_data.split('-')
        a0: Anchor = self[ak0]
        a1: Anchor = self[ak1]
        
        if a0 is None or a1 is None:
            print(f"{ak0=} or {ak1=} does not exist")
            return
        
        link = Link(a0, a1)
        self.links[link_key] = link
    
    def _export(self) -> dict[str]:
        data = {
            "metadata": {
                "version": "0.1.5",
                # "counter": self.counts,
            },
            "blocks": {},
            "links": {},
        }
        
        for block_key, block_obj in self.blocks.items():
            exp = block_obj._export()
            data["blocks"][block_key] = exp
        
        for link_key, link_obj in self.links.items():
            data["links"][link_key] = link_obj._export()
        
        return data
    
    def __get_count(self, key: str, inc: bool = False) -> int:
        count = self.counts.get(key, 0)
        if inc:
            count += 1
        self.counts[key] = count
        return count
    
    
    
    def _get_elements(self) -> dict[str, dict[str]]:
        return {
            "links": self.links,
            "blocks": self.blocks,
        }
    
    def _load_blocks(self, clear: bool = False) -> None:
        import jabuti as jb
        import jabuti.utils.finder as finder
        
        clsdesc = finder.find_full_classes([jb.builtin, "./custom/"])
        if clear:
            self.block_maps = {}
        self.block_maps.update(clsdesc)
    
    def add_block(self, block: Block) -> int:
        if block in self.blocks.values():
            return 0
        block_id = self.__get_count("block", True)
        self.blocks[block_id] = block
        return block_id
    
    def rmv_block(self, block_id: int) -> Block:
        return self.blocks.pop(block_id, None)
    
    def add_link(self, ba0: tuple[int, str], ba1: tuple[int, str]) -> Link:
        b0: Block = self.blocks.get(ba0[0])
        b1: Block = self.blocks.get(ba1[0])
        link = b0[f"<{ba0[1]}"].link_with(b1[f">{ba1[1]}"])
        lid = self.__get_count("link", True)
        self.links[lid] = link
        return lid
    
    def rmv_link(self, link_id: int):
        if link_id not in self.links:
            return
        
        link = self.links.pop(link_id)
        link.unlink()
    
    def reset_blocks(self) -> None:
        self.finished = False
        for block in self.blocks.values():
            block.reset()
        self.awaiting = self.blocks.copy()
    
    def run_next(self) -> None:
        if not self.awaiting or self.finished:
            # print(f"Nothing to run")
            return
        
        for block in self.awaiting.values():
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
