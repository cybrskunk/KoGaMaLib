import requests
import time
from typing import Optional
from datetime import datetime

C = '\033[36m'
W = '\033[0m'   # White
R = '\033[31m'  # Red
G = '\033[32m'  # Green

session = requests.Session()

class Console: # Ignore this shit code
    def log(
        content: Optional[str],
        mode: str = "",
        user: str = None,
        user2: str = None
    ) -> None:
        now = datetime.now()
        _console = now.strftime(f" {C}[%H:%M:%S]{W} ")
        if mode != "":
            if mode in ["error", "failed"]:
                color = R
            else:
                color = G
            mode = f"{color}{mode.upper()}{W} "
        if user != None:
            user = f"{L}value={B}{user}"
        else:
            user = ""
        if user2 != None:
            user += f" {W}| {L}value2={B}{user2}"

        print(f"{_console}" + mode + user + content)

session.headers = {
    'accept': 'application/json,text/plain,*/*',
    'accept-encoding': 'gzip,deflate,br',
    'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7',
    'cache-control': 'no-cache',
    'connection': 'keep-alive',
    'host': 'www.kogama.com',
    'pragma': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
}


def get_accounts() -> dict:
    with open('accounts.txt', 'r') as file:
        accs = file.read().strip().splitlines()
    return accs

def post_game_like(game_id) -> None:
    likee = session.post(f'https://www.kogama.com/game/{game_id}/like/')
    if likee.status_code in [200, 201, 204]:
        Console.log(f'{G}LIKED GAME{W} | Profile ID: {likee.json()["data"]["user_id"]} | Game ID: {game_id}')
        time.sleep(0.1)
        
    elif likee.status_code == 429:
        Console.log(f'{R}FAILED: Demasiadas respuestas{W}')
        time.sleep(6)
    else:
        Console.log(f'{R}FAILED: {likee.text}{W}')
        time.sleep(0.5)

def auth_account(username, password, game_id: int) -> None:
    datak = {
        'username': username,
        'password': password
    }

    aut = session.post(
        'https://www.kogama.com/auth/login/',
        json=datak
    )

    session.cookies = aut.cookies  # temporaily

    if aut.status_code == 200:
        post_game_like(game_id)
    else:
        Console.log(f'{R}ACCOUNT LOGIN FAILED: {aut.status_code}{W}')

    session.cookies.clear()

if __name__ == '__main__':
    game_id = int(input('ID del juego:  '))

    if len(get_accounts()) <= 0:
        print('No tienes cuentas asignadas a "accounts.txt"')
        sys.exit()

    for account in get_accounts():
        if ':' not in account:
            continue

        username, password = account.split(':')
        auth_account(username, password, game_id)
