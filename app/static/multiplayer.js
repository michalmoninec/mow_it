document.addEventListener('DOMContentLoaded', () => {
    create_game = document.getElementById('create_game');

    create_game.addEventListener('click', () => {
        window.location.href = '/create_game';
    });
});
