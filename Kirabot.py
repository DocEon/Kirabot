#!/usr/local/bin/python

import socket
import ssl
import time
import re
from random import randrange


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
		  print str(e)
		  continue # don't crash on exception; keep going

      
### Everything else


def processInput(text):
# process a line of text from the IRC server.

  # TODO: replacement: hang out in different while loop, checking that a nick is in a channel; 
  # when it leaves, come in;
  # if it joins (and you are in replacement mode, but in this loop now), leave.
  
  # TODO: if message(text) contains my nickname, "must be a typo."
  # TODO: if message(text) contains 'correct' nickname, "that's totally me"
  
  # TODO: proper-die-roll-mode: if user is registered as wanting proper die rolls, sort, highlight, etc.
  # (register yana*, anybody who asks)
  # ignore/refuse ramc
  
  # try to get contents of a message
  # these functions will return emtpy things if it wasn't actually a message to the channel
  firstAndRest = getFirstWordAndRest(text)
  userName = getName(text)
  
  # initialize helper variables for responding to message:
  firstWord = ""
  restOfText = ""
  sortedRoll = ""
  sloppyCode = ""
  
  if len(firstAndRest) > 0:  # must have found a message to the channel
    firstWord = firstAndRest[0]
    
    if len(firstAndRest) > 1: # there is more than one word in the message
      restOfText = firstAndRest[1].strip()
      sloppyCode = restOfText
      sortedRoll = sloppyCode.split()[0]

  # respond to message as needed:
  if firstWord == 'hay':
    sendMsg(userName+', hay v:')

  elif firstWord == 'Kirabot,':
  	irc.send(restOfText + "\n")
  elif firstWord == 'sux' !=-1:
    sendMsg('Ken, '+userName+' sucks the cocks!')
  elif firstWord == 'jetfuel':
   	sendMsg('Don\'t be silly. Jet fuel can\'t melt steel beams.')
  elif firstWord == 'wz':
  	irc.send("MODE "+channel +" +o "+ userName + "\n")
  elif firstWord == 'goto':
    global channel
    sendMsg("I was in " +channel+ ", Fin.")
    channel = restOfText
    sendMsg("... but now I'm here in " +channel+ ", Fin. I liked it better over there.")
    #todo - give the bot memory of the channel it was in - some kind of log list would be cool. making the bot log would also be really cool
    #and probably doable - file IO can't be impossible.
  elif firstWord == 'sort':
      (num, sides) = matchDice(sortedRoll)
      if num > 0:
        dice = rollDice(num, sides)
        dice.sort()
        # TODO: functions for 'classic', 'proper' modes of display?
        sumStr = str(sum(dice))
        redux = sortedRoll  # the text to display/repeat with the dice roll response
        if restOfText != '':
          redux = restOfText
        msg = 'SORTED: '+ userName+', '+redux+': '+sumStr+' ['+sortedRoll+'='
        first = True
        for die in dice:
          if not first:
            msg += ','
          first = False
          msg += str(die)
        msg += ']'
        sendMsg(msg)
  else: # try to find a die roll
      (num, sides) = matchDice(firstWord)
      if num > 0:
        dice = rollDice(num, sides)
        # TODO: functions for 'classic', 'proper' modes of display?
        sumStr = str(sum(dice))
        redux = firstWord  # the text to display/repeat with the dice roll response
        if restOfText != '':
          redux = restOfText
        msg = userName+', '+redux+': '+sumStr+' ['+firstWord+'='
        first = True
        for die in dice:
          if not first:
            msg += ','
          first = False
          msg += str(die)
        msg += ']'
        sendMsg(msg)


def sendMsg(line):
  # send message to irc channel
  irc.send('PRIVMSG '+channel+' :'+line+' \r\n')

  
def getName(line):
  # assumes format :[name]!blahblah
  return line[1:line.find('!')] 

  
def getMsg(line):
  # returns the contents of a message to the channel
  # assumes format "PRIVMSG #channel :[message]"
  # TODO: account for not finding the substring
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
    lastActiveChannel = n[0]
    return n[1]
  else:
    return ""
  
# TODO: get nth word?
  
  
def getFirstWord(line):
  # returns the first word of a message to the channel.
  # same assumption as getMsg
  msg = getMsg(line)
  return msg.split()[0]
  
  
def getFirstWordAndRest(line):
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