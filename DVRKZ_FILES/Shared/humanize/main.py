import os
import json
import colr
import time
import httpx
import random
import requests

from datetime import datetime
from requests.cookies import RequestsCookieJar
from concurrent.futures import ThreadPoolExecutor

R = colr.Colr().hex('#Fb0707')
B = '\33[94m'   # Blue
L = '\033[90m'  # Grey
G = '\033[92m'  # Green
W = '\033[0m'   # White
P = colr.Colr().hex('#b207f5')

BADGES_CODE = []

_site = requests.get('https://kogama.fandom.com/wiki/Badges').text
s = _site.split('common Coupon Codes for')[1].split('These Coupon Codes can')
s = s[0].replace('<b>', '').replace('</b>', '').replace(' ', '')
s = s.replace('Badgesare;', '').split(',')

for badge in s:
    if badge == 'scaryandcoolcat.':
        a, p = badge.replace('and', ',').replace('.', '').split(',')
        BADGES_CODE.append(a)
        BADGES_CODE.append(p)
    else:
        BADGES_CODE.append(badge)

def log(content, mode, color=W):
    #_time = datetime.now().strftime('[%H:%M:%S]')
    print(f'{color}{mode.upper()}{W} |', content, W)

class TempMailAPI:
    def __init__(self, proxies: list) -> None:
        self.api = 'http://disposablemail.com'
        self.client = httpx.Client(follow_redirects=True)
        self.client.headers = {
            'x-requested-with': 'XMLHttpRequest'
        }
        #self.proxies = proxies

        self.attempt = 0
        self.email = None

    def _setup(self) -> None:
        site = self.client.get(self.api)
        self.client.cookies = site.cookies

    def new_email(self) -> str:
        self._setup()
        email_data = self.client.get(f'{self.api}/index/index/').text
        self.email = str(email_data).split('{"email":"')[1].split('","heslo"')[0]
        return self.email

    def verify_account(self):
        verify_url = None 
        while not verify_url or self.attempt >= 25:
            messages = self.client.get(f'{self.api}/index/refresh')

            for message in messages.json():
                index_id = message['id']

                if index_id in [2, 3]:
                    window = self.client.get(f'{self.api}/email/id/1/')
                    verify_url = str(window.text).split('href="')[2].split('/"')[0]
                    break
                
                self.attempt += 1
                time.sleep(1)
        
        if verify_url is not None:
            verify = self.client.get(verify_url)
            if verify.status_code == 200:
                log(f'E: {self.email}', mode='updated email', color=P)
            else:
                log(f'S: {verify.status_code} | E: {self.email}', mode='failed', color=R)

class Kogama:
    def __init__(self, proxies: list) -> None:
        self.url = 'https://www.kogama.com'
        self.session = requests.Session()
        self.session.headers = {
            'accept': 'application/json,text/plain,*/*',
            'accept-encoding': 'gzip,deflate,br',
            'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7',
            'cache-control': 'no-cache',
            'connection': 'keep-alive',
            'host': 'www.kogama.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'pragma': 'no-cache',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }

        self.proxies = proxies
        if len(self.proxies) > 1:
            proxy = random.choice(self.proxies)
            proxy_dict = {
                'http': proxy,
                'https': proxy
            }
            self.session.proxies = proxy_dict
    
    def _build_cookies(self, session=None) -> requests.cookies:
        cookie_jar = RequestsCookieJar()
        cookies_dict = {
            'm': '0',
            '_pp': 'WINDOWS',
            '_kref': 'kogama',
            'is_american': 'true',
            'is_european': 'false',
            'language': 'en_US'
        }
        if session is not None:
            cookies_dict.update({'session': session})

        for cookie_name, value in cookies_dict.items():
            cookie_jar.set(name=cookie_name, value=value, domain=self.url)
        return cookie_jar
    
    def auth_account(self, username, password) -> tuple:
        try:
            post_data = {
                'username': username,
                'password': password
            }
            self.session.headers['content-length'] = str(len(json.dumps(post_data)))
            login = self.session.post(
                f'{self.url}/auth/login/',
                cookies=self._build_cookies(),
                json=post_data
            )
            if login.status_code == 200:
                return login.cookies['session'], login.json()['data']['id']
            else:
                r_err = login.json()['error']['__all__'][0]
                log(f'E: {r_err}', mode='failed', color=R)
                return None, None
        except Exception as e:
            print(e)

    def _badge_show_added(self) -> str:
        xd = '('
        for added in self.badges_added:
            xd += added + ', '
        xd = xd.rstrip(', ') + ')'
        return xd

    def claim_coupon_code(self, username, session) -> None:
        self.session.headers['referer'] = self.url + '/coupon/'

        for badge_code in BADGES_CODE:
            post_data = {
                'code': badge_code
            }
            claim = self.session.post(
                f'{self.url}/api/coupon/redeem/',
                cookies=self._build_cookies(session),
                json=post_data
            )

            if claim.status_code in [200, 201, 203]:
                log(f'S: {session[:30]}** | U: {username} | C: {badge_code}', mode='claimed', color=G)
            else:
                r_err = claim.json()['error']['code'][0]
                log(f'S: {session[:30]}** | U: {username} | E: {r_err}', mode='failed', color=R)

    def send_email_verification(self, session, profile_id, email, password) -> bool:
        post_data = {
            'email': email,
            'password': password
        }
        self.session.headers['content-length'] = str(len(json.dumps(post_data)))
        send = self.session.put(
            f'{self.url}/user/{profile_id}/email/',
            cookies=self._build_cookies(session),
            json=post_data
        )
        if send.status_code == 200:
            return True
        return False

    def description_changer(self, session, bio, username, profile_id) -> None:
        post_data = {
            'birthdate': '1970-01-09',
            'description': bio
        }
        self.session.headers['content-length'] = str(len(json.dumps(post_data)))
        change = self.session.put(
            f'{self.url}/user/{profile_id}/',
            cookies=self._build_cookies(session),
            json=post_data
        )
        if change.status_code == 200:
            log(f'S: {session[:30]}** | U: {username} | B: {bio}', mode='updated', color=G)
        else:
            log(f'S: {session[:30]}** | U: {username} | E: {change.json()}', mode='failed', color=R)


if __name__ == '__main__':
    os.system('clear||cls')
    max_threads = 15

    accounts = open('accounts.txt', 'r').read().strip().splitlines()
    proxies = open('proxies.txt', 'r').read().strip().splitlines()

    change_b = input('Change Account(s) Bio (y/n): ').lower() == 'y'
    if change_b:
        bio = input('Bio: ')

    def startThread(username, password):
        try:
            k = Kogama(proxies)
            temp = TempMailAPI(proxies)
    
            # humanize
            session, profile_id = k.auth_account(username, password)
            if session is not None:
                email = temp.new_email()
                a = k.send_email_verification(session, profile_id, email, password)
                temp.verify_account()
    
                time.sleep(2.5)
                k.claim_coupon_code(username, session)
                if change_b:
                    k.description_changer(session, bio, username, profile_id)
        except Exception as e:
            print(e)
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for account in accounts:
            if not ':' in account:
                continue

            username, password = account.split(':')
            executor.submit(startThread, username, password)
