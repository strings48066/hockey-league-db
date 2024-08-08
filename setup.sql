CREATE TABLE Seasons (
    SeasonID SERIAL PRIMARY KEY,
    Year INT NOT NULL
);

CREATE TABLE Teams (
    TeamID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    City VARCHAR(100),
    Coach VARCHAR(100)
);

CREATE TABLE TeamSeasons (
    TeamSeasonID SERIAL PRIMARY KEY,
    TeamID INT NOT NULL,
    SeasonID INT NOT NULL,
    FOREIGN KEY (TeamID) REFERENCES Teams(TeamID),
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID)
);

CREATE TABLE Players (
    PlayerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Position VARCHAR(50),
    JerseyNumber INT,
    Email VARCHAR(100) UNIQUE
);

CREATE TABLE PlayerTeamSeasons (
    PlayerTeamSeasonID SERIAL PRIMARY KEY,
    PlayerID INT NOT NULL,
    TeamID INT NOT NULL,
    SeasonID INT NOT NULL,
    IsCurrent BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (TeamID) REFERENCES Teams(TeamID),
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID),
    CONSTRAINT unique_player_team_season UNIQUE (PlayerID, TeamID, SeasonID)
);

CREATE TABLE PlayerTransfers (
    TransferID SERIAL PRIMARY KEY,
    PlayerID INT NOT NULL,
    FromTeamID INT,
    ToTeamID INT NOT NULL,
    TransferDate DATE NOT NULL,
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (FromTeamID) REFERENCES Teams(TeamID),
    FOREIGN KEY (ToTeamID) REFERENCES Teams(TeamID)
);

CREATE TABLE Games (
    GameID SERIAL PRIMARY KEY,
    SeasonID INT NOT NULL,
    Date DATE NOT NULL,
    Time VARCHAR(100) NOT NULL,
    ref1 VARCHAR(100) NOT NULL,
    ref2 VARCHAR(100) NOT NULL,
    gamelink VARCHAR(100) NOT NULL,
    HomeTeamID INT NOT NULL,
    AwayTeamID INT NOT NULL,
    HomeScore INT,
    AwayScore INT,
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID),
    FOREIGN KEY (HomeTeamID) REFERENCES Teams(TeamID),
    FOREIGN KEY (AwayTeamID) REFERENCES Teams(TeamID)
);

CREATE TABLE Standings (
    StandingID SERIAL PRIMARY KEY,
    SeasonID INT NOT NULL,
    TeamID INT NOT NULL,
    Wins INT DEFAULT 0,
    Losses INT DEFAULT 0,
    Ties INT DEFAULT 0,
    Points INT DEFAULT 0,
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID),
    FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
);

CREATE TABLE PlayerStatistics (
    StatisticID SERIAL PRIMARY KEY,
    SeasonID INT NOT NULL,
    PlayerID INT NOT NULL,
    TeamID INT NOT NULL,
    GamesPlayed INT DEFAULT 0,
    Goals INT DEFAULT 0,
    Assists INT DEFAULT 0,
    Points INT GENERATED ALWAYS AS (Goals + Assists) STORED,
    PenaltyMinutes INT DEFAULT 0,
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID),
    FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
    FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
);

CREATE TABLE TeamRecords (
    RecordID SERIAL PRIMARY KEY,
    TeamID INT NOT NULL,
    SeasonID INT NOT NULL,
    RecordType VARCHAR(100),
    RecordValue VARCHAR(100),
    FOREIGN KEY (TeamID) REFERENCES Teams(TeamID),
    FOREIGN KEY (SeasonID) REFERENCES Seasons(SeasonID)
);

