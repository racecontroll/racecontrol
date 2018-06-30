const Express = require("express");
const Http = require("http");
const Path = require("path");
const Redis = require("redis");
const Socketio = require("socket.io");


const app = Express();
const server = Http.Server(app)
const sio = Socketio(server);
const redis = Redis.createClient();


/* Redis error handler */
redis.on("error", function (err) {
    console.log("Error " + err);
});

/* Index server */
app.get('/',(req, res) => {
  res.sendFile(Path.join(__dirname + "/public/" + "/index.html"));
});

/* Socketio */
sio.on("connection",(socket) => {
  // Get IP
  const ip = socket.handshake.address;
  console.log(`${ip} connected`);

  // Track event
  socket.on("track-event", (e) => {
    // Log
    console.log(`Received track event: ${e}`);
    // Push to redis pubsub input_events
    const pub_event = {
        request: "track",
        type: "lap_finished",
        ...e
      };
    pub.publish("input_events", pub_event);
  }) 

  // Disconnect
  socket.on("disconnect", () => {
    console.log(`${ip} disconnected`);
  });
});

/* Start server */
server.listen(3000, () => {
  console.log("Listening on port 3000");
});
