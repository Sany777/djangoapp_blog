const delayInMilliseconds = 3000;

const redirectUrl = '/blog/';

function redirectToDashboard() {
    window.location.href = redirectUrl;
}


setTimeout(redirectToDashboard, delayInMilliseconds);