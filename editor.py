from entities import EditorButton


class Editor:
    """ A set of development tools that improves productivity. """

    def __init__(self, game):
        self.game = game
        self.ui_objects = []
        EditorButton(
            game, 10, 10,
            self.game.add_block, (32, 42),
            "block"
        )
        EditorButton(
            game, 22, 10,
            self.game.add_bush, [32, 42],
            "tree_m"
        )

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

    def update(self, dt):
        for o in self.ui_objects:
            o.update(dt)

    def render(self, dt):
        for o in self.ui_objects:
            if not o.batch:
                o.draw()


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
