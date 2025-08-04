function updateGoalieStats() {
	try {
	  // Sheet names
	  const goaliesSheetName = 'goalies';
	  const gamesPlayedSheetName = 'gamesPlayed';
  
	  // Column indices (0-based)
	  const PLAYER_ID_COL = 0;          // Column A
	  const FIRST_NAME_COL = 1;         // Column B
	  const LAST_NAME_COL = 2;          // Column C
	  const GP_COL = 6;                 // Column G (Games Played)
	  const GS_COL = 7;                 // Column H (Games Subbed)
	  const WIN_COL = 8;                // Column I (Wins)
	  const LOSS_COL = 9;               // Column J (Losses)
	  const TIE_COL = 10;               // Column K (Ties)
	  const GA_COL = 11;                // Column L (Goals Against)
	  const GAA_COL = 12;               // Column M (GAA)
  
	  // Games Played Sheet Columns
	  const GP_GAME_ID_COL = 0;         // Column A
	  const GP_TEAM_COL = 1;            // Column B
	  const GP_PLAYER_NAME_COL = 2;     // Column C
	  const GP_POSITION_COL = 3;        // Column D
	  const GP_JERSEY_NUMBER_COL = 4;   // Column E
	  const GP_SUB_COL = 5;             // Column F
  
	  // ============================
	  // 2. Access Sheets and Data
	  // ============================
  
	  // Access the active spreadsheet
	  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
	  // Access the goalies sheet
	  const goaliesSheet = ss.getSheetByName(goaliesSheetName);
	  if (!goaliesSheet) {
		SpreadsheetApp.getUi().alert(`Sheet "${goaliesSheetName}" not found.`);
		return;
	  }
  
	  const goaliesData = goaliesSheet.getDataRange().getValues();
	  const gamesPlayedSheet = ss.getSheetByName(gamesPlayedSheetName);
	  if (!gamesPlayedSheet) {
		SpreadsheetApp.getUi().alert(`Sheet "${gamesPlayedSheetName}" not found.`);
		return;
	  }
	  const gamesPlayedData = gamesPlayedSheet.getDataRange().getValues();
  
	  // ============================
	  // 3. Initialize Player Stats Map
	  // ============================
  
	  // Create a map using full name for unique identification
	  const goalieStatsMap = {};
  
	  for (let i = 1; i < goaliesData.length; i++) { // Start from 1 to skip header
		const firstName = goaliesData[i][FIRST_NAME_COL] ? goaliesData[i][FIRST_NAME_COL].toString().trim().toLowerCase() : '';
		const lastName = goaliesData[i][LAST_NAME_COL] ? goaliesData[i][LAST_NAME_COL].toString().trim().toLowerCase() : '';
  
		if (firstName && lastName) {
		  const fullName = `${firstName} ${lastName}`;
		  goalieStatsMap[fullName] = { gp: 0, gs: 0, w: 0, l: 0, tie: 0, ga: 0, gaa: 0 };
		} else {
		  Logger.log(`Missing data for player at row ${i + 1}. First Name: "${firstName}", Last Name: "${lastName}"`);
		}
	  }
  
	  // ============================
	  // 4. Calculate Games as Sub (GS) from gamesPlayed Sheet
	  // ============================
  
	  // Process gamesPlayedData to count GS (Games as Sub)
	  for (let i = 1; i < gamesPlayedData.length; i++) { // Start from 1 to skip header
		const playerName = gamesPlayedData[i][GP_PLAYER_NAME_COL] ? gamesPlayedData[i][GP_PLAYER_NAME_COL].toString().trim().toLowerCase() : '';
		const subFlag = gamesPlayedData[i][GP_SUB_COL];
  
		// Convert subFlag to number (0 or 1)
		const isSub = subFlag ? Number(subFlag) : 0;
  
		if (playerName && goalieStatsMap.hasOwnProperty(playerName)) {
		  goalieStatsMap[playerName].gp += 1; //increment games played
		  if (isSub === 1) {
			goalieStatsMap[playerName].gs += 1;
		  }
		} else if (playerName) {
		  Logger.log(`Player "${playerName}" from gamesPlayed sheet not found in players list.`);
		}
	  }

    // ============================
    // 6. Prepare Data for Batch Update
    // ============================

    // Arrays to hold updated stats
    const gsCounts = [];
    const gpCounts = [];

	for (let i = 1; i < goaliesData.length; i++) { // Start from 1 to skip header
		const firstName = goaliesData[i][FIRST_NAME_COL] ? goaliesData[i][FIRST_NAME_COL].toString().trim().toLowerCase() : '';
		const lastName = goaliesData[i][LAST_NAME_COL] ? goaliesData[i][LAST_NAME_COL].toString().trim().toLowerCase() : '';
  
		if (firstName && lastName) {
		  const fullName = `${firstName} ${lastName}`;
		  const stats = goalieStatsMap[fullName];
  
		  if (stats) {
			gsCounts.push([stats.gs]);
            gpCounts.push([stats.gp]);

			Logger.log(`Setting stats for ${fullName}`);
		  } else {
			// Player not found; set stats to 0
			gsCounts.push([0]);
			gpCounts.push([0]);
  
			Logger.log(`No stats found for ${fullName}. Setting all stats to 0.`);
		  }
		} else {
		  gsCounts.push([0]);
		  gpCounts.push([0]);
  
		  Logger.log(`Player with missing first or last name at row ${i + 1}. Setting stats to 0.`);
		}
	  }

    // ============================
    // 7. Batch Update the Players Sheet
    // ============================

    const startRow = 2; // Assuming headers are in row 1
    
	// Update Games Played (Column G)
    const gpRange = goaliesSheet.getRange(startRow, GP_COL + 1, gpCounts.length, 1);
    gpRange.setValues(gpCounts);

	// Update Games as Sub (Column H)
    const gsRange = goaliesSheet.getRange(startRow, GS_COL + 1, gsCounts.length, 1);
    gsRange.setValues(gsCounts);



	} catch (error) {
	Logger.log('Error in updateGoalieStats: ' + error);
	}
  }