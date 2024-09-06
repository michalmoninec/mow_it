import { updateGrid, setModalPosition } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('p_grid');
    const backButton = document.getElementById('back');
    const scoreLabel = document.getElementById('score_label');
    const levelLabel = document.getElementById('level_label');
    const levelCompletedModal = document.getElementById('my_modal');
    const levelAdvanceLabel = document.getElementById('level_advance_label');

    const advanceLevelButton = document.getElementById('advance_level');
    const restartLevelButton = document.getElementById('restart_level');
    const returnHomeButton = document.getElementById('return_home');

    let map;
    let score;
    let completed;
    let allLevelsCompleted;
    let level;
    let userID = getUserID();
    console.log(userID);
    console.log(grid.offsetWidth);
    console.log(grid.getBoundingClientRect().top);

    //for now hardcoded 10x10 grid
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            grid.appendChild(gridItem);
        }
    }

    setModalPosition(
        document.getElementById('single_content'),
        document.getElementById('my_modal_content')
    );
    retrieveMap();

    function retrieveMap() {
        fetch('/single_player/retrieve_map', {
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
                let user_state = data.user_state;

                if (userID == null) {
                    localStorage.setItem('userID', data.user_id);
                }

                map = user_state.map;
                score = user_state.score;
                completed = user_state.completed;
                level = user_state.level;
                updateGrid(map, 'player');
                updateScoreAndLevel(score, level);
            })
            .catch((error) => console.error('Error:', error));
    }

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function sendKeyPress(key) {
        fetch('/single_player/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                key: key,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                let game_state = data.user_state;
                allLevelsCompleted = game_state.game_completed;

                map = game_state.map;
                score = game_state.score;
                level = game_state.level;
                // updatedMap = updateMap(map);
                updateGrid(map, 'player');
                updateScoreAndLevel(score, level);

                if (allLevelsCompleted) {
                    document.getElementById('level_advance_label').innerText =
                        'CONGRATULATIONS, ALL LEVELS CLEARED';
                }
                if (game_state.completed) {
                    levelCompletedModal.style.display = 'flex';
                }
            })
            .catch((error) => console.error('Error:', error));
    }

    function advanceCurrentLevel() {
        if (allLevelsCompleted) {
            window.location.href = '/single_player/level_selection';
        } else {
            fetch('/single_player/advance_current_level', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: '',
            })
                .then((response) => {
                    if (!response.ok) {
                        console.log('error occured');
                    }
                    return response.json();
                })
                .then(() => {
                    retrieveMap();
                })
                .catch((error) => console.error('Error:', error));
        }
    }

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            sendKeyPress(key);
        }
        if (['Enter'].includes(key)) {
            if (levelCompletedModal.style.display === 'flex') {
                advanceCurrentLevel();
                levelCompletedModal.style.display = 'none';
            }
        }
    });

    window.addEventListener('resize', () => {
        console.log('resize');
        setModalPosition(
            document.getElementById('single_content'),
            document.getElementById('my_modal_content')
        );
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    returnHomeButton.addEventListener('click', () => {
        window.location.href = '/';
        levelCompletedModal.style.display = 'none';
    });

    advanceLevelButton.addEventListener('click', () => {
        advanceCurrentLevel();
        levelCompletedModal.style.display = 'none';
    });

    restartLevelButton.addEventListener('click', () => {
        retrieveMap();
        levelCompletedModal.style.display = 'none';
    });

    function updateScoreAndLevel(score, level) {
        scoreLabel.innerHTML = score;
        levelLabel.innerHTML = level;
    }
});
