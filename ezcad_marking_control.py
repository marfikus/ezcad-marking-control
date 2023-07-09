
from pynput import keyboard
import time


OPERATIONS_DELAY = 0.2

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

                    if char == '1':
                        press_alt_tab()
                        time.sleep(OPERATIONS_DELAY)
                        press_f1()


if __name__ == "__main__":
    main()
