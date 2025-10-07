import os
import sys
import requests
import random
import time
from typing import Union

session = requests.Session()
lang = 'en_US'

G = '\033[32m'  # Green
W = '\033[0m'   # White
Y = '\033[33m'  # Yellow

class KoGaMaData:
    SERVER = 'https://www.kogama.com'
    LANG = 'en_US'

    HEADERS = {
        'accept': 'application/json,text/plain,*/*',
        'accept-encoding': 'gzip,deflate,br',
        'cache-control': 'no-cache',
        'connection': 'keep-alive',
        'host': 'www.kogama.com',
        'pragma': 'no-cache',
        'sec-ch-ua': None,
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

    COOKIES = {
        'is_american': 'false',
        'is_european': 'false',
        '_kref': 'kogama',
        'is_child': 'false',
        'ad_consent': 'false',
        'm': '0',
        'language': lang
    }

def clean_proxy(proxy) -> Union[dict, str]:
    print(proxy)
    if isinstance(proxy, str):
        parts = proxy.split(':')
        if '@' in proxy or len(parts) == 2:
            return proxy
        elif len(parts) == 4:
            return f'{parts[2:]}@{parts[:2]}'
        elif '.' in parts[0]:
            return f'{parts[2:]}@{parts[:2]}'
        else:
            return f'{parts[:2]}@{parts[2:]}'
    elif isinstance(proxy, dict):
        http_proxy = proxy.get("http") or proxy.get("https")
        https_proxy = proxy.get("https") or proxy.get("http")
        if http_proxy or https_proxy:
            return {
                "http://": http_proxy,
                "https://": https_proxy
            }
        elif proxy in [dict(), {}]:
            return {}
    return proxy

def get_proxies() -> dict:
    with open('proxies.txt', 'r') as file:
        proxies = file.read().strip().splitlines()
    print(proxies)
    return proxies

def random_proxy() -> str:
    return random.choice(get_proxies())

def get_session() -> requests.Session:
    session = requests.Session()
    proxies = get_proxies()

    if len(proxies) > 1:
        proxy = clean_proxy(random_proxy())
        if isinstance(proxy, str):
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        elif isinstance(proxy, dict):
            proxy_dict = proxy

        print(proxy_dict)
        session.proxies = proxy_dict

    session.headers = KoGaMaData.HEADERS
    return session

def post_session_play(game_id: int, amount, session=get_session()) -> None:
    try:
        params = {
            'objectID': str(game_id),
            'profileID': '0',
            'lang': lang,
            'type': 'play'
        }
    
        for i in range(amount):
            while True:
                try:
                    playing = session.post(
                        f'{KoGaMaData.SERVER}/locator/session/',
                        params=params
                    )
                    if playing.status_code in [200, 201, 204]:
                        _token = playing.json()['id']
                        print(f'{G}JOINED SUCCESSFUL{W} | Play: {G}{i}{W}| ID: {_token}')
                        break
                    elif playing.status_code == 429:
                        wait_time = 60 + (i * 1.6)  # Incremental wait time
                        print(f'{Y}FAILED: Demasiadas respuestas{W}. Esperando {wait_time} segundos.')
                        time.sleep(wait_time)
                    else:
                        print(f'FAILED: Response Code: {playing.json()["error"]}')
                        break
                except Exception as c:
                    time.sleep(0.5)
                    continue
    except Exception as e:
        print(f'Error en post_session_play: {str(e)}')
        return post_session_play(game_id, amount)


if __name__ == '__main__':
    game_id = int(input('[WWW] ID del juego: '))
    amount = int(input('Aumento de repeticiones:  '))

    try:
        post_session_play(game_id, amount)
    except Exception as e:
        print(f'Error en la ejecución principal: {str(e)}')
        post_session_play(game_id, amount)

