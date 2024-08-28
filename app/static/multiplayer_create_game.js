document.addEventListener('DOMContentLoaded', () => {
    const levelChoosed = document.getElementById('level_choosed');
    const backButton = document.getElementById('back');

    levelChoosed.addEventListener('click', () => {
        window.location.href = '/multiplayer/create_game/room';
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
