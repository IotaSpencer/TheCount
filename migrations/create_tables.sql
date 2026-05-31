-- Create tables expected by the bot. Adjust types if your DB is not MySQL.

CREATE TABLE IF NOT EXISTS channels (
  channelID VARCHAR(64) PRIMARY KEY,
  serverID VARCHAR(64),
  current_count DOUBLE DEFAULT 0,
  last_userID VARCHAR(64) DEFAULT '0',
  times_counted INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS highscores (
  channelID VARCHAR(64) PRIMARY KEY,
  serverID VARCHAR(64),
  score INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS settings (
  channelID VARCHAR(64) PRIMARY KEY,
  Step DOUBLE DEFAULT 1,
  StartingNumber DOUBLE DEFAULT 0,
  EnableWolframAlpha TINYINT(1) DEFAULT 0,
  EnableBinary TINYINT(1) DEFAULT 1,
  EnableExpressions TINYINT(1) DEFAULT 1,
  RoundAllGuesses TINYINT(1) DEFAULT 0,
  AllowSingleUserCount TINYINT(1) DEFAULT 0,
  ForceIntegerConversions TINYINT(1) DEFAULT 1
);

CREATE TABLE IF NOT EXISTS streakrankability (
  channelID VARCHAR(64) PRIMARY KEY,
  rankable TINYINT(1) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS leaderboards (
  channelID VARCHAR(64) PRIMARY KEY,
  name VARCHAR(255),
  guildname VARCHAR(255),
  score INT DEFAULT 0
);
