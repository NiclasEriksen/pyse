from PIL import Image
from PIL.ImageOps import flip


def tile_img(img, width, height):
    # Opens an image
    bg = Image.open(img)
    # The width and height of the background tile
    bg_w, bg_h = bg.size
    # Creates a new empty image, RGB mode, and size 1000 by 1000
    new_im = Image.new('RGB', (width, height))

    # The width and height of the new image
    w, h = new_im.size

    # Iterate through a grid, to place the background tile
    for i in range(0, w, bg_w):
        for j in range(0, h, bg_h):
            # bg = Image.eval(bg, lambda x: x+(i+j)/1000)
            new_im.paste(bg, (i, j))

            # paste the image at location i, j:

    new_im = flip(new_im)

    return new_im.tobytes()
    # new_im.show()
