import sqlite3
import os
from datetime import datetime

spotify_folder_location = str(os.getenv('APPDATA')) + "/Spotify/"
database_location = spotify_folder_location + "/spotify_addblocker.db"

def DB_CONNECT():
    global db_connection
    global db_cursor
    db_connection = sqlite3.connect(database_location)
    db_cursor = db_connection.cursor()

def DB_DISCONNECT():
    db_connection.commit()
    db_connection.close()

def DB_TABLES():
    sql = f'CREATE TABLE IF NOT EXISTS "blocker_count" ("id" INTEGER NOT NULL, "counting" INTEGER,PRIMARY KEY("id" AUTOINCREMENT))'
    db_cursor.execute(sql)
    sql = f'CREATE TABLE IF NOT EXISTS "last_blocked_time" ("id" INTEGER NOT NULL, "last_time" TEXT,PRIMARY KEY("id" AUTOINCREMENT))'
    db_cursor.execute(sql)
    sql = f'CREATE TABLE IF NOT EXISTS "checkbox" ("id" INTEGER NOT NULL, "status" TEXT,PRIMARY KEY("id" AUTOINCREMENT))'
    db_cursor.execute(sql)
    db_connection.commit()

    try:
        sql = f'INSERT INTO "checkbox" (id) VALUES(1)'
        db_cursor.execute(sql)
        sql = f'INSERT INTO "last_blocked_time" (id, last_time) VALUES(1, "None")'
        db_cursor.execute(sql)
        sql = f'INSERT INTO "blocker_count" (id, counting) VALUES(1, 0)'
        db_cursor.execute(sql)
        db_connection.commit()
    except sqlite3.IntegrityError:
        pass

def DB_CHECKBOX():
    sql = "SELECT * FROM 'checkbox'"
    db_cursor.execute(sql)
    row = db_cursor.fetchall()
    return row[0][1]

def DB_CHECKBOX_CHANGE(change):
    if change == "CHECKED":
        sql = f'UPDATE "checkbox" SET status="CHECKED" WHERE id=1'
        db_cursor.execute(sql)
        db_connection.commit()
    else:
        sql = f'UPDATE "checkbox" SET status="NOT CHECKED" WHERE id=1'
        db_cursor.execute(sql)
        db_connection.commit()

def ADDING_LAST_BLOCKED_TIME():
    now = str(datetime.strftime(datetime.now(), "%d %B %Y %H:%M"))
    sql = f'UPDATE "last_blocked_time" SET "last_time"="{now}" WHERE "id"=1'
    db_cursor.execute(sql)
    db_connection.commit()

def GETTING_LAST_BLOCKED_TIME():
    sql = f'SELECT * FROM "last_blocked_time"'
    db_cursor.execute(sql)
    row = db_cursor.fetchall()
    return row[0][1]

def ADDING_BLOCK_COUNT():
    new_count = GETTING_BLOCK_COUNT() + 1
    sql = f'UPDATE "blocker_count" SET "counting"="{new_count}" WHERE "id"=1'
    db_cursor.execute(sql)
    db_connection.commit()

def GETTING_BLOCK_COUNT():
    sql = f'SELECT * FROM "blocker_count"'
    db_cursor.execute(sql)
    row = db_cursor.fetchall()
    return row[0][1]