/**
 *  Main interface to the racecontrol backend
 */
class WSUpdate {

  /**
   * Connects to a websocket
   **/
  constructor({host, port, streamPath, inputPath}) {
    this.stream = new WebSocket(`ws://${host}:${port}/${streamPath}`);
    this.input = new WebSocket(`ws://${host}:${port}/${inputPath}`);
    this.stream.onmessage = this.handle;
  }

  /**
   * Handles incoming messages
   */
  handle(e) {
    try {
      // Parse input
      const input = JSON.parse(e.data);
      switch(input.type) {
        case "update_positions":
          WSUpdate.updateView(input);
          break;
        default:
          console.log(`Unknown type: ${input.type}`);
          break;
      }
    } catch(e) {
      console.error(e);
    }
  }

  /**
   * Generates the table header
   */
  static getTableHeader() {
    const headers = ["POSITION", "NAME", "TOTAL LAPS", "BEST LAP", "LAST LAP"];

    let toRet = "<thead>";
    for(let header of headers) {
      toRet += `<th>${header}</th>`;
    }
    toRet += "</thead>"

    return toRet;
  }

  /**
   * Generates the dynamic position view
   */
  static updateView(currState) {
    let tableInnerHTML = WSUpdate.getTableHeader() + "<tr>";

    // Iterate over the state and generate the inner HTML for the table
    for(let driverId of currState["positions"]) {
      driverId = driverId[0]; // @TODO, for now ignore the lap count and get it from the state dict
      const shortname = document.getElementById(`player-${driverId}-shortname`).innerHTML;
      // Build row
      let row = `<tr class="player-entry" id="player-${driverId}">
                      <td id="player-${driverId}-position">#${driverId}</td>
                      <td>${shortname}</td>
                      <td id="player-${driverId}-lap-count">${currState[driverId].lap_count}</td>
                      <td id="player-${driverId}-best-lap">${currState[driverId].best_time / 1000.0}s</td>
                      <td id="player-${driverId}-lap-time-last">${currState[driverId].lap_time / 1000.0}s</td>
                  </tr>`;
      tableInnerHTML += row;
    }
    tableInnerHTML += "</tr>"

    // Set new table
    document.getElementById("stateTable").innerHTML = tableInnerHTML;
  }

  /**
   * Start game
   */
  start() {
    console.log("Starting race");
    try {
      this.input.send(JSON.stringify({"request": "start"}));
    } catch(e) {
      console.error(e);
    }
  }

  /**
   * Pause game
   */
  pause() {
    try {
    this.input.send(JSON.stringify({"request": "pause"}));
    } catch(e) {
      console.error(e);
    }
  }

  /**
   * Reset game
   */
  reset() {
    try {
    this.input.send(JSON.stringify({"request": "reset"}));
    } catch(e) {
      console.error(e);
    }
  }

  /**
   * @TODO REMOVE
   *
   * Sends a track event
   */
  trackEvent({trackId, time}) {
    try {
      this.input.send(JSON.stringify({
        "request": "track",
        "type": "lap_finished",
        "track_id": trackId,
        "lap_finished": time
      }));
    } catch(e)  {
      console.error(e);
    }
  }

}
