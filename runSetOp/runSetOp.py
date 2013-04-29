######################################################
# Author: Steven Stinson                             #
# Date: 6/11/2012                                    #
# Description: Set Operation Interpreter for VASP    #
######################################################

import sys
import string
import os
import random
import math
import time
import glob

#The lookup table of variables
variables = {}

#The final list of shells, essentially the output file
output = ""

#The number of temporary files created
numTemps = 0

#A list of temporary files created for the current script being generated
temps = []

#the number of processors
processors = 0

#the number of final SURF files that have been generated
finals = 0

#the type of operation, whether it be just generating a surface, taking a volume, or generating a fragment
op = 's'

######################################################
## Main Method
######################################################
def main():
	global processors
	
	start = time.time()
	
	if len(sys.argv) !=4:
		usage()
		sys.exit(2)
	
	processors = int(sys.argv[3])
	
	filename = sys.argv[1]
	
	if (sys.argv[2] == "-l"):
		parseLists(filename)
	elif (sys.argv[2] == "-p"):
		parsePairwise(filename)
	elif (sys.argv[2] == "-b"):
		getVariables(filename)
		expr = getExpression(filename)
		parse(expr, "script.scr")
	else:
		usage()
		sys.exit(2)
		
	os.system("./masterScript.scr")
	os.system("rm -rf *.scr")
	
	end = time.time()
	
	print "RUNTIME: "+str(end-start)+" SECONDS"
######################################################
## Parses a file with lists in variables. Essentially
## A wrapper for expression() that runs it however
## many times is necessary for the lists to be
## processed
######################################################
def parseLists(filename):
	global output
	lists = getLists(filename)
	keys = lists.keys()
	expr = getExpression(filename)
	
	maxlen = len(lists[keys[0]])
	
	for key in keys:
		if len(lists[key]) != maxlen:
			print "ERROR: In -l all lists must be same size"
	
	i = 0
	while i < maxlen:
		for key in keys:
			index = 0
			if i>=len(lists[key]):
				index = len(lists[key]) - 1
			else:
				index = i
			variables[key]=lists[key][index]
		parse(expr, "scr"+str(i)+".scr")
		output = ""
		i+=1
	
	genMasterScript(i)
		
######################################################
## Parses the script to be run pairwise. This would
## make it such that:
## a = [x.SURF, w.SURF]
## b = [y.SURF, z.SURF]
## (a [U] b)
## runs four union operaions, x u y, x u z, w u y,
## and w u z.
######################################################
def parsePairwise(filename):
	global output
	lists = getLists(filename)
	keys = lists.keys()
	expr = getExpression(filename)
	
	scripts = 0
	positionVector = []
	for i in range (0,len(keys)):
		positionVector.append(0)
	
	while True:
		
		for i in range (0,len(keys)):
			variables[keys[i]]=lists[keys[i]][positionVector[i]]
		
		parse(expr, "scr"+str(scripts)+".scr")
		output = ""
		scripts+=1
		if not goAhead(positionVector, lists):
			break
	
	genMasterScript(scripts)
	
	
######################################################
## Generates a master script that will execute all of
## the mini-scripts in parallel, the number of which
## being run at the same time is equal to the number
## of processors noted on the command line. If the number
## of processors is listed as zero or less, it will
## run all at the same time in parallel.
######################################################
def genMasterScript(numScripts):
	global processors
	masterScript = ""
	i = 0
	
	if processors>0:
		resetCounter = 0
		while i < numScripts:
			resetCounter+=math.ceil(processors/2.0);
			commands = []
			while i < resetCounter:
				if i == numScripts:
					break
				commands.append(["./scr"+str(i)+".scr"])
				i+=1
			
			masterScript+=createSubshells(commands)
	else:
		commands = []
		for i in range(0,numScripts):
			commands.append(["./scr"+str(i)+".scr > /dev/null"])
		masterScript+=createSubshells(commands)
	
	commands = []
	if (op == 'v' or op == 'f'):
		for i in range(0,finals):
			commands.append("cat final"+str(i)+".txt")
			commands.append("rm -rf final"+str(i)+".txt")
		masterScript+=createSubshells([commands])

		
	file = open("masterScript.scr","wt")
	file.write(masterScript)
	file.close()
	os.system("chmod 777 masterScript.scr")

######################################################
## Iterates the position vector and checks to see if
## anything is out of bounds. Iterates from left to
## right. If no more iteration is possible, then it
## will return False, otherwise it will return True
######################################################
def goAhead(positionVector, lists):
	keys = lists.keys()

	for i in range(0,len(keys)):
		if positionVector[i]+1!=len(lists[keys[i]]):
			positionVector[i]=positionVector[i]+1
			return True
		positionVector[i] = 0
		
	return False
	
	
######################################################
## Gets the lists from the files and puts them
## into a dictionary
######################################################
def getLists(filename):
	file = open(filename, "rt")
	
	line = file.readline()
	lists = {}
	
	while (line):
		if len(line)>2:
			if line[2] == '=':
				var = []
				if line[3:].strip().startswith('['):
					startIndex = string.find(line, '[')+1
					endIndex = string.find(line, ']')
					var.extend(string.split(line[startIndex:endIndex],','))
					#if endIndex == -1:
					#	endIndex = string.find(line, ']')
					#while endIndex!=-1:
					#	var.append(line[startIndex+1:endIndex].strip())
					#	startIndex = endIndex+1
					#	endIndex = string.find(line, ',', startIndex)
					#	if endIndex == -1:
					#		endIndex = string.find(line, ']', startIndex)
				elif line[3:].strip().startswith('-d'):
					switchIndex = string.find(line, 'd')
					dir = line[switchIndex+1:].strip()
					vard.extend(glob.glob(os.path.join(dir,"*.SURF")))
				else:
					var.append(line[4:].strip())
				
				lists[line[0]] = var
				
		line = file.readline()
	file.close()
	return lists

######################################################
## Extracts the expression from the given file
######################################################
def getExpression(filename):
	file = open(filename, "rt")
	global op
		
	expr = ""
	
	line = file.readline()
	while (line):
		if len(line)>2:
			if line[2] != '=':
				if line.strip().startswith('v'):
					op = "v"
					expr = line.strip()[1:]
				elif line.strip().startswith('f'):
					op = "f"
					expr = line.strip()[1:]
				else:
					expr = line
				
		line = file.readline()
	
	file.close()
	
	return expr

######################################################
## Definition of Usage
######################################################
def usage():

	print "A = [x.SURF, y.SURF, z.SURF]"
	print "B = [-s receptor.PDB, ligand.PDB]"
	print "C = -d directory"
	print ""
	print "v((A [U] B) [I] C)"
	print ""
	print "-----------------------------------------------------"
	print ""
	print "v(...) = volume of result"
	print "f(...) = fragmentation of result"
	print "all operations must be surrounded by parentheses"
	print ""
	print "operations:"
	print ""
	print "x [U] y = union"
	print "x [I] y = intersection"
	print "x [D] y = difference"
	print "x [C] y = surfCombine"
	print ""
	print "use variable names that don't conflict with operation names"
	print "(case sensitive, i.e. 'u' is okay) for best results, though"
	print "the script will still run correctly."
	print ""
	print "command line:"
	print "python runSetOp.py [input File] [option] [# of processors]"
	print "input File: The file to read the expression/vars from. See top of"
	print "      this file for format."
	print "option:"
	print "	-p: pairwise. Will run all As with all Bs with all Cs etc."
	print "	-l: list matching. Will run the first element of all lists,"
	print "	    then the second, then the third, etc. Requires all lists"
	print "	    to be the same length"
	print "	-b: Only one element per list."
	print "# of processors: The number of processors available to be used. Used"
	print "      to calculated parallelization. If you don't want to use this"
	print "      or don't know use 1."
	print ""
	print "If you have any questions contact Steve Stinson: srs514@lehigh.edu"

	
######################################################
## Gets the variable names/files in the input file
######################################################
def getVariables(filename):
	file = open(filename, "rt")
	
	line = file.readline()
	
	while (line):
		if len(line)>2:
			if line[2] == '=':
				var = ""
				var = line[4:].strip()
				
				variables[line[0]] = var
				#print var
				
		line = file.readline()
	
	file.close()

######################################################
## Parses the expression in the file, making sure
## it is a correct set of set operations.
######################################################
def parse(expr, scriptFilename):
	global output, finals, op
	
	unixLine=expression(expr, "final"+str(finals)+".SURF")
	
	
	commands = []
	commands.append(unixLine)
	if (op == 's'):
		commands.append(["echo \""+getLineHeader(expr)+" = final"+str(finals)+'.SURF\"'])
	else:
		output +=createSubshells(commands)
		commands = []
		if (op == 'v'):
			list = []
			list.append("echo \""+getLineHeader(expr)+" = \">final"+str(finals)+".txt")
			list.append("./surfaceExtractor -surveyVolume final"+str(finals)+".SURF | grep \"Final Volume\" >>final"+str(finals)+".txt")
			list.append("rm -rf final"+str(finals)+".SURF > /dev/null")
			commands.append(list)
		elif (op == 'f'):
			list = []
			list.append("echo \""+getLineHeader(expr)+" = \">final"+str(finals)+".txt")
			list.append("./surfaceExtractor -surfSeparateFrags final"+str(finals)+".SURF frag"+str(finals)+"- | grep \"LARGEST\" >>final"+str(finals)+".txt")
			list.append("rm -rf final"+str(finals)+".SURF > /dev/null")
			list.append("rm -rf frag"+str(finals)+"-* > /dev/null")
			commands.append(list)
		
	finals +=1
	output += createSubshells(commands)
	
	#clean up the temp files
	if temps != []:
		commands = []
		for filename in temps:
			commands.append("rm -rf "+filename)
		output += createSubshells([commands])
	
	file = open(scriptFilename, "wt")
	file.write(output)
	file.close()
	os.system("chmod 777 "+scriptFilename)
	
######################################################
## Takes in a set notation expression, returns the
## expression with the variables replaced with
## their filenames under the variables dictionary
######################################################
def getLineHeader(expr):
	
	result = ""
	
	for i in range(1,len(expr)):
		appended = False
		for key in variables.keys():
			if (expr[i] == key and expr[i-1] != '['):
				result+=variables[key]
				appended = True
		if not appended:		
			result+=expr[i]
	
	return result
	
	
######################################################
## Parses an expression starting at the given index.
## An expression is defined as:
## (<variable> [<operation>] <variable>)
## where <variable> is either another expression or
## a single alphanumeric character, and <operation>
## is either U, representing a union; N, representing
## an intersection; D, representing a difference, or
## C, representing a surfCombine.
######################################################
def expression(line, out):
	global output
	line = line.strip()
	
	
	if (len(line) > 0):
		check (line[0]=='(' and line[len(line)-1]==')',"ERROR: expressions must be surrounded by parentheses")
		
		#op is an array holding the elements of the vasp operation
		op =  []
		#commands are the unix shell commands to be executed
		commands = []
		
		
		#arr[0] is the remaining line, arr[1] is the filename(s) in the operation,
		#arr[2] is the line of vasp needed for the subexpression of the variable
		arr = variable(line[1:len(line)-1])
		line = arr[0]
		op.append(arr[1])
		if len(arr)==3:
			commands.append(arr[2])
		
		arr = operation(line)
		line = arr[0]
		op.append(arr[1])
		
		arr = variable(line)
		line = arr[0]
		op.append(arr[1])
		if len(arr)==3:
			commands.append(arr[2])
		
		#print commands
		
		if commands!=[]:
			output = output + createSubshells(commands)
		
		vaspLines = []
		if op[1] == 'C':
			vaspLines.append("./surfaceExtractor -surfCombine "+op[0]+" "+op[2]+" "+out+" > /dev/null")
		else:
			vaspLines.append("./vasp -csg "+op[0]+" "+op[2]+" "+op[1]+" "+out+" 0.5 > /dev/null")
	
	return vaspLines

######################################################
## See the comment about expression() to see what
## the definition of a variable is. This will see
## if there is a correct variable and then return the
## line skipping it.
######################################################
def variable(line):
	global numTemps, finals
	line = line.strip()
	
	if (len(line)>0):
		if line[0] == '(':
			#variable is an expression, so we have to find the close paren
			index = 1
			parens = 1
			
			while (parens > 0):
				if line[index] == '(':
					parens = parens + 1
				elif line[index] == ')':
					parens = parens - 1
				index+=1
			
			#creates/names temp files
			filename = "temp"+str(numTemps)+".SURF"
			
			temps.append(filename)
			numTemps = numTemps+1
			vaspLines = expression(line[0:index+1], filename)
			return [line[index+1:], filename, vaspLines]
			
			
		else:
			#Else variable is just a single character variable (supposedly)
			var = str(line[0])
			
			if variables[var].strip().startswith("-s"):
				receptor = variables[var][3:string.find(variables[var][3:],' ')+3]
				ligand = variables[var][string.find(variables[var][3:],' ')+4:]
				variables[var]=convert(receptor,ligand)
		
			#check if the variable is an alphabetic character (this is why
			#it's defined as a string and not a character)
			check (var.isalpha(),"ERROR: variables must be alphanumeric")
			return [line[1:], variables[var]]
	else:
		print "ERROR: Bad input, check parentheses"
		exit(1)

#######################################################
## Checks if the next thing in the line is a legal
## set operation. See the comment above expression()
## to see what a legal operation is defined as.
#######################################################
def operation(line):
	line = line.strip()
	
	if len(line) > 3:
		check (line[0]=='[' and line[2]==']',"ERROR: operations must be surrounded by brackets")
		check (line[1]=='D' or line[1]=='U' or line[1]=='I' or line[1]=='C', "ERROR: not a legal operation")
		
		return [line[3:], line[1]]
	else:
		print "ERROR: Bad input, check parentheses"
		sys.exit(1)
		
#########################################################
## Checks whether the boolean expression b is true or not.
## If it is false, print the error message, then exit.
#########################################################
def check(b,message):
	if (not b):
		print message
		sys.exit(1)
		
		
#########################################################
## Given that the input file will most likely be in pdb
## format, this will convert the pdb files into SURF files.
#########################################################
def convert(receptor, ligand):
	global output
	
	commands = []
	
	commands.append("./surfaceExtractor -surfOutput "+receptor+" 1.4 receptor-MS.SURF")
	commands.append("./surfaceExtractor -surfOutput "+receptor+" 5.0 receptor-EV.SURF")
	commands.append("./surfaceExtractor -surfProbeGen "+ligand+" probe.SURF 5.0 .5")
	commands.append("./vasp -csg probe.SURF receptor-MS.SURF D probe-MS.SURF .5")
	commands.append("./vasp -csg probe-MS.SURF receptor-EV.SURF I probe-MS-EV.SURF .5")
	commands.append("./surfaceExtractor -surfBooleanClean probe-MS-EV.SURF "+receptor[:len(receptor)-4]+".SURF")
	
	output = output + createSubshells([commands])
	
	return receptor[:len(receptor)-4]+".SURF"
		
#########################################################
## Creates a full set of subshells per one wait command.
## Input is a list of lists of strings. Each list of strings
## is one shell to be executed at the same time as the other
## lists of strings.
#########################################################
def createSubshells(lists):
	out = ""
	for list in lists:
		out = out + "("
		for string in list:
			out = out + string + "; "
		out = out + ") & "
	out = out[:len(out)-3]
	out = out + "\nwait;\n\n"
	
	return out

if __name__ == "__main__":
    main()
