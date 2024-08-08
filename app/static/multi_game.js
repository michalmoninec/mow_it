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

    // updateGridItem(map_p);

    socket.on('connect', () => {
        console.log('Connected to server');
        socket.emit('joined');
    });

    socket.on('retrieve_map', (data) => {
        updateGrid(data.map, 'player');
        player_id = data.player_id;
    });

    socket.on('disconnect', () => {
        console.log('disconnecting from server');
    });

    socket.on('players', (data) => {
        console.log('Players ID:', data.players);
        let p1 = data.players.find((id) => id == player_id);
        let p2 = data.players.find((id) => id !== player_id);

        p1_val.innerText = 'Boy he thick!';
        if (p2) {
            p2_val.innerText = p2;
        } else {
            p2_val.innerText = 'Player not joined, but he better be thick!';
        }
    });

    socket.on('update_grid', (data) => {
        if (data['player_id'] == player_id) {
            updateGrid(data['map'], 'player');
        } else {
            pass;
            // updateGrid(data['map'], 'oponent');
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
        socket.emit('update_values', { key: key });
    }
});
