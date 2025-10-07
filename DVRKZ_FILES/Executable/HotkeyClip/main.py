import os, sys, time, json, subprocess, keyboard
from colorama import Fore, Style, init
init(autoreset=True)

PRESETS_FILE = "presets.json"
hotkeys = {}

def color_log(msg, color=Fore.LIGHTRED_EX):
    print(f"{color}{msg}{Style.RESET_ALL}")

def install_requirements():
    if not os.path.exists('requirements.txt'):
        return
    color_log("Installing dependencies from requirements.txt...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    os.remove('requirements.txt')
    color_log("requirements.txt deleted after installation.\n")

def load_presets():
    if not os.path.exists(PRESETS_FILE):
        color_log("No presets found. Create one using Ctrl+Shift.", Fore.YELLOW)
        return
    with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
        hotkeys.update(json.load(f))
    color_log(f"Loaded {len(hotkeys)} saved preset(s):", Fore.LIGHTBLUE_EX)
    for hk, txt in hotkeys.items():
        print(f"  {Fore.CYAN}Hotkey:{Style.RESET_ALL} {hk} {Fore.MAGENTA}→{Style.RESET_ALL} {txt}")

def save_presets():
    with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(hotkeys, f, indent=2)

def loading(msg="Loading New Preset", duration=2):
    anim = "|/-\\"
    for i in range(int(duration * 10)):
        sys.stdout.write(f"\r[{anim[i % 4]}] {Fore.LIGHTRED_EX}{msg}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
    print("\r", end="")

def set_preset():
    loading()
    while True:
        hk = input(f"\n{Fore.YELLOW}Enter hotkey:{Style.RESET_ALL} ").strip()
        if not hk:
            color_log("Hotkey cannot be empty.", Fore.RED)
        elif hk.lower() in ("ctrl", "shift", "alt"):
            color_log("Invalid single modifier key.", Fore.RED)
        elif hk in hotkeys:
            color_log("Hotkey already exists.", Fore.RED)
        else:
            break
    txt = input(f"{Fore.YELLOW}Enter text to type:{Style.RESET_ALL} ")
    hotkeys[hk] = txt
    save_presets()
    color_log(f"[ + ] Added hotkey '{hk}' → \"{txt}\"", Fore.GREEN)

def trigger(hk):
    text = hotkeys.get(hk)
    if not text:
        color_log(f"Unknown hotkey: {hk}", Fore.RED)
        return
    keyboard.press_and_release('ctrl+a, delete')
    keyboard.write(text)
    keyboard.press_and_release('enter')

def register_hotkeys():
    keyboard.add_hotkey('ctrl+shift', set_preset)
    for hk in hotkeys:
        keyboard.add_hotkey(hk, trigger, args=(hk,))
    color_log("Hotkeys loaded successfully.", Fore.LIGHTMAGENTA_EX)

def main():
    install_requirements()
    color_log("Script created by Simon.", Fore.LIGHTRED_EX)
    color_log("Press Ctrl+Shift anytime to create a new preset.\n", Fore.LIGHTCYAN_EX)
    load_presets()
    register_hotkeys()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        save_presets()
        color_log("\nExiting gracefully.", Fore.YELLOW)

if __name__ == "__main__":
    main()
