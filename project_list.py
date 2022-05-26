# project_list.py

'''
title: Construction Project List
author: Duncan Nickel
date-created: 13/5/22
'''

import sqlite3, sys, pathlib
from flask import Flask, redirect, render_template, request, url_for

### --- Variables -- ###

PROJECT_LIST = "project_list.txt"
MATERIAL_LIST = "material_list.db"


FIRST_RUN = True
# Either both files exist, or neither do (unless the user does something dumb)
if (pathlib.Path.cwd() / PROJECT_LIST).exists() and (pathlib.Path.cwd() / MATERIAL_LIST).exists(): FIRST_RUN = False

### --- Flask --- ###

app = Flask(__name__)

@app.route("/",methods = ["GET","POST"])
def index():
    """Website homepage
    """
    return render_template("index.html")

@app.route("/createProject",methods = ["GET","POST"])
def createProject():
    """Form to create a project
    """
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    ALERT = ""
    # Used to determine alert colour since I can't use f strings in jinja
    # 0 for green, 1 for red, and I might add more later
    ALERT_TONE = 0

    if request.form:
        PROJECT_NAME = request.form.get("title")
        PROJECT_NAME.replace(" ","-") # Replaces any spaces with hyphens because spaces might break sqlite (I didn't test it)
        DIFFICULTY = request.form.get("difficulty")
        TIME = request.form.get("time")
        TEXT = [PROJECT_NAME,f"(Difficulty: {DIFFICULTY}|Time: {TIME} hours)"]
        CURSOR.execute("""
        CREATE TABLE ?
            VALUES(
                part_name TEXT PRIMARY KEY,
                pieces TEXT, material TEXT,
                fin_thick TEXT, fin_width TEXT, fin_lenght TEXT,
                rough_thick TEXT, rough_width TEXT, rough_length TEXT
            )
        ;""")
        CONNECTION.commit()
        CONNECTION.close()
        # Redirects to the home page if form is submitted
        return redirect("/")
    
    return render_template("new-project.html",alert=ALERT,tone=ALERT_TONE)

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



### --- Outputs --- ###

def writeFile(DATA):
    """Writes data to the given file

    Args:
        DATA (_type_): _description_
    """
    FILE = open(PROJECT_LIST, "w")
    FILE.writelines(DATA)
    FILE.close()

### --- Main Code --- ###

if __name__ == "__main__":
    if FIRST_RUN: createFiles()
    DATA = readFile()
    app.run(debug=True)