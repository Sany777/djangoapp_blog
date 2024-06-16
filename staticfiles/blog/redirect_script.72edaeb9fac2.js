const delayInMilliseconds = 2000;

const redirectUrl = '/blog/';

function redirectToDashboard() {
    window.location.href = redirectUrl;
}


setTimeout(redirectToDashboard, delayInMilliseconds);