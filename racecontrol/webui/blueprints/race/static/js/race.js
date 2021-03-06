/**
 *  Main interface to the racecontrol backend
 */
class WSUpdate {

  /**
   * Connects to the backend
   **/
  constructor(args) {
    this.args = args;
    setTimeout(() => this.connect(this.args), 3000);
  }

  /**
   * Connects to the websocket
   */
  connect({host, port, streamPath, inputPath}) {
    this.stream = new WebSocket(`ws://${host}:${port}/${streamPath}`);
    this.input = new WebSocket(`ws://${host}:${port}/${inputPath}`);
    this.stream.onmessage = this.handle;

    /*
    this.stream.onerror = () => {
      WSUpdate.setWSFailed();
      setTimeout(() => this.connect(this.args), 3000);
    };
    */

    this.stream.onclose = () => {
      WSUpdate.setWSFailed();
      this.stream.close()
      this.input.close()
      setTimeout(() => this.connect(this.args), 3000);
    };
  }

  /**
   * Sets the ws status to failed
   */
  static setWSFailed() {
    document.getElementById("ws-status").className = "ws-status-failed";
    document.getElementById("ws-status").innerHTML = "<i class=\"fas fa-sync fa-spin\"></i>";
  }

  /**
   * Sets the ws status to OK
   */
  static setWSOK() {
    document.getElementById("ws-status").className = "ws-status-ok";
    document.getElementById("ws-status").innerHTML = "<i class=\"fas fa-plug\"></i>";
  }

  /**
   * Handles incoming messages
   */
  handle(e) {
    // WS is likely ok if we receive data!
    WSUpdate.setWSOK();
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
        jsDisableElement("btn-reset");
        jsEnableElement("btn-go");
        // Change text
        document.getElementById("btn-go-caption").innerHTML = " Start"
        document.getElementById("btn-pause-caption").innerHTML = ""
        document.getElementById("btn-reset-caption").innerHTML = ""
        break;
      case "started":
        console.log("Race running");
        jsDisableElement("btn-go");
        jsDisableElement("btn-reset");
        jsEnableElement("btn-pause");
        // Change text
        document.getElementById("btn-go-caption").innerHTML = ""
        document.getElementById("btn-pause-caption").innerHTML = " Pause"
        document.getElementById("btn-reset-caption").innerHTML = ""
        break;
      case "paused":
        console.log("Race paused");
        jsDisableElement("btn-pause");
        jsEnableElement("btn-reset");
        jsEnableElement("btn-go");
        // Change text
        document.getElementById("btn-reset-caption").innerHTML = " Reset"
        document.getElementById("btn-go-caption").innerHTML = " Resume"
        document.getElementById("btn-pause-caption").innerHTML = ""
        break;
      case "finished":
        console.log("Race finished");
        jsDisableElement("btn-pause");
        jsDisableElement("btn-reset");
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
    for(let i = 0; i < currState["positions"].length; i++) {
      const driverId = currState["positions"][i][0]; // @TODO, for now ignore the lap count and get it from the state dict
      const shortname = document.getElementById(`player-${driverId}-shortname`).innerHTML;
      // Build row
      let row = `<tr class="player-entry" id="player-${driverId}">
                      <td id="player-${driverId}-position">#${i + 1}</td>
                      <td>${shortname}</td>
                      <td id="player-${driverId}-lap-count">${currState[driverId].lap_count}</td>
                      <td id="player-${driverId}-best-lap">${cvtTime(currState[driverId].best_time)}</td>
                      <td id="player-${driverId}-lap-time-last">${cvtTime(currState[driverId].lap_time)}</td>
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
    this.input.send(JSON.stringify({"request": "finish"}));
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
    document.getElementById(id).className = "btn btn-enabled";
  }
}

function jsDisableElement(id) {
  if (document.getElementById(id)) {
    document.getElementById(id).className = "btn btn-disabled";
  }
}

function cvtTime(time) {
  const formatNumber = (number) => ("0" + parseInt(number)).slice(-2);

  if(time !== -1) {
    return `${formatNumber(time / 60000)}:${formatNumber((time / 1000) % 60)}:${formatNumber((time % 1000) / 10)}`
  } else  {
    return "NaN";
  }
} 
