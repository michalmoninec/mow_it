document.addEventListener('DOMContentLoaded', () => {
    let socket = null;

    map_p = JSON.parse(map);
    // console.log(map_p);
    // map_p.prototype.forEach((e) => console.log(e));

    const grid = document.getElementById('p_grid');

    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
            gridItem.id = `${col}${row}`;
            grid.appendChild(gridItem);
        }
    }

    // console.log(map_p);
    // map_p.forEach((element) => {
    //     console.log(element);
    // });
    updateGrid(map_p);

    function updateGrid(map) {
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
                position = data.position;
                //TODO: implement logic for movement.
                // console.log(data.map);
                updateGrid(data.map);
            })
            .catch((error) => console.error('Error:', error));
    }

    document.addEventListener('keydown', (event) => {
        const key = event.key;
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            sendKeyPress(key);
        }
    });
});
