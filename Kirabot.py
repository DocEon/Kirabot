#!/usr/local/bin/python


import sys
import ssl
import socket
import time
import re
from random import randrange


### global variables (with defaults that will likely be overridden)


quoteDatabase = [""]
server = "irc.arcti.ca"
port = 6697
password = ""
channel = "#Mage"
botnick = "Kirabot"
irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc = ssl.wrap_socket(irc_C)


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


### IRC stuff


def tryGettingInput(callback):
  # try reading a line of IRC input.
  # callback is a function that takes one argument - the raw line of input - and processes it as desired.
  try:
    text=irc.recv(2040) # wait for the next bit of input from the IRC server. Limit to 2040 characters.
    # (the rest would stay in the buffer and get processed afterwards, I think)
    if text.strip() != '':
      print text
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
  while True:
    tryGettingInput(processInput)


def sendIrcCommand(command):
  # send IRC command and also print it to the console
  irc.send(command)
  print ' > '+command


### Actual Bot Logic

peopleToSortFor = set()
manualMode = set(['Ramc'])# people to never sort/count for


def processInput(text):
  # process a line of text from the IRC server.
  global channel, peopleToSortFor
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
    peopleToSortFor.add(userName)
    sendMsg('always sorting rolls for '+userName)
  elif message.strip() == 'manual-mode':
    manualMode.add(userName)
    sendMsg('manual mode enabled for '+userName)
  elif message.strip() == 'non-manual-mode':
    manualMode.remove(userName)
    sendMsg('manual mode disabled for '+userName)
  elif firstWord == 'Kirasay':
    sendMsg(restOfText, chan)
  elif firstWord == 'Kiraquote':
    kiraquote(restOfText, chan)
  elif firstWord == 'Kirasearch':
    kirasearch(restOfText, chan)
  elif firstWord == 'Kirabot,':
  	sendIrcCommand(restOfText + "\n")
  elif firstWord == 'sux' !=-1:
    sendMsg('>:|', chan)
  elif firstWord == 'jetfuel':
   	sendMsg('Don\'t be silly. Jet fuel can\'t melt steel beams.')
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
  elif firstWord == 'sort':
    tryRollingDice(restOfText, userName, chan, True)
  else: # try to find a dice roll
    tryRollingDice(message, userName, chan)
  # TODO(yanamal): user preference for 'always sort and display diff result'?

## Message sending


def sendMsg(line, chan=None):
  # send message to irc channel
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
  # returns tuple with number and sides of dice to roll, if the word is of the format 1d10
  # otherwise returns (0,0)
  m = re.match(r'([0-9]+)d([0-9]+)', word)
  if m:
    num = int(m.group(1))
    sides = int(m.group(2))
    return (num, sides)
  else:
    return (0,0)


def rollDice(num, sides):
  rolls = []
  for i in range(num):
    rolls.append(randrange(sides)+1)
  return rolls


def tryRollingDice(message, user, chan=None, sort=False):
  global peopleToSortFor, manualMode
  (num, sides) = matchDice(message)
  if num > 0:
    dice = rollDice(num, sides)
    if user not in manualMode and (sort or (user in peopleToSortFor)):
      dice.sort()
      # TODO: put back "SORTED"?
    words = message.split()
    roll = words[0]
    diff = sides/2+1 # assume diff6 by default (for d10, diff11 for d20, etc.)
    explanation = ' '.join(words[1:])+' ' # the rest of the words, joined back by spaces
    if len(words) > 1:
      maybeDiff = words[1]
      m = re.match(r'diff([0-9]+)', maybeDiff)
      if m:
        diff = int(m.group(1))
        explanation = ' '.join(words[2:]) # don't include diffN in the beginning of the explanation text
    # TODO: use diff to calculate number of successes and add to explanation.
    # right here. diff is already the correct thing.
    successes = False
    numSuc = 0
    for die in dice:
      if die == 1:
        numSuc -= 1
      elif die >= diff:
        numSuc += 1
        successes = True
    sucString = ': BOTCH!!'
    if numSuc >= 0 or (successes):
      sucString = ': '+str(max(numSuc, 0))+' successes'
    if user in manualMode: # ramc mode - no successes
      sucString = ''
    sendMsg(user + ', ' + explanation + roll + sucString +': ' + str(dice), chan)


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


### main


def main():
  global channel, botnick
  # process command-line arguments
  # TODO(yanamal): look into better argument syntax?
  
  if len(sys.argv) > 1:
    channel = '#' + sys.argv[1]
  else:
    channel = raw_input('What channel would you like to join?\n')
  
  if len(sys.argv) > 2:
    botnick = sys.argv[2]
  else:
    botnick = raw_input('And what nickname?\n')
    
  # load data from file(s)
  loadQuotes()
  
  # start bot
  connectAndJoin()
  inputLoop()


if __name__ == "__main__":
  main()
# this means that main() is run only if kirabot.py was called directly rather than imported.
# otherwise, it is treated as a library, essentially.