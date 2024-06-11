import random
import tkinter as tk
import tkinter.font as tkfont
from typing import Literal

import jabuti as jb


# region consts and utils
GAP = 24              # [12, 16, 24, 32, 40]
BSIZE = 4             # block size in GAPs
ASIZE = GAP / 4 / GAP # anchor radius in GAPs, don't ask me how it works, it just works
WIDTH = 56 * GAP
HEIGHT = 32 * GAP
FONT1 = ("consolas", int(GAP/2.5))
FONT2 = ("consolas", int(GAP/3.0))

#print(f"{FONT1 = }")
#print(f"{FONT2 = }")

BG_COLOR = "#202020"
GRID_COLOR = "#424242"
LINK_COLOR = "#D0D0D0"
LABEL_COLOR = "#F0F0F0"
ANCHOR_COLOR = "#10A010"



def snap(num: float, base: float) -> float:
    return base * round(num/base)

def calc_line_points(
    p0: tuple[int, int],
    p1: tuple[int, int],
    orient: str,
    gap: float,
    ) -> tuple[int, ...]:
    # TODO: Improve line pathing
    mid = []
    xdif = p1[0] - p0[0]
    ydif = p1[1] - p0[1]
    match orient.lower():
        case "h-h":
            if xdif >= 2 * gap:
                mid = [
                    p0[0] + gap, p0[1],
                    p1[0] - gap, p1[1],
                ]
        
        case "v-v":
            if ydif > 2 * gap:
                mid = [
                    p0[0], p0[1] + gap,
                    p1[0], p1[1] - gap,
                ]
        
        case "h-v":
            pass
    
    return *p0, *mid, *p1

def calc_link_shape(a0: "GUIAnchor", a1: "GUIAnchor") -> tuple[int, ...]:
    orient = f"{a0.orient}-{a1.orient}"
    return calc_line_points(a0.center(), a1.center(), orient, GAP)



# region GUI Objects
class GUIObjBase:
    def __init__(self, id: int, tag: str, canvas: tk.Canvas) -> None:
        self.id: int = id
        self.tag: str = tag
        self.canvas: tk.Canvas = canvas
        self.can_grab: bool = False
    
    def __repr__(self) -> str:
        return f"id:{self.id} tag:{self.tag}"
    
    def rmv(self) -> None:
        pass
    
    def pos(self) -> tuple[int, int, int, int]:
        return self.canvas.coords(self.id)
    
    def center(self) -> tuple[float, float]:
        pos = self.canvas.coords(self.id)
        cx = (pos[0] + pos[2]) / 2
        cy = (pos[1] + pos[3]) / 2
        return cx, cy
    
    def update_shape(self) -> None:
        pass

class GUILink(GUIObjBase):
    def __init__(self, id: int, tag: str, canvas: tk.Canvas) -> None:
        super().__init__(id, tag, canvas)
        self.anchors: tuple["GUIAnchor", "GUIAnchor"] = None
    
    def rmv(self) -> None:
        for anchor in self.anchors:
            anchor.links.pop(self.id, None)
        self.anchors = None
    
    def update_shape(self) -> None:
        pts = calc_link_shape(self.anchors[0], self.anchors[1])
        self.canvas.coords(self.id, pts)

class GUILabel(GUIObjBase):
    def __init__(self, id: int, tag: str, canvas: tk.Canvas, parent: "GUIObject", text: str) -> None:
        super().__init__(id, tag, canvas)
        self.text: str = text
        self.parent: "GUIObject" = parent
        self.can_grab = False
    
    def rmv(self) -> None:
        self.parent = None

class GUIAnchor(GUIObjBase):
    def __init__(self, id: int, tag: str, canvas: tk.Canvas, block: "GUIBlock", type: Literal["in", "out"], orient: Literal["h", "v"]) -> None:
        super().__init__(id, tag, canvas)
        self.type: str = type
        self.block: "GUIBlock" = block
        self.label: "GUILabel" = None
        self.links: dict[int, "GUILink"] = {}
        self.orient: str = orient
    
    def rmv(self) -> None:
        # for link in self.links.values():
        #     link.rmv()
        self.label.rmv()
        self.label = None
        self.block = None
        self.links = None

class GUIBlock(GUIObjBase):
    def __init__(self, id: int, tag: str, canvas: tk.Canvas) -> None:
        super().__init__(id, tag, canvas)
        self.can_grab = True
        self.label: "GUILabel" = None
        self.anchors: dict[int, GUIAnchor] = {}
        self.enabler: GUIAnchor = None
        self.runflag: GUIAnchor = None
    
    def rmv(self):
        self.label.rmv()
        self.label = None
        for link in self.get_links():
            link.rmv()
        for anchor in self.anchors.values():
            anchor.rmv()
        self.anchors = None
    
    def get_links(self) -> list[GUILink]:
        links = []
        for anchor in self.anchors.values():
            links.extend(anchor.links.values())
        links.extend(self.enabler.links.values())
        links.extend(self.runflag.links.values())
        return [l for l in links if l is not None]
    
    def get_labels(self) -> list[GUILabel]:
        labels = [self.label]
        for anchor in self.anchors.values():
            labels.append(anchor.label)
        labels.extend([self.enabler.label, self.runflag.label])
        return [l for l in labels if l is not None]
    
    def get_all_ids(self) -> list[int]:
        ids = [self.label.id]
        ids.extend(list(self.anchors.keys()))
        ids.append(self.enabler.id)
        ids.append(self.runflag.id)
        ids.extend([link.id for link in self.get_links()])
        ids.extend([label.id for label in self.get_labels()])
        return set(ids)
    
    def update_shape(self) -> None:
        for link in self.get_links():
            link.update_shape()

GUIObject  = GUIBlock | GUIAnchor | GUILink
CoreObject = jb.Block | jb.Anchor | jb.Link


# region IdManager
class IDManager:
    def __init__(self) -> None:
        self.id2tag: dict[int, str] = {}
        self.id2obj: dict[int, GUIObject] = {}
        self.id2core: dict[int, CoreObject] = {}
        self.counts: dict[str, int] = {}
    
    def __contains__(self, item) -> bool:
        return item in self.id2tag or item in self.id2obj or item in self.id2core
    
    def __getitem__(self, key) -> tuple[str, GUIObject]:
        return self.id2tag.get(key, None), self.id2obj.get(key, None), self.id2core.get(key, None)
    
    def tag(self, id: int) -> str:
        return self.id2tag.get(id, None)
    
    def obj(self, id: int) -> GUIObject:
        return self.id2obj.get(id, None)
    
    def core(self, id: int) -> CoreObject:
        return self.id2core.get(id, None)
    
    def reg(self, id: int, tag: str, obj: GUIObject, core: CoreObject = None) -> None:
        self.id2tag[id] = tag
        self.id2obj[id] = obj
        self.id2core[id] = core
    
    def pop(self, id: int) -> tuple[str, GUIObject]:
        return self.id2tag.pop(id, None), self.id2obj.pop(id, None), self.id2core.pop(id, None)
    
    def rmv(self, id: int) -> None:
        self.pop(id)
    
    def _tag_count(self, tag: str) -> str:
        count = self.counts.get(tag, 0) + 1
        self.counts[tag] = count
        return f"{tag}{count}"



# region PopMenu
# source: https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
class PopMenu(tk.Menu):
    def __init__(self, parent: tk.Canvas) -> None:
        super().__init__(parent, tearoff=0)
        self.submenus: dict[str, tk.Menu] = {}
    
    def handle_selection(self, value) -> None:
        print(f"{value = }")
    
    def show(self, event: tk.Event) -> None:
        self.post(event.x_root, event.y_root)
    
    def add_submenu(self, name: str, options: list[str]) -> None:
        # https://stackoverflow.com/questions/74907864/using-the-menu-add-command-function-in-a-for-loop-only-uses-the-last-iterable
        
        submenu = tk.Menu(self, tearoff=0)
        for option in options:
            label = f"{name}/{option}"
            submenu.add_command(label=option, font=FONT2,
                command=lambda label=label: self.handle_selection(value=label))
        
        self.add_cascade(label=name, menu=submenu, font=FONT1)
        self.submenus[name] = submenu
    
    def add_submenus(self, data: dict[str, list[str]]) -> None:
        for name, options in data.items():
            self.add_submenu(name, options)



# region Board
default_drag_data = {"id": None, "tag": None, "obj": None, "event": None}
class Board:
    def __init__(self, master):
        self.master: tk.Tk = master
        self.canvas: tk.Canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
        self.idmgr: IDManager = IDManager()
        
        self.tag_counts: dict[str, int] = {}
        
        self.drag_data: dict[str, int | str | GUIObject | tk.Event] = default_drag_data
        self.link_data: list[GUIAnchor] = []
        
        self.pop_menu: PopMenu = PopMenu(self.canvas)
        self.pop_menu.add_submenus({
            "math": ["add", "sub", "mult", "div", "inv", "abs", "pow", "sqrt", "min", "max", "avg", "sum"],
            "text": ["format", "replace", "concat"],
            "json": ["load", "dump"],
            "table": ["read_csv", "write_csv", "left_join", "union"],
            "API": ["request", "get", "post"],
            "SQL": ["SELECT", "DELETE", "UPDATE", "DROP"],
        })
        self.canvas.bind("<Button-3>", self.pop_menu.show)
        self.canvas.bind("<Button-1>", lambda event: self.pop_menu.unpost())
        
        self.__create_grid()
        
        # Events binding
        self.canvas.bind("<Double-1>",         self.on_create_block)
        self.canvas.bind("<Control-Button-1>", self.on_remove)
        self.master.bind("<space>",            self.dbg_print_all)
        self.master.bind("<Escape>",           self.on_clear_all)
    
    def __create_grid(self) -> None:
        for y in range(0, HEIGHT, GAP):
            self.canvas.create_line((0, y, WIDTH, y), dash=(1, 5), fill=GRID_COLOR, tags=("grid", "background"))
        for x in range(0, WIDTH, GAP):
            self.canvas.create_line((x, 0, x, HEIGHT), dash=(1, 5), fill=GRID_COLOR, tags=("grid", "background"))
        self.canvas.pack()
    
    def clear_links(self) -> None:
        for anchor in self.link_data:
            self.canvas.itemconfig(anchor.id, width=1) # Revert anchor thickness to 3
        self.link_data = []
    
    def clear_drag(self) -> None:
        self.drag_data = default_drag_data
    
    def on_clear_all(self, event: tk.Event) -> None:
        self.clear_drag()
        self.clear_links()
    
    def place_tag_snap(self, tag: str, x: float, y: float) -> None:
        x = snap(x, GAP) - 1
        y = snap(y, GAP) - 1
        self.canvas.moveto(tag, x, y)
    
    
    # region creators
    def _create_link(self) -> tuple[int, str, GUILink]:
        a0, a1 = self.link_data
        ca0: jb.Anchor = self.idmgr.core(a0.id)
        ca1: jb.Anchor = self.idmgr.core(a1.id)
        
        #  on the same block       of same anchor type       for different purposes
        if a0.block == a1.block or type(ca0) == type(ca1) or ca0.vtype != ca1.vtype:
            self.clear_links()
            return
        
        if a1.type == "out": # Output -> Input, otherwise inverts them
            a0, a1 = a1, a0
        
        pts = calc_link_shape(a0, a1)
        tag = self.idmgr._tag_count("link")
        params = dict(width=2.5, fill=LINK_COLOR, arrow="last")
        if a0.orient == "v":
            params["dash"] = (1, 5)
            params["width"] = 3
        id = self.canvas.create_line(pts, tags=("link", tag, a0.tag, a1.tag), **params)
        obj = GUILink(id, tag, self.canvas)
        obj.anchors = (a0, a1)
        a0.links[id] = obj
        a1.links[id] = obj
        self.idmgr.reg(id, tag, obj)
        
        # TODO: Improve z position
        self.canvas.tag_raise(id, "block")
        self.canvas.tag_lower(id, "anchor")
        
        return id, tag, obj
    
    def _create_label(self, parent: GUIAnchor | GUIBlock, text: str) -> tuple[int, str, GUIAnchor]:
        tags = [parent.tag]
        if isinstance(parent, GUIAnchor):
            just, offset = {
                ("in",  "h") : ("w", (  ASIZE*2.5, ASIZE )),
                ("out", "h") : ("e", ( -ASIZE/2,   ASIZE )),
                ("in",  "v") : ("n", (  ASIZE/2,   ASIZE*1.5 )), # DNU
                ("out", "v") : ("s", (  ASIZE/2,   0 )),         # DNU
            }.get((parent.type, parent.orient))
            
            pos = parent.pos()
            x = pos[0] + offset[0] * GAP
            y = pos[1] + offset[1] * GAP
            tags.append(parent.block.tag)
        
        elif isinstance(parent, GUIBlock):
            just = "n"
            # pos = parent.pos()
            # x = (pos[0] + pos[2]) / 2
            # y = pos[1] + FONT2[1] * 1.5
            x, y = parent.center()
            font = tkfont.Font(font=FONT2)
            h = font.metrics("linespace")
            y -= len(text.split('\n') * h) / 2
        
        else:
            return
        
        tag = self.idmgr._tag_count("label")
        tags.append(tag)
        id = self.canvas.create_text(
            x, y, justify="center",
            text=text, anchor=just,
            fill=LABEL_COLOR, font=FONT2,
            tags=tags
        )
        obj = GUILabel(id, tag, self.canvas, parent, tag)
        self.idmgr.reg(id, tag, obj)
        
        return id, tag, obj
    
    def parse_anchor(self, block: GUIBlock, anchor: jb.Anchor, pos: tuple[int, int], ofs: tuple[int, int], type: str, orient: str) -> tuple[int, str, GUIAnchor]:
        x, y = pos[0] + ofs[0], pos[1] + ofs[1]
        x0 = (x - ASIZE) * GAP
        y0 = (y - ASIZE) * GAP
        x1 = (x + ASIZE) * GAP - 1 # subpixel
        y1 = (y + ASIZE) * GAP - 1 # subpixel
        
        tag = self.idmgr._tag_count("anchor")
        match anchor.vtype:
            case "value":
                id = self.canvas.create_oval(x0-1, y0-1, x1+1, y1+1, fill=ANCHOR_COLOR, tags=("anchor", tag, block.tag))
            case "flag":
                id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=ANCHOR_COLOR, tags=("anchor", tag, block.tag))
            case _:
                return
        
        obj = GUIAnchor(id, tag, self.canvas, block, type, orient)
        self.idmgr.reg(id, tag, obj, anchor)
        self.canvas.tag_bind(id, "<ButtonPress-1>", self.on_create_link)
        
        if orient == "h":
            _, _, lobj = self._create_label(obj, anchor.name)
            # print(f"label object {lobj = }")
            obj.label = lobj
        
        return id, tag, obj
    
    def parse_block(self, block: jb.Block, pos: tuple[float, float]) -> tuple[int, str, GUIBlock]:
        size = block._size() + 1
        color = f"#{random.randint(32, 160):02x}{random.randint(32, 160):02x}{random.randint(32, 160):02x}"
        
        # Position calculation
        x0 = pos[0]     * GAP
        y0 = pos[1]     * GAP
        x1 = x0 + BSIZE * GAP # - 1 # subpixel
        y1 = y0 + size  * GAP # - 1 # subpixel
        
        # BLOCK creation
        tag = self.idmgr._tag_count("block")
        id = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, tags=("block", tag))
        obj = GUIBlock(id, tag, self.canvas)
        self.idmgr.reg(id, tag, obj, block)
        
        # ANCHORS
        for anchor, type, orient, ofs in block._export_anchors():
            # pos = x0 + ofs[0]*GAP*BSIZE, y0 + ofs[1]*GAP
            a_id, _, a_obj = self.parse_anchor(obj, anchor, pos, (ofs[0]*BSIZE, ofs[1]), type, orient)
            match anchor.name:
                case "enabler":
                    obj.enabler = a_obj
                case "runflag":
                    obj.runflag = a_obj
                case _:
                    obj.anchors[a_id] = a_obj
        
        _, _, lobj = self._create_label(obj, block.__class__.__name__)
        # print(f"label object {lobj = }")
        obj.label = lobj
        
        self.canvas.tag_bind(tag, "<ButtonPress-1>",   self.on_block_press)
        self.canvas.tag_bind(tag, "<B1-Motion>",       self.on_block_motion)
        self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_block_release)
        
        return id, tag, obj
    
    
    # region events
    def __find_block(self, event: tk.Event) -> tuple[int, str, GUIObject]:
        empty = (None, None, None)
        
        prev = None
        for _ in range(3):
            id = self.canvas.find_closest(event.x, event.y, halo=0, start=prev)[0]
            if id not in self.idmgr:
                return empty
            
            tag, obj, _ = self.idmgr[id]
            if obj.can_grab:
                return id, tag, obj
            
            prev = tag
        
        return empty
    
    def on_block_press(self, event: tk.Event) -> None:
        id, tag, obj = self.__find_block(event)
        if id is None:
            self.clear_drag()
            return
        
        self.drag_data = {"id": id, "tag": tag, "obj": obj, "event": event}
    
    def on_block_motion(self, event: tk.Event) -> None:
        if self.drag_data["id"] is None:
            return
        
        delta_x = event.x - self.drag_data["event"].x
        delta_y = event.y - self.drag_data["event"].y
        self.canvas.move(self.drag_data["tag"], delta_x, delta_y)
        self.drag_data["event"] = event
        self.drag_data["obj"].update_shape()
    
    def on_block_release(self, event: tk.Event) -> None:
        if self.drag_data["id"] is None:
            return
        
        x, y, *_ = self.canvas.coords(self.drag_data["id"])
        self.place_tag_snap(self.drag_data["tag"], x, y)
        self.drag_data["obj"].update_shape()
        self.clear_drag()
    
    
    def on_remove(self, event: tk.Event) -> None:
        id, tag, obj = None, None, None
        prev = None
        found = False
        for _ in range(5):
            id = self.canvas.find_closest(event.x, event.y, halo=0, start=prev)[0]
            if id not in self.idmgr:
                continue
            
            tag, obj, _ = self.idmgr[id]
            if isinstance(obj, (GUIBlock, GUILink)):
                found = True
                break
            
            prev = tag
        
        if not found:
            return
        
        self.idmgr.rmv(id)
        self.canvas.delete(tag)
        
        # print(f"del {tag=}")
        if tag.startswith("block"):
            # print(f"{obj.get_all_ids() = }")
            for id in obj.get_all_ids():
                self.idmgr.rmv(id)
                self.canvas.delete(id)
        
        obj.rmv()
    
    def on_create_block(self, event: tk.Event) -> None:
        x0 = int(event.x/GAP)
        y0 = int(event.y/GAP)
        blocks = [jb.builtin.Abs, jb.builtin.Sum, jb.builtin.Div, jb.builtin.Cmp]
        block = random.choice(blocks)
        self.parse_block(block(), (x0, y0))
    
    def on_create_link(self, event: tk.Event) -> None:
        if event.state & 0x4:
            return
        
        id = self.canvas.find_closest(event.x, event.y, halo=ASIZE)[0]
        if not id in self.idmgr:
            return
        
        tag, obj, _ = self.idmgr[id]
        if not tag.startswith("anchor"):
            return
        
        self.canvas.itemconfig(id, width=3) # Set anchor thickness to 3
        
        if obj not in self.link_data:
            self.link_data.append(obj)
        
        if len(self.link_data) == 2:
            self._create_link()
            self.clear_links()
    
    
    # region debuggers
    def dbg_print_all(self, event: tk.Event) -> None:
        print(f"{self.idmgr.id2tag =}")
        print(f"{self.idmgr.id2core=}")
        # print(f"{self.idmgr.id2obj = }")
        allids = [i for i in self.canvas.find_all() if i in self.idmgr]
        print(f"{allids = }")
    
    def dbg_block_links(self, event: tk.Event) -> None:
        id = self.canvas.find_closest(event.x, event.y)[0]
        if not id in self.idmgr:
            return
        
        tag, obj, _ = self.idmgr[id]
        if not tag.startswith("block"):
            return
        
        links = obj.get_links()
        
        print(f"{id=} {tag=} {links=}")



# region main
if __name__ == "__main__":
    root = tk.Tk()
    app = Board(root)
    # root.wm_state('zoomed')
    root.mainloop()
