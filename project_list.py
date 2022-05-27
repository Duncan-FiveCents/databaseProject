# project_list.py

'''
title: Construction Project List
author: Duncan Nickel
date-created: 13/5/22
'''

import sqlite3, os, pathlib
from flask import Flask, redirect, render_template, request, session

### --- Variables -- ###

PROJECT_LIST = "project_list.txt"
MATERIAL_LIST = "material_list.db"

DIFFICULTIES = {
    1:"Simple",
    2:"Easy",
    3:"Medium",
    4:"Difficult",
    5:"Morbin' Time"
}

FIRST_RUN = True
# Either both files exist, or neither do (unless the user does something dumb)
if (pathlib.Path.cwd() / PROJECT_LIST).exists() and (pathlib.Path.cwd() / MATERIAL_LIST).exists(): FIRST_RUN = False

ALERT_SHOWN = False # Used for determining whether to show alerts

### --- Flask --- ###

app = Flask(__name__)

# This key is needed to use the "session" stuff between pages
# There was probably an easier way to send data between pages without the session
# But I didn't find it
KEY = os.urandom(12)
app.secret_key = KEY

@app.route("/",methods = ["GET","POST"])
def index():
    global ALERT_SHOWN
    """Website homepage
    """
    if "ALERT" in session and ALERT_SHOWN == False:
        ALERT = session["ALERT"]
        ALERT_SHOWN = True
    else:
        ALERT = ["",0]
        ALERT_SHOWN = False

    return render_template("index.html",alert=ALERT[0],tone=ALERT[1])

@app.route("/createProject",methods = ["GET","POST"])
def createProject():
    """Form to create a project
    """
    global ALERT_SHOWN

    if request.form:
        PROJECT_NAME = request.form.get("title")
        DIFFICULTY = request.form.get("difficulty")
        TIME = request.form.get("time")
        TEXT = [PROJECT_NAME,f"(Difficulty: {DIFFICULTIES[DIFFICULTY]}|Time: {TIME} hours)"]
        writeProject(TEXT)
        PROJECT_NAME = PROJECT_NAME.replace(" ","_") # Replaces any spaces with underscores because spaces break

        if tableQuery(PROJECT_NAME) == None:
            createTable(PROJECT_NAME)
            # Used to determine alert colour since I can't use f strings in jinja
            # 0 for green, 1 for red, and I might add more later
            ALERT_DATA = ["Project successfully created!",0]
        else:
            ALERT_DATA = ["Project with that name already exists!",1]
        
        # Essentially makes the alert data accessible from other pages
        session["ALERT"] = ALERT_DATA

        ALERT_SHOWN = False

        # Redirects to the home page if form is submitted
        return redirect("/")

    return render_template("new-project.html")

@app.route("/<project>",methods = ["GET","POST"])
def displayProject(PROJECT):
    LIST = readFile()
    for i in range(len(LIST)):
        if LIST[i][0] == PROJECT:
            PROJECT = LIST[i][0]
            break
    PROJECT_NAME = PROJECT[0]
    INFO = PROJECT[1]
    INSTRUCTIONS = PROJECT[2:]
    return render_template("/project",name=PROJECT_NAME,info=INFO,instructions=INSTRUCTIONS)


### --- Inputs --- ###

def createFiles():
    """Creates needed files. Also I'm not sure why I'm counting this as an input
    """
    global PROJECT_LIST,MATERIAL_LIST
    FILE = open(PROJECT_LIST, "w")
    FILE.close()
    FILE = open(MATERIAL_LIST, "w")
    FILE.close()

def readFile():
    """Opens and reads the contents of the instruction file

    Returns:
        list: data of each line
    """
    FILE = open(PROJECT_LIST)
    DATA = FILE.readlines()
    FILE.close()
    return DATA

### --- Processing --- ###

def createTable(NAME):
    """Creates a table with the given name

    Args:
        NAME (str): name of table
    """
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()
    CURSOR.execute(f"""
        CREATE TABLE IF NOT EXISTS {NAME}
            (
                part_name TEXT PRIMARY KEY,
                pieces TEXT, material TEXT,
                fin_thick TEXT, fin_width TEXT, fin_lenght TEXT,
                rough_thick TEXT, rough_width TEXT, rough_length TEXT
            )
    ;""")
    CONNECTION.commit()
    CONNECTION.close()

def writeProject(PROJECT):
    """Writes a new project to the project file

    Args:
        NAME (list): project title, difficulty, and time
    """
    DATA = readFile()
    DATA.append(PROJECT)
    writeFile(DATA)

def getAllProjects():
    pass

### --- Outputs --- ###

def writeFile(DATA):
    """Writes data to the project list

    Args:
        DATA (_type_): _description_
    """
    FILE = open(PROJECT_LIST, "w")
    FILE.writelines(DATA)
    FILE.close()

def tableQuery(NAME):
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    QUERY = CURSOR.execute(f"""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='{NAME}'
    ;""").fetchone()
    return QUERY

### --- Main Code --- ###

if __name__ == "__main__":
    if FIRST_RUN: createFiles()
    app.run(debug=True)