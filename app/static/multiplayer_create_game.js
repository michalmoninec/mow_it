document.addEventListener('DOMContentLoaded', () => {
    const createGameButton = document.getElementById('create_game');
    const backButton = document.getElementById('back');

    let userID = getUserID();

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function retrieveUserAndRoom() {
        fetch('/multiplayer/create_game', {
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
                if (userID == null) {
                    localStorage.setItem('userID', data.user_id);
                }
                window.location.href = `/multiplayer_game/join_room/${data.room_id}`;
            });
    }

    createGameButton.addEventListener('click', () => {
        retrieveUserAndRoom();
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
