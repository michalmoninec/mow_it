document.addEventListener('DOMContentLoaded', () => {
    const createGameButton = document.getElementById('create_game');
    const backButton = document.getElementById('back');

    let userID = getUserID();

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function retrieveUserAndRoom() {
        fetch('/multiplayer/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userID,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    console.log('ERROR OCCURED');
                }
                return response.json();
            })
            .then((data) => {
                if (data.user_id && data.room_id) {
                    localStorage.setItem('userID', data.user_id);
                    localStorage.setItem('roomID', data.room_id);
                }
                window.location.href = `/multiplayer/play`;
            });
    }

    createGameButton.addEventListener('click', () => {
        retrieveUserAndRoom();
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
