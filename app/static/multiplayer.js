import { updateGrid } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    let socket = io.connect('http://' + document.domain + ':' + location.port);
    let p1_name = document.getElementById('p1_name');
    let p1_score = document.getElementById('p1_score');
    let p1_level = document.getElementById('p1_level');

    let p2_name = document.getElementById('p2_name');
    let p2_score = document.getElementById('p2_score');
    let p2_level = document.getElementById('p2_level');

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
    const grid = document.createElement('div');
    grid.id = 'p-grid';
    grid.className = 'grid';
    const o_grid = document.createElement('div');
    o_grid.id = 'o_grid';
    o_grid.className = 'grid';

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            grid.appendChild(gridItem);
        }
    }

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `o${col}${row}`;
            o_grid.appendChild(gridItem);
        }
    }

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
        gridContainerPlayer.innerHTML = grid.outerHTML;
        gridContainerOponent.innerHTML = o_grid.outerHTML;
        socket.emit('request_initial_maps');
    });

    socket.on('response_update_data', (data) => {
        if (data.player_id == player_id) {
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
            updateGrid(data.map, 'oponent');
            p2_name.innerText = data['name'];
            p2_level.innerText = data['level'];
            p2_score.innerText = data['score'];
        }
    });

    socket.on('response_player_finished_level', (data) => {
        console.log('Player finished level.');
        if (data.player_id == player_id) {
            gridContainerPlayer.innerHTML =
                'Waiting for another player to finish level.';
        } else {
            gridContainerOponent.innerHTML =
                'Waiting for another player to finish level.';
        }
    });

    socket.on('response_advance_level_confirmation', () => {
        readyToPlay = true;
        gridContainerPlayer.innerHTML = grid.outerHTML;
        gridContainerOponent.innerHTML = o_grid.outerHTML;
        socket.emit('request_level_advance');
    });

    socket.on('response_player_finished_game', (data) => {
        if (data.player_id == player_id) {
            readyToPlay = false;
            gridContainerPlayer.innerHTML = 'All levels completed.';
        } else {
            gridContainerOponent.innerHTML = 'All levels completed.';
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

    function playerFinishedLevel() {}
    function playerFinishedGame() {}
});
