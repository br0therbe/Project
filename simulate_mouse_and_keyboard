# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2019/8/8 11:57
# @Version     : Python 3.6.8
# @Description : simulate mouse and keyboard
import logging
import time
import win32api
import win32clipboard
import win32con
import win32gui

WAIT_TIME = 0.02019
FUNCTIONAL_KEY_MAP = {
    "backspace": 8,
    "tab": 9,
    "enter": 13,
    "shift": 16,
    "ctrl": 17,
    "alt": 18,
    "capslock": 20,
    "esc": 27,
    "ins": 45,
    "del": 46
}
ORDINARY_KEY_MAP = {
    "0": 48,
    "1": 49,
    "2": 50,
    "3": 51,
    "4": 52,
    "5": 53,
    "6": 54,
    "7": 55,
    "8": 56,
    "9": 57,
    "a": 65,
    "b": 66,
    "c": 67,
    "d": 68,
    "e": 69,
    "f": 70,
    "g": 71,
    "h": 72,
    "i": 73,
    "j": 74,
    "k": 75,
    "l": 76,
    "m": 77,
    "n": 78,
    "o": 79,
    "p": 80,
    "q": 81,
    "r": 82,
    "s": 83,
    "t": 84,
    "u": 85,
    "v": 86,
    "w": 87,
    "x": 88,
    "y": 89,
    "z": 90,
    "+": 187,
    ",": 188,
    "-": 189,
    ".": 190,
    "/": 191,
    ";": 186,
    "[": 219,
    "\\": 220,
    "]": 221,
    "'": 222,
    "`": 192
}
SHIFT_KEY_MAP = {
    ")": "0",
    "!": "1",
    "@": "2",
    "#": "3",
    "$": "4",
    "%": "5",
    "^": "6",
    "&": "7",
    "*": "8",
    "(": "9",
    "A": "a",
    "B": "b",
    "C": "c",
    "D": "d",
    "E": "e",
    "F": "f",
    "G": "g",
    "H": "h",
    "I": "i",
    "J": "j",
    "K": "k",
    "L": "l",
    "M": "m",
    "N": "n",
    "O": "o",
    "P": "p",
    "Q": "q",
    "R": "r",
    "S": "s",
    "T": "t",
    "U": "u",
    "V": "v",
    "W": "w",
    "X": "x",
    "Y": "y",
    "Z": "z",
    "+": "+",
    "<": ",",
    "_": "-",
    ">": ".",
    "?": "/",
    ":": ";",
    "{": "[",
    "|": "\\",
    "}": "]",
    "\"": "'",
    "~": "`"
}
logger = logging


def time_sleep(func):
    """
    time decorator for waiting
    :param func: function object
    :return: the result of function
    """

    def _inner(*args, **kwargs):
        time.sleep(WAIT_TIME)
        result = func(*args, **kwargs)
        return result

    return _inner


@time_sleep
def run_app(app_path, wait_time: int = 3):
    """
    start application program
    :param app_path: path of application program
    :param wait_time: wait time result from it is application program that need some time to start
     rather than load all modules right now
    :return: None
    """
    try:
        win32api.ShellExecute(0, 'open', app_path, '', '', 1)
        time.sleep(wait_time)
    except Exception as e:
        logger.error(f'APP Failed to Start!\nError Message is {e}', exc_info=1)


@time_sleep
def full_window(class_name):
    """
    make application program full window
    :param class_name: the class name of application program
    :return: None
    """
    handle = win32gui.FindWindow(class_name, None)
    win32gui.SetForegroundWindow(handle)
    win32gui.ShowWindow(handle, 3)


@time_sleep
def mouse_click(horizontal_pixel, vertical_pixel):
    """
    click screen pixel absolute location
    :param horizontal_pixel: horizontal pixels
    :param vertical_pixel: vertical pixels
    :return: None
    """
    win32api.SetCursorPos((horizontal_pixel, vertical_pixel))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


@time_sleep
def _single_shortcut_key(ordinary_key_code: int, functional_key_code: int):
    win32api.keybd_event(functional_key_code, 0, 0, 0)
    time.sleep(WAIT_TIME)
    win32api.keybd_event(ordinary_key_code, 0, 0, 0)
    time.sleep(WAIT_TIME)
    win32api.keybd_event(ordinary_key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(WAIT_TIME)
    win32api.keybd_event(functional_key_code, 0, win32con.KEYEVENTF_KEYUP, 0)


@time_sleep
def write2clipboard(strings: str):
    """
    write text to the clipboard
    :param strings: text
    :return: None
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(strings)
    win32clipboard.CloseClipboard()


@time_sleep
def password_input(password):
    """
    input password by keyboard
    :param password: password
    :return:
    """
    for char in password:
        if char in ORDINARY_KEY_MAP:
            win32api.keybd_event(ORDINARY_KEY_MAP[char], 0, 0, 0)
            win32api.keybd_event(ORDINARY_KEY_MAP[char], 0, win32con.KEYEVENTF_KEYUP, 0)
        elif char in SHIFT_KEY_MAP:
            shortcut_key(SHIFT_KEY_MAP[char], 'shift')
        else:
            raise ValueError('Invalid Input!')
        time.sleep(WAIT_TIME)


def get_app_class_name(app_path, app_name):
    hwnd_dict = {}

    def foo(hwnd, _):
        if all([win32gui.IsWindow(hwnd), win32gui.IsWindowEnabled(hwnd), win32gui.IsWindowVisible(hwnd)]):
            title = win32gui.GetWindowText(hwnd)
            if title:
                hwnd_dict[title] = win32gui.GetClassName(hwnd)

    # start app
    run_app(app_path)
    # get active windows
    win32gui.EnumWindows(foo, 0)
    for key, value in hwnd_dict.items():
        if app_name in key:
            return value
    else:
        raise ValueError('Wrong App Name')


def shortcut_key(normal_key: str, functional_key: str = 'ctrl'):
    """
    only single shortcut key, but double or triple shortcut keys
    :param normal_key: non-functional-key
    :param functional_key: ctrl, shift or alt
    :return: None
    """
    normal_key = normal_key.lower()
    functional_key = functional_key.lower()
    ordinary_key_code = ORDINARY_KEY_MAP[normal_key]
    if functional_key == 'ctrl':
        _single_shortcut_key(ordinary_key_code, 0x11)
    elif functional_key == 'shift':
        _single_shortcut_key(ordinary_key_code, 0x10)
    else:
        _single_shortcut_key(ordinary_key_code, 0x12)


def paste_text(text):
    write2clipboard(text)
    shortcut_key('V')


if __name__ == '__main__':
    a = r'''0123456789abcdefghijklmnopqrstuvwxyz+,-./;[\]'`)!@#$%^&*(ABCDEFGHIJKLMNOPQRSTUVWXYZ+<_>?:{|}"~'''
    password_input(a)
