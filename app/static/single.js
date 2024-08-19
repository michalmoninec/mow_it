import { updateGrid } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('p_grid');
    const backButton = document.getElementById('back');

    let map;
    let position;
    let score;

    //for now hardcoded 10x10 grid
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            grid.appendChild(gridItem);
        }
    }

    retrieveMap();

    function retrieveMap() {
        fetch('/single_player/retrieve_map', {
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
            .then((data) => {
                updateGrid(data.map, 'player');
                map = data.map;
                position = data.pos;
                score = data.score;
            })
            .catch((error) => console.error('Error:', error));
    }

    function sendKeyPress(key) {
        fetch('/single_player/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                key: key,
                map: map,
                pos: position,
                score: score,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                updateGrid(data.map, 'player');
                map = data.map;
                position = data.pos;
                score = data.score;
            })
            .catch((error) => console.error('Error:', error));
    }

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            sendKeyPress(key);
        }
    });

    backButton.addEventListener('click', () => {
        window.location.href = '/';
    });
});
