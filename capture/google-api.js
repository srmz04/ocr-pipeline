// Google API Client Manager
class GoogleAPIClient {
    constructor() {
        this.gapi = null;
        this.tokenClient = null;
        this.accessToken = null;
        this.isInitialized = false;
    }

    async initialize() {
        try {
            // Load Google API scripts
            await this.loadScript('https://apis.google.com/js/api.js');
            await this.loadScript('https://accounts.google.com/gsi/client');

            // Initialize gapi
            await new Promise((resolve) => {
                gapi.load('client', resolve);
            });

            await gapi.client.init({
                apiKey: CONFIG.GOOGLE_API_KEY,
                discoveryDocs: [
                    'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest',
                    'https://sheets.googleapis.com/$discovery/rest?version=v4'
                ],
            });

            // Initialize token client for OAuth
            this.tokenClient = google.accounts.oauth2.initTokenClient({
                client_id: CONFIG.GOOGLE_CLIENT_ID,
                scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/spreadsheets',
                callback: (response) => {
                    if (response.access_token) {
                        this.accessToken = response.access_token;
                        gapi.client.setToken({ access_token: response.access_token });
                        console.log('✅ Google API autorizada');
                    }
                },
            });

            this.gapi = gapi;
            this.isInitialized = true;
            console.log('✅ Google API Client inicializado');

            return true;
        } catch (error) {
            console.error('❌ Error inicializando Google API:', error);
            return false;
        }
    }

    async loadScript(src) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async requestAuth() {
        return new Promise((resolve) => {
            this.tokenClient.callback = (response) => {
                if (response.access_token) {
                    this.accessToken = response.access_token;
                    gapi.client.setToken({ access_token: response.access_token });
                    resolve(true);
                } else {
                    resolve(false);
                }
            };

            this.tokenClient.requestAccessToken({ prompt: '' });
        });
    }

    async ensureAuth() {
        if (!this.accessToken) {
            return await this.requestAuth();
        }
        return true;
    }
}

window.GoogleAPIClient = GoogleAPIClient;
