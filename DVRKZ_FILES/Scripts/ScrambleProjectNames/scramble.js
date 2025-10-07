// this sucks ongggggg, makes me suicidal and stuff
(function() {
    'use strict';
    const overlayKey = 'network-monitor-state';
    const minimizedKey = 'network-monitor-minimized';

    function setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
    }
    function getCookie(name) {
        const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
        return match ? decodeURIComponent(match[2]) : null;
    }
    function deleteCookie(name) {
        setCookie(name, '', -1);
    }

    const savedState = JSON.parse(getCookie(overlayKey)) || {};
    const isMinimized = getCookie(minimizedKey) === 'true';

    if (window.self === window.top) {
        const darkModeDiv = document.createElement('div');
        darkModeDiv.id = 'network-monitor';
        darkModeDiv.style.position = 'fixed';
        darkModeDiv.style.top = savedState.top || '0';
        darkModeDiv.style.left = savedState.left || '0';
        darkModeDiv.style.width = isMinimized ? '100px' : (savedState.width || '400px');
        darkModeDiv.style.height = isMinimized ? '50px' : (savedState.height || '100%');
        darkModeDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        darkModeDiv.style.color = '#fff';
        darkModeDiv.style.overflowY = 'scroll';
        darkModeDiv.style.zIndex = '9999';
        darkModeDiv.style.fontSize = '12px';
        darkModeDiv.style.padding = '10px';
        darkModeDiv.style.boxSizing = 'border-box';
        darkModeDiv.style.borderLeft = '5px solid #ff4081';
        darkModeDiv.style.transition = 'width 0.3s, height 0.3s, top 0.3s, left 0.3s';
        darkModeDiv.style.userSelect = 'none';
        darkModeDiv.style.position = 'fixed';
        darkModeDiv.style.top = isMinimized ? 'auto' : savedState.top || '0';
        darkModeDiv.style.left = isMinimized ? 'auto' : savedState.left || '0';
        darkModeDiv.style.bottom = isMinimized ? '0' : savedState.bottom || 'auto';
        darkModeDiv.style.right = isMinimized ? '0' : savedState.right || 'auto';

        const header = document.createElement('div');
        header.innerText = 'Network Monitor';
        header.style.fontWeight = 'bold';
        header.style.marginBottom = '10px';
        header.style.padding = '10px';
        header.style.backgroundColor = '#ff4081';
        header.style.color = '#fff';
        header.style.cursor = 'move';
        header.style.position = 'relative';
        header.style.zIndex = '10000';
        darkModeDiv.appendChild(header);

        const minimizeButton = document.createElement('button');
        minimizeButton.innerText = isMinimized ? 'Maximize' : 'Minimize';
        minimizeButton.style.position = 'absolute';
        minimizeButton.style.top = '10px';
        minimizeButton.style.right = '10px';
        minimizeButton.style.backgroundColor = '#ff4081';
        minimizeButton.style.color = '#fff';
        minimizeButton.style.border = 'none';
        minimizeButton.style.cursor = 'pointer';
        minimizeButton.style.zIndex = '10001';
        minimizeButton.addEventListener('click', () => {
            if (darkModeDiv.style.width === '100px') {
                // Restore to previous state
                darkModeDiv.style.width = savedState.width || '400px';
                darkModeDiv.style.height = savedState.height || '100%';
                darkModeDiv.style.top = savedState.top || '0';
                darkModeDiv.style.left = savedState.left || '0';
                darkModeDiv.style.bottom = savedState.bottom || 'auto';
                darkModeDiv.style.right = savedState.right || 'auto';
                minimizeButton.innerText = 'Minimize';
                setCookie(minimizedKey, 'false', 7);
            } else {

                savedState.width = darkModeDiv.style.width;
                savedState.height = darkModeDiv.style.height;
                savedState.top = darkModeDiv.style.top;
                savedState.left = darkModeDiv.style.left;
                savedState.bottom = darkModeDiv.style.bottom;
                savedState.right = darkModeDiv.style.right;

                darkModeDiv.style.width = '100px';
                darkModeDiv.style.height = '50px';
                darkModeDiv.style.top = '';
                darkModeDiv.style.left = '';
                darkModeDiv.style.bottom = '0';
                darkModeDiv.style.right = '0';

                minimizeButton.innerText = 'Maximize';
                setCookie(minimizedKey, 'true', 7);
            }
            setCookie(overlayKey, JSON.stringify(savedState), 7);
        });
        darkModeDiv.appendChild(minimizeButton);

        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search URL';
        searchInput.style.width = '100%';
        searchInput.style.padding = '5px';
        searchInput.style.marginBottom = '10px';
        darkModeDiv.appendChild(searchInput);

        const requestList = document.createElement('div');
        darkModeDiv.appendChild(requestList);

        document.body.appendChild(darkModeDiv);

        const createResizeHandle = (position) => {
            const handle = document.createElement('div');
            handle.style.position = 'absolute';
            handle.style.background = '#ff4081';
            handle.style.width = '10px';
            handle.style.height = '10px';
            handle.style.zIndex = '10000';
            handle.style.cursor = `${position}-resize`;
            handle.style.borderRadius = '50%';
            darkModeDiv.appendChild(handle);
            return handle;
        };
        const handleTopLeft = createResizeHandle('nw');
        handleTopLeft.style.top = '0';
        handleTopLeft.style.left = '0';
        const handleTopRight = createResizeHandle('ne');
        handleTopRight.style.top = '0';
        handleTopRight.style.right = '0';
        const handleBottomLeft = createResizeHandle('sw');
        handleBottomLeft.style.bottom = '0';
        handleBottomLeft.style.left = '0';
        const handleBottomRight = createResizeHandle('se');
        handleBottomRight.style.bottom = '0';
        handleBottomRight.style.right = '0';
        let isDragging = false;
        let offsetX, offsetY;
        let dragTimeout;
        header.addEventListener('mousedown', (event) => {
            isDragging = true;
            offsetX = event.clientX - darkModeDiv.getBoundingClientRect().left;
            offsetY = event.clientY - darkModeDiv.getBoundingClientRect().top;
            clearTimeout(dragTimeout);
            document.body.style.cursor = 'move';
        });

        window.addEventListener('mousemove', (event) => {
            if (isDragging) {
                clearTimeout(dragTimeout);
                dragTimeout = setTimeout(() => {
                    const x = event.clientX - offsetX;
                    const y = event.clientY - offsetY;
                    darkModeDiv.style.left = `${x}px`;
                    darkModeDiv.style.top = `${y}px`;
                }, 1);
            }
        });

        window.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                setCookie(overlayKey, JSON.stringify({
                    top: darkModeDiv.style.top,
                    left: darkModeDiv.style.left,
                    width: darkModeDiv.style.width,
                    height: darkModeDiv.style.height
                }), 7);
                document.body.style.cursor = '';
            }
        });

        const startResizing = (event, direction) => {
            event.preventDefault();

            const startX = event.clientX;
            const startY = event.clientY;
            const startWidth = parseInt(document.defaultView.getComputedStyle(darkModeDiv).width, 10);
            const startHeight = parseInt(document.defaultView.getComputedStyle(darkModeDiv).height, 10);
            const startTop = parseInt(document.defaultView.getComputedStyle(darkModeDiv).top, 10);
            const startLeft = parseInt(document.defaultView.getComputedStyle(darkModeDiv).left, 10);

            const doResize = (event) => {
                let newWidth = startWidth;
                let newHeight = startHeight;
                let newTop = startTop;
                let newLeft = startLeft;

                if (direction.includes('e')) {
                    newWidth = Math.max(startWidth + (event.clientX - startX), 100);
                }
                if (direction.includes('s')) {
                    newHeight = Math.max(startHeight + (event.clientY - startY), 100);
                }
                if (direction.includes('w')) {
                    newWidth = Math.max(startWidth - (event.clientX - startX), 100);
                    newLeft = startLeft + (event.clientX - startX);
                }
                if (direction.includes('n')) {
                    newHeight = Math.max(startHeight - (event.clientY - startY), 100);
                    newTop = startTop + (event.clientY - startY);
                }

                darkModeDiv.style.width = `${newWidth}px`;
                darkModeDiv.style.height = `${newHeight}px`;
                darkModeDiv.style.top = `${newTop}px`;
                darkModeDiv.style.left = `${newLeft}px`;
            };

            const stopResizing = () => {
                window.removeEventListener('mousemove', doResize);
                window.removeEventListener('mouseup', stopResizing);
                setCookie(overlayKey, JSON.stringify({
                    top: darkModeDiv.style.top,
                    left: darkModeDiv.style.left,
                    width: darkModeDiv.style.width,
                    height: darkModeDiv.style.height
                }), 7);
            };

            window.addEventListener('mousemove', doResize);
            window.addEventListener('mouseup', stopResizing);
        };

        handleTopLeft.addEventListener('mousedown', (event) => startResizing(event, 'nw'));
        handleTopRight.addEventListener('mousedown', (event) => startResizing(event, 'ne'));
        handleBottomLeft.addEventListener('mousedown', (event) => startResizing(event, 'sw'));
        handleBottomRight.addEventListener('mousedown', (event) => startResizing(event, 'se'));

        const requests = [];

        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;

        XMLHttpRequest.prototype.open = function(method, url) {
            this._method = method;
            this._url = url;
            this._requestBody = '';
            this.addEventListener('load', function() {
                logRequest({
                    method: this._method,
                    url: this._url,
                    status: this.status,
                    responseText: this.responseText,
                    requestHeaders: this.getAllResponseHeaders(),
                    requestBody: this._requestBody
                });
            });
            this.addEventListener('error', function() {
                logRequest({
                    method: this._method,
                    url: this._url,
                    status: 'ERROR',
                    responseText: '',
                    requestHeaders: this.getAllResponseHeaders(),
                    requestBody: this._requestBody
                });
            });
            originalOpen.apply(this, arguments);
        };

        XMLHttpRequest.prototype.send = function(body) {
            this._requestBody = body || '';
            originalSend.apply(this, arguments);
        };

        const originalFetch = window.fetch;

        window.fetch = function(url, options) {
            const requestDetails = {
                method: options && options.method || 'GET',
                url: url,
                status: 'Pending',
                responseText: '',
                requestHeaders: options && options.headers ? JSON.stringify(options.headers) : '',
                requestBody: options && options.body ? JSON.stringify(options.body) : ''
            };

            return originalFetch(url, options).then(response => {
                response.clone().text().then(text => {
                    requestDetails.status = response.status;
                    requestDetails.responseText = text;
                    logRequest(requestDetails);
                });
                return response;
            }).catch(error => {
                requestDetails.status = 'ERROR';
                logRequest(requestDetails);
                throw error;
            });
        };

        function logRequest(request) {
            requests.push(request);
            const requestDiv = document.createElement('div');
            requestDiv.style.borderBottom = '1px solid #444';
            requestDiv.style.padding = '5px';
            requestDiv.style.marginBottom = '5px';
            requestDiv.style.cursor = 'pointer';
            requestDiv.style.position = 'relative';
            requestDiv.innerHTML = `
                <div>
                    ${request.method} ${request.url} - ${request.status}
                </div>
                <div class="details" style="display: none; margin-top: 5px;">
                    <button class="copy-btn" style="display: block; margin-bottom: 5px;">Copy Data</button>
                    <div><strong>Request Headers:</strong></div>
                    <pre>${request.requestHeaders}</pre>
                    <div><strong>Request Body:</strong></div>
                    <pre>${request.requestBody}</pre>
                    <div><strong>Response:</strong></div>
                    <pre>${request.responseText}</pre>
                </div>
            `;

            requestDiv.addEventListener('click', () => {
                const details = requestDiv.querySelector('.details');
                details.style.display = details.style.display === 'none' ? 'block' : 'none';
            });

            const copyButton = requestDiv.querySelector('.copy-btn');
            copyButton.addEventListener('click', (event) => {
                event.stopPropagation();
                const dataToCopy = `
                    Method: ${request.method}
                    URL: ${request.url}
                    Status: ${request.status}
                    Request Headers: ${request.requestHeaders}
                    Request Body: ${request.requestBody}
                    Response: ${request.responseText}
                `;
                navigator.clipboard.writeText(dataToCopy).catch(err => {
                    console.error('Failed to copy data: ', err);
                });
            });

            requestList.appendChild(requestDiv);
        }

        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const requestDivs = requestList.getElementsByTagName('div');
            for (const requestDiv of requestDivs) {
                const url = requestDiv.innerHTML.toLowerCase();
                if (url.includes(filter)) {
                    requestDiv.style.display = '';
                } else {
                    requestDiv.style.display = 'none';
                }
            }
        });

        window.addEventListener('keydown', (event) => {
            if (event.shiftKey && event.key === 'Q') {
                event.preventDefault();
                const requestList = darkModeDiv.querySelectorAll('div:not(.copy-btn):not(.details)');
                requestList.forEach((request) => {
                    if (request !== header && request !== minimizeButton && request !== searchInput) {
                        darkModeDiv.removeChild(request);
                    }
                });
                requests.length = 0;
            }
        });
    }

    function monitorIframeRequests(iframe) {
        iframe.addEventListener('load', () => {
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

            const originalIframeOpen = iframeDocument.XMLHttpRequest.prototype.open;
            const originalIframeSend = iframeDocument.XMLHttpRequest.prototype.send;

            iframeDocument.XMLHttpRequest.prototype.open = function(method, url) {
                this._method = method;
                this._url = url;
                this._requestBody = '';
                this.addEventListener('load', function() {
                    logRequest({
                        method: this._method,
                        url: this._url,
                        status: this.status,
                        responseText: this.responseText,
                        requestHeaders: this.getAllResponseHeaders(),
                        requestBody: this._requestBody
                    });
                });
                this.addEventListener('error', function() {
                    logRequest({
                        method: this._method,
                        url: this._url,
                        status: 'ERROR',
                        responseText: '',
                        requestHeaders: this.getAllResponseHeaders(),
                        requestBody: this._requestBody
                    });
                });
                originalIframeOpen.apply(this, arguments);
            };

            iframeDocument.XMLHttpRequest.prototype.send = function(body) {
                this._requestBody = body || '';
                originalIframeSend.apply(this, arguments);
            };

            const originalIframeFetch = iframeDocument.fetch;

            iframeDocument.fetch = function(url, options) {
                const requestDetails = {
                    method: options && options.method || 'GET',
                    url: url,
                    status: 'Pending',
                    responseText: '',
                    requestHeaders: options && options.headers ? JSON.stringify(options.headers) : '',
                    requestBody: options && options.body ? JSON.stringify(options.body) : ''
                };

                return originalIframeFetch(url, options).then(response => {
                    response.clone().text().then(text => {
                        requestDetails.status = response.status;
                        requestDetails.responseText = text;
                        logRequest(requestDetails);
                    });
                    return response;
                }).catch(error => {
                    requestDetails.status = 'ERROR';
                    logRequest(requestDetails);
                    throw error;
                });
            };
        });
    }

    document.querySelectorAll('iframe').forEach(monitorIframeRequests);
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.tagName === 'IFRAME') {
                    monitorIframeRequests(node);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });

})();

(function() {
    'use strict';
    function showNotification(requestDetails) {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.top = '10px';
        notification.style.right = '10px';
        notification.style.backgroundColor = '#f8d7da';
        notification.style.color = '#721c24';
        notification.style.border = '1px solid #f5c6cb';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
        notification.style.zIndex = '9999';
        notification.style.padding = '15px';
        notification.style.maxWidth = '400px';
        notification.style.minWidth = '200px';
        notification.style.cursor = 'move';
        notification.style.resize = 'both';
        notification.style.overflow = 'auto';
        const header = document.createElement('div');
        header.style.fontWeight = 'bold';
        header.innerText = 'Suspicious Activity Caught';
        notification.appendChild(header);
        const subheader = document.createElement('div');
        subheader.innerText = 'Were you logged?';
        notification.appendChild(subheader);
        const body = document.createElement('pre');
        body.style.whiteSpace = 'pre-wrap';
        body.style.wordWrap = 'break-word';
        body.innerText = formatRequestDetails(requestDetails);
        notification.appendChild(body);
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';

        const dismissButton = document.createElement('button');
        dismissButton.innerText = 'Dismiss';
        dismissButton.style.marginRight = '10px';
        dismissButton.addEventListener('click', () => {
            document.body.removeChild(notification);
        });
        buttonContainer.appendChild(dismissButton);
        const copyButton = document.createElement('button');
        copyButton.innerText = 'Copy';
        copyButton.addEventListener('click', () => {
            copyToClipboard(formatRequestDetails(requestDetails));
        });
        buttonContainer.appendChild(copyButton);
        notification.appendChild(buttonContainer);
        document.body.appendChild(notification);
        makeDraggable(notification);
    }
    function formatRequestDetails(details) {
        return `
URL: ${details.url}
Method: ${details.method}
Headers: ${details.headers ? formatJson(details.headers) : 'No headers'}
Body: ${details.body ? formatJson(details.body) : 'No body'}`;
    }
    function formatJson(json) {
        try {
            return JSON.stringify(JSON.parse(json), null, 2);
        } catch (e) {
            return json;
        }
    }
    function makeDraggable(element) {
        let offsetX, offsetY, initialX, initialY;

        element.onmousedown = function(event) {
            event.preventDefault();
            initialX = event.clientX;
            initialY = event.clientY;
            document.onmousemove = function(event) {
                offsetX = event.clientX - initialX;
                offsetY = event.clientY - initialY;
                initialX = event.clientX;
                initialY = event.clientY;
                element.style.top = (element.offsetTop + offsetY) + 'px';
                element.style.left = (element.offsetLeft + offsetX) + 'px';
            };
            document.onmouseup = function() {
                document.onmousemove = null;
                document.onmouseup = null;
            };
        };
    }
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Request information copied to clipboard!');
            }).catch(err => {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    }
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed'; // prevent scroll jumping to the bottom
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            alert('Request information copied to clipboard!');
        } catch (err) {
            alert('Failed to copy request information.');
        }
        document.body.removeChild(textArea);
    }
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch(...args).then(response => {
            if (response.url.includes('discord.com/api/webhooks')) {
                response.clone().text().then(body => {
                    showNotification({
                        url: response.url,
                        method: 'FETCH',
                        headers: response.headers ? formatHeaders(response.headers) : null,
                        body: body
                    });
                });
            }
            return response;
        });
    };
    const originalXhrOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(...args) {
        this.addEventListener('load', function() {
            if (this.responseURL.includes('discord.com/api/webhooks')) {
                showNotification({
                    url: this.responseURL,
                    method: this.method,
                    headers: formatHeaders(this.getAllResponseHeaders()),
                    body: this.responseText
                });
            }
        });
        return originalXhrOpen.apply(this, args);
    };
    function formatHeaders(headers) {
        const headerObject = {};
        headers.forEach((value, key) => {
            headerObject[key] = value;
        });
        return formatJson(headerObject);
    }

})();
