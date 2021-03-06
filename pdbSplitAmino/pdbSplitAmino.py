import os
import sys
from collections import deque

####################################################
# Author: Steven Stinson
# Description: Takes a .pdb file; splits it into
#              several files where each represents
#              a singular amino acid.
####################################################

AMINO_ACID_BEGIN = 17
AMINO_ACID_END = 20

#Returns a generator containing all of the lines beginning with ATOM
#corresponding to the next amino acid in the pdbLines list of strings.
#Side Effect: all of the lines returned and those skipped are popped off
#of pdbLibes
def getAcid(pdbLines):
    acid = ""
    currentAcid = ""
    while(len(pdbLines)>0 and currentAcid==acid):
        line = pdbLines.popleft().strip()
        if (line.startswith("ATOM ")):
            currentAcid = line[AMINO_ACID_BEGIN:AMINO_ACID_END]
            if (acid==""):
                acid = currentAcid
            #print line
            yield line+"\n"

#Writes acidLines to a filename generated in the way usage() describes in the directory
#provided
def outputAcidFile(dir,id,acidLines):
    firstLine = acidLines.__iter__().next()
    outputFileName = os.path.join(dir,id+firstLine[AMINO_ACID_BEGIN:AMINO_ACID_END]+firstLine[23:26].strip())

    outFile = open(outputFileName+".pdb","w")
    outFile.write(firstLine)
    outFile.writelines(acidLines)

#Main method. opens the pdb file, adds the pdb lines to a queue, then
#breaks off each amino acid in order then writes them to a file.
def main():
    if len(sys.argv) != 2:
	usage()
	exit()

    pdbFile = open(sys.argv[1],"r")
    splitFile = os.path.split(sys.argv[1])
    id = splitFile[1][0:4]
    dir = splitFile[0]
    pdbLines = deque(pdbFile.readlines())
   
    while (len(pdbLines)>0):
        acidLines = getAcid(pdbLines)
        outputAcidFile(dir,id,acidLines)

#Prints the usage of the script when it is not invoked correctly.
def usage():
	print "USAGE:"
	print "--------------------------------------------------"
	print "python pdbSplitAmino.py XXXX.pdb"
	print "Will generate n files, where n is the number of"
	print "amino acids in the pdb file, named:"
	print "XXXXYYYZZ.pdb"
	print "Where XXXX is the pdb id, YYY is the acid name, and ZZ is the acid number"
	print "For any questions please contact me at srs514@lehigh.edu"
	print "--------------------------------------------------"

if __name__ == "__main__":
            main()


