export function updateGrid(map, player) {
    let idPrefix = '';
    if (player == 'oponent') {
        idPrefix = 'o';
    }

    for (const row of map) {
        for (const cell of row) {
            const gridItem = document.getElementById(
                `${idPrefix}${cell.x}${cell.y}`
            );
            if (cell.active) {
                gridItem.className = idPrefix + 'active';
            } else if (cell.visited) {
                gridItem.className = 'visited';
                gridItem.style.transform = 'none';
            } else if (cell.blocker) {
                gridItem.className = 'blocked';
                gridItem.style.transform = 'none';
            } else {
                gridItem.className = 'grid-item';
                gridItem.style.transform = 'none';
            }
        }
    }
}

export function setModalPosition(grid, modal) {
    modal.style.width = `${grid.offsetWidth}px`;
    modal.style.height = `${grid.offsetHeight}px`;
    let pos = grid.getBoundingClientRect();
    modal.style.top = `${pos.top}px`;
    modal.style.left = `${pos.left}px`;
}

export function validateMove(key, score) {
    let [posX, posY] = getMowerPosition();
    let [prevPosX, prevPosY] = [posX, posY];
    let newPos = [posX, posY];
    switch (key) {
        case 'ArrowUp':
            newPos = [posX, posY - 1];
            break;
        case 'ArrowDown':
            newPos = [posX, posY + 1];
            break;
        case 'ArrowLeft':
            newPos = [posX - 1, posY];
            break;
        case 'ArrowRight':
            newPos = [posX + 1, posY];
            break;
    }
    if (newPos[0] < 0 || newPos[0] > 9 || newPos[1] < 0 || newPos[1] > 9) {
        return [[posX, posY], score];
    }
    let gridItem = document.getElementById(`${newPos[0]}${newPos[1]}`);
    if (gridItem.classList.contains('blocked')) {
        return [[posX, posY], score];
    }
    gridItem.classList.add('active');
    if (gridItem.classList.contains('visited')) {
        score = score - 100;
    } else {
        score = score + 100;
    }
    gridItem = document.getElementById(`${posX}${posY}`);
    gridItem.classList.remove('active');
    gridItem.classList.add('visited');
    const style = window.getComputedStyle(gridItem);
    const transform = style.transform;
    gridItem.style.transform = transform === 'none' ? 'none' : 'rotate(90deg)';

    return [newPos, score];
}

export function getMowerPosition() {
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const gridItem = document.getElementById(`${col}${row}`);
            if (gridItem.classList.contains('active')) {
                return [col, row];
            }
        }
    }
}
