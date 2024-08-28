document.addEventListener('DOMContentLoaded', () => {
    const singlePlayerButton = document.getElementById('single_player');
    const multiplayerButton = document.getElementById('multi_player');

    singlePlayerButton.addEventListener('click', () => {
        window.location.href = '/single_player/level_selection';
    });

    multiplayerButton.addEventListener('click', () => {
        window.location.href = '/multiplayer/create_game';
    });
});
