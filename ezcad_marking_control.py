
import os
from pynput import keyboard
import time
import configparser


CONFIG_FILE = "ezcad_marking_control.ini"
DEFAULT_CONFIG = {
    "char_f1": '1',
    "operations_delay": 0.2,
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found! Loaded DEFAULT_CONFIG")
        return DEFAULT_CONFIG

    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    config = {}

    try:
        config["char_f1"] = parser["DEFAULT"]["char_f1"]
    except KeyError:
        print("No key 'char_f1' in config file! Loaded from DEFAULT_CONFIG")
        config["char_f1"] = DEFAULT_CONFIG["char_f1"]
        
    try:
        config["operations_delay"] = float(parser["DEFAULT"]["operations_delay"])
    except KeyError:
        print("No key 'operations_delay' in config file! Loaded from DEFAULT_CONFIG")
        config["operations_delay"] = DEFAULT_CONFIG["operations_delay"]

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
    # print(config)

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
                        press_alt_tab()
                        time.sleep(config["operations_delay"])
                        press_f1()


if __name__ == "__main__":
    main()
