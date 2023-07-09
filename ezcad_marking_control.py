
import os
from pynput import keyboard
import time
import configparser


CONFIG_FILE = "ezcad_marking_control.ini"
DEFAULT_CONFIG = {
    "char_f1": '1',
    "char_f2": '2',
    "operations_delay": 0.2,
    "window_title": "Маркировка цилиндров (вектор)",
    "element_title": "X",
    "shift_from_element": 1,
    "switch_windows": True
}

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


def main():
    config = load_config()
    print(config)

    ctrl_l_count = 0
    alt_l_count = 0
    suspended = False

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
                    if config["switch_windows"]:
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
                        press_f1()


if __name__ == "__main__":
    main()
