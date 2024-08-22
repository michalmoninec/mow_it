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
            } else if (cell.blocker) {
                gridItem.className = 'blocked';
            } else {
                gridItem.className = 'grid-item';
            }
        }
    }
}

export function updateMap(map, key) {}
