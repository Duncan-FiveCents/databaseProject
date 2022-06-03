# project_list.py

'''
title: Construction Project List
author: Duncan Nickel
date-created: 13/5/22
'''

import sqlite3, os, pathlib
from flask import Flask, redirect, render_template, request, session, url_for

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

# Used to make some code cleaner later
PART_DATA = {
    1:"part_name",
    2:'pieces',3:"material",
    4:"fin_thick",5:"fin_width",6:"fin_length",
    7:"rough_thick",8:"rough_width",9:"rough_length"
}

FIRST_RUN = True
# Either both files exist, or neither do (unless whoever is running this does something dumb)
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
    """Website homepage
    """
    global ALERT_SHOWN

    if "ALERT" in session and ALERT_SHOWN == False:
        ALERT = session["ALERT"]
        ALERT_SHOWN = True
    else:
        ALERT = ["",0]
        ALERT_SHOWN = False
    
    PROJECTS = getAllProjects()

    return render_template("index.html",alert=ALERT[0],tone=ALERT[1],projects=PROJECTS)

@app.route("/createProject",methods = ["GET","POST"])
def createProject():
    """Form to create a project
    """
    global ALERT_SHOWN

    if request.form:
        PROJECT_NAME = request.form.get("title")
        DIFFICULTY = request.form.get("difficulty")
        TIME = request.form.get("time")
        TEXT = [PROJECT_NAME,f" (Difficulty: {DIFFICULTIES[int(DIFFICULTY)]} | Time: {TIME} hours)"]
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
def displayProject(project):
    LIST = getAllProjects()

    # Checks for a matching project name and grabs that data
    PROJECT_NAME, INFO, INSTRUCTIONS = "","",""
    for i in range(len(LIST)):
        if LIST[i][0] == project:
            project = LIST[i]
            PROJECT_NAME = project[0]
            INFO = project[1]
            INSTRUCTIONS = project[2:]
            break

    # This if statement specifically checks if the project is called "favicon.ico"
    # This happens when the browser sends a request for the icon, overwriting the initial project search
    # I added code to each HTML page which prevents the request, at the cost of having no icon
    # Although the code in the HTML makes this statement pointless, I kept it for two reasons
    # 1. In case the request happens, and 2. I needed a spot to explain why there's no icon
    if PROJECT_NAME != "f": PARTS = getMaterials(PROJECT_NAME)
    else: PARTS = []

    if request.form:
        if "task" in request.form: # Checks which submit button was pressed
            # Adding an instruction
            NEW_INSTRUCTIONS = request.form.get("new_task")
        else:
            # Adding a part
            NEW_PART = []
            for i in range(9): NEW_PART.append(request.form.get(PART_DATA[i+1]))
            addPart(NEW_PART,PROJECT_NAME)
            # This forces a refresh so that the new part shows up immediately
            return redirect(url_for('displayProject',project=PROJECT_NAME))

    return render_template("/project.html",name=PROJECT_NAME,info=INFO,instructions=INSTRUCTIONS,parts=PARTS)


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
    for i in range(len(DATA)):
        DATA[i].rstrip()
    FILE.close()
    return DATA

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
                fin_thick TEXT, fin_width TEXT, fin_length TEXT,
                rough_thick TEXT, rough_width TEXT, rough_length TEXT
            )
    ;""")
    CONNECTION.commit()
    CONNECTION.close()

def addPart(PART,PROJECT):
    """Adds a new part to the material list

    Args:
        PART (list): list of new part information
        PROJECT (str): the project to add the part to
    """
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    PROJECT = PROJECT.replace(" ","_") # Replaces spaces with underscores before checking database

    CURSOR.execute(f"""
        INSERT INTO {PROJECT} (
            part_name,
            pieces, material,
            fin_thick, fin_width, fin_length,
            rough_thick, rough_width, rough_length
        )
        VALUES(?,?,?,?,?,?,?,?,?)
    ;""",PART)
    CONNECTION.commit()
    CONNECTION.close()

### --- Processing --- ###



### --- Outputs --- ###

def writeFile(DATA):
    """Writes data to the project list

    Args:
        DATA (list): list of projects
    """
    NEW_DATA = ""
    FILE = open(PROJECT_LIST, "w")
    for i in range(len(DATA)):
        for j in range(len(DATA[i])):
            NEW_DATA += f"{DATA[i][j]},"
    NEW_DATA += "\n"
    FILE.write(NEW_DATA)
    FILE.close()

def writeProject(PROJECT):
    """Writes a new project to the project file

    Args:
        NAME (list): project title, difficulty, and time
    """
    DATA = readFile()
    DATA.append(PROJECT)
    writeFile(DATA)

def tableQuery(NAME):
    """Checks if a certain table already exists

    Returns:
        str: returns the name of the table, or None if the table does not exist
    """
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    QUERY = CURSOR.execute(f"""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='{NAME}'
    ;""").fetchone()
    return QUERY

def getAllProjects():
    """Reads and cleans up items from the project file

    Returns:
        list: projects with info and instructions
    """
    DATA = readFile()
    PROJECTS = []
    for i in range(len(DATA)):
        PROJECTS.append(DATA[i].split(","))
        if PROJECTS[i][-1] == "\n": PROJECTS[i].pop(-1)
    return PROJECTS

def getMaterials(NAME):
    """Gets the material list for a single project
    
    Args:
        NAME (str): name of project
    
    Returns:
        list: list of parts
    """
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    NAME = NAME.replace(" ","_")

    DATA = CURSOR.execute(f"""
        SELECT *
        FROM {NAME}
    ;""").fetchall()
    CONNECTION.close()

    # Cleans data so that it won't display "None" in the table
    for i in range(len(DATA)):
        for j in range(len(DATA[i])):
            if DATA[i][j] == None:
                DATA[i][j] = ""

    return DATA

### --- Main Code --- ###

if __name__ == "__main__":
    if FIRST_RUN: createFiles()
    app.run(debug=True)