document.addEventListener('DOMContentLoaded', () => {
    const appTitle = document.getElementById('app-title');

    appTitle.addEventListener('click', () => {
        window.location.href = '/';
    });
});
