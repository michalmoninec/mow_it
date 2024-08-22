document.addEventListener('DOMContentLoaded', () => {
    const levelChoosed = document.getElementById('level_choosed');
    const backButton = document.getElementById('back');

    levelChoosed.addEventListener('click', () => {
        window.location.href = '/single_player';
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
