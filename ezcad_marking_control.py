
import os
from pynput import keyboard
import time
import configparser
from winGuiAuto import *


CONFIG_FILE = "ezcad_marking_control.ini"
DEFAULT_CONFIG = {
    "char_f1": '1',
    "char_f2": '2',
    "operations_delay": 0.2,
    "window_title": "Маркировка цилиндров (вектор)",
    "element_title": "X",
    "shift_from_element": 1,
    "switch_windows": True,
    "auto_start_burn": True,
}

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
        # print(obj)
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


def load_config():
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
        except KeyError:
            print(f"No key '{key}' in config file! Loaded from DEFAULT_CONFIG")
            value = DEFAULT_CONFIG[key]    

        return value


    if not os.path.exists(CONFIG_FILE):
        print("Config file not found! Loaded DEFAULT_CONFIG")
        return DEFAULT_CONFIG

    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE, encoding="utf-8")
    config = {}

    config["char_f1"] = load_key(parser, "char_f1")
    config["char_f2"] = load_key(parser, "char_f2")
    config["operations_delay"] = load_key(parser, "operations_delay", "float")
    config["window_title"] = load_key(parser, "window_title")
    config["element_title"] = load_key(parser, "element_title")
    config["shift_from_element"] = load_key(parser, "shift_from_element", "int")
    config["switch_windows"] = load_key(parser, "switch_windows", "bool")
    config["auto_start_burn"] = load_key(parser, "auto_start_burn", "bool")

    return config


kb = keyboard.Controller()

def press_alt_tab():
    kb.press(keyboard.Key.alt)
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.release(keyboard.Key.alt)    

def press_f1():
    kb.press(keyboard.Key.f1)
    kb.release(keyboard.Key.f1)

def press_f2():
    kb.press(keyboard.Key.f2)
    kb.release(keyboard.Key.f2)


def main():
    config = load_config()
    print(config)

    ctrl_l_count = 0
    alt_l_count = 0
    suspended = False
    source_field_value = {}

    with keyboard.Events() as events:
        for event in events:
            # print(event)
            # print(event.key.char)

            if type(event) is not keyboard.Events.Release:
                continue        

            if event.key == keyboard.Key.ctrl_l:
                alt_l_count = 0
                ctrl_l_count += 1

                if ctrl_l_count == 2:
                    if not suspended:
                        suspended = True
                        print("program suspended")
                elif ctrl_l_count == 4:
                    print("program stopped")
                    return
            
            elif event.key == keyboard.Key.alt_l:
                ctrl_l_count = 0
                alt_l_count += 1

                if alt_l_count == 2:
                    if suspended:
                        suspended = False
                        alt_l_count = 0
                        print("program resumed")
            else:
                ctrl_l_count = 0
                alt_l_count = 0

                if suspended:
                    continue

                # print(event)

                if event.key == keyboard.Key.esc:
                    # если авто старт, то дождаться возврата ротора и нажать f2
                    if config["auto_start_burn"]:
                        # нужно таймаут добавить на всякий случай
                        while True:
                            current_field_value = get_field_value(
                                config["window_title"], 
                                config["element_title"], 
                                config["shift_from_element"]
                            )
                            if current_field_value["error"]:
                               print("Auto start is unavailable: no value for tracking") 
                               break
                            elif (current_field_value["value"] == source_field_value["value"]):
                                print("f2")
                                press_f2()
                                break

                            print("await rotor...")
                            time.sleep(0.5)

                    if config["switch_windows"]:
                        time.sleep(config["operations_delay"])
                        press_alt_tab()
                else:
                    char = ''
                    try:
                        char = event.key.char
                        # print(char)
                    except AttributeError as e:
                        # print(e)
                        pass

                    if char == config["char_f1"]:
                        if config["switch_windows"]:
                            press_alt_tab()
                            time.sleep(config["operations_delay"])

                        if config["auto_start_burn"]:
                            # запомнить исходное значение поля позиции ротора
                            source_field_value = get_field_value(
                                config["window_title"], 
                                config["element_title"], 
                                config["shift_from_element"]
                            )
                            if source_field_value["error"]:
                               print("Auto start is unavailable: no value for tracking") 

                        print("f1")
                        press_f1()


if __name__ == "__main__":
    main()
