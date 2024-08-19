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
                gridItem.classList.add('active');
            } else if (cell.visited) {
                gridItem.classList.remove('active');
                gridItem.classList.add('visited');
            } else if (cell.blocker) {
                gridItem.classList.remove('active');
                gridItem.classList.add('blocked');
            } else {
                gridItem.classList.remove('active');
                gridItem.classList.remove('visited');
            }
        }
    }
}
