import mysql.connector
import queries as q
import ui

dbCon = q.databaseConnector()
dbCon.dbInit()

uiManager = ui.uiManager()
uiManager.setDbCon(dbCon)
uiManager.createWindow()
