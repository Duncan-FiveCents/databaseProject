# project_list.py

'''
title: Construction Project List
author: Duncan Nickel
date-created: 13/5/22
'''

import sqlite3, sys, pathlib
from flask import Flask, render_template, request

### --- Variables -- ###

PROJECT_LIST = "project_list.txt"
MATERIAL_LIST = "material_list.db"


FIRST_RUN = True
# Either both files exist, or neither do (unless the user does something dumb)
if (pathlib.Path.cwd() / PROJECT_LIST).exists() and (pathlib.Path.cwd() / MATERIAL_LIST).exists(): FIRST_RUN = False

### --- Flask --- ###

app = Flask(__name__)

@app.route("/")
def index():
    """Website homepage
    """
    return render_template("index.html")

@app.route("/new-project")
def createProject():
    global PROJECT_LIST,MATERIAL_LIST
    CONNECTION = sqlite3.connect(MATERIAL_LIST)
    CURSOR = CONNECTION.cursor()

    if request.form:
        pass


### --- Inputs --- ###

def createFiles():
    """Creates needed files. Also I'm not sure why I'm counting this as an input
    """
    global PROJECT_LIST,MATERIAL_LIST
    FILE = open(PROJECT_LIST, "w")
    FILE.close()
    FILE = open(MATERIAL_LIST, "w")
    FILE.close()

### --- Processing --- ###



### --- Outputs --- ###



### --- Main Code --- ###

if __name__ == "__main__":
    if FIRST_RUN:
        createFiles()
    app.run(debug=True)