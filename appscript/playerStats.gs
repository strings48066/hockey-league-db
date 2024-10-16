function updatePlayerStats() {
  try {
    // ============================
    // 1. Configuration
    // ============================

    // Sheet names
    const playersSheetName = 'players';
    const gameEventsSheetName = 'gameEvents';
    const gamesPlayedSheetName = 'gamesPlayed';

    // Column indices (0-based)
    const PLAYER_ID_COL = 0;          // Column A
    const FIRST_NAME_COL = 1;         // Column B
    const LAST_NAME_COL = 2;          // Column C
    const GP_COL = 6;                 // Column G (Games Played)
    const GOALS_COL = 7;              // Column H
    const ASSISTS_COL = 8;            // Column I
    const PTS_COL = 9;                // Column J
    const PIM_COL = 10;               // Column K
    const GWG_PLAYERS_COL = 11;       // Column L (GWG in players sheet)
    const GS_COL = 12;                // Column M (GS - Games as Sub)

    // Game Events Sheet Columns
    const SCORED_BY_COL = 4;          // Column E
    const ASST1_COL = 5;              // Column F
    const ASST2_COL = 6;              // Column G
    const PENALTY_PLAYER_COL = 7;     // Column H
    const PIM_GAME_EVENTS_COL = 9;    // Column J
    const GWG_GAME_EVENTS_COL = 10;   // Column K (GWG in gameEvents sheet)

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

    // Access the players sheet
    const playersSheet = ss.getSheetByName(playersSheetName);
    if (!playersSheet) {
      SpreadsheetApp.getUi().alert(`Sheet "${playersSheetName}" not found.`);
      return;
    }

    // Access the gameEvents sheet
    const gameEventsSheet = ss.getSheetByName(gameEventsSheetName);
    if (!gameEventsSheet) {
      SpreadsheetApp.getUi().alert(`Sheet "${gameEventsSheetName}" not found.`);
      return;
    }

    // Access the gamesPlayed sheet
    const gamesPlayedSheet = ss.getSheetByName(gamesPlayedSheetName);
    if (!gamesPlayedSheet) {
      SpreadsheetApp.getUi().alert(`Sheet "${gamesPlayedSheetName}" not found.`);
      return;
    }

    // Retrieve all data from players, gameEvents, and gamesPlayed sheets
    const playersData = playersSheet.getDataRange().getValues();
    const gameEventsData = gameEventsSheet.getDataRange().getValues();
    const gamesPlayedData = gamesPlayedSheet.getDataRange().getValues();

    // ============================
    // 3. Initialize Player Stats Map
    // ============================

    // Create a map using full name for unique identification
    const playerStatsMap = {};

    for (let i = 1; i < playersData.length; i++) { // Start from 1 to skip header
      const firstName = playersData[i][FIRST_NAME_COL] ? playersData[i][FIRST_NAME_COL].toString().trim().toLowerCase() : '';
      const lastName = playersData[i][LAST_NAME_COL] ? playersData[i][LAST_NAME_COL].toString().trim().toLowerCase() : '';

      if (firstName && lastName) {
        const fullName = `${firstName} ${lastName}`;
        playerStatsMap[fullName] = { goals: 0, assists: 0, pim: 0, gwg: 0, gs: 0 };
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

      if (playerName && playerStatsMap.hasOwnProperty(playerName)) {
        if (isSub === 1) {
          playerStatsMap[playerName].gs += 1;
        }
      } else if (playerName) {
        Logger.log(`Player "${playerName}" from gamesPlayed sheet not found in players list.`);
      }
    }

    // ============================
    // 5. Process Game Events
    // ============================

    for (let i = 1; i < gameEventsData.length; i++) { // Start from 1 to skip header
      const scoredBy = gameEventsData[i][SCORED_BY_COL] ? gameEventsData[i][SCORED_BY_COL].toString().trim().toLowerCase() : '';
      const asst1 = gameEventsData[i][ASST1_COL] ? gameEventsData[i][ASST1_COL].toString().trim().toLowerCase() : '';
      const asst2 = gameEventsData[i][ASST2_COL] ? gameEventsData[i][ASST2_COL].toString().trim().toLowerCase() : '';
      const penaltyPlayer = gameEventsData[i][PENALTY_PLAYER_COL] ? gameEventsData[i][PENALTY_PLAYER_COL].toString().trim().toLowerCase() : '';
      const pim = gameEventsData[i][PIM_GAME_EVENTS_COL] ? Number(gameEventsData[i][PIM_GAME_EVENTS_COL]) : 0;
      const validPim = isNaN(pim) ? 0 : pim;
      const gwgValue = gameEventsData[i][GWG_GAME_EVENTS_COL];

      // GWG detection logic
      const isGWG = gwgValue && (
        gwgValue.toString().trim().toLowerCase() === 'yes' ||
        gwgValue.toString().trim() === '1' ||
        gwgValue === 1
      );

      // Count Goals
      if (scoredBy && playerStatsMap.hasOwnProperty(scoredBy)) {
        playerStatsMap[scoredBy].goals++;

        // Count GWG if applicable
        if (isGWG) {
          playerStatsMap[scoredBy].gwg++;
        }
      } else if (scoredBy) {
        Logger.log(`Scored By player "${scoredBy}" not found in players list.`);
      }

      // Count Assists from Asst1
      if (asst1 && playerStatsMap.hasOwnProperty(asst1)) {
        playerStatsMap[asst1].assists++;
      } else if (asst1) {
        Logger.log(`Assist1 player "${asst1}" not found in players list.`);
      }

      // Count Assists from Asst2
      if (asst2 && playerStatsMap.hasOwnProperty(asst2)) {
        playerStatsMap[asst2].assists++;
      } else if (asst2) {
        Logger.log(`Assist2 player "${asst2}" not found in players list.`);
      }

      // Count Penalty Minutes
      if (penaltyPlayer && playerStatsMap.hasOwnProperty(penaltyPlayer)) {
        playerStatsMap[penaltyPlayer].pim += validPim;
      } else if (penaltyPlayer) {
        Logger.log(`Penalty player "${penaltyPlayer}" not found in players list.`);
      }
    }

    // ============================
    // 6. Prepare Data for Batch Update
    // ============================

    // Arrays to hold updated stats
    const goalCounts = [];
    const assistCounts = [];
    const pimCounts = [];
    const ptsCounts = [];
    const gwgCounts = [];
    const gsCounts = []; // For Games as Sub

    for (let i = 1; i < playersData.length; i++) { // Start from 1 to skip header
      const firstName = playersData[i][FIRST_NAME_COL] ? playersData[i][FIRST_NAME_COL].toString().trim().toLowerCase() : '';
      const lastName = playersData[i][LAST_NAME_COL] ? playersData[i][LAST_NAME_COL].toString().trim().toLowerCase() : '';

      if (firstName && lastName) {
        const fullName = `${firstName} ${lastName}`;
        const stats = playerStatsMap[fullName];

        if (stats) {
          goalCounts.push([stats.goals]);
          assistCounts.push([stats.assists]);
          pimCounts.push([stats.pim]);
          ptsCounts.push([stats.goals + stats.assists]);
          gwgCounts.push([stats.gwg]);
          gsCounts.push([stats.gs]);

          Logger.log(`Setting stats for ${fullName}: Goals=${stats.goals}, Assists=${stats.assists}, PIM=${stats.pim}, PTS=${stats.goals + stats.assists}, GWG=${stats.gwg}, GS=${stats.gs}`);
        } else {
          // Player not found; set stats to 0
          goalCounts.push([0]);
          assistCounts.push([0]);
          pimCounts.push([0]);
          ptsCounts.push([0]);
          gwgCounts.push([0]);
          gsCounts.push([0]);

          Logger.log(`No stats found for ${fullName}. Setting all stats to 0.`);
        }
      } else {
        // If first or last name is missing, set stats to 0
        goalCounts.push([0]);
        assistCounts.push([0]);
        pimCounts.push([0]);
        ptsCounts.push([0]);
        gwgCounts.push([0]);
        gsCounts.push([0]);

        Logger.log(`Player with missing first or last name at row ${i + 1}. Setting stats to 0.`);
      }
    }

    // ============================
    // 7. Batch Update the Players Sheet
    // ============================

    const startRow = 2; // Assuming headers are in row 1

    // Update Goals (Column H)
    const goalsRange = playersSheet.getRange(startRow, GOALS_COL + 1, goalCounts.length, 1);
    goalsRange.setValues(goalCounts);

    // Update Assists (Column I)
    const assistsRange = playersSheet.getRange(startRow, ASSISTS_COL + 1, assistCounts.length, 1);
    assistsRange.setValues(assistCounts);

    // Update Points (Column J)
    const pointsRange = playersSheet.getRange(startRow, PTS_COL + 1, ptsCounts.length, 1);
    pointsRange.setValues(ptsCounts);

    // Update PIM (Column K)
    const pimRange = playersSheet.getRange(startRow, PIM_COL + 1, pimCounts.length, 1);
    pimRange.setValues(pimCounts);

    // Update GWG (Column L)
    const gwgRange = playersSheet.getRange(startRow, GWG_PLAYERS_COL + 1, gwgCounts.length, 1);
    gwgRange.setValues(gwgCounts);

    // Update Games as Sub (Column M)
    const gsRange = playersSheet.getRange(startRow, GS_COL + 1, gsCounts.length, 1);
    gsRange.setValues(gsCounts);

    // ============================
    // 8. Completion Notification
    // ============================

    SpreadsheetApp.getUi().alert('Player stats have been updated successfully, including Games as Sub and other stats!');

  } catch (error) {
    SpreadsheetApp.getUi().alert(`An error occurred: ${error.message}`);
    Logger.log(`Error: ${error}`);
  }
}