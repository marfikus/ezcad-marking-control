
from pynput import keyboard
import time

kb = keyboard.Controller()

delay = 0.2
count = 0

def press_alt_tab():
    kb.press(keyboard.Key.alt)
    kb.press(keyboard.Key.tab)
    kb.release(keyboard.Key.tab)
    kb.release(keyboard.Key.alt)    

def press_f1():
    kb.press(keyboard.Key.f1)
    kb.release(keyboard.Key.f1)


with keyboard.Events() as events:
    for event in events:
        # print(event)
        # print(event.key.char)
        if type(event) is keyboard.Events.Release:
            if event.key == keyboard.Key.ctrl_l:
                count += 1
                if count == 3: # 3 ctrl_l подряд для остановки скрипта
                    break
            else:
                count = 0
                if event.key == keyboard.Key.esc:
                    press_alt_tab()

            char = ''
            try:
                char = event.key.char
            except AttributeError:
                pass

            if char == '`' or char == '1': # потом сделать один вариант (настройка в конфиге)
                press_alt_tab()
                time.sleep(delay)
                press_f1()

