document.addEventListener('DOMContentLoaded', () => {
    socket = io.connect('http://' + document.domain + ':' + location.port);
    p1_val = document.getElementById('p1_val');
    p2_val = document.getElementById('p2_val');

    let p1_posX = 0;
    let p1_posY = 0;
    let last_visited = [p1_posX, p1_posY];

    const grid = document.getElementById('p_grid');
    const o_grid = document.getElementById('o_grid');

    map_p = JSON.parse(map);

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            grid.appendChild(gridItem);
        }
    }

    updateGridItem(map_p);

    socket.on('connect', () => {
        console.log('Connected to server');
        socket.emit('joined');
    });

    socket.on('disconnect', () => {
        console.log('disconnecting from server');
    });

    socket.on('players', (data) => {
        console.log('Players ID:', data.players);
        let p1 = data.players.find((id) => id == player_id);
        let p2 = data.players.find((id) => id !== player_id);

        p1_val.innerText = p1;
        if (p2) {
            p2_val.innerText = p2;
        } else {
            p2_val.innerText = 'Player not joined.';
        }

        console.log(p1);
        // let opponentId = Object.keys(maps).find((id) => id !== playerId);
    });

    socket.on('update_grid', (data) => {
        // console.log(p1_map);
        if (data['player_id'] == player_id) {
            updateGridItem(data['map']);
        } else {
            updateGridItemOponent(data['coords'][0], data['coords'][1]);
        }
    });

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            event.preventDefault();
            sendKeyPress(key);
        }
    });

    function sendKeyPress(key) {
        socket.emit('update_values', { key: key });
    }

    function updateGridItem(map) {
        console.log(map);
    }

    function updateGridItem(map) {
        for (const row of map) {
            for (const cell of row) {
                gridItem = document.getElementById(`${cell.x}${cell.y}`);
                if (cell.active) {
                    gridItem.classList.add('active');
                } else if (cell.visited) {
                    gridItem.classList.remove('active');
                    gridItem.classList.add('visited');
                } else {
                    gridItem.classList.remove('active');
                }
            }
        }
    }
});
