#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import ssl
import socket
import time
import re
from random import randrange

#todo: put in Kirabot. Port Kirabot to Slack.
reload(sys)
sys.setdefaultencoding("utf-8")
whitePieces = ["k","q","r","b","n","p"]
blackPieces = ["K","Q","R","B","N","P"]

whiteWindowSet = {\
"K":u'\u265A', "Q":u'\u265B', "R":u'\u265C', "B":u'\u265D', "N":u'\u265E', "P":u'\u265F', \
"k":u'\u2654', "q":u'\u2655', "r":u'\u2656', "b":u'\u2657', "n":u'\u2658', "p":u'\u2659' \
}
blackWindowSet = {\
"k":u'\u265A', "q":u'\u265B', "r":u'\u265C', "b":u'\u265D', "n":u'\u265E', "p":u'\u265F', \
"K":u'\u2654', "Q":u'\u2655', "R":u'\u2656', "B":u'\u2657', "N":u'\u2658', "P":u'\u2659' \
}
# Prints out the board from the perspective of White
def drawBoardWhite(board):
	if board["tileSet"] == "blackwindow":
		for key in board:
			if key != "moveList" and board[key] in blackWindowSet:
				board[key] = blackWindowSet[board[key]]
	elif board["tileSet"] == "whitewindow":
		for key in board:
			if key != "moveList" and board[key] in whiteWindowSet:
				board[key] = whiteWindowSet[board[key]]
	# wat. this is actually changing the real board. Maybe I SHOULD output this as a 2D array whose values are stored in a dict.
	print "   ╔═══╦═╦═╦═══╦═╦═╦═══╦═╦═╦═══╦═╦═╗"
	print " 8 ║ "+board["A8"]+" ╠ "+board["B8"]+" ╣ "+board["C8"]+" ╠ "+board["D8"]+" ╣ "+board["E8"]+" ╠ "+board["F8"]+" ╣ "+board["G8"]+" ╠ "+board["H8"]+" ╣     " + board["capturedWhitePieces"]
	print "   ╠═╦═╬═╩═╬═══╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╣"
	print " 7 ╠ "+board["A7"]+" ╣ "+board["B7"]+" ╠ "+board["C7"]+" ╣ "+board["D7"]+" ╠ "+board["E7"]+" ╣ "+board["F7"]+" ╠ "+board["G7"]+" ╣ "+board["H7"]+" ║"
	print "   ╠═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╣"
	print " 6 ║ "+board["A6"]+" ╠ "+board["B6"]+" ╣ "+board["C6"]+" ╠ "+board["D6"]+" ╣ "+board["E6"]+" ╠ "+board["F6"]+" ╣ "+board["G6"]+" ╠ "+board["H6"]+" ╣"
	print "   ╠═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╣"
	print " 5 ╠ "+board["A5"]+" ╣ "+board["B5"]+" ╠ "+board["C5"]+" ╣ "+board["D5"]+" ╠ "+board["E5"]+" ╣ "+board["F5"]+" ╠ "+board["G5"]+" ╣ "+board["H5"]+" ║"
	print "   ╠═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╣"
	print " 4 ║ "+board["A4"]+" ╠ "+board["B4"]+" ╣ "+board["C4"]+" ╠ "+board["D4"]+" ╣ "+board["E4"]+" ╠ "+board["F4"]+" ╣ "+board["G4"]+" ╠ "+board["H4"]+" ╣"
	print "   ╠═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╣"
	print " 3 ╠ "+board["A3"]+" ╣ "+board["B3"]+" ╠ "+board["C3"]+" ╣ "+board["D3"]+" ╠ "+board["E3"]+" ╣ "+board["F3"]+" ╠ "+board["G3"]+" ╣ "+board["H3"]+" ║"
	print "   ╠═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╣"
	print " 2 ║ "+board["A2"]+" ╠ "+board["B2"]+" ╣ "+board["C2"]+" ╠ "+board["D2"]+" ╣ "+board["E2"]+" ╠ "+board["F2"]+" ╣ "+board["G2"]+" ╠ "+board["H2"]+" ╣"
	print "   ╠═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╬═╦═╬═╩═╣"
	print " 1 ╠ "+board["A1"]+" ╣ "+board["B1"]+" ╠ "+board["C1"]+" ╣ "+board["D1"]+" ╠ "+board["E1"]+" ╣ "+board["F1"]+" ╠ "+board["G1"]+" ╣ "+board["H1"]+" ║     " + board["capturedBlackPieces"]
	print "   ╚═╩═╩═══╩═╩═╩═══╩═╩═╩═══╩═╩═╩═══╝"
	print "     A   B   C   D   E   F   G   H"

# Prints out the board from the perspective of Black.
def drawBoardBlack(board):
	print "   ╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗"
	print " 1 ║ "+board["H1"]+" ║ "+board["G1"]+" ║ "+board["F1"]+" ║ "+board["E1"]+" ║ "+board["D1"]+" ║ "+board["C1"]+" ║ "+board["B1"]+" ║ "+board["A1"]+" ║    " + board["capturedBlackPieces"]
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 2 ║ "+board["H2"]+" ║ "+board["G2"]+" ║ "+board["F2"]+" ║ "+board["E2"]+" ║ "+board["D2"]+" ║ "+board["C2"]+" ║ "+board["B2"]+" ║ "+board["A2"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 3 ║ "+board["H3"]+" ║ "+board["G3"]+" ║ "+board["F3"]+" ║ "+board["E3"]+" ║ "+board["D3"]+" ║ "+board["C3"]+" ║ "+board["B3"]+" ║ "+board["A3"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 4 ║ "+board["H4"]+" ║ "+board["G4"]+" ║ "+board["F4"]+" ║ "+board["E4"]+" ║ "+board["D4"]+" ║ "+board["C4"]+" ║ "+board["B4"]+" ║ "+board["A4"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 5 ║ "+board["H5"]+" ║ "+board["G5"]+" ║ "+board["F5"]+" ║ "+board["E5"]+" ║ "+board["D5"]+" ║ "+board["C5"]+" ║ "+board["B5"]+" ║ "+board["A5"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 6 ║ "+board["H6"]+" ║ "+board["G6"]+" ║ "+board["F6"]+" ║ "+board["E6"]+" ║ "+board["D6"]+" ║ "+board["C6"]+" ║ "+board["B6"]+" ║ "+board["A6"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 7 ║ "+board["H7"]+" ║ "+board["G7"]+" ║ "+board["F7"]+" ║ "+board["E7"]+" ║ "+board["D7"]+" ║ "+board["C7"]+" ║ "+board["B7"]+" ║ "+board["A7"]+" ║"
	print "   ╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print " 8 ║ "+board["H8"]+" ║ "+board["G8"]+" ║ "+board["F8"]+" ║ "+board["E8"]+" ║ "+board["D8"]+" ║ "+board["C8"]+" ║ "+board["B8"]+" ║ "+board["A8"]+" ║    " + board["capturedWhitePieces"]
	print "   ╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝"
	print "     H   G   F   E   D   C   B   A"


def newBoard():
	# Initializes dictionary board, which contains position and other game information.
	board ={\
	"A1":"r", "A2":"p", "A3":" ", "A4":" ", "A5":" ", "A6":" ", "A7":"P", "A8":"R", \
	"B1":"n", "B2":"p", "B3":" ", "B4":" ", "B5":" ", "B6":" ", "B7":"P", "B8":"N",\
	"C1":"b", "C2":"p", "C3":" ", "C4":" ", "C5":" ", "C6":" ", "C7":"P", "C8":"B",\
	"D1":"q", "D2":"p", "D3":" ", "D4":" ", "D5":" ", "D6":" ", "D7":"P", "D8":"Q",\
	"E1":"k", "E2":"p", "E3":" ", "E4":" ", "E5":" ", "E6":" ", "E7":"P", "E8":"K",\
	"F1":"b", "F2":"p", "F3":" ", "F4":" ", "F5":" ", "F6":" ", "F7":"P", "F8":"B",\
	"G1":"n", "G2":"p", "G3":" ", "G4":" ", "G5":" ", "G6":" ", "G7":"P", "G8":"N",\
	"H1":"r", "H2":"p", "H3":" ", "H4":" ", "H5":" ", "H6":" ", "H7":"P", "H8":"R",\
	"blackTime":"", "whiteTime":"","gameTime":0, "stowage":"", "turnNumber":1, "oldTime":0, \
	"capturedBlackPieces":"", "capturedWhitePieces":"", "moveList":[], "tileSet":"letters", \
	"gameOver":"False"}
	return board


def main():
	print "Welcome to Chessbot. Say the piece you want to move and then where you want it to go to send a command - e.g. e2 e4. Or you can _exit_ or _takeback_.\n"
	board = newBoard()
	board["tileSet"] = raw_input("Which tileset would you like? letters, blackwindow, or whitewindow?")
	drawBoardWhite(board)
	while board["gameOver"]== "False":
		# take moves
#white's turn
		if board["turnNumber"]%2==1:
			board["oldTime"] = time.time()
			print("Turn %d." % board["turnNumber"])
			nextMove = raw_input("White to move.\n")
			nextMove = nextMove.upper()
			if nextMove == "EXIT":
				break
			elif nextMove == "TAKEBACK":
				board["turnNumber"] -= 1
				board[oldPosition] = board[newPosition]
				board[newPosition] = board["stowage"]
				print "Move taken back."
				drawBoardBlack(board)
			elif nextMove == "MOVELIST":
				print board["moveList"]
			#Checks if move is properly formatted.
			elif (nextMove[4].isdigit() and nextMove[1].isdigit() and ord(nextMove[0]) >= 65) and (ord(nextMove[0]) <= 72) and (int(nextMove[1]) >=1) and (int(nextMove[1]) <= 8) and (nextMove[2] == " ") and (ord(nextMove[3]) >= 65) and (ord(nextMove[3]) <= 72) and (int(nextMove[4]) >=1) and (int(nextMove[4]) <= 8):
				oldPosition = nextMove[0]+nextMove[1]
				newPosition = nextMove[3]+nextMove[4]
				if isLegal(oldPosition, newPosition, board):
					board = resolveMove(oldPosition, newPosition, board)
					board["moveList"].append(nextMove)
					drawBoardBlack(board)
				else:
					print "Move is illegal. Try again."
			else:
				print "Not a valid chess move. Format is e2 e4; commands are movelist, takeback, exit."

#black's turn

		else:
			print("Turn %d." % board["turnNumber"])
			nextMove = raw_input("Black to move.\n")
			board["oldTime"] = time.time()
			nextMove = nextMove.upper()
			if nextMove == "EXIT":
				break
			elif nextMove == "TAKEBACK":
				board["turnNumber"] -= 1
				board[oldPosition] = board[newPosition]
				board[newPosition] = board["stowage"]
				if board["stowage"] in board["capturedBlackPieces"]:
					board["capturedBlackPieces"] -= board["stowage"]
				print "Move taken back."
				drawBoardWhite(board)
			elif nextMove == "MOVELIST":
				print board["moveList"]
			#checks if move is properly formatted. This is hideous, but it works. 
			elif (nextMove[4].isdigit() and nextMove[1].isdigit() and ord(nextMove[0]) >= 65) and (ord(nextMove[0]) <= 72) and (int(nextMove[1]) >=1) and (int(nextMove[1]) <= 8) and (nextMove[2] == " ") and (ord(nextMove[3]) >= 65) and (ord(nextMove[3]) <= 72) and (int(nextMove[4]) >=1) and (int(nextMove[4]) <= 8):
				oldPosition = nextMove[0]+nextMove[1]
				newPosition = nextMove[3]+nextMove[4]
				if isLegal(oldPosition, newPosition, board):
					board = resolveMove(oldPosition, newPosition, board)
					board["moveList"].append(nextMove)
					drawBoardWhite(board)
				else:
					"Move is illegal. Try again."
			else:
				print ord(nextMove[0]) >= 65 and (ord(nextMove[0]) <= 71)
				print nextMove[1]
				print ord(nextMove[3])
				print nextMove[4]
				print "Not a valid chess move. Format is e2 e4; commands are movelist, takeback, exit."

# def generateMoveList(oldPosition, board):
# 	currentPiece = board[oldPosition]
# 	whoseTurn = whoseTurnIsIt(board)
# 	validMoves = []
# 	if whoseTurn = "white":
# 		# Changes current piece from unicode to single characters, upper for black, lower for white.
# 		currentPiece = whitePieces[currentPiece]
# 		if currentPiece = 'p':
# 			newPositionCandidate = oldPosition[0]+str(int(oldPosition[1]+1))
# 			if board(newPositionCandidate) != " ":
# 				break
# 			validMoves.append(oldPosition + " " + newPositionCandidate
# 			if oldPosition[1] == "2":
# 				validMoves.append(oldPosition + " " + oldPosition[0] + str(int(oldPosition[1]+2)))



def resolveMove(oldPosition, newPosition, board):
	if board[newPosition] != " ":
		# If space is occupied...
		if board[oldPosition] in whitePieces:
			if board[newPosition] in whitePieces:
				print "Your "+board[newPosition] + " is already at that square. Try again."
			else:
				print board[oldPosition]+" takes "+board[newPosition]
				if board[newPosition] in blackPieces:
					board["capturedBlackPieces"] = board["capturedBlackPieces"] + board[newPosition]
				else:
					board["capturedWhitePieces"] = board["capturedWhitePieces"] + board[newPosition]
				board["stowage"]=board[newPosition]
				board[newPosition]=board[oldPosition]
				board[oldPosition]=" "
				board["gameTime"]=board["gameTime"]+(time.time()-board["oldTime"])
				board["turnNumber"] += 1
		elif board[oldPosition] in blackPieces:
			if board[newPosition] in blackPieces:
				print "Your "+board[newPosition] + " is already at that square. Try again."
			else:
				print board[oldPosition]+" takes "+board[newPosition]
				board["stowage"]=board[newPosition]
				board[newPosition]=board[oldPosition]
				board[oldPosition]=" "
				board["gameTime"]=board["gameTime"]+(time.time()-board["oldTime"])
				board["turnNumber"] += 1
	# If it's a white King, check if we're castling.
	elif board[oldPosition]==u'\u2654':
		if (newPosition == "G1") and (board["H1"] == u'\u2656'):
			print "White castles kingside."
			board[oldPosition] = " "
			board["H1"] = " "
			board[newPosition] = u'\u2654'
			board["F1"] = u'\u2656'
			board["turnNumber"] += 1
			return board
		elif (newPosition == "C1")and (board["A1"] == u'\u2656'):
			print "White castles queenside."
			board[oldPosition] = " "
			board["A1"] = " "
			board[newPosition] = u'\u2654'
			board["D1"] = u'\u2656'
			board["turnNumber"] += 1
			return board
		else:
			print("Piece at " +  oldPosition + " moves to " + newPosition + ".")
			board["stowage"]=board[newPosition]
			board[newPosition]=board[oldPosition]
			board[oldPosition]=" "
			board["gameTime"]=board["gameTime"]+(time.time()-board["oldTime"])
	# If it's a black King, check if we're castling.
	elif board[oldPosition] == u'\u265A':
		if (newPosition == "G8") and (board["H8"] == u'\u265C'):
			print "Black castles kingside."
			board[oldPosition] = " "
			board["H8"] = " "
			board[newPosition] = u'\u265A'
			board["F8"] = u'\u265C'
			board["turnNumber"] += 1
			return board
		elif (newPosition == "C8") and (board["A8"] == u'\u265C'):
			print "Black castles queenside."
			board[oldPosition] = " "
			board["A8"] = " "
			board[newPosition] = u'\u265A'
			board["D8"] = u'\u265C'
			board["turnNumber"] += 1
			return board
		else:
			print("Piece at " +  oldPosition + " moves to " + newPosition + ".")
			board["stowage"]=board[newPosition]
			board[newPosition]=board[oldPosition]
			board[oldPosition]=" "
			board["gameTime"]=board["gameTime"]+(time.time()-board["oldTime"])
	# Make a 'normal' move.
	else:
		print("Piece at " +  oldPosition + " moves to " + newPosition + ".")
		board["stowage"]=board[newPosition]
		board[newPosition]=board[oldPosition]
		board[oldPosition]=" "
		board["gameTime"]=board["gameTime"]+(time.time()-board["oldTime"])
		board["turnNumber"]+= 1
	# If a piece is a white pawn...
	if board[newPosition] == u'\u2659':
		if newPosition[1] == 8:
			promoteQuery = raw_input("Promote to q or n? Case sensitive.")
			if promoteQuery == "queen":
				board[newPosition]=u'\u2655'
			elif promoteQuery =="knight":
				board[newPosition]=u'\u2658'
			else:
				print "Whatever, you get a q."
				board[newPosition]=u'\u2655'
	# If a piece is a black pawn...
	elif board[newPosition] == u'\u265F':
		if newPosition[1]==1:
			promoteQuery = raw_input("Promote to Q or N? Case sensitive.")
			if promoteQuery =="Q":
				board[newPosition]=u'\u265B'
			elif promoteQuery == "N":
				board[newPosition]=u'\u265E'
			else:
				print "Whatever, you get a Q."
				board[newPosition]=u'\u265B'
	return board


def whoseTurnIsIt(board):
	# Takes a board as an argument and returns a string, either "white" or "black," depending on whose turn it is.
	if board["turnNumber"]%2==1:
		return "white"
	else:
		return "black"

def isLegal(oldPosition, newPosition, board):
	color = whoseTurnIsIt(board)
	if color == "white":
		if board[oldPosition] in blackPieces:
			print "You can't move black's pieces."
			return False
	elif color == "black":
		if board[oldPosition] in whitePieces:
			print "You can't move white's pieces."
			return False
	elif board[oldPosition] == " ":
		print "There's no piece here."
		return False
	return True

main()