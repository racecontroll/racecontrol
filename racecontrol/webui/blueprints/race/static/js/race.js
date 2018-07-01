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
          WSUpdate.updatePositionView(input);
          WSUpdate.updateUiButtons(input.status);
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
   * Updates the UI icons based on the game state
   */
  static updateUiButtons(status) {
    const default_bg_color = "#333";
    const clickable_bg_color = "#0f0";

    switch(status) {
      case "not_started":
        console.log("Race not started yet");
        jsDisableElement("btn-pause");
        jsEnableElement("btn-go");
        // Change text
        document.getElementById("btn-go-caption").innerHTML = " Start"
        document.getElementById("btn-pause-caption").innerHTML = ""
        break;
      case "started":
        console.log("Race running");
        jsDisableElement("btn-go");
        jsEnableElement("btn-pause");
        // Change text
        document.getElementById("btn-go-caption").innerHTML = ""
        document.getElementById("btn-pause-caption").innerHTML = " Pause"
        break;
      case "paused":
        console.log("Race paused");
        jsDisableElement("btn-pause");
        jsEnableElement("btn-go");
        // Change text
        document.getElementById("btn-go-caption").innerHTML = " Resume"
        document.getElementById("btn-pause-caption").innerHTML = ""
        break;
      case "finished":
        console.log("Race finished");
        jsDisableElement("btn-pause");
        jsDisableElement("btn-go");
        break;
      default:
        console.log(`Unknown status: ${status}`);
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
  static updatePositionView(currState) {
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

// Love u stackoverflow
function jsEnableElement(id) {
  if (document.getElementById(id)) {
    document.getElementById(id).removeAttribute("btn-disabled");
    document.getElementById(id).className = "btn btn-enabled";
  }
}

function jsDisableElement(id) {
  if (document.getElementById(id)) {
    document.getElementById(id).removeAttribute("btn-enabled");
    document.getElementById(id).className = "btn btn-disabled";
  }
}
