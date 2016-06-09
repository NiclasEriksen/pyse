from entities import EditorButton, Block, ForegroundImage, InputListener
# from utils.ebs import Entity


class Editor:
    """ A set of development tools that improves productivity. """

    def __init__(self, world):
        self.world = world
        self.ui_objects = []
        self.selected_block = None
        self.input_left = InputListener(world, self.add_block)
        self.input_left = InputListener(
            world, self.clear_selection, btn="right"
        )
        EditorButton(
            world, 10, 10,
            self.select_block, "block",
            "block"
        )
        EditorButton(
            world, 22, 10,
            self.select_block, "tree",
            "tree_m"
        )
        self.blocks = dict(
            block=Block,
            tree=ForegroundImage
        )

    def clear_selection(self):
        self.world.log.debug("Selection cleared.")
        self.selected_block = None

    def select_block(self, name):
        print("block: {0} name: {0}".format(self.selected_block, name))
        self.selected_block = str(name)

    def add_block(self):
        if self.selected_block:
            # print(self.selected_block)
            x, y = self.world.mouse_x, self.world.mouse_y
            try:
                b = self.blocks[self.selected_block]
            except KeyError:
                return False
            else:
                b(self.world, x=x, y=y)

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
