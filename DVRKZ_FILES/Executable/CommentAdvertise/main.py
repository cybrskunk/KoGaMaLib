import json, time, re, itertools, requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

RAINBOW = itertools.cycle([
    Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX,
    Fore.LIGHTGREEN_EX, Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.BLUE,
    Fore.MAGENTA, Fore.LIGHTMAGENTA_EX
])

def colorize(text):
    return f"{next(RAINBOW)}{text}{Style.RESET_ALL}"

def log(msg):
    print(f"{Fore.LIGHTMAGENTA_EX}[{Style.RESET_ALL}{colorize('DVRKZ')}{Fore.LIGHTMAGENTA_EX}]{Style.RESET_ALL} {msg}")

class Config:
    def __init__(self, path='config.json'):
        self.path = path
        with open(path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def remove_bad(self, username, password):
        # < - remove account from memory, then persist - >
        self.data['accounts'] = [a for a in self.data['accounts'] if a['username'] != username]
        self.save()
        with open('bad_accounts.txt', 'a', encoding='utf-8') as bad_f:
            bad_f.write(f"// {username}:{password}\n")


class KoGaMaClient:
    LOGIN_URL = "https://www.kogama.com/auth/login"
    LOGOUT_URL = "https://www.kogama.com/auth/logout"
    COMMENT_URL = "https://www.kogama.com/game/{}/comment/"

    def __init__(self, username, password):
        self.username, self.password = username, password
        self.session = requests.Session()

    def _locale(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup.find('script', string=re.compile(r'options\.bootstrap'))
        if tag and (m := re.search(r"'locale':\s*'(\w+)'", tag.string)):
            return m.group(1)
        return "en-US"

    def login(self):
        try:
            page = self.session.get(self.LOGIN_URL, timeout=5)
            _ = self._locale(page.text)  # not used, could be removed
            r = self.session.post(self.LOGIN_URL, json={
                'username': self.username, 'password': self.password
            }, timeout=5)
            if r.status_code == 200 and 'data' in r.json():
                return True
            msg = r.json().get('message', '').lower()
            return not any(k in msg for k in ['invalid', 'username', 'password'])
        except Exception:
            return False

    def logout(self):
        try:
            r = self.session.get(self.LOGOUT_URL, timeout=5)
            if r.status_code != 200:
                self.session.post(self.LOGOUT_URL, timeout=5)
        except Exception:
            pass

    def post_comment(self, target_id, content):
        try:
            r = self.session.post(
                self.COMMENT_URL.format(target_id),
                json={'comment': content},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            return r.status_code == 201
        except Exception:
            return False

class CommentBot:
    def __init__(self, config):
        self.cfg = config
        self.total, self.posted = 0, 0
        self.start = datetime.now()

    def _estimate(self):
        if self.posted == 0: return "unknown"
        elapsed = (datetime.now() - self.start) / self.posted
        remaining = elapsed * (self.total - self.posted)
        return str(timedelta(seconds=int(remaining.total_seconds())))

    def run(self):
        per_game = int(input("Provide amount of comments per game: "))
        self.total = per_game * len(self.cfg.data['gamelist'])
        for gid in self.cfg.data['gamelist']:
            posted = 0
            while posted < per_game:
                for acc in list(self.cfg.data['accounts']):
                    client = KoGaMaClient(acc['username'], acc['password'])
                    if not client.login():
                        log(f"{Fore.MAGENTA}Invalid credentials for {acc['username']}, removing.{Style.RESET_ALL}")
                        self.cfg.remove_bad(acc['username'], acc['password'])
                        continue
                    content = self.cfg.data['presets'].get(acc['username'])
                    if not content:
                        log(f"{Fore.MAGENTA}No preset found for {acc['username']}{Style.RESET_ALL}")
                        continue
                    if client.post_comment(gid, content):
                        log(f"{Fore.MAGENTA}Sent comment from {Fore.RESET}{acc['username']}{Fore.MAGENTA} under {Fore.LIGHTCYAN_EX}{gid}{Style.RESET_ALL}")
                        self.posted += 1; posted += 1
                    client.logout(); time.sleep(1)
                    if posted >= per_game: break
                if posted < per_game:
                    log(f"{Fore.MAGENTA}Waiting 120s to avoid rate limit...{Style.RESET_ALL}")
                    time.sleep(120)
            log(f"{Fore.MAGENTA}ETA: {self._estimate()}{Style.RESET_ALL}")
        log(f"{Fore.MAGENTA}Finished: {self.posted} comments total.{Style.RESET_ALL}")

if __name__ == "__main__":
    CommentBot(Config()).run()
