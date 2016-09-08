#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import ssl
import socket
import time
import re
import json
import os.path
import glob
from random import randrange

### global variables (with defaults that will likely be overridden)

os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
time.tzset()
quoteDatabase = [""]
server = "irc.choopa.net"
port = 9999
password = ""
channel = "#Mage"
botnick = "Kirabot"
irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc = ssl.wrap_socket(irc_C)
userDictionary = {}
logHelperList = []
copyLogs = False
logCopyDirectory = ""
logDictionary = {}

### TODO: Fix Kira's logging of PMs - I don' know what it's doing with msgs from private users, but I need to trace that down. 

### Quotes database
def loadQuotes():
  global quoteDatabase
  f = open("quotes.txt", 'r')
  currentIndex = 0
  for line in f:
      if line.strip() == "":
        if quoteDatabase[len(quoteDatabase)-1] != "":
          quoteDatabase.append("")
      else:
        quoteDatabase[len(quoteDatabase)-1] += "\n" + line

def loadLogs():
  global logDictionary
  listOfLogs = glob.glob(logCopyDirectory + "\*.txt")
  for log in listOfLogs:
    newList = [""]
    if log.find("results.txt") == -1:
      f = open(log, 'r')
      for line in f:
        newList.append(line)
      logDictionary[log] = newList

def logSearch(stringToFind):
  resultDictionary = {}
  resultList = []
  for key in logDictionary:
    for line in logDictionary[key]:
      if (line.lower()).find(stringToFind.lower()) != -1:
        resultList.append(line)
    if len(resultList) > 0:
      resultDictionary[key] = resultList
      # should be filename rather than key - or, better yet, url.
      resultList = []
  print "Found occurences of your string. Wrote the results to results.txt."
  writeSearchResultsToFile(resultDictionary)
  return resultDictionary

def writeSearchResultsToFile(resultDictionary):
  fullFileName = os.path.join(logCopyDirectory, "results.txt")
  resultFile = open(fullFileName, 'w')
  for key in resultDictionary:
    resultFile.write("Results from " + key + ":\n")
    for line in resultDictionary[key]:
      resultFile.write(line + "\n")
    resultFile.write("~~~~~~~~~~\n")

def logCleaner(line):
  m = re.split('(\d{2}:\d{2}:\d{2})\s:(\w*)!(~\S*)\s(\S*)\s', line)
  if len(m) < 4:
    cleanLine = line
  elif m[4] == "PRIVMSG":
    n = re.split("(.*)\sPRIVMSG (#\S{0,10})\s:(.*)", line)
    cleanLine = "("+ m[1]+")" + " | " + m[2] + ": " + n[3]
    #n[1] should be the stuff before privmsg, n[2] should be the channel, n[3] should be the text.
  else:
    cleanLine = "("+m[1]+")"+" | "+m[2] + " " + m[4]
  return cleanLine

### IRC stuff


def tryGettingInput(callback):
  # try reading a line of IRC input.
  # callback is a function that takes one argument - the raw line of input - and processes it as desired.
  global logHelperList
  try:
    text=irc.recv(2040) # wait for the next bit of input from the IRC server. Limit to 2040 characters.
    # (the rest would stay in the buffer and get processed afterwards, I think)
    timestampedLine = time.strftime("%H:%M:%S ") + text
    try:
      cleanLine = logCleaner(timestampedLine)
      print cleanLine
    except IndexError:
      cleanLine = timestampedLine
    if not text.find('PING') != -1:
      logHelperList.append(cleanLine)
    if len(logHelperList) > 10:
      logHelperList = logAList(logHelperList)
    # Prevent Timeout - this is how the IRC servers know to kick you off for inactivity, when your client doesn't PONG to a PING.
    if text.find('PING') != -1: # if there is a "PING" anywhere in the text
      sendIrcCommand('PONG ' + text.split()[1] + '\r\n')
      # TODO: what's with the 'PONG AUTH' when first connecting connecting? debug.
    return callback(text) # actually process the input
  except Exception as e:
    # this prints the error message whenever something throws an exception.
    (exType, value, traceback) = sys.exc_info()
    print str(e)
    print 'on line '+str(traceback.tb_lineno)
    sendMsg('Oops, I derped') # TODO(yanamal): user preference for "PM me error messages"?
    sendMsg(str(e))


def respondToConnectionCommands(text):
  # see if the text contains commands for the bot to respond to in order to complete the connection
  # respond as necessary.
  # look for PONG requestes and welcome messages of the format:
  # ":irc.eversible.com 001 yanabot :Welcome to the EFNet Internet Relay Chat Network yanabot""
  connected = False
  if text.find('To connect type /QUOTE PONG') != -1:
    sendIrcCommand('PONG' + text.split('To connect type /QUOTE PONG')[1] + '\r\n')
  
  if text.find('Welcome') != -1: # Note: for some reason the match fails on the 'EFNet' part of the expected welcome message.
    # leaving it at just 'Welcome'. Nothing can go wrong.
    sendIrcCommand("PRIVMSG nickserv :iNOOPE\r\n") #auth
    sendIrcCommand("JOIN "+ channel +"\n")
    connected = True
  return connected


def connectAndJoin():
  # connect to irc, then join the channel requested.
  
  print "Establishing connection to [%s]" % (server)
  # Connect
  irc.connect((server, port))
  sendIrcCommand("USER "+ botnick +" "+ botnick +" "+ botnick +" :testbot\n")
  sendIrcCommand("NICK "+ botnick +"\n")
  
  connected = False
  while not connected:
    connected = tryGettingInput(respondToConnectionCommands)


def inputLoop():
  # An infinite loop waiting for input and processing it.
  global logHelperList
  keepLooping = 0
  while keepLooping < 25:
    startTime = time.time()
    tryGettingInput(processInput)
    if (time.time()-startTime) < 0.1:
      keepLooping += 1
    else:
      keepLooping = 0
  #print "Looped too fast " + keepLooping + " times in a row. Disconnecting."
  logHelperList = logAList(logHelperList)
  print "Disconnected. Trying to reconnect in 5 minutes..."
  time.sleep(300)
  connectAndJoin()
  inputLoop()




def sendIrcCommand(command):
  # send IRC command and also print it to the console
  irc.send(command)
  print ' > '+command

### Actual Bot Logic

def processInput(text):
  # process a line of text from the IRC server.
  global channel
  global userDictionary
  global logHelperList
  global logCopyDirectory
  # try to get contents of a message
  # these functions will return emtpy things if it wasn't actually a message to the channel
  firstAndRest = getFirstWordAndRest(text)
  userName = getName(text)
  
  # initialize helper variables for responding to message:
  (chan, message) = getMsg(text)
  firstWord = ""
  restOfText = ""
  allWords = message.split()
  
  if len(firstAndRest) > 0:  # must have found a message to the channel
    firstWord = firstAndRest[0]
    if len(firstAndRest) > 1: # there is more than one word in the message
      restOfText = firstAndRest[1].strip()
  
  # respond to message as needed:
  # TODO(yanamal): make generic firstWord/action registration instead?
  # (pros: readability; can create commands dynamically as you go!
  #  con: any actions not triggered by firstWord would still have to be a manual if check.)
  
  # TODO: check end of kira-related message(s) for "in [channel]" modifier, send response to that channel if it exists.
  
  if firstWord == 'hay':
    sendMsg(userName+', hay v:', chan)
  elif message.strip() == 'always-sort':
    if userName not in userDictionary:
      userDictionary = makeNewUser(userDictionary, userName)
    changeUserProperty(userDictionary, userName, "sort", "True")
    sendMsg('always sorting rolls for '+userName)
  elif message.strip() == 'never-sort':
    if userName not in userDictionary:
      userDictionary = makeNewUser(userDictionary, userName)
    changeUserProperty(userDictionary, userName, "sort", "False")
    sendMsg('Never sorting for '+userName)
  elif firstWord == 'Kirasay':
    sendMsg(restOfText, chan)
  elif firstWord == 'Kiraquote':
    kiraquote(restOfText, chan)
  elif firstWord == 'Kirasearch':
    kirasearch(restOfText, chan)
  elif firstWord == 'logSearch':
      resultDictionary = logSearch(restOfText)
      sendMsg("Results are located at http://50.116.55.11/kiralogs/results.txt", userName)
  elif firstWord == 'Kirabot,':
  	sendIrcCommand(restOfText + "\n")
  elif firstWord == 'sux' !=-1:
    sendMsg('>:|', chan)
  elif firstWord == "reloadLogs":
    loadLogs()
  elif firstWord == 'Kirahelp':
    sendMsg('Check out https://github.com/DocEon/Kirabot/blob/master/documentation.txt for a list of what I can do.')
  elif firstWord == 'wz':
  	# TODO: if the person is already an op, don't give it to them.
    sendIrcCommand("MODE "+channel +" +o "+ userName + "\n")
  elif firstWord == 'goto':
    sendMsg("MUTE command sent to Kira @ " + channel+ ". \"t(- - t)\"")
    channel = restOfText
    sendMsg("Unmuted in "+ channel+", sir!")
    # TODO: give the bot memory of the channel it was in - some kind of log list would be cool. making the bot log would also be really cool
    # and probably doable - file IO can't be impossible.
    # TODO: move this out into a separate function if it gets any longer.
  elif firstWord == '!shades':
  	sendMsg('( •_•)    ( •_•)>⌐■-■    (⌐■_■)')
  elif firstWord == 'userProperty':
    printUserProperty(userDictionary, restOfText, chan)
  elif firstWord == '!dump':
    logAList(logHelperList)
    sendMsg("Saved the log up to now!")
  elif firstWord == "todaysLog":
    logAList(logHelperList)
    print logCopyDirectory
    sendMsg("Check out http://50.116.55.11/kiralogs/"+time.strftime("%m_%d_%Y")+"_LOG.txt for today's log.", userName)
  else: # try to find a dice roll
    tryRollingDice(message, userName, chan)
  # TODO(yanamal): user preference for 'always sort and display diff result'?

## Message sending


def sendMsg(line, chan=None):
  # send message to irc channel
  global logHelperList
  global botnick
  if not chan:
    chan = channel
  maxlen = 420 # max. length of message to send. Approximately size where it cuts off 
  # (428 in tests, but I suspect it depends on the prefixes like "PRIVMSG ..." etc.)
  explicit_lines = line.split('\n')
  for el in explicit_lines:
    while len(el) > 0:
      cutoff = min(420, len(el))
      msg = el[0:cutoff]
      el = el[cutoff:]
      sendIrcCommand('PRIVMSG '+chan+' :'+msg+' \r\n')
      newLine = "(" + time.strftime("%H:%M:%S") + ") | " + botnick + ": "+ msg
      logHelperList.append(newLine)



## Generic input message handling


def getName(line):
  # assumes format :[name]!blahblah
  return line[1:line.find('!')] 


def getMsg(line):
  # returns the contents of a message, and the channel(or user) it was send to
  # assumes format "PRIVMSG #channel :[message]"
  # or "PRIVMSG user :[message]"
  m = line.split('PRIVMSG ')
  if len(m)>1:
    n = m[1].split(' :')
    msg = n[1]
    chan = n[0]
    if chan[0]!= '#': # for PM, get the sender. Otherwise the bot just starts talking to itself.
      chan = getName(line)
    return (chan, msg)
  else:
    return ("", "")


def getFirstWordAndRest(line):
  # same assumption as getMsg
  # NOTE: this means it assumes that line is a whole irc line, not an arbitrary string.
  # i.e. PRIVMSG etc.
  return getMsg(line)[1].split(None,1)


## Dice logic


def matchDice(word):
  # returns tuple with number and sides of dice to roll, if the word is of the format 1d10.
  # if there's a + sign after the roll, it returns the number after the +; otherwise, the third number in the tuple is 0.
  # otherwise returns (0,0,0)
  shouldIAdd = re.match(r'([0-9]+)d([0-9]+)\+([0-9]+)', word)
  m = re.match(r'([0-9]+)d([0-9]+)', word)
  if shouldIAdd:
  	num = int(shouldIAdd.group(1))
  	sides = int(shouldIAdd.group(2))
  	adder = int(shouldIAdd.group(3))
  	return (num, sides, adder)
  elif m:
    num = int(m.group(1))
    sides = int(m.group(2))
    return (num, sides, 0)
  else:
    return (0,0,0)


def rollDice(num, sides):
  rolls = []
  for i in range(num):
    rolls.append(randrange(sides)+1)
  return rolls


def tryRollingDice(message, user, chan=None, sort=False):
  global userDictionary
  (num, sides, adder) = matchDice(message)
  # check for if addition is neccesary:
  if num > 0:
    dice = rollDice(num, sides)
    # if userDatabase[user]["sort"] != "False"
    if user not in userDictionary or userDictionary[user]["sort"] == "True":
      dice.sort()
      # TODO: put back "SORTED"?
    words = message.split()
    roll = words[0]
    # (KEN: default diff doesn't seem to fit most use cases) 
    # * diff = sides/2+1 # assume diff6 by default (for d10, diff11 for d20, etc.)
    explanation = ' '.join(words[1:])+' ' # the rest of the words, joined back by spaces
    sucString = ''
    if len(words) > 1:
      m = re.match(r'diff([0-9]+)', words[1])
      if m:
        diff = int(m.group(1))
        intSuccesses = calculateSuccesses(dice, diff)
        sucString = successesToString(intSuccesses)
        explanation = ' '.join(words[2:])
    if adder > 0:
    	total = str(sum(dice)+adder)
    	sendMsg((user + ', ' + explanation + roll + ': ' + str(dice) + " = <" + total + "> " + sucString), chan)
    else:
		sendMsg((user + ', ' + explanation + roll + ': ' + str(dice) + " " + sucString), chan)

def calculateSuccesses(dice, diff):
  # A botch is going to return as an int with value -1
  successes = False
  numSuc = 0
  for die in dice:
    if die == 1:
      numSuc -= 1
    elif die >= diff:
      numSuc += 1
      successes = True
  if numSuc < 0 and successes == False:
    return -1
  elif numSuc <= 0:
    return 0
  else:
    return numSuc

def successesToString(numSuc):
  if numSuc == -1:
    return "(BOTCH)"
  elif numSuc == 0:
    return "(Fail)"
  elif numSuc == 1:
    return "(1 success)"
  else:
    return "(" + str(numSuc) + " successes)"


## Kirabot functionality


def kirasearch(searchString, chan):
  # Loops through the quote array searching for a user-input string. When it finds the string,
  # it prints out that quote.
  # TODO: 'searchString[2]' prints out the second incidence of the string.
  quoteIndex = 0
  searchNumber = 1
  matchIndices = []
  while quoteIndex != len(quoteDatabase)-1:
    if (quoteDatabase[quoteIndex].lower()).find(searchString.lower()) != -1:
      if searchNumber == 1:
        # sendMsg("String \"" + searchString + "\" located in quote #" + str(quoteIndex) + ":\n")
        int(quoteIndex)
        matchIndices.append(quoteIndex)
        #sendMsg(quoteDatabase[quoteIndex])
        quoteIndex = quoteIndex + 1
    else:
      quoteIndex = quoteIndex + 1
  if len(matchIndices) == 0:
    sendMsg("No matches found.", chan)
    #works
  else:
  # build match list:
    strMatches = "#"
    first = True
    for i in matchIndices:
      if first:
        strMatches+=str(i)
        first = False
      else:
        strMatches+=(", #" + str(i))
    strMatches+=(".\n")
    sendMsg("Found match(es) in quotes " + strMatches, chan)

def kiraquote(restOfText, chan):
  if restOfText == "":
    quoteIndex = randrange(len(quoteDatabase))
    sendMsg("Quote #" + str(quoteIndex) + ":", chan)
    sendMsg(quoteDatabase[quoteIndex], chan)
  else:
    quoteIndex = int(restOfText) # TODO: handle strange input gracefully (e.g. "Kiraquote 5 please" "Kiraquote Foo")
    sendMsg("Quote #" + str(quoteIndex) + ":", chan)
    sendMsg(quoteDatabase[quoteIndex], chan)


### Persistent user state functionality using JSON

## to check property 'property' for user 'user', use userDictionary['user']['property']
## e.g. userDictionary['Fin']['auto-op'] will return 'True' if Fin is set to auto-op.

## Populates dictionary userDictionary with deserialized information from the json file.
def readUserDictionary():
  f = open('JSONUsers.txt', 'r')
  userDictionary = json.load(f)
  f.close()
  return userDictionary

def changeUserProperty(userDictionary, userToChange, propertyToChange, newValue):
  userDictionary[userToChange][propertyToChange] = newValue
  writeUserDictionaryFile(userDictionary)
  return userDictionary

def writeUserDictionaryFile(userDictionary):  
  f = open('JSONUsers.txt', 'w')
  json.dump(userDictionary, f, indent = 4)
  f.close()
  # this gets called every time someone changes a setting. It generates a new list of all users
  # and prints out that stuff as .json and then saves it as a .txt from which it reads on startup.

#For testing purposes.
def printUserProperty(userDictionary, restOfText, chan):
  commands = restOfText.split()
  userToRead = commands[0]
  propertyToRead = commands[1]
  if userToRead in userDictionary:
    sendMsg(userDictionary[userToRead][propertyToRead], chan)
  else:
    sendMsg("That user doesn't have a profile yet.", chan)

def buildMode(userDictionary):
  print "Welcome to Kirabot. Type connect to use default settings, config if you'd like to change connection settings, alt if you want to use the other server."
  command = ""
  global server, port, channel, botnick, copyLogs, logCopyDirectory
  while command != "connect":
    command = raw_input("Input command:\n")
    if command == "printDictionary":
      print userDictionary
    elif command == "change":
      userToChange = raw_input("Who do you want to change?\n")
      if userToChange not in userDictionary:
        userDictionary = makeNewUser(userDictionary, userToChange)
      propertyToChange = raw_input("What do you want to change?\n")
      newValue = raw_input("What's the new value?\n")
      print "Old value: " + userDictionary[userToChange][propertyToChange]
      changeUserProperty(userDictionary, userToChange, propertyToChange, newValue)
      print "New value: " + userDictionary[userToChange][propertyToChange]
    elif command == "config":
      server = raw_input("What's the new server?")
      port = raw_input("What's the new port?")
      port = int(port)
      channel = raw_input("What channel?")
      botnick = raw_input("What nickname?")
    elif command == "alt":
    	server = "efnet.portlane.se"
    	port = 9999
    elif command == "name":
      botnick = raw_input("What nickname?")
    elif command == "channel":
      channel = raw_input("What channel?")
    elif command == "copyLogs":
      copyLogs = True
      logCopyDirectory = raw_input("Where should logs go? On linode we're looking for /srv/http/kiralogs\n")
      loadLogs()
    elif command == "logSearch":
      stringToFind = raw_input("What string are you looking for?\n")
      resultDictionary = logSearch(stringToFind)
    elif command == "printResults":
      for line in resultList:
        print line
  return userDictionary

def makeNewUser(userDictionary, userToMake):
  userDictionary[userToMake] = {"sort": "True", "nickname": userToMake, "real_name": "default"}
  writeUserDictionaryFile(userDictionary)
  return userDictionary

## Log Stuff

# This function takes a list of lines and writes them to a text file at ./logs with a filename based on the date.
# It first checks to make sure that the log folder exists. 
# After writing the list to the text file, it clears the list and returns the new, empty list. So, proper use should be:
# listToLog = logAList(listToLog)

def logAList(listToLog):
  global logCopyDirectory
  path = os.path.join(os.path.abspath("."), "logs")
  if not os.path.exists(path):
    print "No logs folder detected. Making a new folder for logs at " + path
    os.makedirs(path)
  fileName = time.strftime("%m_%d_%Y") + "_LOG.txt"
  fullName = os.path.join(path, fileName)
  logFile = open(fullName, 'a')
  for i in listToLog:
    logFile.write(i + "\n")
  if copyLogs:
    copyPath = logCopyDirectory
    if not os.path.exists(logCopyDirectory):
      print "No log folder here."
    else:
      fullCopyName = os.path.join(logCopyDirectory, fileName)
      logCopyFile = open(fullCopyName, 'a')
      for i in listToLog:
        logCopyFile.write(i + "\n")
  listToLog = []
  logFile.close()
  return listToLog


### main

def main():
  global channel, botnick
    
  # load data from file(s)
  loadQuotes()

  # start bot
  connectAndJoin()
  inputLoop()

if __name__ == "__main__":
  userDictionary = readUserDictionary()
  userDictionary = buildMode(userDictionary)
  main()
# this means that main() is run only if kirabot.py was called directly rather than imported.
# otherwise, it is treated as a library, essentially.