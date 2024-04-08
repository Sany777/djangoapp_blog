const delayInMilliseconds = 2500;

const redirectUrl = '/blog/';

function redirectToDashboard() {
    window.location.href = redirectUrl;
}

setTimeout(redirectToDashboard, delayInMilliseconds);