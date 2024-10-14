function updatePlayerStats() {
  try {
    // ============================
    // 1. Configuration
    // ============================

    // Sheet names
    const playersSheetName = 'players';
    const gameEventsSheetName = 'gameEvents';

    // Column indices (0-based)
    const PLAYER_ID_COL = 0;          // Column A
    const FIRST_NAME_COL = 1;         // Column B
    const LAST_NAME_COL = 2;          // Column C
    const GOALS_COL = 7;              // Column H
    const ASSISTS_COL = 8;            // Column I
    const PTS_COL = 9;                // Column J
    const PIM_COL = 10;               // Column K
    const GWG_PLAYERS_COL = 11;       // Column L (GWG in players sheet)

    // Game Events Sheet Columns
    const SCORED_BY_COL = 4;          // Column E
    const ASST1_COL = 5;              // Column F
    const ASST2_COL = 6;              // Column G
    const PENALTY_PLAYER_COL = 7;     // Column H
    const INFRACTION_COL = 8;         // Column I
    const PIM_GAME_EVENTS_COL = 9;    // Column J
    const GWG_GAME_EVENTS_COL = 10;    // Column J (GWG in gameEvents sheet)

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

    // Retrieve all data from players and gameEvents sheets
    const playersData = playersSheet.getDataRange().getValues();
    const gameEventsData = gameEventsSheet.getDataRange().getValues();

    // ============================
    // 3. Initialize Player Stats Map
    // ============================

    // Create a map using PLAYER_ID for unique identification
    const playerStatsMap = {};

    for (let i = 1; i < playersData.length; i++) { // Start from 1 to skip header
      const playerID = playersData[i][PLAYER_ID_COL] ? playersData[i][PLAYER_ID_COL].toString().trim() : '';
      const firstName = playersData[i][FIRST_NAME_COL] ? playersData[i][FIRST_NAME_COL].toString().trim().toLowerCase() : '';
      const lastName = playersData[i][LAST_NAME_COL] ? playersData[i][LAST_NAME_COL].toString().trim().toLowerCase() : '';

      if (playerID && firstName && lastName) {
        const fullName = `${firstName} ${lastName}`;
        playerStatsMap[fullName] = { goals: 0, assists: 0, pim: 0, gwg: 0 };
      } else {
        Logger.log(`Missing data for player at row ${i + 1}. PLAYER_ID: "${playerID}", First Name: "${firstName}", Last Name: "${lastName}"`);
      }
    }

    // ============================
    // 4. Process Game Events
    // ============================

    for (let i = 1; i < gameEventsData.length; i++) { // Start from 1 to skip header
      const scoredBy = gameEventsData[i][SCORED_BY_COL] ? gameEventsData[i][SCORED_BY_COL].toString().trim().toLowerCase() : '';
      const asst1 = gameEventsData[i][ASST1_COL] ? gameEventsData[i][ASST1_COL].toString().trim().toLowerCase() : '';
      const asst2 = gameEventsData[i][ASST2_COL] ? gameEventsData[i][ASST2_COL].toString().trim().toLowerCase() : '';
      const penaltyPlayer = gameEventsData[i][PENALTY_PLAYER_COL] ? gameEventsData[i][PENALTY_PLAYER_COL].toString().trim().toLowerCase() : '';
      const pim = gameEventsData[i][PIM_GAME_EVENTS_COL] ? Number(gameEventsData[i][PIM_GAME_EVENTS_COL]) : 0;
      const validPim = isNaN(pim) ? 0 : pim;
      const gwgValue = gameEventsData[i][GWG_GAME_EVENTS_COL] ? Number(gameEventsData[i][GWG_GAME_EVENTS_COL]) : 0;
      const isGWG = gwgValue === 1;

      // Count Goals
      if (scoredBy && playerStatsMap.hasOwnProperty(scoredBy)) {
        playerStatsMap[scoredBy].goals++;
        Logger.log(`Incremented goals for ${scoredBy}: ${playerStatsMap[scoredBy].goals}`);

        // Count GWG if applicable
        if (isGWG) {
          playerStatsMap[scoredBy].gwg++;
          Logger.log(`Incremented GWG for ${scoredBy}: ${playerStatsMap[scoredBy].gwg}`);
        }
      } else if (scoredBy) {
        Logger.log(`Scored By player "${scoredBy}" not found in players list.`);
      }

      // Count Assists from Asst1
      if (asst1 && playerStatsMap.hasOwnProperty(asst1)) {
        playerStatsMap[asst1].assists++;
        Logger.log(`Incremented assists for ${asst1}: ${playerStatsMap[asst1].assists}`);
      } else if (asst1) {
        Logger.log(`Assist1 player "${asst1}" not found in players list.`);
      }

      // Count Assists from Asst2
      if (asst2 && playerStatsMap.hasOwnProperty(asst2)) {
        playerStatsMap[asst2].assists++;
        Logger.log(`Incremented assists for ${asst2}: ${playerStatsMap[asst2].assists}`);
      } else if (asst2) {
        Logger.log(`Assist2 player "${asst2}" not found in players list.`);
      }

      // Count Penalty Minutes
      if (penaltyPlayer && playerStatsMap.hasOwnProperty(penaltyPlayer)) {
        playerStatsMap[penaltyPlayer].pim += validPim;
        Logger.log(`Added ${validPim} PIM to ${penaltyPlayer}: Total PIM = ${playerStatsMap[penaltyPlayer].pim}`);
      } else if (penaltyPlayer) {
        Logger.log(`Penalty player "${penaltyPlayer}" not found in players list.`);
      }
    }

    // ============================
    // 5. Prepare Data for Batch Update
    // ============================

    // Arrays to hold updated stats
    const goalCounts = [];
    const assistCounts = [];
    const pimCounts = [];
    const ptsCounts = [];
    const gwgCounts = [];

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
          Logger.log(`Setting goals for ${fullName} to ${stats.goals}`);
          Logger.log(`Setting assists for ${fullName} to ${stats.assists}`);
          Logger.log(`Setting PIM for ${fullName} to ${stats.pim}`);
          Logger.log(`Setting PTS for ${fullName} to ${stats.goals + stats.assists}`);
          Logger.log(`Setting GWG for ${fullName} to ${stats.gwg}`);
        } else {
          // Player not found in gameEvents; set stats to 0
          goalCounts.push([0]);
          assistCounts.push([0]);
          pimCounts.push([0]);
          ptsCounts.push([0]);
          gwgCounts.push([0]);
          Logger.log(`No stats found for ${fullName}. Setting all stats to 0.`);
        }
      } else {
        // If first or last name is missing, set stats to 0
        goalCounts.push([0]);
        assistCounts.push([0]);
        pimCounts.push([0]);
        ptsCounts.push([0]);
        gwgCounts.push([0]);
        Logger.log(`Player with missing first or last name at row ${i + 1}. Setting stats to 0.`);
      }
    }

    // ============================
    // 6. Batch Update the Players Sheet
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

    // ============================
    // 7. Completion Notification
    // ============================

    SpreadsheetApp.getUi().alert('Player stats have been updated successfully, including Game-Winning Goals!');

  } catch (error) {
    SpreadsheetApp.getUi().alert(`An error occurred: ${error.message}`);
    Logger.log(`Error: ${error}`);
  }
}