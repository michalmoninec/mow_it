document.addEventListener('DOMContentLoaded', () => {
    const appTitle = document.getElementById('app-title');
    // const navbarSpacer = document.getElementById('navbar-spacer');
    // const appLogin = document.getElementById('app-login');

    // fillSpacer();

    appTitle.addEventListener('click', () => {
        window.location.href = '/';
    });

    // function fillSpacer() {
    //     navbarSpacer.style.width = window.getComputedStyle(appLogin).width;
    // }

    window.addEventListener('resize', () => {
        // fillSpacer();
    });
});
