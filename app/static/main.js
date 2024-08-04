document.addEventListener('DOMContentLoaded', () => {
    const single_player = document.getElementById('single_player');
    const multi_player = document.getElementById('multi_player');
    const versus_ai = document.getElementById('versus_ai');

    single_player.addEventListener('click', () => {
        window.location.href = '/single';
    });

    multi_player.addEventListener('click', () => {
        window.location.href = '/create_game';
    });

    versus_ai.addEventListener('click', () => {
        window.location.href = '/versus_ai';
    });
});
