function get_game_events(sourceSpreadsheetUrl) {
  // URLs and sheet names
  var sourceSheetName = 'scoresheet';                     // Your source sheet name
  var destinationSheetName = 'gameEvents';                     // Your destination sheet name
  var infoSheetName = 'gameInfo';                         // Sheet containing game info

  // Open the source spreadsheet and sheets
  var sourceSpreadsheet = SpreadsheetApp.openByUrl(sourceSpreadsheetUrl);
  var sourceSheet = sourceSpreadsheet.getSheetByName(sourceSheetName);
  var infoSheet = sourceSpreadsheet.getSheetByName(infoSheetName);

  // Get the gameid from the GameInfo sheet (assuming it's in cell A2)
  var gameId = infoSheet.getRange('A2').getValue();

  // Validate gameId
  if (!gameId) {
    SpreadsheetApp.getActive().toast('Error: gameid is missing in the gameInfo sheet.');
    return;
  }

  // Get the data range from the source sheet
  var sourceRange = sourceSheet.getRange('A18:J34');
  var sourceData = sourceRange.getValues();

  // Get the destination sheet
  var destinationSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var destinationSheet = destinationSpreadsheet.getSheetByName(destinationSheetName);

  // Get existing IDs from the destination sheet for de-duplication
  var destDataRange = destinationSheet.getDataRange();
  var destDataValues = destDataRange.getValues();
  var destHeaders = destDataValues.shift(); // Remove headers from data

  // Create a set to store existing IDs
  var existingIds = new Set();
  destDataValues.forEach(function(row) {
    var id = row[0]; // Assuming 'id' is in the first column
    existingIds.add(id);
  });

  // Initialize arrays to hold the combined data to append
  var goalEntries = [];
  var penaltyEntries = [];

  // Initialize counters for incremental numbers
  var goalCounter = 1;
  var penaltyCounter = 1;

  // Process each row in the source data
  sourceData.forEach(function(row) {
    // Check if there is goal data (Columns A-E)
    var hasGoalData = row[0] && row[1] && row[2];
    // Check if there is penalty data (Columns F-J)
    var hasPenaltyData = row[5] && row[6] && row[7];

    // Process goal data
    if (hasGoalData) {
      var eventType = 'G';
      var entryId = gameId + '-' + eventType + '-' + goalCounter; // e.g., 'Game123-G-1'

      var goalEntry = [
        entryId,      // id (unique identifier)
        gameId,       // gameid
        row[0],       // eventTime (Time, Column A)
        row[1],       // Team (Column B)
        row[2],       // ScoredBy (Goal, Column C)
        row[3],       // Asst1 (Column D)
        row[4],       // Asst2 (Column E)
        '',           // PenaltyPlayer
        '',           // Infraction
        '',           // PIM
        ''            // GWG flag (to be determined later)
      ];

      // Check if the ID already exists
      if (!existingIds.has(entryId)) {
        goalEntries.push(goalEntry);
        existingIds.add(entryId);
      }
      goalCounter++; // Increment goal counter
    }

    // Process penalty data
    if (hasPenaltyData) {
      var eventType = 'P';
      var entryId = gameId + '-' + eventType + '-' + penaltyCounter; // e.g., 'Game123-P-1'

      var penaltyEntry = [
        entryId,      // id (unique identifier)
        gameId,       // gameid
        row[5],       // eventTime (Time, Column F)
        row[6],       // Team (Column G)
        '',           // ScoredBy
        '',           // Asst1
        '',           // Asst2
        row[7],       // PenaltyPlayer (Player, Column H)
        row[8],       // Infraction (Column I)
        row[9],       // PIM
        ''            // GWG flag (empty for penalties)
      ];

      // Check if the ID already exists
      if (!existingIds.has(entryId)) {
        penaltyEntries.push(penaltyEntry);
        existingIds.add(entryId);
      }
      penaltyCounter++; // Increment penalty counter
    }
  });

  // Determine the Game-Winning Goal (GWG)
  if (goalEntries.length > 0) {
    // Collect unique team names from the goal data
    var teams = [...new Set(goalEntries.map(function(goal) { return goal[3]; }))]; // Team is at index 3

    // Initialize team scores
    var finalScores = {};
    teams.forEach(function(team) {
      finalScores[team] = 0;
    });

    // Determine final scores
    goalEntries.forEach(function(goal) {
      var team = goal[3]; // Team is at index 3
      finalScores[team]++;
    });

    // Identify the winning and losing teams
    var winningTeam = '';
    var losingTeam = '';
    var winningScore = 0;
    var losingScore = 0;

    if (finalScores[teams[0]] > finalScores[teams[1]]) {
      winningTeam = teams[0];
      losingTeam = teams[1];
      winningScore = finalScores[winningTeam];
      losingScore = finalScores[losingTeam];
    } else if (finalScores[teams[0]] < finalScores[teams[1]]) {
      winningTeam = teams[1];
      losingTeam = teams[0];
      winningScore = finalScores[winningTeam];
      losingScore = finalScores[losingTeam];
    } else {
      // The game is a tie; no GWG
      SpreadsheetApp.getActive().toast('The game ended in a tie. No Game-Winning Goal to determine.');
    }

    // If there's a winning team, identify the GWG
    if (winningTeam) {
      // Reset team scores for tracking during the game
      var cumulativeScores = {};
      teams.forEach(function(team) {
        cumulativeScores[team] = 0;
      });

      // Iterate through goals to find the GWG
      for (var i = 0; i < goalEntries.length; i++) {
        var goal = goalEntries[i];
        var team = goal[3]; // Team is at index 3
        cumulativeScores[team]++;

        // Check if this goal puts the winning team ahead of the losing team's final score
        if (team === winningTeam && cumulativeScores[winningTeam] === losingScore + 1) {
          // Mark this goal as the GWG
          goal[10] = 'Yes'; // GWG flag is at index 10
          break; // GWG found
        }
      }
    }
  }

  // Combine goalEntries and penaltyEntries
  var combinedData = goalEntries.concat(penaltyEntries);

  // Append the combined data to the destination sheet
  if (combinedData.length > 0) {
    // Check if headers are present; if not, add them
    var lastRow = destinationSheet.getLastRow();
    if (lastRow === 0) {
      var headers = ['id', 'gameid', 'eventTime', 'Team', 'ScoredBy', 'Asst1', 'Asst2', 'PenaltyPlayer', 'Infraction', 'PIM', 'GWG'];
      destinationSheet.appendRow(headers);
      lastRow = 1;
    }

    // Write the combined data in bulk
    var startRow = lastRow + 1;
    var numRows = combinedData.length;
    var numCols = combinedData[0].length;
    destinationSheet.getRange(startRow, 1, numRows, numCols).setValues(combinedData);

    SpreadsheetApp.getActive().toast('Data appended successfully with the Game-Winning Goal identified!');
  } else {
    SpreadsheetApp.getActive().toast('No new data to append.');
  }
}

function runGames() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var gameLinksSheet = ss.getSheetByName('gamelinks');
  
  if (!gameLinksSheet) {
    SpreadsheetApp.getUi().alert('Sheet "gamelinks" not found.');
    return;
  }
  
  var dataRange = gameLinksSheet.getDataRange();
  var data = dataRange.getValues();
  
  // Assuming the first row contains headers
  for (var i = 1; i < data.length; i++) {
    var id = data[i][0];
    var link = data[i][1];
    
    if (link) {
      get_game_events(link);
    }
  }
  
  SpreadsheetApp.getActive().toast('All game events have been processed.');
}