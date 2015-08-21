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
lastActiveChannel = ""
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
      irc.send('PONG ' + text.split()[1] + '\r\n')
      print "PONGING"
    return callback(text) # actually process the input
  except Exception as e:
    # this prints the error message whenever something throws an exception.
    print str(e) # TODO: self-subscribe users to admin stuff, like getting the error message in IRC?
    # TODO: print line number of exception? stack trace? (sys.exc_info())


def respondToConnectionCommands(text):
  # see if the text contains commands for the bot to respond to in order to complete the connection
  # respond as necessary.
  connected = False
  if text.find('To connect type /QUOTE PONG') != -1:
    msg = 'PONG' + text.split('To connect type /QUOTE PONG')[1] + '\r\n'
    irc.send(msg)
    print msg
  
  if text.find('Welcome') != -1: # Note: for some reason the match fails on the 'EFNet' part of the expected welcome message.
    # leaving it at just 'Welcome'. Nothing can go wrong.
    print "JOINING"
    irc.send("PRIVMSG nickserv :iNOOPE\r\n") #auth
    irc.send("JOIN "+ channel +"\n")
    connected = True
  return connected


def connectAndJoin():
  # connect to irc, then join the channel requested upon seeing welcome message
  # of the format:
  # ":irc.eversible.com 001 yanabot :Welcome to the EFNet Internet Relay Chat Network yanabot""
  
  print "Establishing connection to [%s]" % (server)
  # Connect
  irc.connect((server, port))
  irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :testbot\n")
  irc.send("NICK "+ botnick +"\n")
  
  connected = False
  while not connected:
    connected = tryGettingInput(respondToConnectionCommands)


def inputLoop():
  # An infinite loop waiting for input and processing it.
  while True:
    # TODO: find list index out of bounds error
    tryGettingInput(processInput)


# TODO: wrap irc.send in a helper function that also echoes the output to the console.


### Actual Bot Logic


def processInput(text):
  # process a line of text from the IRC server.
  global channel
  # try to get contents of a message
  # these functions will return emtpy things if it wasn't actually a message to the channel
  firstAndRest = getFirstWordAndRest(text)
  userName = getName(text)
  
  # initialize helper variables for responding to message:
  message = getMsg(text)
  firstWord = ""
  restOfText = ""
  allWords = message.split()
  
  if len(firstAndRest) > 0:  # must have found a message to the channel
    firstWord = firstAndRest[0]
    if len(firstAndRest) > 1: # there is more than one word in the message
      restOfText = firstAndRest[1].strip()
  
  # respond to message as needed:
  # TODO: make generic firstWord/action registration instead?
  # (pros: readability; can create commands dynamically as you go!
  #  con: any actions not triggered by firstWord would still have to be a manual if check.)
  if firstWord == 'hay':
    sendMsg(userName+', hay v:')
  elif firstWord == 'Kirasay':
    sendMsg(restOfText)
  elif firstWord == 'Kiraquote':
    kiraquote(restOfText)
  elif firstWord == 'Kirasearch':
    kirasearch(restOfText)
  elif firstWord == 'Kirabot,':
  	irc.send(restOfText + "\n")
  elif firstWord == 'sux' !=-1:
    sendMsg('>:|')
  elif firstWord == 'jetfuel':
   	sendMsg('Don\'t be silly. Jet fuel can\'t melt steel beams.')
  elif firstWord == 'wz':
  	# TODO: if the person is already an op, don't give it to them.
    irc.send("MODE "+channel +" +o "+ userName + "\n")
  elif firstWord == 'goto':
    sendMsg("MUTE command sent to Kira @ " + channel+ ". \"t(- - t)\"")
    channel = restOfText
    sendMsg("Unmuted in "+ channel+", sir!")
    # TODO: give the bot memory of the channel it was in - some kind of log list would be cool. making the bot log would also be really cool
    # and probably doable - file IO can't be impossible.
    # TODO: move this out into a separate function if it gets any longer.
  elif firstWord == 'sort':
    tryRollingDice(restOfText, userName, True)
  else: # try to find a dice roll
    tryRollingDice(message, userName)
  # TODO: command to always sort a given user's dice from now on.


## Message sending


def sendMsg(line):
  # send message to irc channel
  maxlen = 420 # max. length of message to send. Approximately size where it cuts off 
  # (428 in tests, but I suspect it depends on the prefixes like "PRIVMSG ..." etc.)
  explicit_lines = line.split('\n')
  for el in explicit_lines:
    while len(el) > 0:
      cutoff = min(420, len(el))
      msg = el[0:cutoff]
      el = el[cutoff:]
      irc.send('PRIVMSG '+channel+' :'+msg+' \r\n')


## Generic input message handling


def getName(line):
  # assumes format :[name]!blahblah
  return line[1:line.find('!')] 


def getMsg(line):
  # returns the contents of a message to the channel
  # assumes format "PRIVMSG #channel :[message]"
  
  # So right now, it takes the input after the colon and returns it: i.e. return m[1]
  # what if instead I did m=line.split('PRIVMSG '); that'd make m[1] into "#channel :outputoutput"
  # and then if I were to do lastActiveChannel = m.split()[0];
  # and then just the code as it is, except with lastActiveChannel in the place of channel
  # So. I still need to split it at PRIVMSG. And then I need to make sure that what it returns is what comes after the #channel : part.
  # But I need to get that lastActiveChannel out somehow. :( HOW THO I thought I had it there. 
  m = line.split('PRIVMSG ')
  if len(m)>1:
    n = m[1].split(' :')
    # probably unnecessary, but I'm not sure if it breaks something, so I'm leaving it here.
    lastActiveChannel = n[0] # TODO: pass around channel/person from message
    return n[1]
  else:
    return ""


def getFirstWordAndRest(line):
  # same assumption as getMsg
  # NOTE: this means it assumes that line is a whole irc line, not an arbitrary string.
  # i.e. PRIVMSG etc.
  return getMsg(line).split(None,1)


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


def tryRollingDice(message, user, sort=False):
  (num, sides) = matchDice(message)
  if num > 0:
    dice = rollDice(num, sides)
    if sort:
      dice.sort()
      # TODO: put back "SORTED"?
    words = message.split()
    roll = words[0]
    diff = 5 # assume diff5 by default
    explanation = ' '.join(words[1:]) # the rest of the words, joined back by spaces
    if len(words) > 1:
      maybeDiff = words[1]
      m = re.match(r'diff([0-9]+)', maybeDiff)
      if m:
        diff = int(m.group(1))
        explanation = ' '.join(words[2:]) # don't include diffN in the beginning of the explanation text
    # TODO: use diff to calculate number of successes and add to explanation.
    # right here. diff is already the correct thing.
    sendMsg(user + ', ' + explanation + ' ' + roll + ': ' + str(dice))


## Kirabot functionality


def kirasearch(searchString):
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
    sendMsg("No matches found.")
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
    sendMsg("Found match(es) in quotes " + strMatches)


def kiraquote(restOfText):
  if restOfText == "":
    quoteIndex = randrange(len(quoteDatabase))
    sendMsg("Quote #" + str(quoteIndex) + ":")
    sendMsg(quoteDatabase[quoteIndex])
  else:
    quoteIndex = int(restOfText) # TODO: handle strange input gracefully (e.g. "Kiraquote 5 please" "Kiraquote Foo")
    sendMsg("Quote #" + str(quoteIndex) + ":")
    sendMsg(quoteDatabase[quoteIndex])


### main


def main():
  global channel, botnick
  # process command-line arguments
  # TODO: look into better argument syntax?
  
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