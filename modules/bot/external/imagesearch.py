import numpy as np
import random
import cv2


def imagesearcharea(window, image, x1, y1, x2, y2, precision=0.8, im=None, logger=None):
    """
    Searches for an image within an area

    input :
    window : window object being searched
    image : path to the image file (see opencv imread for supported types)
    x1 : top left x value
    y1 : top left y value
    x2 : bottom right x value
    y2 : bottom right y value
    precision : the higher, the lesser tolerant and fewer false positives are found, default is 0.8
    im : a PIL image, useful if you intend to search the same unchanging region for several elements

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not
    """
    if im is None:
        im = window.screenshot(region=(x1, y1, x2, y2))

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

    if isinstance(image, str):
        template = cv2.imread(image, 0)
    else:
        template = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    try:
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < precision:
            return [-1, -1]
        return max_loc

    # Catching our error, logging some information about it, and continuing our operation.
    # It seems like that an cv2.error is raised sometimes when attempting to run a cv2.matchTemplate.
    # I cant determine exactly how or why, but it's infrequent, safe to pass.
    except cv2.error as error:
        if logger:
            logger.exception("error occurred while trying to search for image: {image}".format(image=image))

        # Returning the default "not found" list value when our image search does fail.
        # Our log is present and if many errors are occurring, it can be debugged by users.
        return [-1, -1]


def click_image(window, image, position, button, offset=5, pause=0):
    """
    Click on the center of an image with a bit of randomness.
    """
    img = cv2.imread(image)
    height, width, channels = img.shape

    point = int(position[0] + r(width / 2, offset)), int(position[1] + r(height / 2, offset))
    window.click(point=point, button=button, offset=offset, pause=pause)


def r(num, rand):
    return num + rand * random.random()
