from entities import EditorButton, Block, ForegroundImage, InputListener, MouseBoundImage
# from utils.ebs import Entity


class Editor:
    """ A set of development tools that improves productivity. """

    def __init__(self, world):
        self.world = world
        self.ui_objects = []
        self.last_block = None
        self.selected_block = None
        self.mouse_img = None
        InputListener(world, self.add_block)
        InputListener(
            world, self.clear_selection, btn="right"
        )
        InputListener(
            world, self.select_block, params="block", type="kb", btn="_1"
        )
        InputListener(
            world, self.select_block, params="wood", type="kb", btn="_2"
        )
        InputListener(
            world, self.select_block, params="tree_m", type="kb", btn="_3"
        )
        InputListener(
            world, self.select_block, params="flower", type="kb", btn="_4"
        )
        EditorButton(
            world, 10, 10,
            self.select_block, "block",
            "block"
        )
        EditorButton(
            world, 22, 10,
            self.select_block, "wood",
            "wood"
        )
        EditorButton(
            world, 34, 10,
            self.select_block, "tree_m",
            "tree_m"
        )
        EditorButton(
            world, 46, 10,
            self.select_block, "flower",
            "flower"
        )
        self.blocks = dict(
            block=Block,
            wood=Block,
            tree_m=ForegroundImage,
            flower=ForegroundImage
        )

    def clear_selection(self):
        if self.selected_block:
            self.world.log.debug("Selection cleared.")
            self.selected_block = None
            self.mouse_img.delete()
            self.mouse_img = None

    def select_block(self, name):
        # print("block: {0} name: {0}".format(self.selected_block, name))
        self.world.log.debug("Block \"{0}\" selected.".format(name))
        self.selected_block = name
        if self.mouse_img:
            self.mouse_img.delete()
        self.mouse_img = MouseBoundImage(self.world, name)

    def add_block(self):
        if self.selected_block:
            x = self.world.mouse_x - round(self.world.offset_x)
            # print(self.world.mouse_x, self.world.offset_x, x)
            y = self.world.mouse_y - round(self.world.offset_y)
            try:
                b = self.blocks[self.selected_block]
            except KeyError:
                self.world.log.error(
                    "No such block: \"{0}\"".format(self.select_block)
                )
                return False
            else:
                self.last_block = b(
                    self.world, x=x, y=y, sprite=self.selected_block
                )
                self.world.log.debug("Spawning block {0}".format(b))

    def undo(self):
        if self.last_block:
            if hasattr(self.last_block, "staticphysicsbody"):
                if self.last_block.staticphysicsbody:
                    self.world.phys_space.remove(
                        self.last_block.staticphysicsbody.shape
                    )
            elif hasattr(self.last_block, "physicsbody"):
                if self.last_block.physicsbody:
                    for s in self.last_block.physicsbody.body.shapes:
                        self.world.phys_space.remove(s)
                    self.world.phys_space.remove(
                        self.last_block.physicsbody.body
                    )
            self.last_block.delete()
            self.last_block = None

    def show_context_for_obj(self, obj):
        """
            Show context menu for given object. Object needs to return a
            dictionary of title:methodcall when "obj.get_options()" is called.
        """
        pass

    def show_info_for_obj(self, obj):
        """
            Show info for given object, object should supply a dictionary of
            strings that will be shown here, through the function call
            "obj.get_info()".
        """
        pass

    def handle_mouse(self, x, y, dx=None, dy=None, btn=None):
        """ Takes pyglet mouse event data and handles it """
        pass

    def handle_keys(self, btn, mod):
        """ Takes pyglet style button/modifier flags. """
        pass


class UIObject:

    def __init__(
        self, batch,
        x, y, w, h,
        bgc="grey", fgc="white"
    ):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.bgc, self.fgc = bgc, fgc
        self.batch = batch
        self.sprite = None


class InfoObject(UIObject):

    def __init__(self, owner):
        self.owner = owner
        super().__init__(self, None, 5, 5, 20, 8)

    def draw(self):
        print("DRAWING")

    def update(self, dt):
        if self.owner:
            self.x, self.y = self.owner.x, self.owner.y
