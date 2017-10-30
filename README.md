# D2D-load-balance
This is my work during internship in IE of CUHK.

The main work is to design a low-complexity algorithm for a conference paper that pubilshed in 2015, https://staff.ie.cuhk.edu.hk/~mhchen/papers/D2D.LB.MASS.15.pdf.  

Yet, we have sumbitted the paper into http://arxiv.org/. You can find our work at https://export.arxiv.org/abs/1710.02636. My main contribution in this work is to design the low-complexity algorithm. Python is programming language and the optimization toolbox is Gurobi (http://www.gurobi.com/).

There are two functions in files, named as Function_LP.py and Function_YDS.py. The former achieves the YDS algorithm [1], whose time complexity is ![](http://latex.codecogs.com/gif.latex?O(n^3)), even ![](http://latex.codecogs.com/gif.latex?O(n^{2}\\log{n})) with special data structure. The latter achieves building the LP problem module, `Min-Overhead`. It is well to be reminded when ![](http://latex.codecogs.com/gif.latex?\\lambda=0), `Min-Overhead` is equal to `Min-Spectrum-D2D`. 

In addition, you should use `Python2` instead of Python3 due to there are some same operations with different results, such like division of integers.

## References
[1] Yao F F, Demers A J, Shenker S, et al. A scheduling model for reduced CPU energy[C]. foundations of computer science, 1995: 374-382.
