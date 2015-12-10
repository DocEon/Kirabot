#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import ssl
import socket
import time
import re
import json
from random import randrange

def readUserDictionary():
	f = open('JSONUsers.txt', 'r')
	userDictionary = json.load(f)
	#for line in f:
	#	userFromDictionary = json.loads(line)
	#	userDictionary[userFromDictionary["nickname"]] = json.loads(line)
	return userDictionary

def writeToFile(userDictionary):	
	f = open('JSONUsers.txt', 'w')
	json.dump(userDictionary, f, indent = 4)
	print("Successfully updated user database")
	# this gets called every time someone changes a setting. It generates a new list of all users
	# and prints out that stuff as .json and then saves it as a .txt from which it reads on startup.

def changeProperty(userToChange, propertyToChange, newValue):
	userDictionary[userToChange][propertyToChange] = newValue
	writeToFile(userDictionary)

def main():
	run = True
	while run:
		print "Welcome! What do you want to do?"
		userInput = raw_input("Options include: showProfile, dump, change, exit\n")
		if userInput == "showProfile":
			nickname = raw_input("Who do you want to see?\n")
			propertyToCheck = raw_input("And what do you want to check? e.g. manual_mode, real_name, sort\n")
			print userDictionary[nickname][propertyToCheck]
		elif userInput == "dump":
			writeToFile(userDictionary)
		elif userInput == "change":
			userToChange = raw_input("Who do you want to change?")
			propertyToChange = raw_input("What property do you want to change? e.g. manual_mode, real_name, sort\n")
			newValue = raw_input("And what is your new value? Please capitalize any boolean choices.")
			changeProperty(userToChange, propertyToChange, newValue)
		elif userInput == "exit":
			print "This works!"
			run = False

userDictionary = readUserDictionary()
main()