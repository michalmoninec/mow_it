document.addEventListener('DOMContentLoaded', () => {
    let userID = getUserID();

    console.log(roomID);

    retrieveUserAndRoom();

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function retrieveUserAndRoom() {
        fetch(`/multiplayer/join/${roomID}/`, {
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
                if (data.user_id) {
                    localStorage.setItem('userID', data.user_id);
                    localStorage.setItem('roomID', data.room_id);
                }
                if (data.room_id) {
                    window.location.href = '/multiplayer/play';
                } else {
                    window.location.href = '/';
                }
            });
    }
});
