import { updateGrid } from './shared.js';

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('p_grid');
    const backButton = document.getElementById('back');
    const scoreLabel = document.getElementById('score_label');
    const levelLabel = document.getElementById('level_label');

    let map;
    let position;
    let score;
    let completed;
    let level;

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
        console.log('retrieve probehlo');
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
                let game_state = data.game_state;
                if (game_state.levels_completed) {
                    window.location.href = '/levels_completed';
                } else {
                    map = game_state.map;
                    position = game_state.pos;
                    score = game_state.score;
                    completed = game_state.completed;
                    level = game_state.level;
                    updateGrid(map, 'player');
                    updateScoreAndLevel(score, level);
                }
            })
            .catch((error) => console.error('Error:', error));
    }

    function sendKeyPress(key) {
        console.log(`position is ${position.x}, ${position.y}`);
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
                let game_state = data.game_state;
                if (game_state.levels_completed) {
                    window.location.href = '/levels_completed';
                } else {
                    map = game_state.map;
                    position = game_state.pos;
                    score = game_state.score;
                    level = game_state.level;
                    updateGrid(map, 'player');
                    updateScoreAndLevel(score, level);
                }

                if (game_state.completed) {
                    //show modal window and by choice move to next level, reset current level or move to homepage
                    retrieveMap();
                }
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

    function updateScoreAndLevel(score, level) {
        scoreLabel.innerHTML = score;
        levelLabel.innerHTML = level;
    }
});
