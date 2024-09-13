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
    const grassBlock = document.getElementById('grass-block');

    let map;
    let score;
    let completed;
    let allLevelsCompleted;
    let level;
    let userID = getUserID();
    let readyToPlay;
    let lastDirection = 'horizontal';

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
                readyToPlay = true;
                updateGrid(map, 'player', grassBlock);
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
                updateGrid(map, 'player', grassBlock);
                updateScoreAndLevel(score, level);
                rotateMower(key, lastDirection);

                if (allLevelsCompleted) {
                    document.getElementById('level_advance_label').innerText =
                        'CONGRATULATIONS, ALL LEVELS CLEARED';
                }
                if (game_state.completed) {
                    readyToPlay = false;
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

    function rotateMower(key, lastDirection) {
        console.log(key);
        console.log(lastDirection);
        if (
            ['ArrowLeft', 'ArrowRight'].includes(key) &&
            lastDirection != 'horizontal'
        ) {
            console.log('Should rotate to horizontal');
            document.querySelector('.active').style.transform = 'rotate(90deg)';
            lastDirection = 'horizontal';
        } else if (
            ['ArrowUp', 'ArrowDown'].includes(key) &&
            lastDirection != 'vertical'
        ) {
            console.log('Should rotate to vertical');
            document.querySelector('.active').style.transform = 'rotate(90deg)';
            lastDirection = 'vertical';
        }
    }

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (
            ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key) &&
            readyToPlay
        ) {
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
    let prevButtonStates = [];

    function pollGamepad() {
        const gamepads = navigator.getGamepads();

        if (gamepads[0]) {
            // Check if at least one gamepad is connected
            const gamepad = gamepads[0];

            // Loop through all the buttons
            gamepad.buttons.forEach((button, index) => {
                // Check if the button was just pressed
                if (button.pressed && !prevButtonStates[index]) {
                    console.log(`Button ${index} pressed`);
                }

                // Check if the button was just released
                if (!button.pressed && prevButtonStates[index]) {
                    console.log(`Button ${index} released`);
                }

                // Store the current state for the next frame
                prevButtonStates[index] = button.pressed;
            });
        }

        // Keep polling the gamepad
        requestAnimationFrame(pollGamepad);
    }
    let prevAxesStates = [];

    function pollGamepadAxes() {
        const gamepads = navigator.getGamepads();

        if (gamepads[0]) {
            // Check if at least one gamepad is connected
            const gamepad = gamepads[0];

            // Loop through all the axes
            gamepad.axes.forEach((axisValue, index) => {
                // Check if the axis value has changed significantly (to avoid noise)
                const threshold = 0.1; // Define a threshold to detect significant movement
                if (
                    Math.abs(axisValue - (prevAxesStates[index] || 0)) >
                    threshold
                ) {
                    console.log(`Axis ${index} moved: ${axisValue}`);
                }

                // Store the current state for the next frame
                prevAxesStates[index] = axisValue;
            });
        }

        // Keep polling the gamepad
        requestAnimationFrame(pollGamepadAxes);
    }

    // Start polling when the gamepad is connected

    // Start polling the gamepad when it is connected
    // window.addEventListener('gamepadconnected', () => {
    //     prevButtonStates = []; // Initialize the previous button states
    //     prevAxesStates = []; // Initialize the previous axis states
    //     requestAnimationFrame(pollGamepadAxes);
    //     requestAnimationFrame(pollGamepad);
    // });
});
