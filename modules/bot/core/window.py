from modules.bot.core.globals import Globals
from modules.bot.core.enumerations import Button
from modules.bot.core.exceptions import WindowNotFoundError

from PIL import Image
from ctypes import windll
from threading import Lock

from enum import Enum

import win32gui
import win32ui
import win32api
import win32con

import random
import time
import json

# Use a threading lock to ensure that our window library can only attempt to
# take a single screenshot at any given time. This avoids issues with multiple
# sessions running at the same time and competing for windows resources.
_lock = Lock()

# Create a module level reference to our globals utility wrapper.
# We can use this to check if we should raise exceptions instead of
# running through normal functionality for windows.
_globals = Globals()


class Window(object):
    """
    Window objects encapsulate all of the functionality that handles window screenshots, clicks, drags in the background.
    """
    class ClickEvent(Enum):
        LEFT = [win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP]
        RIGHT = [win32con.WM_RBUTTONDOWN, win32con.WM_RBUTTONUP]
        MIDDLE = [win32con.WM_MBUTTONDOWN, win32con.WM_MBUTTONUP]

    # Storing some references to the available filtering options
    # for each supported emulator.
    class Filter(Enum):
        MEMU = ["memu"]
        NOX = ["nox", "noxplayer"]

        @classmethod
        def all(cls):
            """
            Grab and extend all available filters into a single list.
            """
            return sum([f.value for f in cls], [])

    # Local references to the windows32con library constants
    # that are used by the windows object in some way.
    class Event(Enum):
        MOUSE_MOVE = win32con.WM_MOUSEMOVE

    # Expected emulator height and width values that we must
    # have to ensure proper bot execution takes places.
    EMULATOR_WIDTH = 480
    EMULATOR_HEIGHT = 800

    def __init__(self, hwnd):
        """
        Initialize a new window object with the specified hwnd value.
        """
        self.hwnd = int(hwnd)
        self.subtract = 0

        # Depending on the type of emulator being used, some differences in thr way their window implementation
        # is handled exists, for example, the MEmu emulator includes the x axis value when we try to get the width
        # and height of the emulator, whereas the nox emulator does not include these values.
        if self.text in self.Filter.MEMU.value:
            self.subtract = 38

    def __str__(self):
        return "{text} (X: {x}, Y: {y}, W: {w}, H: {h})".format(text=self.text, x=self.x, y=self.y, w=self.width, h=self.height)

    def __repr__(self):
        return "<Window: {window}>".format(window=self)

    @property
    def text(self):
        """
        Retrieve the text (title) value for the window.
        """
        return win32gui.GetWindowText(self.hwnd).lower()

    @property
    def rectangle(self):
        """
        Retrieve the client rectangle for the window.
        """
        return win32gui.GetClientRect(self.hwnd)

    @property
    def x_padding(self):
        """
        Retrieve the amount of x padding for the window.
        """
        return self.width - self.EMULATOR_WIDTH

    @property
    def y_padding(self):
        """
        Retrieve the amount of y padding for the window.
        """
        return self.height - self.EMULATOR_HEIGHT

    @property
    def x(self):
        """
        Retrieve the x value for the window.
        """
        return self.rectangle[0] + self.x_padding

    @property
    def y(self):
        """
        Retrieve the y value for the window.
        """
        return self.rectangle[1] + self.y_padding

    @property
    def width(self):
        """
        Retrieve the width for the window.
        """
        return self.rectangle[2] - self.subtract

    @property
    def height(self):
        """
        Retrieve the height for the window.
        """
        return self.rectangle[3]

    @staticmethod
    def _gen_offset(point, amount):
        """
        Generate an offset on the given point.
        """
        if not amount:
            # Maybe the amount specified is just 0,
            # return the original point.
            return point

        # Modify our points to use a random value between
        # the original value with amount offset.
        return (
            point[0] + random.randint(-amount, amount),
            point[1] + random.randint(-amount, amount)
        )

    def search(self, value):
        """
        Perform a check to see if a specified value is present within the windows text value.
        """
        # If a single string has been specified as our search value,
        # place it into a list for looping, ensuring that we can use both strings
        # and list for our search.
        if isinstance(value, str):
            value = [value.lower()]

        # Otherwise, we're already using a list, great, let's also make sure
        # all values are set to lowercase for the search.
        else:
            value = [v.lower() for v in value]

        # Loop through each available search term, checking to see
        # if the value is present in the window.
        for val in value:
            if self.text.find(val) != -1:
                return True

        # Value couldn't be found in any of our specified
        # search terms.
        return False

    def click(self, point, clicks=1, interval=0.0, button=Button.LEFT, offset=5, pause=0.0):
        """
        Perform a click on this window in the background.
        """
        # Globals failsafe check to raise errors if trying to exit.
        _globals.failsafe_check()

        # Ensure we properly modify the point to respect the offset
        # specified, adding randomness to the click.
        point = self._gen_offset(point=point, amount=offset)

        # Create the windows compliant long value that will instruct
        # the window on which location should be clicked.
        _parameter = win32api.MAKELONG(point[0], point[1] + self.y_padding)

        for _ in range(clicks):
            # Perform a check on each click to see if failsafe should be raised.
            _globals.failsafe_check()

            # Looping through all specified clicks amount,
            # performing a click on the specified point each time.
            win32api.SendMessage(self.hwnd, self.ClickEvent[button.name].value[0], 1, _parameter)
            win32api.SendMessage(self.hwnd, self.ClickEvent[button.name].value[1], 0, _parameter)

            # Should we sleep for a bit between each click?
            # This differs from the pause amount.
            if interval:
                time.sleep(interval)

        # Should we pause for a bit after clicks have been performed?
        if pause:
            time.sleep(pause)

    def drag(self, start, end, button=Button.LEFT, pause=0.5):
        """
        Perform a drag on this window in the background.
        """
        # Globals failsafe check go raise errors if trying to exit.
        _globals.failsafe_check()

        # Create the windows compliant long value that will instruct
        # the window on which locations should be dragged.
        _parameter_start = win32api.MAKELONG(start[0], start[1] + self.y_padding)
        _parameter_end = win32api.MAKELONG(end[0], end[1] + self.y_padding)

        # Perform an actionable click on the start point just to ensure that
        # the window is active and a drag is prepped and good to begin.

        # Moving the mouse to the starting position for the duration of our
        # mouse dragging, button is DOWN after this point.
        win32api.SendMessage(self.hwnd, self.ClickEvent[button.name].value[0], 1, _parameter_start)

        # Determine which direction our mouse dragging will go,
        # we can go up or down easily, left and right may cause issues.
        direction = start[1] > end[1]
        clicks = start[1] - end[1] if direction else end[1] - start[1]

        time.sleep(0.05)

        for i in range(clicks):
            # Looping with i for the amount of needed clicks
            # to complete our entire mouse drag.
            _parameter = win32api.MAKELONG(start[0], start[1] - i if direction else start[1] + i)

            # Send another message to drag the mouse down start[1] +/- i.
            win32api.SendMessage(self.hwnd, self.Event.MOUSE_MOVE.value, 1, _parameter)

            # Sleep slightly after each drag. Ensuring that we don't
            # drag too quickly and miss our drags.
            time.sleep(0.001)

        time.sleep(0.1)

        # Send a message to the window to let go of the mouse and to
        # stop dragging at this point.
        win32api.SendMessage(self.hwnd, self.Event.MOUSE_MOVE.value, 0, _parameter_end)

        # Should we pause for a bit after the drag has been completed?
        if pause:
            time.sleep(pause)

    def screenshot(self, region=None):
        """
        Perform a screenshot on this window or region within, ignoring any windows in front of the window.
        """
        with _lock:
            # Waiting until we've acquired the lock before even beginning
            # the screenshot process for the window.
            hwnd_dc = win32gui.GetWindowDC(self.hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, self.width, self.height)

            save_dc.SelectObject(save_bitmap)

            # Store the actual screenshot result here through
            # the use of the windll object.
            windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 0)

            bmp_info = save_bitmap.GetInfo()
            bmp_str = save_bitmap.GetBitmapBits(True)

            # Store the actual Image object retrieved from our windows calls
            # in this variable.
            image = Image.frombuffer("RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_str, "raw", "BGRX", 0, 1)

            # Cleanup any dc objects that are currently in use.
            # This also makes sure when we come back, nothing is in use.
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()

            win32gui.ReleaseDC(self.hwnd, hwnd_dc)
            win32gui.DeleteObject(save_bitmap.GetHandle())

            # Ensure we also remove any un-needed image data, we only
            # want the in game screen, which should be the proper emulator height and width.
            image = image.crop(box=(
                0,
                self.y_padding,
                self.EMULATOR_WIDTH,
                self.EMULATOR_HEIGHT + self.y_padding
            ))

            # If a region has been specified as well, we should crop the image to meet our
            # region bbox specified, regions should already take into account our expected y padding.
            if region:
                image = image.crop(box=region)

            # Image has been collected, parsed, and cropped.
            # Return the image now, exiting will release our lock.
            return image

    def json(self):
        """
        Return a dictionary containing information about this window.
        """
        return {
            "formatted": self.__str__(),
            "hwnd": self.hwnd,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

    def dump(self):
        """
        Dump the window object as a json string.
        """
        return json.dumps(self.json())


class WindowHandler(object):
    """
    Window handler object can encapsulate all of the functionality used to gran and store references to windows.
    """
    DEFAULT_IGNORE_SMALLER = (400, 720)

    def __init__(self, initial=False):
        """
        Initialize handler and create empty dictionary of available windows.
        """
        self._windows = {}

        # Allow for optional instant enumeration and window population
        # when the handler is initialized.
        if initial:
            self.enumerate()

    def _callback(self, hwnd, extra):
        """
        Callback handler used when windows are enumerated.
        """
        # Make sure out hwnd is coerced into a string
        # so that we can go to and from windows with
        # a single data source for the keys.
        hwnd = str(hwnd)

        if hwnd in self._windows:
            # Hwnd is already present, not totally likely
            # but better to avoid duplicate keys or overwriting.
            pass

        # Hwnd found is not yet present in the dictionary containing
        # all window instances. Add it now.
        self._windows[hwnd] = Window(hwnd=hwnd)

    def enumerate(self):
        """
        Begin enumerating windows and generate window objects if not present in windows dictionary yet.
        """
        win32gui.EnumWindows(self._callback, None)

    def grab(self, hwnd):
        """
        Attempt to grab the specified hwnd from the dictionary of available windows.
        """
        if not self._windows:
            # If no windows are available in our dictionary of all
            # available windows at this point, run our enumeration.
            self.enumerate()

        # Some windows are available at this point, try and find the window
        # based on the hwnd specified.
        try:
            return self._windows[hwnd]
        # KeyError may occur when the hwnd specified
        # doesn't actually exist within the dictionary
        # of available windows.
        except KeyError:
            raise WindowNotFoundError()

    def filter(self, filter_titles=True, ignore_hidden=True, ignore_smaller=DEFAULT_IGNORE_SMALLER):
        """
        Filter all currently available windows to ones that meet the specified criteria.
        """
        # Filtering based on titles, the available titles are ones that
        # contain some sort of text that represent a supported emulator.
        if filter_titles:
            _dct = {
                hwnd: window for hwnd, window in self._windows.items() if window.search(value=Window.Filter.all())
            }
        # Otherwise, we'll go ahead and use all available windows for our initial
        # dictionary of windows.
        else:
            _dct = self._windows

        # Hide any windows that don't contain a valid width or height value
        # based on the parameters specified above.
        if ignore_hidden:
            _dct = {
                hwnd: window for hwnd, window in _dct.items() if window.width != 0 and window.height != 0
            }
        # Hide any windows that don't contain valid size values based on the
        # ignore smaller values specified above.
        if ignore_smaller:
            _dct = {
                hwnd: window for hwnd, window in _dct.items() if window.width > ignore_smaller[0] and window.height > ignore_smaller[1]
            }

        return _dct
