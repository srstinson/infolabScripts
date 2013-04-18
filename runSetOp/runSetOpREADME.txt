A = [x.SURF, y.SURF, z.SURF]
B = [-s receptor.PDB, ligand.PDB]
C = -d directory

v((A [U] B) [I] C)

-----------------------------------------------------

v(...) = volume of result
f(...) = fragmentation of result
all operations must be surrounded by parentheses

operations:

x [U] y = union
x [I] y = intersection
x [D] y = difference
x [C] y = surfCombine

use variable names that don't conflict with operation names
(case sensitive, i.e. 'u' is okay) for best results, though
the script will still run correctly.

command line:
python runSetOp.py [input File] [option] [# of processors]
input File: The file to read the expression/vars from. See top of
      this file for format.
option:
	-p: pairwise. Will run all As with all Bs with all Cs etc.
	-l: list matching. Will run the first element of all lists,
	    then the second, then the third, etc. Requires all lists
	    to be the same length
	-b: Only one element per list.
# of processors: The number of processors available to be used. Used
      to calculated parallelization. If you don't want to use this
      or don't know use 1.

If you have any questions contact Steve Stinson: srs514@lehigh.edu