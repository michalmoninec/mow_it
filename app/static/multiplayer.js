import {
    updateGrid,
    setModalPosition,
    getMowerPosition,
    validateMove,
} from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    let socket = io.connect('http://' + document.domain + ':' + location.port);

    let p1_name = document.getElementById('p1_name');
    let p1_score = document.getElementById('p1_score');
    // let p1_level = document.getElementById('p1_level');
    let p1_grid = document.getElementById('p1_grid');
    let p1_modal = document.getElementById('player_modal');
    let p1_modal_text = document.getElementById('player_modal_text');
    let p1_rounds_label = document.getElementById('player_rounds');
    let p1ModalLinkDiv = document.getElementById('link-div');

    let p2_name = document.getElementById('p2_name');
    let p2_score = document.getElementById('p2_score');
    // let p2_level = document.getElementById('p2_level');
    let p2_grid = document.getElementById('p2_grid');
    let p2_modal = document.getElementById('oponent_modal');
    let p2_modal_text = document.getElementById('oponent_modal_text');
    let p2_rounds_label = document.getElementById('oponent_rounds');

    let endGameModal = document.getElementById('end_game_modal');

    let backButton = document.getElementById('back');
    let homePageButton = document.getElementById('back_home');
    let roundHomePageButton = document.getElementById('round_back_home');
    let restartGameButton = document.getElementById('restart_game');
    let roundValue = document.getElementById('round_value');
    let winnerLabel = document.getElementById('winner_label');
    let levelLabel = document.getElementById('level-value');
    let roundEndModal = document.getElementById('round_end_modal');
    let roundWinnerLabel = document.getElementById('winner-label');
    let nextRoundButton = document.getElementById('next_round');

    const grassBlock = document.getElementById('grass-block');
    let user_id = getUserID();
    let room_id = getRoomID();
    let gameStatus;
    let readyToPlay;
    let oponentMap;

    let lastDirection = 'horizontal';

    const gridContainerPlayer = document.getElementById(
        'grid-container-player'
    );
    const gridContainerOponent = document.getElementById(
        'grid-container-oponent'
    );

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            p1_grid.appendChild(gridItem);
        }
    }

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `o${col}${row}`;
            p2_grid.appendChild(gridItem);
        }
    }

    setModalPosition(
        document.getElementById('player_container'),
        document.getElementById('player_modal_content')
    );
    setModalPosition(document.getElementById('oponent_container'), p2_modal);

    socket.on('connect', () => {
        console.log('Connected to server');
        fetch('/multiplayer/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: user_id,
                room_id: room_id,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    console.log('ERROR OCCURED');
                }
                return response.json();
            })
            .then((data) => {
                console.log(data.valid);
                if (data.valid) {
                    socket.emit('join_room', {
                        user_id: user_id,
                        room_id: room_id,
                    });
                } else {
                    window.location.href = `/`;
                }
            });
    });

    socket.on('response_user_id_and_status', (data) => {
        user_id = data.user_id;
        gameStatus = data.game_status;
        room_id = data.room_id;

        if (gameStatus == 'finished') {
            readyToPlay = false;
            setModalDisable(p1_modal);
            setModalDisable(p2_modal);
            setModalVisible(endGameModal);
        } else if (gameStatus == 'ready') {
            p1ModalLinkDiv.style.display = 'none';
            socket.emit('request_maps_from_server', { room_id: room_id });
        } else if (gameStatus == 'finished') {
            finishedGame();
        } else {
            waitingForPlayerToJoin();
        }
    });

    socket.on('response_maps_from_server', () => {
        setModalDisable(roundEndModal);
        readyToPlay = true;
        socket.emit('request_initial_maps', {
            user_id: user_id,
            room_id: room_id,
        });
    });

    socket.on('response_update_data', (data) => {
        if (data.user_id == user_id) {
            setModalDisable(p1_modal);
            setModalDisable(endGameModal);
            updateGrid(data.map, 'player');
            if (data.key) {
                rotateMower(data.key);
            }
            p1_name.innerText = data.name;
            p1_score.innerText = data.score;
            p1_rounds_label.innerText = data.rounds_won;
            if (data.game_completed) {
                socket.emit('request_game_finished', {
                    user_id: user_id,
                    room_id: room_id,
                });
            } else if (data.level_completed) {
                socket.emit('request_level_advance_confirmation', {
                    room_id: room_id,
                    user_id: user_id,
                });
            }
        } else {
            setModalDisable(p2_modal);
            setModalDisable(endGameModal);
            if (data.map) {
                oponentMap = data.map;
                updateGrid(data.map, 'oponent');
            }
            if (data.key) {
                rotateOponentMower(data.key);
            }
            p2_name.innerText = data['name'];
            p2_score.innerText = data['score'];
            p2_rounds_label.innerText = data.rounds_won;
        }
    });
    socket.on('response_update_my_oponent', (data) => {
        if (data.user_id == user_id) {
            if (data.map) {
                oponentMap = data.map;
                updateGrid(data.map, 'oponent');
            }
            if (data.key) {
                rotateOponentMower(data.key);
            }
            p2_name.innerText = data['name'];
            p2_score.innerText = data['score'];
            p2_rounds_label.innerText = data.rounds_won;
        }
    });
    socket.on('response_update_oponent_data', (data) => {
        if (data.user_id != user_id) {
            if (data.map) {
                oponentMap = data.map;
                updateGrid(data.map, 'oponent');
            }
            if (data.key) {
                rotateOponentMower(data.key);
            }
            p2_name.innerText = data['name'];
            p2_score.innerText = data['score'];
            p2_rounds_label.innerText = data.rounds_won;
        }
    });

    socket.on('response_player_finished_level', (data) => {
        console.log('Player finished level.');
        if (data.user_id == user_id) {
            readyToPlay = false;
            p1_modal_text.innerText = 'Level completed, waiting for oponent.';
            p1ModalLinkDiv.style.display = 'none';
            setModalVisible(p1_modal);
        } else {
            p2_modal_text.innerText = 'Level completed.';
            setModalVisible(p2_modal);
        }
    });

    socket.on('response_advance_level_confirmation', () => {
        console.log('server thinks he is ready to advance for this client');
        readyToPlay = true;
        socket.emit('request_level_advance', {
            user_id: user_id,
            room_id: room_id,
        });
    });

    socket.on('response_player_finished_game', (data) => {
        if (data.user_id == user_id) {
            readyToPlay = false;
            p1_modal_text.innerText =
                'All levels of this round completed, congratulations.';
            setModalVisible(p1_modal);
        } else {
            p2_modal_text.innerText = 'All levels of this round completed.';
            setModalVisible(p2_modal);
        }
    });

    socket.on('response_both_players_finished_game', (data) => {
        if (data.round_winner == user_id) {
            readyToPlay = false;
            roundWinnerLabel.innerText = 'You have won this round!';
            setModalDisable(p1_modal);
            setModalVisible(roundEndModal);
        } else {
            readyToPlay = false;
            setModalDisable(p1_modal);
            roundWinnerLabel.innerText = 'Oponent has won this round!';
            setModalVisible(roundEndModal);
        }
    });

    socket.on('response_player_finished_all_rounds', (data) => {
        readyToPlay = false;
        setModalDisable(p1_modal);
        setModalDisable(p2_modal);
        setModalVisible(endGameModal);
        if (data.winner_id == user_id) {
            winnerLabel.innerText = 'You won.';
        } else if (data.winner_id == null) {
            winnerLabel.innerText = 'It is a tie.';
        } else {
            winnerLabel.innerText = 'Oponent won.';
        }
    });

    socket.on('response_round_update', (data) => {
        roundValue.innerText = data.round;
        levelLabel.innerText = data.level;
    });

    socket.on('response_init_data_update', () => {
        socket.emit('request_data_update', {
            user_id: user_id,
            room_id: room_id,
        });
    });

    socket.on('response_score_update', (data) => {
        if (data.user_id == user_id) {
            p1_score.innerText = data.score;
            p1_rounds_label.innerText = data.rounds_won;
        } else {
            p2_score.innerText = data.score;
            p2_rounds_label.innerText = data.rounds_won;
        }
    });

    socket.on('response_player_disconnected', () => {
        // socket.emit('join_room');
        console.log('someone disconnected');
    });

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            event.preventDefault();
            sendKeyPress(key);
        }
        if (key == 'Enter') {
            socket.emit('advance_level_confirmed');
        }
    });

    window.addEventListener('resize', () => {
        setModalPosition(
            document.getElementById('player_container'),
            document.getElementById('player_modal_content')
        );
        setModalPosition(
            document.getElementById('oponent_container'),
            p2_modal
        );
    });

    window.onbeforeunload = function () {
        socket.disconnect();
        console.log('before unload happens..');
        socket.emit('disconnect', {
            user_id: user_id,
            room_id: room_id,
        });
    };

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    homePageButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    roundHomePageButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    nextRoundButton.addEventListener('click', () => {
        socket.emit('request_round_advance', {
            user_id: user_id,
            room_id: room_id,
        });
    });

    restartGameButton.addEventListener('click', () => {
        socket.emit('request_game_state_reset', {
            room_id: room_id,
        });
    });

    function updateGameState(key) {
        let newPos = validateMove(key);
        if (newPos) {
            socket.emit('request_update_data', {
                key: key,
                user_id: user_id,
                room_id: room_id,
            });
            lastDirection = key;
        }
    }

    function sendKeyPress(key) {
        if (readyToPlay) {
            updateGameState(key);
            rotateMower(key);
        }
    }

    function waitingForPlayerToJoin() {
        console.log('Game not ready yet..');
        readyToPlay = false;
        p1_modal_text.innerText = `Waiting for oponent to join.`;
        p1ModalLinkDiv.innerText = getRoomLink();

        setModalVisible(p1_modal);
    }

    function startGame() {
        console.log('Game is ready, starting!');
    }

    function finishedGame() {
        console.log('Game finished');
    }

    function setModalVisible(modal) {
        console.log('modal should be visible');
        modal.style.display = 'flex';
    }

    function setModalDisable(modal) {
        modal.style.display = 'none';
    }

    function getRoomLink() {
        return `http://${document.domain}:${location.port}/multiplayer/join/${room_id}`;
    }

    function rotateMower(key) {
        if (['ArrowLeft', 'ArrowRight'].includes(key)) {
            document.querySelector('.active').style.transform = 'rotate(0deg)';
        } else if (['ArrowUp', 'ArrowDown'].includes(key)) {
            document.querySelector('.active').style.transform = 'rotate(90deg)';
            console.log('should be vertical');
        }
    }

    function rotateOponentMower(key) {
        if (['ArrowLeft', 'ArrowRight'].includes(key)) {
            document.querySelector('.oactive').style.transform = 'rotate(0deg)';
        } else if (['ArrowUp', 'ArrowDown'].includes(key)) {
            document.querySelector('.oactive').style.transform =
                'rotate(90deg)';
        }
    }

    function getUserID() {
        return localStorage.getItem('userID');
    }

    function getRoomID() {
        return localStorage.getItem('roomID');
    }

    p1ModalLinkDiv.addEventListener('click', () => {
        console.log('button works');
        // window.location.href = '/';
    });
});
