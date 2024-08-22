document.addEventListener('DOMContentLoaded', () => {
    const levelChoosed = document.getElementById('save_map');
    const backButton = document.getElementById('back');

    // levelChoosed.addEventListener('click', () => {
    //     window.location.href = '/create_multiplayer_game';
    // });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
