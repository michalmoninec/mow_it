document.addEventListener('DOMContentLoaded', () => {
    const singlePlayerButton = document.getElementById('single_player');
    const multiplayerButton = document.getElementById('multi_player');
    const versusAIButton = document.getElementById('versus_ai');
    const mapCreationButton = document.getElementById('map_creation');

    singlePlayerButton.addEventListener('click', () => {
        window.location.href = '/single_player_level_selection';
    });

    multiplayerButton.addEventListener('click', () => {
        window.location.href = '/multiplayer_level_selection';
    });

    versusAIButton.addEventListener('click', () => {
        window.location.href = '/versus_ai';
    });

    mapCreationButton.addEventListener('click', () => {
        window.location.href = '/map_creation';
    });
});
