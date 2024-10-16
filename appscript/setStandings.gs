function updateStandingsWithStreaks() {
	// Get the active spreadsheet
	var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  
	// Get the "standings" sheet
	var standingsSheet = spreadsheet.getSheetByName("standings");
	if (!standingsSheet) {
	  Logger.log('Sheet "standings" not found.');
	  return;
	}
  
	// Get the "games" sheet
	var gamesSheet = spreadsheet.getSheetByName("games");
	if (!gamesSheet) {
	  Logger.log('Sheet "games" not found.');
	  return;
	}
  
	// Define the columns (adjust if needed)
	var teamNameColumn = 2; // Column B in "standings" sheet
	var winsColumn = 3;     // Column C in "standings" sheet
	var lossesColumn = 4;   // Column D in "standings" sheet
	var tiesColumn = 5;     // Column E in "standings" sheet
	var pointsColumn = 6;   // Column F in "standings" sheet
	var goalsForColumn = 7;     // Column G in "standings" sheet
	var goalsAgainstColumn = 8; // Column H in "standings" sheet
	var pimColumn = 9;          // Column I in "standings" sheet
	var homeRecordColumn = 10;  // Column J in "standings" sheet
	var awayRecordColumn = 11;  // Column K in "standings" sheet
	var streakColumn = 12;      // Column L in "standings" sheet
  
	var dateColumn = 3;        // Column C in "games" sheet (Date)
	var homeTeamColumn = 7;    // Column G in "games" sheet
	var awayTeamColumn = 8;    // Column H in "games" sheet
	var homeScoreColumn = 9;   // Column I in "games" sheet
	var awayScoreColumn = 10;  // Column J in "games" sheet
	var homePIMColumn = 13;    // Column M in "games" sheet
	var awayPIMColumn = 14;    // Column N in "games" sheet
	var winColumn = 18;        // Column R in "games" sheet
	var lossColumn = 19;       // Column S in "games" sheet
	var tieHomeColumn = 20;    // Column T in "games" sheet
	var tieAwayColumn = 21;    // Column U in "games" sheet
  
	// Points per outcome
	var pointsPerWin = 2;
	var pointsPerTie = 1;
	var pointsPerLoss = 0;
  
	// Get team names from the standings sheet
	var standingsLastRow = standingsSheet.getLastRow();
	var teamNames = [];
	if (standingsLastRow >= 2) {
	  var teamRange = standingsSheet.getRange(2, teamNameColumn, standingsLastRow - 1, 1);
	  teamNames = teamRange.getValues().flat().filter(String);
	} else {
	  Logger.log('No team data found in standings sheet.');
	}
  
	// Initialize counts and streaks for each team
	var winCounts = {};
	var lossCounts = {};
	var tieCounts = {};
	var pointCounts = {};
	var goalsForCounts = {};
	var goalsAgainstCounts = {};
	var pimCounts = {};
	var homeWinCounts = {};
	var homeLossCounts = {};
	var homeTieCounts = {};
	var awayWinCounts = {};
	var awayLossCounts = {};
	var awayTieCounts = {};
	var streaks = {}; // For storing current streaks
	teamNames.forEach(function(team) {
	  var teamKey = team.trim().toLowerCase();
	  winCounts[teamKey] = 0;
	  lossCounts[teamKey] = 0;
	  tieCounts[teamKey] = 0;
	  pointCounts[teamKey] = 0;
	  goalsForCounts[teamKey] = 0;
	  goalsAgainstCounts[teamKey] = 0;
	  pimCounts[teamKey] = 0;
	  homeWinCounts[teamKey] = 0;
	  homeLossCounts[teamKey] = 0;
	  homeTieCounts[teamKey] = 0;
	  awayWinCounts[teamKey] = 0;
	  awayLossCounts[teamKey] = 0;
	  awayTieCounts[teamKey] = 0;
	  streaks[teamKey] = { type: null, count: 0 };
	});
  
	// Get game results from the games sheet
	var gamesLastRow = gamesSheet.getLastRow();
	if (gamesLastRow >= 2) {
	  var numRows = gamesLastRow - 1; // Exclude header row
	  var gamesRange = gamesSheet.getRange(2, dateColumn, numRows, tieAwayColumn - dateColumn + 1);
	  var gamesData = gamesRange.getValues();
  
	  // Sort games by date (assuming dates are in Column C)
	  gamesData.sort(function(a, b) {
		var dateA = new Date(a[0]);
		var dateB = new Date(b[0]);
		return dateA - dateB;
	  });
  
	  // Process each game
	  gamesData.forEach(function(row, index) {
		var date = row[0]; // Date column
		var homeTeam = row[homeTeamColumn - dateColumn] ? row[homeTeamColumn - dateColumn].trim().toLowerCase() : '';
		var awayTeam = row[awayTeamColumn - dateColumn] ? row[awayTeamColumn - dateColumn].trim().toLowerCase() : '';
		var homeScore = parseFloat(row[homeScoreColumn - dateColumn]);
		var awayScore = parseFloat(row[awayScoreColumn - dateColumn]);
		var homePIM = parseFloat(row[homePIMColumn - dateColumn]) || 0;
		var awayPIM = parseFloat(row[awayPIMColumn - dateColumn]) || 0;
		var winTeam = row[winColumn - dateColumn] ? row[winColumn - dateColumn].trim().toLowerCase() : '';
		var lossTeam = row[lossColumn - dateColumn] ? row[lossColumn - dateColumn].trim().toLowerCase() : '';
		var tieHome = row[tieHomeColumn - dateColumn];
		var tieAway = row[tieAwayColumn - dateColumn];
  
		// Validate team names and scores
		if (homeTeam && awayTeam && !isNaN(homeScore) && !isNaN(awayScore)) {
		  // Update goals for and against
		  if (goalsForCounts.hasOwnProperty(homeTeam)) {
			goalsForCounts[homeTeam] += homeScore;
			goalsAgainstCounts[homeTeam] += awayScore;
			pimCounts[homeTeam] += homePIM;
		  }
		  if (goalsForCounts.hasOwnProperty(awayTeam)) {
			goalsForCounts[awayTeam] += awayScore;
			goalsAgainstCounts[awayTeam] += homeScore;
			pimCounts[awayTeam] += awayPIM;
		  }
  
		  // Process win
		  if (winTeam) {
			var winTeamKey = winTeam;
			if (winCounts.hasOwnProperty(winTeamKey)) {
			  winCounts[winTeamKey] += 1;
			  pointCounts[winTeamKey] += pointsPerWin;
			}
  
			// Update streak
			updateStreak(streaks, winTeamKey, 'W-');
  
			// Determine if the win was at home or away
			if (winTeamKey === homeTeam) {
			  homeWinCounts[homeTeam] += 1;
			} else if (winTeamKey === awayTeam) {
			  awayWinCounts[awayTeam] += 1;
			}
		  }
  
		  // Process loss
		  if (lossTeam) {
			var lossTeamKey = lossTeam;
			if (lossCounts.hasOwnProperty(lossTeamKey)) {
			  lossCounts[lossTeamKey] += 1;
			  pointCounts[lossTeamKey] += pointsPerLoss;
			}
  
			// Update streak
			updateStreak(streaks, lossTeamKey, 'L-');
  
			// Determine if the loss was at home or away
			if (lossTeamKey === homeTeam) {
			  homeLossCounts[homeTeam] += 1;
			} else if (lossTeamKey === awayTeam) {
			  awayLossCounts[awayTeam] += 1;
			}
		  }
  
		  // Process tie for home team
		  if (tieHome && tieCounts.hasOwnProperty(homeTeam)) {
			if (isTieIndicator(tieHome)) {
			  tieCounts[homeTeam] += 1;
			  pointCounts[homeTeam] += pointsPerTie;
			  homeTieCounts[homeTeam] += 1;
			  updateStreak(streaks, homeTeam, 'T-');
			}
		  }
  
		  // Process tie for away team
		  if (tieAway && tieCounts.hasOwnProperty(awayTeam)) {
			if (isTieIndicator(tieAway)) {
			  tieCounts[awayTeam] += 1;
			  pointCounts[awayTeam] += pointsPerTie;
			  awayTieCounts[awayTeam] += 1;
			  updateStreak(streaks, awayTeam, 'T-');
			}
		  }
		} else {
		  Logger.log('Invalid data in games sheet at row: ' + (index + 2));
		}
	  });
	} else {
	  Logger.log('No game data found in games sheet.');
	}
  
	// Update the standings sheet
	teamNames.forEach(function(team, index) {
	  var teamKey = team.trim().toLowerCase();
	  var wins = winCounts[teamKey] || 0;
	  var losses = lossCounts[teamKey] || 0;
	  var ties = tieCounts[teamKey] || 0;
	  var points = pointCounts[teamKey] || 0;
	  var goalsFor = goalsForCounts[teamKey] || 0;
	  var goalsAgainst = goalsAgainstCounts[teamKey] || 0;
	  var pim = pimCounts[teamKey] || 0;
	  var homeWins = homeWinCounts[teamKey] || 0;
	  var homeLosses = homeLossCounts[teamKey] || 0;
	  var homeTies = homeTieCounts[teamKey] || 0;
	  var awayWins = awayWinCounts[teamKey] || 0;
	  var awayLosses = awayLossCounts[teamKey] || 0;
	  var awayTies = awayTieCounts[teamKey] || 0;
  
	  // Format home and away records
	  var homeRecord = homeWins + '-' + homeLosses + '-' + homeTies;
	  var awayRecord = awayWins + '-' + awayLosses + '-' + awayTies;
  
	  // Get streak
	  var streakData = streaks[teamKey];
	  var streakStr = '';
	  if (streakData.type && streakData.count > 0) {
		streakStr = streakData.type + streakData.count;
	  }
  
	  var rowNumber = index + 2; // Data starts from row 2
	  standingsSheet.getRange(rowNumber, winsColumn).setValue(wins);
	  standingsSheet.getRange(rowNumber, lossesColumn).setValue(losses);
	  standingsSheet.getRange(rowNumber, tiesColumn).setValue(ties);
	  standingsSheet.getRange(rowNumber, pointsColumn).setValue(points);
	  standingsSheet.getRange(rowNumber, goalsForColumn).setValue(goalsFor);
	  standingsSheet.getRange(rowNumber, goalsAgainstColumn).setValue(goalsAgainst);
	  standingsSheet.getRange(rowNumber, pimColumn).setValue(pim);
	  standingsSheet.getRange(rowNumber, homeRecordColumn).setValue(homeRecord);
	  standingsSheet.getRange(rowNumber, awayRecordColumn).setValue(awayRecord);
	  standingsSheet.getRange(rowNumber, streakColumn).setValue(streakStr);
	});
  
	Logger.log('Standings updated successfully with streaks.');
  }
  
  // Helper function to determine if a value indicates a tie
  function isTieIndicator(value) {
	if (typeof value === 'number') {
	  return value === 1;
	} else if (typeof value === 'string') {
	  value = value.trim().toLowerCase();
	  return value === '1' || value === 'yes' || value === 'true';
	}
	return false;
  }
  
  // Helper function to update streaks
  function updateStreak(streaks, teamKey, resultType) {
	var currentStreak = streaks[teamKey];
  
	if (currentStreak.type === resultType) {
	  // Continue the streak
	  currentStreak.count += 1;
	} else {
	  // Reset the streak
	  currentStreak.type = resultType;
	  currentStreak.count = 1;
	}
  }