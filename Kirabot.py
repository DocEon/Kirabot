#!/usr/local/bin/python

import socket
import ssl # TODO: try without ssl
import time
import re
from random import randrange

# TODO: command line argument for default testing nick/channel

# fileinput.filelineno()
quoteDatabase = [""]
f = open("quotes.txt", 'r')
currentIndex = 0
for line in f:
    if line.strip() == "":
      if quoteDatabase[len(quoteDatabase)-1] != "":
        quoteDatabase.append("")
    else:
      quoteDatabase[len(quoteDatabase)-1] += "\n" + line

### IRC stuff
# irc-related constants
server = "irc.arcti.ca"
port = 6697
channel = raw_input('What channel would you like to join?\n')
botnick = raw_input('And what nickname?\n')
password = ""
lastActiveChannel = ""
# make stuff that lets you talk to IRC
irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
irc = ssl.wrap_socket(irc_C)
  
def connectAndLoop():
  # Connect to the irc channel and go into an infinite loop waiting for input and processing it.
  # TODO: separate connect and loop; switch on seeing "welcome..."" message
  # ":irc.eversible.com 001 yanabot :Welcome to the EFNet Internet Relay Chat Network yanabot"
  # irc.setblocking(False)  # sets socket as non-blocking (other things can use it, I guess) but breaks... something so screw it.
  print "Establishing connection to [%s]" % (server)
  # Connect
  irc.connect((server, port))
  # irc.send("PASS %s\n" % (password))  # not bothering with passwords
  irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :testbot\n")
  irc.send("NICK "+ botnick +"\n")
  irc.send("PRIVMSG nickserv :iNOOPE\r\n")    #auth
  irc.send("JOIN "+ channel +"\n")

  while True:  # TODO: have a boolean variable 
    #time.sleep(2)  # this would wait 2 seconds before waiting for the next input each time, but it's a bit silly to do that. 

    try:
      text=irc.recv(2040) # wait for the next bit of input from the IRC server. Limit to 2040 characters.
      # (the rest would stay in the buffer and get processed afterwards, I think)
      if text.strip() != '':
        print text
      
      if text.find('To connect type /QUOTE PONG') != -1: # if there is a "PING" anywhere in the text
        msg = '/QUOTE PONG' + text.split('To connect type /QUOTE PONG') [1] + '\r\n'
        msg = 'PONG' + text.split('To connect type /QUOTE PONG')[1] + '\r\n'
        irc.send(msg)
        print "PONGING"
        print msg
        irc.send("JOIN "+ channel +"\n") # TODO: do all the joining and stuff after pong connection is established
      
      # Prevent Timeout - this is how the IRC servers know to kick you off for inactivity, when your client doesn't PONG to a PING.
      if text.find('PING') != -1: # if there is a "PING" anywhere in the text
        irc.send('PONG ' + text.split()[1] + '\r\n')
        print "PONGING"
      
      processInput(text) # actually process the input

    except Exception as e:
      # this is just in case something within the 'try' block throws an exception.
      # not sure what would do that. might be unnecessary.
		  print str(e) # TODO: is this actually the error message? self-subscribe users to admin stuff?
		  continue # don't crash on exception; keep going

      
### Everything else


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
  
  sortedRoll = ""
  # This variable preserves restOfText from having to go through the split function, which is important because we use it later.
  preserver = "" # TODO: ??
  
  if len(firstAndRest) > 0:  # must have found a message to the channel
    firstWord = firstAndRest[0]
    # TODO: move to sorted logic
    if len(firstAndRest) > 1: # there is more than one word in the message
      restOfText = firstAndRest[1].strip()
      preserver = restOfText 
      sortedRoll = preserver.split()[0]


  # respond to message as needed:
  if firstWord == 'hay':
    sendMsg(userName+', hay v:')
  elif firstWord == 'Kirasay':
    sendMsg(restOfText)
  elif firstWord == 'Kiraquote':
    if restOfText == "":
      quoteIndex = randrange(len(quoteDatabase))
      sendMsg("Quote #" + str(quoteIndex) + ":")
      sendMsg(quoteDatabase[quoteIndex])
    else:
      quoteIndex = int(restOfText)
      sendMsg("Quote #" + str(quoteIndex) + ":")
      sendMsg(quoteDatabase[quoteIndex])
  elif firstWord == 'Kirasearch':
    # Loops through the quote array searching for a user-input string. When it finds the string,
    # it prints out that quote.
    # TODO: 'searchString[2]' prints out the second incidence of the  string.
    quoteIndex = 0
    searchString = restOfText
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


  elif firstWord == 'Kirabot,':
  	irc.send(restOfText + "\n")
  elif firstWord == 'sux' !=-1:
    sendMsg('>:|')
  elif firstWord == 'jetfuel':
   	sendMsg('Don\'t be silly. Jet fuel can\'t melt steel beams.')
  elif firstWord == 'wz':
  	# TODO if the person is already an op, don't give it to them.
    irc.send("MODE "+channel +" +o "+ userName + "\n")
  elif firstWord == 'goto':
    sendMsg("MUTE command sent to Kira @ " + channel+ ". \"t(- - t)\"")
    channel = restOfText
    sendMsg("Unmuted in "+ channel+", sir!")
    #todo - give the bot memory of the channel it was in - some kind of log list would be cool. making the bot log would also be really cool
    #and probably doable - file IO can't be impossible.
  elif firstWord == 'sort':
    tryRollingDice(restOfText, userName, True)
  else: # try to find a dice roll
    tryRollingDice(message, userName)

def tryRollingDice(message, user, sort=False):
  (num, sides) = matchDice(message)
  if num > 0:
    dice = rollDice(num, sides)
    if sort:
      dice.sort()
      # TODO: put back "SORTED"?
    words = message.split()
    roll = words[0]
    explanation = ' '.join(words[1:]) # the rest of the words, joined back by spaces
    sendMsg(user + ', ' + explanation + ' ' + roll + ': ' + str(dice))

# TODO: wrap irc.send in a helper function that also echoes it to the console.

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
  
# TODO: get nth word?
  
  
def getFirstWord(line):
  # returns the first word of a message to the channel.
  # same assumption as getMsg
  # TODO: why did I make this? I'm not using it.
  msg = getMsg(line)
  return msg.split()[0]
  
  
def getFirstWordAndRest(line):
  # same assumption as getMsg
  # NOTE: this means it assumes that line is a whole irc line, not an arbitrary string.
  # i.e. PRIVMSG etc.
  return getMsg(line).split(None,1)
  
  
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


# should really be main
connectAndLoop()