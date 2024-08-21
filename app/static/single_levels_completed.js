document.addEventListener('DOMContentLoaded', () => {
    resetLevelsButton = document.getElementById('reset_levels');
    homepageButton = document.getElementById('homepage');

    homepageButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    resetLevelsButton.addEventListener('click', () => {
        window.location.href = '/single_player_reset_level';
    });
});
