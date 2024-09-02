import { updateGrid } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    let socket = io.connect('http://' + document.domain + ':' + location.port);
    let p1_val = document.getElementById('p1_val');
    let p2_val = document.getElementById('p2_val');
    let backButton = document.getElementById('back');

    const grid = document.getElementById('p_grid');
    const o_grid = document.getElementById('o_grid');
    let player_id;

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

    socket.on('connect', (data) => {
        console.log('Connected to server');
        socket.emit('join_room');
    });

    socket.on('request_maps_from_server', () => {
        console.log('getting maps after join');
        socket.emit('request_initial_maps');
    });

    socket.on('response_player_id', (data) => {
        player_id = data.player_id;
    });

    socket.on('disconnect', () => {
        console.log('disconnecting from server');
    });

    socket.on('response_update_data', (data) => {
        if (data['player_id'] == player_id) {
            updateGrid(data['map'], 'player');
        } else {
            updateGrid(data['map'], 'oponent');
        }
    });

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            event.preventDefault();
            sendKeyPress(key);
        }
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });

    function sendKeyPress(key) {
        socket.emit('request_update_data', { key: key });
    }
});
