#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import ssl
import socket
import time
import re
from random import randrange

gameOver = False

def drawBoardWhite(board):
	print "   ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗"
	print " 8 ║ "+board["A8"]+" ║ "+board["B8"]+" ║ "+board["C8"]+" ║ "+board["D8"]+" ║ "+board["E8"]+" ║ "+board["F8"]+" ║ "+board["G8"]+" ║ "+board["H8"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 7 ║ "+board["A7"]+" ║ "+board["B7"]+" ║ "+board["C7"]+" ║ "+board["D7"]+" ║ "+board["E7"]+" ║ "+board["F7"]+" ║ "+board["G7"]+" ║ "+board["H7"]+" ║        Game time:" 
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 6 ║ "+board["A6"]+" ║ "+board["B6"]+" ║ "+board["C6"]+" ║ "+board["D6"]+" ║ "+board["E6"]+" ║ "+board["F6"]+" ║ "+board["G6"]+" ║ "+board["H6"]+" ║           %d" % board["Game Time"]
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 5 ║ "+board["A5"]+" ║ "+board["B5"]+" ║ "+board["C5"]+" ║ "+board["D5"]+" ║ "+board["E5"]+" ║ "+board["F5"]+" ║ "+board["G5"]+" ║ "+board["H5"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 4 ║ "+board["A4"]+" ║ "+board["B4"]+" ║ "+board["C4"]+" ║ "+board["D4"]+" ║ "+board["E4"]+" ║ "+board["F4"]+" ║ "+board["G4"]+" ║ "+board["H4"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 3 ║ "+board["A3"]+" ║ "+board["B3"]+" ║ "+board["C3"]+" ║ "+board["D3"]+" ║ "+board["E3"]+" ║ "+board["F3"]+" ║ "+board["G3"]+" ║ "+board["H3"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 2 ║ "+board["A2"]+" ║ "+board["B2"]+" ║ "+board["C2"]+" ║ "+board["D2"]+" ║ "+board["E2"]+" ║ "+board["F2"]+" ║ "+board["G2"]+" ║ "+board["H2"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 1 ║ "+board["A1"]+" ║ "+board["B1"]+" ║ "+board["C1"]+" ║ "+board["D1"]+" ║ "+board["E1"]+" ║ "+board["F1"]+" ║ "+board["G1"]+" ║ "+board["H1"]+" ║"
	print "   ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝"
	print "     A   B   C   D   E   F   G   H"

def drawBoardBlack(board):
	print "   ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗"
	print " 1 ║ "+board["H1"]+" ║ "+board["G1"]+" ║ "+board["F1"]+" ║ "+board["E1"]+" ║ "+board["D1"]+" ║ "+board["C1"]+" ║ "+board["B1"]+" ║ "+board["A1"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 2 ║ "+board["H2"]+" ║ "+board["G2"]+" ║ "+board["F2"]+" ║ "+board["E2"]+" ║ "+board["D2"]+" ║ "+board["C2"]+" ║ "+board["B2"]+" ║ "+board["A2"]+" ║        Game time:"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 3 ║ "+board["H3"]+" ║ "+board["G3"]+" ║ "+board["F3"]+" ║ "+board["E3"]+" ║ "+board["D3"]+" ║ "+board["C3"]+" ║ "+board["B3"]+" ║ "+board["A3"]+" ║           %d" % board["Game Time"]
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 4 ║ "+board["H4"]+" ║ "+board["G4"]+" ║ "+board["F4"]+" ║ "+board["E4"]+" ║ "+board["D4"]+" ║ "+board["C4"]+" ║ "+board["B4"]+" ║ "+board["A4"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 5 ║ "+board["H5"]+" ║ "+board["G5"]+" ║ "+board["F5"]+" ║ "+board["E5"]+" ║ "+board["D5"]+" ║ "+board["C5"]+" ║ "+board["B5"]+" ║ "+board["A5"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 6 ║ "+board["H6"]+" ║ "+board["G6"]+" ║ "+board["F6"]+" ║ "+board["E6"]+" ║ "+board["D6"]+" ║ "+board["C6"]+" ║ "+board["B6"]+" ║ "+board["A6"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 7 ║ "+board["H7"]+" ║ "+board["G7"]+" ║ "+board["F7"]+" ║ "+board["E7"]+" ║ "+board["D7"]+" ║ "+board["C7"]+" ║ "+board["B7"]+" ║ "+board["A7"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 8 ║ "+board["H8"]+" ║ "+board["G8"]+" ║ "+board["F8"]+" ║ "+board["E8"]+" ║ "+board["D8"]+" ║ "+board["C8"]+" ║ "+board["B8"]+" ║ "+board["A8"]+" ║"
	print "   ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝"
	print "     H   G   F   E   D   C   B   A"
#todo: put in Kirabot. Port Kirabot to Slack.
def newBoard():
	# Initializes the arrays with starting positions proper. Not in use yet because I don't know how to share arrays properly, but this should start a brand new game if necessary.
	board ={"A1":"r", "A2":"p", "A3":" ", "A4":" ", "A5":" ", "A6":" ", "A7":"P", "A8":"R", \
	"B1":"n", "B2":"p", "B3":" ", "B4":" ", "B5":" ", "B6":" ", "B7":"P", "B8":"N",\
	"C1":"b", "C2":"p", "C3":" ", "C4":" ", "C5":" ", "C6":" ", "C7":"P", "C8":"B",\
	"D1":"q", "D2":"p", "D3":" ", "D4":" ", "D5":" ", "D6":" ", "D7":"P", "D8":"Q",\
	"E1":"k", "E2":"p", "E3":" ", "E4":" ", "E5":" ", "E6":" ", "E7":"P", "E8":"K",\
	"F1":"b", "F2":"p", "F3":" ", "F4":" ", "F5":" ", "F6":" ", "F7":"P", "F8":"B",\
	"G1":"n", "G2":"p", "G3":" ", "G4":" ", "G5":" ", "G6":" ", "G7":"P", "G8":"N",\
	"H1":"r", "H2":"p", "H3":" ", "H4":" ", "H5":" ", "H6":" ", "H7":"P", "H8":"R",\
	"blackTime":"", "whiteTime":"","Game Time":0, "stowage":"", "Turn Number":1, "oldTime":0}
	gameOver = False
	return board

def main():
	print u'\u2654'
	print "Welcome to Chessbot. Say the piece you want to move and then where you want it to go to send a command - e.g. e2 e4. Or you can _exit_ or _takeback_."
	board = newBoard()
	drawBoardWhite(board)
	while gameOver == False:
		# take moves
		moveList =[]
#white's turn
		if board["Turn Number"]%2==1:
			board["oldTime"] = time.time()
			print("Turn %d." % board["Turn Number"])
			nextMove = raw_input("White to move.\n")
			if nextMove == "exit":
				break
			elif nextMove == "takeback":
				board["Turn Number"] -= 1
				board[oldPosition] = board[newPosition]
				board[newPosition] = board["stowage"]
				print "Move taken back."
				drawBoardBlack(board)
			else:
				nextMove = nextMove.upper()
				oldPosition = nextMove[0]+nextMove[1]
				newPosition = nextMove[3]+nextMove[4]
				if isLegal(oldPosition, newPosition, board):
					board = resolveMove(oldPosition, newPosition, board)
					moveList.append(nextMove)
					drawBoardBlack(board)
				else:
					print "Move is illegal. Try again."
#black's turn
		else:
			print("Turn %d." % board["Turn Number"])
			nextMove = raw_input("Black to move.\n")
			board["oldTime"] = time.time()
			if nextMove == "exit":
				break
			elif nextMove == "takeback":
				board["Turn Number"] -= 1
				board[oldPosition] = board[newPosition]
				board[newPosition] = board["stowage"]
				print "Move taken back."
				drawBoardWhite(board)
			else:
				nextMove = nextMove.upper()
				oldPosition = nextMove[0]+nextMove[1]
				newPosition = nextMove[3]+nextMove[4]
				if isLegal(oldPosition, newPosition, board):
					board = resolveMove(oldPosition, newPosition, board)
					moveList.append(nextMove)
					drawBoardWhite(board)
				else:
					"Move is illegal. Try again."


def resolveMove(oldPosition, newPosition, board):
	if board[newPosition] != " ":
		# If space is occupied...
		if board[oldPosition].islower():
			if board[newPosition].islower():
				print "Your "+board[newPosition] + " is already at that square. Try again."
			else:
				print board[oldPosition]+" takes "+board[newPosition]
				board["stowage"]=board[newPosition]
				board[newPosition]=board[oldPosition]
				board[oldPosition]=" "
				board["Game Time"]=board["Game Time"]+(time.time()-board["oldTime"])
				board["Turn Number"] += 1
		elif board[oldPosition].isupper():
			if board[newPosition].isupper():
				print "Your "+board[newPosition] + " is already at that square. Try again."
			else:
				print board[oldPosition]+" takes "+board[newPosition]
				board["stowage"]=board[newPosition]
				board[newPosition]=board[oldPosition]
				board[oldPosition]=" "
				board["Game Time"]=board["Game Time"]+(time.time()-board["oldTime"])
				board["Turn Number"] += 1
	else:
		print("Piece at " +  oldPosition + " moves to " + newPosition + ".")
		board["stowage"]=board[newPosition]
		board[newPosition]=board[oldPosition]
		board[oldPosition]=" "
		board["Game Time"]=board["Game Time"]+(time.time()-board["oldTime"])
		board["Turn Number"]+= 1
	if board[newPosition] == "p":
		if newPosition[1] == 8:
			promoteQuery = raw_input("Promote to q or n? Case sensitive.")
			if promoteQuery == "queen":
				board[newPosition]="q"
			elif promoteQuery =="knight":
				board[newPosition]="n"
			else:
				print "Whatever, you get a q."
				board[newPosition]="q"
	elif board[newPosition] == "P":
		if newPosition[1]==1:
			promoteQuery = raw_input("Promote to Q or N? Case sensitive.")
			if promoteQuery =="Q":
				board[newPosition]="Q"
			elif promoteQuery == "Q":
				board[newPosition]="N"
			else:
				print "Whatever, you get a Q."
				board[newPosition]="Q"

	return board

def whoseTurnIsIt(board):
	# Takes a board as an argument and returns a string, either "white" or "black," depending on whose turn it is.
	if board["Turn Number"]%2==1:
		return "white"
	else:
		return "black"

def isLegal(oldPosition, newPosition, board):
	color = whoseTurnIsIt(board)
	if color == "white":
		if board[oldPosition].isupper():
			print "You can't move black's pieces."
			return False
	elif color == "black":
		if board[oldPosition].islower():
			print "You can't move white's pieces."
			return False
	elif board[oldPosition] == " ":
		print "There's no piece here."
		return False
	return True

main()