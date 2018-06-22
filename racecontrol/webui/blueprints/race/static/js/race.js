/**
 *  Main interface to the racecontrol backend
 */
class WSUpdate {

  /**
   * Connects to a websocket
   **/
  constructor({host, port, path}) {
    this.conn = new WebSocket(`ws://${host}:${port}/${path}`);
    this.conn.onmessage = this.handle;
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
                      <td id="player-${driverId}-best-lap">${currState[driverId].best_time}s</td>
                      <td id="player-${driverId}-lap-time-last">${currState[driverId].lap_time}s</td>
                  </tr>`;
      tableInnerHTML += row;
    }
    tableInnerHTML += "</tr>"

    // Set new table
    document.getElementById("stateTable").innerHTML = tableInnerHTML;
  }

}
