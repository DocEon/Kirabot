#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import ssl
import socket
import time
import re
from random import randrange

gameOver = False
turn = "white"
def drawBoard(a,b,c,d,e,f,g,h):
	print "╔═══╦═══╦═══╦═══╦═══╦═══╦═══╦═══╗"
	print "║ "+a[7]+" ║ "+b[7]+" ║ "+c[7]+" ║ "+d[7]+" ║ "+e[7]+" ║ "+f[7]+" ║ "+g[7]+" ║ "+h[7]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[6]+" ║ "+b[6]+" ║ "+c[6]+" ║ "+d[6]+" ║ "+e[6]+" ║ "+f[6]+" ║ "+g[6]+" ║ "+h[6]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[5]+" ║ "+b[5]+" ║ "+c[5]+" ║ "+d[5]+" ║ "+e[5]+" ║ "+f[5]+" ║ "+g[5]+" ║ "+h[5]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[4]+" ║ "+b[4]+" ║ "+c[4]+" ║ "+d[4]+" ║ "+e[4]+" ║ "+f[4]+" ║ "+g[4]+" ║ "+h[4]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[3]+" ║ "+b[3]+" ║ "+c[3]+" ║ "+d[3]+" ║ "+e[3]+" ║ "+f[3]+" ║ "+g[3]+" ║ "+h[3]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[2]+" ║ "+b[2]+" ║ "+c[2]+" ║ "+d[2]+" ║ "+e[2]+" ║ "+f[2]+" ║ "+g[2]+" ║ "+h[2]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[1]+" ║ "+b[1]+" ║ "+c[1]+" ║ "+d[1]+" ║ "+e[1]+" ║ "+f[1]+" ║ "+g[1]+" ║ "+h[1]+" ║"
	print "╠═══╬═══╬═══╬═══╬═══╬═══╬═══╬═══╣"
	print "║ "+a[0]+" ║ "+b[0]+" ║ "+c[0]+" ║ "+d[0]+" ║ "+e[0]+" ║ "+f[0]+" ║ "+g[0]+" ║ "+h[0]+" ║"
	print "╚═══╩═══╩═══╩═══╩═══╩═══╩═══╩═══╝"

def newGame():
	# Initializes the arrays with starting positions proper. Not in use yet because I don't know how to share arrays properly, but this should start a brand new game if necessary.
	a = ["R", "P", " ", " ", " ", " ", "p", "r"]
	b = ["N", "P", " ", " ", " ", " ", "p", "n"]
	c = ["B", "P", " ", " ", " ", " ", "p", "b"]
	d = ["Q", "P", " ", " ", " ", " ", "p", "q"]
	e = ["K", "P", " ", " ", " ", " ", "p", "k"]
	f = ["B", "P", " ", " ", " ", " ", "p", "b"]
	g = ["N", "P", " ", " ", " ", " ", "p", "n"]
	h = ["R", "P", " ", " ", " ", " ", "p", "r"]
	gameOver = False

def main():
	a = ["R", "P", " ", " ", " ", " ", "p", "r"]
	b = ["N", "P", " ", " ", " ", " ", "p", "n"]
	c = ["B", "P", " ", " ", " ", " ", "p", "b"]
	d = ["Q", "P", " ", " ", " ", " ", "p", "q"]
	e = ["K", "P", " ", " ", " ", " ", "p", "k"]
	f = ["B", "P", " ", " ", " ", " ", "p", "b"]
	g = ["N", "P", " ", " ", " ", " ", "p", "n"]
	h = ["R", "P", " ", " ", " ", " ", "p", "r"]
	gameOver = False
	print "Welcome to Chessbot. Say the piece you want to move and then where you want it to go to send a command - e.g. e2e4"
	drawBoard(a,b,c,d,e,f,g,h)

	while gameOver == False:
		# take moves
		if turn == "white":
			nextMove = raw_input("White to move.\n")
			print "Piece at " +  nextMove[0] + nextMove[1] + " moves to " + nextMove[3] + nextMove[4] + "."
			




main()