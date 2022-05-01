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


  def createDb(self):
      self.cursor.execute("CREATE DATABASE pa2")
      self.cursor.execute("USE pa2")

      tables = [
        "CREATE TABLE Games(" +
        "name varchar(64) NOT NULL UNIQUE," +
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
        "image varchar(128)," +
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

  def dummyEntries():
    entries = [
      # games
      [],
      # tags
      [],
      # assigned tags
      [],
      # players
      [],
      # game copies
      []
    ]

  def addGame(self, name):
    self.cursor.execute("USE pa2")
    self.cursor.execute(f"INSERT INTO Games (name) VALUES ('{name}')")
    print("Game has been added")
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

  # Returns player profile data: name and owned games count
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