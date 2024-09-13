document.addEventListener('DOMContentLoaded', () => {
    const levelChoosed = document.getElementById('level_choosed');
    const backButton = document.getElementById('back');

    let userID = getUserID();

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function retrieveUserAndRoom() {
        fetch('/multiplayer/create_game/get_user_and_room', {
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
            })
            .then(() => {
                window.location.href = '/multiplayer/create_game/room';
            });
    }

    levelChoosed.addEventListener('click', () => {
        retrieveUserAndRoom();
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
