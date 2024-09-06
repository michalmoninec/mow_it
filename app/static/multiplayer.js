import { updateGrid, setModalPosition } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    let socket = io.connect('http://' + document.domain + ':' + location.port);

    let p1_name = document.getElementById('p1_name');
    let p1_score = document.getElementById('p1_score');
    let p1_level = document.getElementById('p1_level');
    let p1_grid = document.getElementById('p1_grid');
    let p1_modal = document.getElementById('player_modal');
    let p1_modal_text = document.getElementById('player_modal_text');

    let p2_name = document.getElementById('p2_name');
    let p2_score = document.getElementById('p2_score');
    let p2_level = document.getElementById('p2_level');
    let p2_grid = document.getElementById('p2_grid');
    let p2_modal = document.getElementById('oponent_modal');
    let p2_modal_text = document.getElementById('oponent_modal_text');

    let backButton = document.getElementById('back');
    let player_id;
    let gameStatus;
    let readyToPlay;

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
        socket.emit('join_room');
    });

    socket.on('response_player_id_and_status', (data) => {
        player_id = data.player_id;
        gameStatus = data.game_status;

        if (gameStatus == 'ready') {
            socket.emit('request_maps_from_server');
        } else if (gameStatus == 'finished') {
            finishedGame();
        } else {
            waitingForPlayerToJoin();
        }
    });

    socket.on('response_maps_from_server', () => {
        readyToPlay = true;
        //TODO - maybe needs modal disable
        socket.emit('request_initial_maps');
    });

    socket.on('response_update_data', (data) => {
        if (data.player_id == player_id) {
            setModalDisable(p1_modal);
            updateGrid(data.map, 'player');
            p1_name.innerText = data['name'];
            p1_level.innerText = data['level'];
            p1_score.innerText = data['score'];
            if (data.game_completed) {
                console.log('Game finished');
                socket.emit('request_game_finished');
            } else if (data.level_completed) {
                console.log('Level finished');
                socket.emit('request_level_advance_confirmation');
            }
        } else {
            setModalDisable(p2_modal);
            updateGrid(data.map, 'oponent');
            p2_name.innerText = data['name'];
            p2_level.innerText = data['level'];
            p2_score.innerText = data['score'];
        }
    });

    socket.on('response_player_finished_level', (data) => {
        console.log('Player finished level.');
        if (data.player_id == player_id) {
            readyToPlay = false;
            p1_modal_text.innerText = 'Level completed, waiting for oponent.';
            setModalVisible(p1_modal);
        } else {
            p2_modal_text.innerText = 'Level completed.';
            setModalVisible(p2_modal);
        }
    });

    socket.on('response_advance_level_confirmation', () => {
        readyToPlay = true;
        socket.emit('request_level_advance');
    });

    socket.on('response_player_finished_game', (data) => {
        if (data.player_id == player_id) {
            readyToPlay = false;
            p1_modal_text.innerText = 'All levels completed, congratulations.';
            setModalVisible(p1_modal);
        } else {
            p2_modal_text.innerText = 'All levels completed.';
            setModalVisible(p2_modal);
        }
    });

    socket.on('disconnect', () => {
        console.log('disconnecting from server');
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
        console.log('resize');
        setModalPosition(
            document.getElementById('player_container'),
            document.getElementById('player_modal_content')
        );
        setModalPosition(
            document.getElementById('oponent_container'),
            p2_modal
        );
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    function sendKeyPress(key) {
        if (readyToPlay) {
            socket.emit('request_update_data', { key: key });
        }
    }

    function waitingForPlayerToJoin() {
        console.log('Game not ready yet..');
        readyToPlay = false;
        gridContainerPlayer.innerHTML =
            'Player ready - Waiting for another player to join game.';
        gridContainerOponent.innerHTML = 'Player not joined.';
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

    function playerFinishedLevel() {}
    function playerFinishedGame() {}
});
