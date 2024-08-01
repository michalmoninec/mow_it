document.addEventListener("DOMContentLoaded", () => {
    // socket = io.connect("http://" + document.domain + ":" + location.port);
    create_game = document.getElementById("create_game");

    // socket.on("connect", () => {
    //     console.log("Connected to server");
    // });

    // socket.on("players", (data) => {
    //     console.log("Players ID:", data.players);
    // });

    // socket.on("player_joined", (data) => {
    //     console.log("Players: ", data.players);
    // });

    // document.addEventListener("keydown", (event) => {
    //     socket.emit("print_pressed", {
    //         player_id: player_id,
    //         pressed: event.key,
    //     });
    //     // console.log("Player " + playerId + " entered: " + event.key);
    // });

    create_game.addEventListener("click", () => {
        window.location.href = "/create_game";
    });
});
