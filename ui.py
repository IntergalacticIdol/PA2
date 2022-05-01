from termios import PARODD
import tkinter as tk
import tkinter.ttk as ttk
from turtle import width
import queries as q

class uiManager:
  dbConnector = None
  listBox = None
  playerList = None
  playerStates = None

  def setDbCon(self, dbConnector):
    self.dbConnector = dbConnector

  # Creates the window, its menu and summons rest of the objects. Sort of starting method.
  def createWindow(self):
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry('300x700')
    root.title("Game Selection Helper")

    mainStyle = ttk.Style(root)
    mainStyle.theme_use('clam')

    # STYLES
    mainStyle.configure('TButton', background='#2958a3', borderwidth=5)
    mainStyle.map('TButton', background=[('!active', '#3669ba')])
    mainStyle.configure('TFrame', background='#5a94f2', relief='ridge')
    mainStyle.configure('TCheckbutton', background='#5a94f2', indicatorbackground='#2958a3', anchor=tk.W, width=13)
    mainStyle.configure('TLabel', width=32, background='white')

    # Menubar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    addMenu = tk.Menu(menubar)
    addMenu.add_command(
      label='Add a game',
      command=lambda: self.addGamePopUp(root)
    )
    addMenu.add_command(
      label='Add a tag',
      command=lambda: self.addTagPopUp(root)
    )
    addMenu.add_command(
      label='Add a player',
      command=lambda: self.addPlayerPopUp(root)
    )
    addMenu.add_command(
      label='Add a game to a player inventory',
      command=lambda: self.addGameCopyPopUp(root)
    )
    
    menubar.add_cascade(
      label="Add",
      menu=addMenu,
      underline=0
    )

    viewMenu = tk.Menu(menubar)
    profileMenu = tk.Menu(viewMenu)
    self.playerList = self.dbConnector.getPlayers()
    for player in self.playerList:
      profileMenu.add_command(
        label=f'{player}',
        command=lambda player=player: self.showProfile(root, player)
      )
    
    viewMenu.add_cascade(
      label="See player profile",
      menu=profileMenu,
      underline=0
    )
    menubar.add_cascade(
      label="View",
      menu=viewMenu,
      underline=0
    )

    self.createContents(root)

    root.mainloop()

  # Takes care of creating objects inside of given window.
  # Splits the window in two.
  def createContents(self, parent):
    paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, width=300, height=700, showhandle=False, sashwidth=0)

    left = tk.Frame(parent, bg='#5a94f2', borderwidth=5)
    left.pack()
    paned.add(left)
    right = tk.Frame(parent, bg='#5a94f2')
    right.pack()
    paned.add(right)

    self.createRightPanel(right)
    self.createLeftPanel(left)

    paned.pack()

  # Right panel creation.
  def createRightPanel(self, parent):
    rightPanel = tk.PanedWindow(parent, orient=tk.VERTICAL, width=150, height=700)
    rightPanel.pack()

    playerBox = ttk.Frame(parent, borderwidth=5)
    playerBox.pack()
    rightPanel.add(playerBox)

    self.playerList = self.dbConnector.getPlayers()
    playerButtons = []
    self.playerStates = [tk.BooleanVar() for x in range(len(self.playerList))]
    for x in range(len(self.playerList)):
      playerButtons.append(ttk.Checkbutton(playerBox, text=self.playerList[x], variable=self.playerStates[x]))
    for button in playerButtons:
      button.pack()

    tagBox = ttk.Frame(parent, borderwidth=5)
    tagBox.pack()
    rightPanel.add(tagBox)

    tagList = self.dbConnector.getTags()
    tagButtons = []
    tagStates = [tk.BooleanVar() for x in range(len(tagList))]
    for x in range(len(tagList)):
      tagButtons.append(ttk.Checkbutton(tagBox, text=tagList[x], variable=tagStates[x]))
    for button in tagButtons:
      button.pack()

    confirm = ttk.Button(tagBox, text='Search', width=13, command=lambda: self.recreateGameList(self.listBox, self.playerList, self.playerStates, tagList, tagStates))
    confirm.pack()

  def createLeftPanel(self, parent):
    # initially creates the list and fills it in
    if (self.listBox == None):
      self.listBox = tk.Listbox(parent, width=17, height=38, selectmode=tk.SINGLE)
      self.listBox.grid(columnspan=2)
      self.listBox.delete(0, tk.END)
      gameList = self.dbConnector.getGameTitles()
      for game in gameList:
        self.listBox.insert(tk.END, game)

    # button
    ttk.Button(parent, text='Play', width=6, command=lambda: self.updateTime()).grid()
    b2 = ttk.Button(parent, text='Info', width=6, command=lambda: self.showGame(parent, self.listBox.get(self.listBox.curselection()))).grid(column=1, row=1)

  def updateTime(self):
    selectedPlayers = []
    for x in range(len(self.playerStates)):
      if self.playerStates[x].get() == True:
        selectedPlayers.append(self.playerList[x])

    self.dbConnector.updateTime(self.listBox.get(self.listBox.curselection()), selectedPlayers)

  def recreateGameList(self, listBox, playerList, playerStates, tagList, tagStates):
    selectedPlayers = []
    for x in range(len(playerStates)):
      if playerStates[x].get() == True:
        selectedPlayers.append(playerList[x])

    selectedTags = []
    for x in range(len(tagStates)):
      if tagStates[x].get() == True:
        selectedTags.append(tagList[x])

    listBox.delete(0, tk.END)
    gameList = self.dbConnector.getGameTitlesByFilters(selectedPlayers, selectedTags)
    for game in gameList:
      listBox.insert(tk.END, game)

  def addGamePopUp(self, parent):
    top = tk.Toplevel(parent)
    top.geometry("300x300")
    top.title("Add a game")

    ttk.Label(top, text='Game title: ').pack()
    nameBox = ttk.Entry(top)
    nameBox.pack()

    tagList = []
    for x in self.dbConnector.getTags():
      tagList.append(x)

    ttk.Label(top, text='Tags: ').pack()
    listBox = tk.Listbox(top, selectmode=tk.MULTIPLE)
    for x in tagList:
      listBox.insert(tk.END, x)
    listBox.pack()

    def onClick():
      self.dbConnector.addGame(nameBox.get())
      for x in listBox.curselection():
        self.dbConnector.addAssigned(nameBox.get(), listBox.get(x))

    confirm = ttk.Button(top, text='Add', command=lambda: onClick()).pack()

  def addPlayerPopUp(self, parent):
    top = tk.Toplevel(parent)
    top.geometry("300x300")
    top.title("Add a Player")

    ttk.Label(top, text='Player name: ').pack()
    nameBox = ttk.Entry(top)
    nameBox.pack()

    # image select

    confirm = ttk.Button(top, text='Add', command=lambda: self.dbConnector.addPlayer(nameBox.get())).pack()

  def addTagPopUp(self, parent):
    top = tk.Toplevel(parent)
    top.geometry("300x300")
    top.title("Add a Tag")

    ttk.Label(top, text='Tag name: ').pack()
    nameBox = ttk.Entry(top)
    nameBox.pack()

    confirm = ttk.Button(top, text='Add', command=lambda: self.dbConnector.addTag(nameBox.get())).pack()

  def addGameCopyPopUp(self, parent):
    top = tk.Toplevel(parent)
    top.geometry("300x300")
    top.title("Add a Game Copy")

    playerList = []
    for x in self.dbConnector.getPlayers():
      playerList.append(x)

    ttk.Label(top, text='Player: ').pack()
    playerBox = ttk.Combobox(top, values=playerList)
    playerBox.pack()

    gameList = []
    for x in self.dbConnector.getGameTitles():
      gameList.append(x)

    ttk.Label(top, text='Game title: ').pack()
    gameBox = ttk.Combobox(top, values=gameList)
    gameBox.pack()

    confirm = ttk.Button(top, text='Add to a player inventory', 
                         command=lambda: self.dbConnector.addGameCopy(playerBox.get(), gameBox.get()))
    confirm.pack()

  def showProfile(self, parent, player):
    top = tk.Toplevel(parent, bg='#5a94f2', bd=5, relief='ridge')
    top.geometry("300x75")
    top.title(f"{player}'s profile")

    playerData = self.dbConnector.queryB(player)
    playerData.append(self.dbConnector.queryE(player))
    playerData.append(player)
    temp = ''
    for element in playerData[1]:
      temp += element + ' '

    ttk.Label(top, text=f'Username: {playerData[2]}').pack()
    ttk.Label(top, text=f'Games owned: {playerData[0]}').pack()
    ttk.Label(top, text=f'Favourite tags: {temp}').pack()

  def showGame(self, parent, game):
    top = tk.Toplevel(parent, bg='#5a94f2', bd=5, relief='ridge')
    top.geometry("300x110")
    top.title(f"Game info")

    gameData = self.dbConnector.queryD(game)
    gameData = gameData[0]
    gameOwners = self.dbConnector.queryC(game)
    owners = ''
    for owner in gameOwners:
      owners += owner + ' '

    ttk.Label(top, text=f'Title: {gameData[0]}').pack()
    ttk.Label(top, text=f'Owned by: {owners}').pack()
    ttk.Label(top, text=f'Release date: {gameData[1]}').pack()
    ttk.Label(top, text=f'Developer: {gameData[2]}').pack()
    ttk.Label(top, text=f'Publisher: {gameData[3]}').pack()