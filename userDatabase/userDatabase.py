#!/usr/local/bin/python

import sys
import ssl
import socket
import time
import re
from random import randrange

# user preferenc ebuilder.
 
userDatabase = open("users.txt", 'r')
# The end-goal of this project is to take a line of text from a text file that looks like this:
#	<Ramc: sort = True; diff = False; doOp = True; etc>
# and then generate a class, User, that stores each preference as a characteristic of the class

# WILL NEED: a method that prints out the User's characteristics as a line of plain text
# WILL NEED: something that loops through the whole dictionary of Users, runs ^ that print method, and saves a .txt file with all that. 
# WILL NEED: a method that reads the text file and appends to the dictionary a new entry.
# d['mynewkey'] = 'mynewvalue'

#START with one pref: USER and sort; Ramc: sort=False, e.g.


def readThroughDatabase():
	userDictionary = {}
	for line in userDatabase:
		if line != "\n":
			temporaryDictionary = buildUserEntry(line)
			userDictionary[temporaryDictionary["Name"]] = buildUserEntry(line)
	return userDictionary


def buildUserEntry(lineFromTextFile):

		userName = ""
		sort = False
		d={}
		# Gets the username from the line.
		userName = lineFromTextFile.split(":")[0]
		d["Name"] = userName

		# Gets the preferences from the line

		preferences = lineFromTextFile.split(":")[1]
		prefSort = preferences.split(";")[0]
		d[prefSort.split("=")[0]] = prefSort.split("=")[1]

		prefDiff = preferences.split(";")[1]
		d[prefDiff.split("=")[0]] = prefDiff.split("=")[1]

		#TODO: turn this into a loop that works for an arbitrary amount of preferences.

		# Builds the list of preferences from the text line:
		return d

			#dictionary necessary here, unless I want something stupid.
		# so if I go users["Fin"]["Sort"]

def printUserList(users):
	for key in users:
		print "User " + users[key]["Name"] + " has SORT set to " + users[key]["sort"] + " and DIFF set to " + users[key]["diff"]

def printDatabaseFormat(users):
	for key in users:
		print users[key]["Name"]+":sort="+users[key]["sort"]+";diff="+users[key]["diff"]

def updateTextFile(users):
	newDatabaseFile = open("users.txt", 'w')
	for key in users:
		newDatabaseFile.write(users[key]["Name"]+":sort="+users[key]["sort"]+";diff="+users[key]["diff"])
def main():
	users = readThroughDatabase()
	printUserList(users)
	updateTextFile(users)
	print "Fin has sort set to " + users["Fin"]["sort"]


main()
