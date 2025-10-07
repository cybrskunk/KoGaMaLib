import requests, json, time, itertools, re
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
init(autoreset=True)

RAINBOW = itertools.cycle([
    Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX,
    Fore.LIGHTGREEN_EX, Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.BLUE,
    Fore.MAGENTA, Fore.LIGHTMAGENTA_EX
])

def color_log(msg):
    print(f"{Fore.LIGHTMAGENTA_EX}[{next(RAINBOW)}DVRKZ{Fore.LIGHTMAGENTA_EX}]{Style.RESET_ALL} {msg}")

def read_accounts(path='config.json'):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f).get('accounts', [])
    except Exception as e:
        color_log(f"Failed to read config: {e}")
        return []

def login(s, acc):
    r = s.post("https://www.kogama.com/auth/login", json={'username': acc['username'], 'password': acc['password']})
    return r.ok and "data" in r.json()

def get_profile_id(s):
    r = s.get("https://www.kogama.com/profile/me/")
    return r.url.split('/')[-2] if r.ok else None

def update_description(s, pid, desc):
    r = s.put(f"https://www.kogama.com/user/{pid}/", json={"birthdate": "1970-01-23", "description": desc})
    return r.ok

def logout(s):
    r = s.get("https://www.kogama.com/auth/logout")
    if not r.ok:
        s.post("https://www.kogama.com/auth/logout")

def process(acc, desc):
    try:
        with requests.Session() as s:
            if not login(s, acc):
                return f"{Fore.RED}Login failed{Style.RESET_ALL} → {acc['username']}"
            pid = get_profile_id(s)
            if not pid:
                return f"{Fore.RED}Profile fetch failed{Style.RESET_ALL} → {acc['username']}"
            ok = update_description(s, pid, desc)
            logout(s)
            return f"{Fore.GREEN if ok else Fore.RED}{'Updated' if ok else 'Failed'}{Style.RESET_ALL} → {acc['username']}"
    except Exception as e:
        return f"{Fore.RED}Error{Style.RESET_ALL} → {acc['username']} ({e})"

def main():
    desc = input("Enter new description for all accounts (use \\br for line breaks): ").replace("\\br", "\n")
    accs = read_accounts()
    if not accs: return color_log("No accounts found in config.json.")

    threads, batch_size, delay = 4, 10, 111
    total = len(accs)
    color_log(f"Starting updates for {total} accounts...")

    for i in range(0, total, batch_size):
        batch = accs[i:i+batch_size]
        with ThreadPoolExecutor(max_workers=threads) as ex:
            for res in ex.map(lambda a: process(a, desc), batch):
                color_log(res)
        if i + batch_size < total:
            color_log(f"Cooldown {delay}s…")
            time.sleep(delay)

    color_log("✅ All accounts processed.")

if __name__ == "__main__":
    main()
