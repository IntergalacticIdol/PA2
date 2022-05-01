import mysql.connector
import datetime

class databaseConnector:

  cursor = None
  connection = None

  def __init__(self):
    self.connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    port=3306
    )
    self.cursor = self.connection.cursor()

  def alphaFilter(self, input):
    input = str(input)
    output = ''
    for x in range(len(input)):
      for char in input[x]:
        if str(char).isalnum() == True or str(char).isspace() == True:
          output += str(char)
    return output

  def dbInit(self):
      self.cursor.execute("SHOW DATABASES LIKE \'pa2\'")
      result = self.cursor.fetchall()
      if(len(result) == 0):
          # db does not exist
          # it will be created
          # it is also likely the first time the app is being run
          self.createDb()
          self.dummyEntries()


  def createDb(self):
      self.cursor.execute("CREATE DATABASE pa2")
      self.cursor.execute("USE pa2")

      tables = [
        "CREATE TABLE Games(" +
        "name varchar(64) NOT NULL UNIQUE," +
        "release_date date," +
        "developer varchar(32)," +
        "publisher varchar(32)," +
        "PRIMARY KEY (name))",

        "CREATE TABLE Tags(" +
        "name varchar(64) NOT NULL UNIQUE," +
        "PRIMARY KEY (name))",

        "CREATE TABLE Assigned_tags(" +
        "assigned_id int NOT NULL AUTO_INCREMENT," +
        "game_name varchar(64)," +
        "tag_name varchar(64)," +
        "PRIMARY KEY (assigned_id)," +
        "CONSTRAINT FK_assigned_to FOREIGN KEY (game_name)" +
        "REFERENCES Games(name)," +
        "CONSTRAINT FK_instance_of FOREIGN KEY (tag_name)" +
        "REFERENCES Tags(name))",

        "CREATE TABLE Players(" +
        "name varchar(16) NOT NULL UNIQUE," +
        "PRIMARY KEY (name))",

        "CREATE TABLE Game_copies(" +
        "copy_id int NOT NULL AUTO_INCREMENT," +
        "owner varchar(16)," +
        "game_name varchar(64)," +
        "last_played datetime," +
        "PRIMARY KEY (copy_id)," +
        "CONSTRAINT FK_owned_by FOREIGN KEY (owner)" +
        "REFERENCES Players(name)," +
        "CONSTRAINT FK_copy_of FOREIGN KEY (game_name)" +
        "REFERENCES Games(name))"
      ]

      for query in tables:
          self.cursor.execute(query)

      self.connection.commit()

  def addGame(self, name, date, dev, pub):
    self.cursor.execute("USE pa2")
    self.cursor.execute(f"INSERT INTO Games (name, release_date, developer, publisher) VALUES ('{name}', '{date}', '{dev}', '{pub}')")
    self.connection.commit()

  # TODO: INPUT IMAGE IN TOO
  def addPlayer(self, name):
    if name != '':
      self.cursor.execute("USE pa2")
      self.cursor.execute(f"INSERT INTO Players (name) VALUES ('{name}')")
      self.connection.commit()

  def addTag(self, name):
    if name != '':
      self.cursor.execute("USE pa2")
      self.cursor.execute(f"INSERT INTO Tags (name) VALUES ('{name}')")
      self.connection.commit()

  def addGameCopy(self, owner, game):
    if owner != '' and game != '':
      self.cursor.execute("USE pa2")
      self.cursor.execute(f"INSERT INTO Game_copies (owner, game_name) VALUES ('{owner}', '{game}')")
      self.connection.commit()

  def addAssigned(self, game, tag):
    self.cursor.execute("USE pa2")
    self.cursor.execute(f"INSERT INTO Assigned_tags (game_name, tag_name) VALUES ('{game}', '{tag}')")
    self.connection.commit()

  def updateTime(self, game, players):
    today = datetime.date.today()
    now = datetime.datetime.now()
    now = now.strftime("%H:%M:%S")

    for player in players:
      self.cursor.execute("USE pa2")
      self.cursor.execute(f"UPDATE Game_copies SET last_played = '{today} {now}' WHERE game_name = '{game}' AND owner = '{player}'")
      self.connection.commit()

  def getPlayers(self):
    self.cursor.execute("USE pa2")
    self.cursor.execute("SELECT name FROM Players")
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  def getGameTitles(self):
    self.cursor.execute("USE pa2")
    self.cursor.execute(f"SELECT name FROM Games")
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  def getGameTitlesByFilters(self, players, tags):
    query = f"SELECT DISTINCT g.name FROM Games AS g INNER JOIN Game_copies AS gc ON gc.game_name = g.name"
    
    if len(players) > 0 or len(tags) > 0:
       query +=  ' WHERE '

    for x in range(len(players)):
      if x == len(players) - 1:
        query += f"EXISTS (SELECT * FROM Game_copies WHERE Game_copies.owner = '{players[x]}' AND Game_copies.game_name = g.name)"
      else:
        query += f"EXISTS (SELECT * FROM Game_copies WHERE Game_copies.owner = '{players[x]}' AND Game_copies.game_name = g.name) AND "

    if len(players) > 0 and len(tags) > 0:
      query += ' AND '

    for x in range(len(tags)):
      if x == len(tags) - 1:
        query += f"EXISTS (SELECT * FROM Assigned_tags WHERE Assigned_tags.game_name = g.name AND Assigned_tags.tag_name = '{tags[x]}')"
      else:
        query += f"EXISTS (SELECT * FROM Assigned_tags WHERE Assigned_tags.game_name = g.name AND Assigned_tags.tag_name = '{tags[x]}') AND "

    self.cursor.execute("USE pa2")
    self.cursor.execute(query)
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  def getTags(self):
    self.cursor.execute("USE pa2")
    self.cursor.execute(f"SELECT name FROM Tags")
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  # Returns player profile data: owned games count
  def queryB(self, player):
    query = f"SELECT COUNT(g.game_name) FROM Game_copies AS g WHERE owner = '{player}'"
    self.cursor.execute(query)
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  # Returns owners of this game
  def queryC(self, game):
    query = f"SELECT p.name FROM Players as p RIGHT JOIN Game_copies as gc ON p.name = gc.owner WHERE gc.game_name = '{game}';"
    self.cursor.execute(query)
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  # Returns info about particular game
  def queryD(self, game):
    query = f"SELECT * FROM Games WHERE Games.name = '{game}'"
    self.cursor.execute(query)
    return self.cursor.fetchall()

  # Returns 3 most popular tags for a player (according to their owned games)
  def queryE(self, player):
    query = f"CREATE OR REPLACE VIEW PlayerTags AS SELECT a.tag_name FROM Assigned_tags AS a RIGHT JOIN Games AS g ON g.name = a.game_name RIGHT JOIN Game_copies as gc ON gc.game_name = g.name WHERE GC.owner = '{player}';"
    self.cursor.execute(query)
    query = f"SELECT tag_name FROM playertags GROUP BY tag_name ORDER BY COUNT(tag_name) DESC LIMIT 3;"
    self.cursor.execute(query)
    
    result = self.cursor.fetchall()
    for x in range(len(result)):
      result[x] = self.alphaFilter(result[x])
    return result

  def dummyEntries(self):
    tables = [
      [
        ("Idle",),
        ("Chompy",),
        ("Bunny",),
        ("Jynx",),
        ("Alice",),
        ("Bread",)
      ],

      [
        ('Stardew Valley', '2016-02-26', 'ConcernedApe', 'ConcernedApe'),
        ('Valheim', '2021-02-02', 'Iron Gate AB', 'Coffee Stain Publishing'),
        ('Devour', '2021-01-28', 'Straight Back Games', 'Straight Back Games'),
        ('Pummel Party', '2018-09-20', 'Rebuilt Games', 'Rebuilt Games'),
        ('Dead by Daylight', '2016-01-14', 'Behaviour Interactive Inc.', 'Behaviour Interactive Inc.'),
        ('Dont Starve Together', '2016-04-21', 'Klei Entertainment', 'Klei Entertainment'),
        ('Terraria', '2011-05-16', 'Re-Logic', 'Re-Logic'),
        ('Phasmophobia', '2020-09-18', 'Kinetic Games', 'Kinetic Games'),
        ('Raft', '2018-05-23', 'Redbeet Interactive', 'Axolot games'),
        ('Worms Revolution', '2012-10-10', 'Team17 Digital Ltd', 'Team17 Digital Ltd')
      ],

      [
        ('Pixel Graphics',),
        ('RPG',),
        ('Relaxing',),
        ('Simulation',),
        ('Sandbox',),
        ('Indie',),
        ('Casual',),
        ('Open World',),
        ('2D',),
        ('Cute',),
        ('Survival',),
        ('Horror',),
        ('Atmospheric',),
        ('Puzzle',),
        ('Party',),
        ('Exploration',)
      ],

      [
        ('Stardew Valley', 'Pixel Graphics'),
        ('Stardew Valley', 'RPG'),
        ('Stardew Valley', 'Relaxing'),
        ('Stardew Valley', 'Simulation'),
        ('Stardew Valley', 'Sandbox'),
        ('Stardew Valley', 'Indie'),
        ('Stardew Valley', 'Casual'),
        ('Stardew Valley', 'Cute'),
        ('Stardew Valley', '2D'),
        ('Valheim', 'RPG'),
        ('Valheim', 'Sandbox'),
        ('Valheim', 'Survival'),
        ('Valheim', 'Exploration'),
        ('Valheim', 'Open World'),
        ('Valheim', 'Indie'),
        ('Devour', 'Horror'),
        ('Devour', 'Survival'),
        ('Devour', 'Puzzle'),
        ('Devour', 'Indie'),
        ('Pummel Party', 'Casual'),
        ('Pummel Party', 'Party'),
        ('Pummel Party', 'Indie'),
        ('Dead by Daylight', 'Horror'),
        ('Dead by Daylight', 'Survival'),
        ('Dead by Daylight', 'Atmospheric'),
        ('Dont Starve Together', 'Exploration'),
        ('Dont Starve Together', 'Open World'),
        ('Dont Starve Together', 'Survival'),
        ('Dont Starve Together', '2D'),
        ('Dont Starve Together', 'Atmospheric'),
        ('Terraria', '2D'),
        ('Terraria', 'Sandbox'),
        ('Terraria', 'Survival'),
        ('Terraria', 'Exploration'),
        ('Terraria', 'Pixel Graphics'),
        ('Terraria', 'Indie'),
        ('Terraria', 'RPG'),
        ('Phasmophobia', 'Horror'),
        ('Phasmophobia', 'Indie'),
        ('Raft', 'Survival'),
        ('Raft', 'Open World'),
        ('Raft', 'Sandbox'),
        ('Raft', 'Indie')
      ],

      [
        ('Chompy', 'Stardew Valley'),
        ('Idle', 'Stardew Valley'),
        ('Jynx', 'Stardew Valley'),
        ('Chompy', 'Valheim'),
        ('Jynx', 'Valheim'),
        ('Chompy', 'Devour'),
        ('Idle', 'Devour'),
        ('Jynx', 'Devour'),
        ('Chompy', 'Pummel Party'),
        ('Idle', 'Pummel Party'),
        ('Jynx', 'Pummel Party'),
        ('Alice', 'Dead by Daylight'),
        ('Chompy', 'Dead by Daylight'),
        ('Idle', 'Dead by Daylight'),
        ('Jynx', 'Dead by Daylight'),
        ('Bunny', 'Dead by Daylight'),
        ('Alice', 'Dont Starve Together'),
        ('Bread', 'Dont Starve Together'),
        ('Idle', 'Dont Starve Together'),
        ('Chompy', 'Dont Starve Together'),
        ('Jynx', 'Dont Starve Together'),
        ('Chompy', 'Terraria'),
        ('Idle', 'Terraria'),
        ('Bread', 'Terraria'),
        ('Chompy', 'Phasmophobia'),
        ('Jynx', 'Phasmophobia'),
        ('Idle', 'Phasmophobia'),
        ('Bunny', 'Phasmophobia'),
        ('Chompy', 'Raft'),
        ('Idle', 'Raft'),
        ('Jynx', 'Raft'),
        ('Chompy', 'Worms Revolution'),
        ('Bunny', 'Worms Revolution'),
        ('Alice', 'Worms Revolution'),
        ('Idle', 'Worms Revolution'),
        ('Bread', 'Worms Revolution')
      ]
    ]

    self.cursor.execute("USE pa2")

    self.cursor.executemany("INSERT INTO Players (name) VALUES (%s)", tables[0])
    self.cursor.executemany("INSERT INTO Games VALUES (%s, %s, %s, %s)", tables[1])
    self.cursor.executemany("INSERT INTO Tags (name) VALUES (%s)", tables[2])
    self.cursor.executemany("INSERT INTO Assigned_tags (game_name, tag_name) VALUES (%s, %s)", tables[3])
    self.cursor.executemany("INSERT INTO Game_copies (owner, game_name) VALUES (%s, %s)", tables[4])

    self.connection.commit()