document.addEventListener("DOMContentLoaded", () => {
    let socket = null;

    const single_player = document.getElementById("single_player");
    const multi_player = document.getElementById("multi_player");
    const versus_ai = document.getElementById("versus_ai");

    // document.addEventListener("keydown", (event) => {
    //     socket.emit("print_pressed", {
    //         player_id: playerId,
    //         pressed: event.key,
    //     });
    //     // console.log("Player " + playerId + " entered: " + event.key);
    // });

    single_player.addEventListener("click", () => {
        // socket.emit("route", { mode: "single_player" });
        window.location.href = "/single";
    });

    multi_player.addEventListener("click", () => {
        // socket.emit("route", { mode: "single_player" });

        // socket = io.connect("http://" + document.domain + ":" + location.port);

        // socket.on("connect", () => {
        //     console.log("Connected to server");
        // });

        // socket.on("player_id", (data) => {
        //     console.log("Player ID:", data.player_id);
        // });
        window.location.href = "/create_game";
    });

    versus_ai.addEventListener("click", () => {
        // socket.emit("route", { mode: "single_player" });
        window.location.href = "/versus_ai";
    });
});
