/**
 * Nametag Admin — Google Apps Script Write Proxy
 *
 * This runs as a free Web App and accepts POST requests from the
 * Flask admin app to write to your public Google Sheets.
 *
 * Deploy once, grab the URL, set it as APPS_SCRIPT_URL in Render.
 *
 * SETUP: See README.md Step 1 for deployment instructions.
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheetId = data.sheetId;
    var action  = data.action;
    var ss = SpreadsheetApp.openById(sheetId);
    var sheet = ss.getSheets()[0]; // first tab

    if (action === "append") {
      sheet.appendRow(data.values);
      return _json({ status: "ok", action: "append" });
    }

    if (action === "update") {
      var row = data.row;
      var values = data.values;
      for (var i = 0; i < values.length; i++) {
        sheet.getRange(row, i + 1).setValue(values[i]);
      }
      return _json({ status: "ok", action: "update", row: row });
    }

    if (action === "delete") {
      sheet.deleteRow(data.row);
      return _json({ status: "ok", action: "delete", row: data.row });
    }

    return _json({ status: "error", message: "Unknown action: " + action });

  } catch (err) {
    return _json({ status: "error", message: err.toString() });
  }
}

// Also handle GET so you can test the URL in a browser
function doGet(e) {
  return _json({ status: "ok", message: "Nametag Admin write proxy is running." });
}

function _json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
