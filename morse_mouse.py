import time

from pynput import keyboard, mouse
from pynput.keyboard import Controller, Key

enabled = False
morse = ""
clicked_time = 0
unclick_time = 0
t = time.time()
dit_time = 0.08

watch_for_space = False
failed_morse = False
fail_keyword = "[FATAL]"  # Error/failed morse keyword
toggle_key = ":"
toggle_pressed = False
restart_mouse_listener = False

print(
    f"MORSE_MOUSE: Type with your mouse.\n"
    f"{'= '*25}\n\n"
    "Force Quit: click fast multiple times.\n\n"
    f"Toggle: press ({toggle_key})\n\n"
    f"'.' = Hold < {dit_time}s, '-' = Hold > {dit_time}s\n\n"
    f"Info: https://en.wikipedia.org/wiki/Morse_code\n\n"
    f"{'= '*25}\n"
    "YOUR MOUSE WILL BE DISABLED WHEN YOU TOGGLE!!!!!\n"
    f"{'= '*25}\n"
)

kbd_controller = Controller()

MORSE_CODE_DICT = {
    ".-": "a",
    "-...": "b",
    "-.-.": "c",
    "-..": "d",
    ".": "e",
    "..-.": "f",
    "--.": "g",
    "....": "h",
    "..": "i",
    ".---": "j",
    "-.-": "k",
    ".-..": "l",
    "--": "m",
    "-.": "n",
    "---": "o",
    ".--.": "p",
    "--.-": "q",
    ".-.": "r",
    "...": "s",
    "-": "t",
    "..-": "u",
    "...-": "v",
    ".--": "w",
    "-..-": "x",
    "-.--": "y",
    "--..": "z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-.-.-": ".",
    "--..--": ",",
    "..--..": "?",
    "-..-.": "/",
}

INVERTED_MORSE_CODE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}


def type_letter(morse, fail=False):
    if not enabled:
        return True

    if morse:
        m = MORSE_CODE_DICT[morse] if morse in MORSE_CODE_DICT else morse
        kbd_controller.press(m)
        kbd_controller.release(m)

    if fail:
        for i in fail_keyword:
            kbd_controller.press(i)
            kbd_controller.release(i)


def backspace(m):
    for _ in range(m):
        kbd_controller.press(Key.backspace)
        kbd_controller.release(Key.backspace)


def toggle():
    global enabled, restart_mouse_listener
    enabled = not enabled
    restart_mouse_listener = True


def on_click(x, y, button, pressed):
    global clicked_time, morse, unclick_time, t, enabled
    t = time.time()

    if enabled and button == button.left:
        if pressed:
            clicked_time = t
        else:
            unclick_time = t
            diff = unclick_time - clicked_time
            morse += "-" if diff >= dit_time else "."


def on_press(key):
    global toggle_key, toggle_pressed
    try:
        if key.char == toggle_key:
            toggle_pressed = True
    except AttributeError:
        pass


def on_release(key):
    global toggle_key, toggle_pressed, backspace, toggle
    try:
        if toggle_pressed and key.char == toggle_key and toggle_pressed:
            toggle_pressed = False
            backspace(1)
            toggle()
    except AttributeError:
        pass


mouse_listener = mouse.Listener(on_click=on_click)
kbd_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
kbd_listener.start()


while True:

    if restart_mouse_listener:
        mouse_listener.stop()
        mouse_listener = mouse.Listener(on_click=on_click, suppress=enabled)
        mouse_listener.start()
        restart_mouse_listener = False

    if clicked_time < unclick_time:
        if (time.time() - unclick_time) > 0.15 and morse != "":  # letter timeout

            if failed_morse and enabled:
                backspace(len(fail_keyword))
                failed_morse = False

            if morse in MORSE_CODE_DICT:
                type_letter(morse)
                watch_for_space = True

            elif not failed_morse and enabled:
                type_letter(False, True)
                failed_morse = True

            morse = ""

        if (
            watch_for_space
            and time.time() - unclick_time > 0.8  # word timeout
            and not failed_morse
        ):
            type_letter(" ")
            watch_for_space = False

        if morse.count(".") >= 7:
            break
