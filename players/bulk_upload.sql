-- Insert data from Players_staging into Players table with conflict handling
INSERT INTO Players (FirstName, LastName, Position, JerseyNumber, Email)
SELECT FirstName, LastName, Position, JerseyNumber, Email
FROM players
ON CONFLICT (Email) DO UPDATE
SET firstname = EXCLUDED.FirstName,
    lastname = EXCLUDED.LastName,
    position = EXCLUDED.Position,
    jerseynumber = EXCLUDED.JerseyNumber;

-- Optionally, verify the data
SELECT * FROM players;