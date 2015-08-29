#!/usr/local/bin/python

import sys
import ssl
import socket
import time
import re
from random import randrange

# user preferenc ebuilder.
 
userDatabase = open("users.txt", 'r')

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
		newDatabaseFile.write(users[key]["Name"]+":sort="+users[key]["sort"]+";diff="+users[key]["diff"]+"\n")

def newUser(userName, users):
	users[userName] = {'Name':userName, 'sort':'false','diff':'false'}

def changePreference(userName, users, keyToChange, valueToChange):
	users[userName][keyToChange] = valueToChange
	
def main():
	users = readThroughDatabase()
	runProgram = True
	while runProgram:
		command = raw_input("What do you want to do?")
		if command == "printUserList":
			printUserList(users)
		elif command == "newUser":
			userName = raw_input("What is the new user's name?")
			#check for duplicates probs
			newUser(userName, users)
			updateTextFile(users)
		elif command == "changePreference":
			keyToChange = raw_input("What preference do you want to change? 'sort' or 'diff'?")
			valueToChange = raw_input("And what is the new value of this preference?")
			changePreference(userName, users, keyToChange, valueToChange)
			updateTextFile(users)
		elif command == "exit":
			runProgram = False
	updateTextFile(users)



main()
