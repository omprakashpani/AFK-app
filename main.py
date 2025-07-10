from pynput import mouse, keyboard
import pyautogui
import time
import keyboard as kb  

action = []
rec = True
last_time = 0
mouse_record_inter = 0.01

def rec_mc(x, y, button, pressed):
    global action
    times = time.time()
    act_type = 'mouse_down' if pressed else 'mouse_up'
    action.append((act_type, x, y, button.name, times))

def rec_mm(x, y):
    global action, last_time
    n = time.time()
    if n - last_time >= mouse_record_inter:
        action.append(('mouse_move', x, y, n))
        last_time = n

def record_key(key):
    global action, rec
    times = time.time()
    if key == keyboard.Key.esc:
        print("\nStopped recording.")
        rec = False
        return False
    try:
        action.append(('key_press', key.char, times))
        print(f"Recorded key: {key.char}")
    except AttributeError:
        action.append(('key_press', key.name, times))
        print(f"Recorded special key: {key.name}")

def startrec():
    global rec, action
    action.clear()
    rec = True
    print("Recording started, Press 'Esc' to stop")

    with mouse.Listener(on_click=rec_mc, on_move=rec_mm) as ml, \
         keyboard.Listener(on_press=record_key) as kl:
        kl.join()
        ml.stop()

def replay(repeat=1):
    if len(action) < 2:
        print("No actions recorded")
        return

    speed_f = 70000.0 
    print(f"\n▶Replaying {repeat} time(s), Press Ctrl+C to stop")

    for r in range(int(repeat) if repeat != float('inf') else 999999999):
        base_t = action[0][-1]
        for i in range(1, len(action)):
            curr = action[i]
            prev = action[i - 1]
            delay = (curr[-1] - prev[-1]) / speed_f
            if delay > 0:
                time.sleep(delay)

            act = curr[0]

            if act == 'mouse_move':
                _, x, y, _ = curr
                pyautogui.moveTo(x, y, duration=0)
            elif act == 'mouse_down':
                _, x, y, butt, _ = curr
                pyautogui.mouseDown(x, y, button=butt)
            elif act == 'mouse_up':
                _, x, y, butt, _ = curr
                pyautogui.mouseUp(x, y, button=butt)
            elif act == 'key_press':
                _, key, _ = curr
                try:
                    if key.lower() == 'caps_lock':
                        kb.send('caps lock')  # Actual toggle
                        print("🔁 CapsLock toggled.")
                    elif key.lower() in pyautogui.KEYBOARD_KEYS:
                        pyautogui.press(key.lower())
                    else:
                        print(f"Skipping unsupported key: {key}")
                except Exception as e:
                    print(f"Error pressing key '{key}': {e}")

        print(f"Completed replay #{r + 1}")


def main():
    print("AFK Recorder")
    input("▶Press Enter to start recording...")

    startrec()

    if not action:
        print("No actions recorded.")
        return

    print(f"\nRecorded {len(action)} actions.")

    try:
        repeat_input = input("🔁 Enter number of replays (or 'inf' for infinite): ").strip()
        repeat = float('inf') if repeat_input.lower() == 'inf' else int(repeat_input)
    except ValueError:
        repeat = 1

    print("\nReplaying in 3 seconds...")
    time.sleep(3)

    replay(repeat)

if __name__ == "__main__":
    main()