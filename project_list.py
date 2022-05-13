# project_list.py

'''
title: Construction Project List
author: Duncan Nickel
date-created: 13/5/22
'''

import sqlite3, sys, pathlib

### --- Variables -- ###

PROJECT_LIST = "project_list.txt"
MATERIAL_LIST = "material_list.db"


FIRST_RUN = False
# Either both files exist, or neither do (unless the user does something dumb)
if (pathlib.Path.cwd() / PROJECT_LIST).exists() and (pathlib.Path.cwd() / MATERIAL_LIST).exists(): FIRST_RUN = True

