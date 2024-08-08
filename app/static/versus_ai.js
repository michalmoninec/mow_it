document.addEventListener('DOMContentLoaded', () => {
    let backButton = document.getElementById('back');

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
