import requests
import time
import colr
from typing import Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor as Thread

C = '\033[36m'
W = '\033[0m'   # White
R = '\033[31m'  # Red
G = '\033[32m'  # Green

session = requests.Session()
count = 0

class Console: # Ignore this shit code
    def log(
        content: Optional[str],
        mode: str = "",
        user: str = None,
        user2: str = None
    ) -> None:
        WDD = colr.Colr().hex('#FFFFFF')
        LDD = colr.Colr().hex('#525052')
        now = datetime.now()
        _console = now.strftime(f" {WDD}[{LDD}%H:%M:%S{WDD}]{W} ")
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


def auth_account(username, password) -> bool:
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
        return True, aut.json()['data']
    else:
        Console.log(f'{R}ACCOUNT LOGIN FAILED: {aut.text}{W}')
        return False, None

    session.cookies.clear()

def account_info(profile_id) -> dict:
    params1 = {
        'objectID': '4',
        'profileID': profile_id,
        'lang': 'en_ES',
        'type': 'play'
    }

    locato = session.get(
        'https://www.kogama.com/locator/session/',
        params=params1
    )

    token = locato.json()['token']
    params2 = {
        'token': token,
        'generation': '0'
    }
    gen = session.get(
        'https://api-www.kgama.com/v1/notify/c/',
        params=params2
    )
    print(gen.text)

def get_friend_ids(profile_id):
    params1 = {
        'count': 12
    }

    total = session.get(
        f'https://www.kogama.com/user/{profile_id}/friend/',
        params=params1
    )

    total = total.json()['paging']['total']

    params2 = {
        'count': total
    }

    friends = session.get(
        f'https://www.kogama.com/user/{profile_id}/friend/',
        params=params2
    )

    for friend in friends.json()['data']:
        friend_id = friend['friend_profile_id']
        if int(friend_id) == 667431006:
            continue
        user_friend = friend['friend_username']
        delete = session.delete(
            f'https://www.kogama.com/user/{profile_id}/friend/{friend_id}/',
        )

        if delete.status_code == 200:
            Console.log(f'DELETED FRIEND: {user_friend} | Profile ID: {friend_id}')
        else:
            print(delete.status_code)


if __name__ == '__main__':
    username = input('Usermame: ')
    password = input('Password: ')
    print(f'User: {username}')
    Console.log('Obteniendo Informacion de la cuenta...')

    is_logged, data = auth_account(username, password)
    if is_logged:
        #account_info(data['id'])
        _id = data['id']
        verified = 'No' if data['email_confirmed'] == 0 else 'Si'
        print(f'Email: {data["email"]}\nEmail Confirmed: {verified}\nLevel: {data["level"]}')
        Console.log('Eliminando todos amigos de la cuenta...')
        get_friend_ids(_id)
