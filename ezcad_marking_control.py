
import os
from pynput import keyboard
import time
import configparser
from winGuiAuto import *
import ast


PROGRAM_VERSION = "1.0.5"

CONFIG_FILE = "ezcad_marking_control.ini"
DEFAULT_CONFIG = {
    "char_f1": '1',
    "char_f2": '2',
    "char_esc": '`',
    "operations_delay": 0.2,
    "await_rotor_cycle_delay": 0.5,
    "await_rotor_timeout": 10.0,
    "rotor_position_diff": 0.05,
    "window_title": "Маркировка цилиндров (вектор)",
    "element_title": "X",
    "shift_from_element": 1,
    "switch_windows": True,
    "auto_start_burn": True,
    "check_foreground_window_on_f1": True,
    "valid_foreground_window_titles_on_f1": ["ezcad_marking_control.exe"],
    "check_foreground_window_on_esc": True,
    "valid_foreground_window_title_on_esc": "Маркировка цилиндров (вектор)",
    "debug_print": True,
}
config = {}

# пока экспериментальный вариант (исправленный относительно winGuiAuto)
# Из однострочного editText вроде извлекает значение нормально, с другими не проверял
def getEditText_fixed(hwnd):
    bufLen = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
    # print(bufLen)
    buffer = win32gui.PyMakeBuffer(bufLen)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, bufLen, buffer)
    # text = buffer[:bufLen]
    # text = win32gui.PyGetString(buffer.buffer_info()[0], bufLen - 1)
    text = win32gui.PyGetString(win32gui.PyGetBufferAddressAndLen(buffer)[0], bufLen - 1)
    return text

def get_field_value(window_title, element_title, shift_from_element):
    field_value = ""
    result = {
        "value": field_value,
        "error": True
    }
    element_found = False

    # найти окно
    try:
        window = findTopWindow(wantedText=window_title)
        dump = dumpWindow(window)
    except WinGuiAutoError:
        print(f"Window '{window_title}' not found!")
        # result["error"] = True
        return result

    # найти элемент
    for obj in dump:
        debug_print(obj)
        if obj[1] == element_title:
            i = dump.index(obj) + shift_from_element
            # print("element: ", dump[i])
            edit = dump[i]
            try:
                field_value = getEditText_fixed(edit[0])
                # print("field_value: ", field_value)
                element_found = True
                # field_value = int(field_value)
            except ValueError:
                print("Incorrect EditText value!")
                # result["error"] = True
                return result

    if element_found:
        result["error"] = False
        result["value"] = field_value

    return result


def is_valid_foreground_window(valid_window_titles):
    result = False

    foreground_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    debug_print(foreground_window_title)

    for title in valid_window_titles:
        if title in foreground_window_title:
            result = True
            break

    return result


def load_config():
    global config

    def load_key(parser, key, type="str"):
        try:
            if type == "str":
                value = parser["DEFAULT"][key]
            elif type == "int":
                value = int(parser["DEFAULT"][key])
            elif type == "float":
                value = float(parser["DEFAULT"][key])
            elif type == "bool":
                value = bool(int(parser["DEFAULT"][key]))
            elif type == "list":
                value = ast.literal_eval(parser["DEFAULT"][key])
        except KeyError:
            print(f"No key '{key}' in config file! Loaded from DEFAULT_CONFIG")
            value = DEFAULT_CONFIG[key]    

        return value


    if not os.path.exists(CONFIG_FILE):
        print("Config file not found! Loaded DEFAULT_CONFIG")
        config = DEFAULT_CONFIG
        return

    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")

    config["char_f1"] = load_key(parser, "char_f1")
    config["char_f2"] = load_key(parser, "char_f2")
    config["char_esc"] = load_key(parser, "char_esc")
    config["operations_delay"] = load_key(parser, "operations_delay", "float")
    config["await_rotor_cycle_delay"] = load_key(parser, "await_rotor_cycle_delay", "float")
    config["await_rotor_timeout"] = load_key(parser, "await_rotor_timeout", "float")
    config["rotor_position_diff"] = load_key(parser, "rotor_position_diff", "float")
    config["window_title"] = load_key(parser, "window_title")
    config["element_title"] = load_key(parser, "element_title")
    config["shift_from_element"] = load_key(parser, "shift_from_element", "int")
    config["switch_windows"] = load_key(parser, "switch_windows", "bool")
    config["auto_start_burn"] = load_key(parser, "auto_start_burn", "bool")
    config["check_foreground_window_on_f1"] = load_key(parser, "check_foreground_window_on_f1", "bool")
    config["valid_foreground_window_titles_on_f1"] = load_key(parser, "valid_foreground_window_titles_on_f1", "list")
    config["check_foreground_window_on_esc"] = load_key(parser, "check_foreground_window_on_esc", "bool")
    config["valid_foreground_window_title_on_esc"] = load_key(parser, "valid_foreground_window_title_on_esc")
    config["debug_print"] = load_key(parser, "debug_print", "bool")


kb = None

def init_keyboard():
    global kb
    kb = keyboard.Controller()

def press_alt_tab():
    kb.press(keyboard.Key.alt)
    kb.press(keyboard.Key.tab)
    delay(config["operations_delay"])
    kb.release(keyboard.Key.tab)
    kb.release(keyboard.Key.alt)    

def press_f1():
    kb.press(keyboard.Key.f1)
    kb.release(keyboard.Key.f1)

def press_f2():
    kb.press(keyboard.Key.f2)
    kb.release(keyboard.Key.f2)

def press_esc():
    kb.press(keyboard.Key.esc)
    kb.release(keyboard.Key.esc)

def delay(delay):
    time.sleep(delay)

def debug_print(msg):
    if config["debug_print"]:
        print(msg)


def main():
    print(f"Program version: {PROGRAM_VERSION}")
    load_config()
    print(f"Current configuration: \n{config}")

    init_keyboard()

    source_field_value = None
    program_f1_clicked = False

    with keyboard.Events() as events:
        for event in events:
            if type(event) is not keyboard.Events.Release:
                continue

            if event.key == keyboard.Key.f1:
                # print(event)

                # фильтрация программных нажатий f1 (их не нужно обрабатывать)
                if program_f1_clicked:
                    program_f1_clicked = False
                    continue

                if not is_valid_foreground_window([config["window_title"]]):
                    debug_print("Invalid foreground window!")
                    continue

                if config["auto_start_burn"]:
                    # запомнить исходное значение поля позиции ротора
                    source_field_value = get_field_value(
                        config["window_title"], 
                        config["element_title"], 
                        config["shift_from_element"]
                    )
                    if source_field_value["error"]:
                       print("Auto start is unavailable: no source value for tracking")

                    debug_print(f"{source_field_value = }")

                debug_print("Real f1 click is processed")
                continue

            char = ''
            try:
                char = event.key.char
                # print(event)
            except AttributeError as e:
                # print(e)
                continue

            if char == config["char_esc"]:
                if config["check_foreground_window_on_esc"]:
                    if not is_valid_foreground_window([config["valid_foreground_window_title_on_esc"]]):
                        debug_print("Invalid foreground window!")
                        continue

                debug_print("esc")
                press_esc()

                # если авто старт, то дождаться возврата ротора и нажать f2
                if config["auto_start_burn"]:
                    cur_time = 0
                    while True:
                        debug_print("Await rotor...")
                        delay(config["await_rotor_cycle_delay"])

                        if source_field_value == None or source_field_value["error"]:
                            print("Auto start is unavailable: no source value for tracking")
                            break

                        # поскольку запрашиваются параметры из конфига, то можно сделать их дефолтными для метода
                        current_field_value = get_field_value(
                            config["window_title"], 
                            config["element_title"], 
                            config["shift_from_element"]
                        )
                        debug_print(f"{current_field_value = }")

                        if current_field_value["error"]:
                           print("Auto start is unavailable: no current value for tracking")
                           break
                        else:
                            # значения могут немного отличаться в тысячных долях (может и в сотых), 
                            # поэтому вычисляем разницу и сравниваем с макс допустимым значением из конфига
                            current_value = float(current_field_value["value"])
                            source_value = float(source_field_value["value"])
                            diff = abs(round(current_value - source_value, 2))
                            debug_print(f"current_value: {current_value}, source_value: {source_value}, diff: {diff}")
                            if diff < config["rotor_position_diff"]:
                                delay(config["operations_delay"])
                                debug_print("f2")
                                press_f2()
                                break
                        
                        cur_time += config["await_rotor_cycle_delay"]
                        # print(cur_time)
                        if cur_time >= config["await_rotor_timeout"]:
                            print("Await rotor timeout!")
                            break

                if config["switch_windows"]:
                    delay(config["operations_delay"])
                    press_alt_tab()


            elif char == config["char_f1"]:
                if not config["switch_windows"]:
                    # если окна не переключаются, то дальше действовать нет смысла
                    # то есть теперь клавиша "1" используется только 
                    # при активном параметре переключения окон, что в общем логично,
                    # поскольку иначе можно пользоваться просто клавишей f1
                    continue

                if config["check_foreground_window_on_f1"]:
                    if not is_valid_foreground_window(config["valid_foreground_window_titles_on_f1"]):
                        debug_print("Invalid foreground window!")
                        continue

                press_alt_tab()
                delay(config["operations_delay"])

                if config["auto_start_burn"]:
                    # запомнить исходное значение поля позиции ротора
                    source_field_value = get_field_value(
                        config["window_title"], 
                        config["element_title"], 
                        config["shift_from_element"]
                    )
                    if source_field_value["error"]:
                       print("Auto start is unavailable: no source value for tracking")
                       # добавить continue?
                    debug_print(f"{source_field_value = }")

                debug_print("f1")
                press_f1()
                program_f1_clicked = True


if __name__ == "__main__":
    main()
