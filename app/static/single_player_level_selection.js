document.addEventListener('DOMContentLoaded', () => {
    const levelChoosed = document.getElementById('level_choosed');
    const backButton = document.getElementById('back');
    const achievedLevels = document.getElementById('achieved_levels');

    let userID = getUserID();

    getUserData();

    function getUserData() {
        fetch('/single_player/level_data', {
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
                    console.log('error occured');
                }
                return response.json();
            })
            .then((data) => {
                if (userID == null) {
                    localStorage.setItem('userID', data.user_id);
                }
                displayAchievedLevels(data.levels);
            });
    }

    function setSelectedLevel(level) {
        fetch('/single_player/selected_level', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                selected_level: level,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    console.log('error occured');
                }
                return response.json();
            })
            .then((data) => {
                window.location.href = '/single_player';
            });
    }

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function displayAchievedLevels(levels) {
        for (let level = 1; level < levels.length + 1; level++) {
            const levelItem = document.createElement('button');
            levelItem.innerText = `Level ${level}`;
            levelItem.id = `level_${level}`;
            levelItem.addEventListener('click', () => {
                setSelectedLevel(level);
            });
            achievedLevels.appendChild(levelItem);
        }
    }

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
