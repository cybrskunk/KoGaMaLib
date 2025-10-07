# This does not generate accounts, you need to provide your own accountlist.
# All this script does is process the account and target invite provided ID.


import requests, json, time, re, itertools
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

def login(session, acc):
    url = "https://www.kogama.com/auth/login"
    resp = session.post(url, json={'username': acc['username'], 'password': acc['password']})
    return resp.ok and "data" in resp.json()

def get_self_id(session):
    resp = session.get("https://www.kogama.com/profile/me/")
    if resp.ok: return resp.url.split('/')[-2]
    return None

def send_request(session, user_id, target_id, username):
    url = f"https://www.kogama.com/user/{user_id}/friend/"
    r = session.post(url, json={'user_id': target_id})
    msg = (f"Sent friend request from {Fore.WHITE}{username}{Style.RESET_ALL} "
           f"({Fore.CYAN}{user_id}{Style.RESET_ALL}) → {Fore.LIGHTRED_EX}{target_id}{Style.RESET_ALL}"
           if r.status_code == 201 else
           f"Failed friend request from {Fore.WHITE}{username}{Style.RESET_ALL} "
           f"({Fore.CYAN}{user_id}{Style.RESET_ALL}) → {Fore.LIGHTRED_EX}{target_id}{Style.RESET_ALL} [{r.status_code}]")
    color_log(msg)

def process_account(acc, target_id):
    try:
        with requests.Session() as s:
            if not login(s, acc): return False
            self_id = get_self_id(s)
            if self_id: send_request(s, self_id, target_id, acc['username'])
            s.get("https://www.kogama.com/auth/logout")
            return True
    except Exception as e:
        color_log(f"Error {acc['username']}: {e}")
        return False

def numeric_key(u): 
    m = re.search(r'\d+', u['username']); return int(m.group()) if m else float('inf')

def main():
    while True:
        try: target_id = int(input("Target user ID: ")); break
        except: print("Enter a valid number.")
    
    accs = sorted(read_accounts(), key=numeric_key)
    if not accs: return color_log("No accounts found in config.json.")

    batch_size, delay, threads = 10, 130, 6
    total = len(accs)
    color_log(f"Starting {total} accounts (est. {total*4}s)")

    for i in range(0, total, batch_size):
        batch = accs[i:i+batch_size]
        color_log(f"Batch {i//batch_size+1}/{-(-total//batch_size)}")

        with ThreadPoolExecutor(max_workers=threads) as ex:
            results = list(ex.map(lambda a: process_account(a, target_id), batch))
        color_log(f"{sum(results)} successful logins in this batch")

        if i + batch_size < total:
            color_log(f"Cooldown {delay}s…")
            time.sleep(delay)

    color_log("Completed all accounts.")

if __name__ == "__main__":
    main()
