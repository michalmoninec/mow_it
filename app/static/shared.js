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
                gridItem.className = 'active';
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

export function updateMap(map, key) {}

export function setModalPosition(grid, modal) {
    modal.style.width = `${grid.offsetWidth}px`;
    modal.style.height = `${grid.offsetHeight}px`;
    let pos = grid.getBoundingClientRect();
    // console.log(pos.top);
    modal.style.top = `${pos.top}px`;
    modal.style.left = `${pos.left}px`;
}
