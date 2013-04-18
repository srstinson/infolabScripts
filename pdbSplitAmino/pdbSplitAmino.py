import os
import sys

####################################################
# Author: Steven Stinson
# Description: Takes a .pdb file; splits it into
#              several files where each represents
#              a singular amino acid.
####################################################

AMINO_ACID_BEGIN = 17
AMINO_ACID_END = 20

def getAcid(pdbLines):
    acid = ""
    acidLines = []
    while(len(pdbLines)>0):
        line = pdbLines.pop(0).strip()
        if (line.startswith("ATOM ")):
            currentAcid = line[AMINO_ACID_BEGIN:AMINO_ACID_END]
            if (acid==""):
                acid = currentAcid
            elif(currentAcid!=acid):
                return acidLines
            else:
                print line
                acidLines.append(line+"\n")
    return []

def outputAcidFile(dir,id,acidLines):
    #print acidLines[0]
    outputFileName = os.path.join(dir,id+acidLines[0][AMINO_ACID_BEGIN:AMINO_ACID_END]+acidLines[0][23:26].strip())

    outFile = open(outputFileName+".pdb","w")
    outFile.writelines(acidLines)

def main():
    pdbFile = open(sys.argv[1],"r")
    splitFile = os.path.split(sys.argv[1])
    id = splitFile[1][0:4]
    dir = splitFile[0]
    pdbLines = pdbFile.readlines()
    while (len(pdbLines)>0):
        acidLines = getAcid(pdbLines)
        if (len(acidLines)!=0):
            outputAcidFile(dir,id,acidLines)

if __name__ == "__main__":
            main()


