document.addEventListener('DOMContentLoaded', () => {
    let userID = getUserID();

    retrieveUserAndRoom();

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function retrieveUserAndRoom() {
        fetch('/join_room/set_user_and_room', {
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
                console.log(userID);
                if (data.room_id) {
                    window.location.href = '/multiplayer_game/play';
                } else {
                    window.location.href = '/';
                }
            });
    }
});
