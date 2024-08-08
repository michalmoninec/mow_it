import { updateGrid } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('p_grid');
    const backButton = document.getElementById('back');

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
        fetch('/single/ready', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: '',
        })
            .then((response) => response.json())
            .then((data) => {
                updateGrid(data.map, 'player');
            })
            .catch((error) => console.error('Error:', error));
    }

    function sendKeyPress(key) {
        fetch('/single/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ key: key }),
        })
            .then((response) => response.json())
            .then((data) => {
                updateGrid(data.map, 'player');
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
