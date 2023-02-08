#!usr/bin/env python
# -*- coding: utf-8 -*-

""" Telegram App: Selective Listener """

from telethon import TelegramClient, events
from pathlib import Path
import yaml
import sqlite3
from datetime import datetime

# Load the script configurations.

PATH = Path("config.yaml")
assert PATH.exists(), "Configuration file not found."

with PATH.open(mode="r") as f:
    cfg = yaml.safe_load(f)

API_ID = cfg["api_id"]
API_HASH = cfg["api_hash"]
TARGETS = cfg["targets"]

# SQLite3 ctrlc+v
def connectDB(sender):
    filename = "tg.msg_" + sender + ".db"
    try:
        sqliteConnection = sqlite3.connect(filename)
        print("Connected db for feed ", sender)
        cursor = sqliteConnection.cursor()
        cursor.close()
    except sqlite3.Error:
        createDB(sender)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def createDB(sender):
    filename = "tg.msg_" + sender + ".db"
    createTable = '''CREATE TABLE Messages (
                    unixtime INTEGER PRIMARY KEY,
                    content TEXT,
                    datetime CHARACTER(20));'''
    try:
        sqliteConnection = sqlite3.connect(filename)
        print("Successfully created db for feed ", sender)
        cursor = sqliteConnection.cursor()
        cursor.execute(createTable)
        sqliteConnection.commit()
        print("SQLite table initialized.")
        cursor.close()
    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("sqlite connection is closed")

# Functions for features
def insertToDB (sender, content, date):
    filename = "tg.msg_" + sender + ".db"
    try:
        sqliteConnection = sqlite3.connect(filename)
        cursor = sqliteConnection.cursor()

        sqlfmt = """INSERT INTO Messages
                          (unixtime, content, datetime) 
                          VALUES (?, ?, ?);"""
        param = (datetime.timestamp(date), content, str(date))
        cursor.execute(sqlfmt, param)
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into db:", sender, error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def textMsg(sender, txt, date):
    msgFmt = "[" + str(date) +"] "+ sender +": " + txt
    print(msgFmt)

def fileMsg(sender, file, date):
    #[download/open file], photo have bytes, rest dk. Bytes retrieving method unknown.
    # NOT WORKING, PoC ONLY.
    supportedContent = ['photo', 'contact', 'document']
    if (file.type == supportedContent):
        msgFmt = "[" + str(date) +"] "+ sender +": " + str(file)
        print(msgFmt)
    else:
        print("Unsupported content, please refer to client app")
        return 0

# Initialize client.
client = TelegramClient("selective-listener", API_ID, API_HASH)

@client.on(events.NewMessage(from_users=TARGETS))
async def on_message_received(event):
    sender = await event.get_sender() 
    if event.message.message:
        textMsg(sender.username, event.message.message, event.message.date)
        print(datetime.timestamp(event.message.date))
    else:
        fileMsg(sender.username, event.message.media, event.message.date)

# Initiate main loop.
# Selectively listen for new messages until the client disconnect/terminate.

client.start()
print("App is ready.")
client.run_until_disconnected()
