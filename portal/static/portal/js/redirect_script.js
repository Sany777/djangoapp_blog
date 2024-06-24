const DELAY_MS = 2500;

const REDIRECT_URL = '/blog/';

function redirectToDashboard() {
    window.location.href = REDIRECT_URL;
}

setTimeout(redirectToDashboard, DELAY_MS);