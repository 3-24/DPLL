## 6. Programming Assignment and Report

Here are two tasks that you will have to do.

* Implement a SAT solver using the DPLL algorithm with clause learning, which we cover in the course, and also using optimisations for SAT solving that you devise or can find in the literature. Your implementation should not use any external python libraries directly related to SAT solving. 
* Write a report that describes what you implemented, the design decision behind your implementation, and the rationale behind those decisions. The report should be at most 4 pages excluding the bibliography and figures. For instance, you can describe a list of possible optimisations for SAT solving, analyse the cons and pros of those optimisations, explain why you decide to choose only some of these optimisations, and justify your decision with experiments. 

#### 6.1. Evaluation

* Implementation (20%). Report (10%). 
* The submitted implementation will be marked automatically using our script. 
* The submitted report will be marked based on the level of originality and experimental or theoretical thoroughness in the analysis of the submitted implementation and its design decision, in a broad context of efficient SAT solving.

#### 6.2. Deadline

* __**23:59 of the 22nd of May in 2023 (Monday).**__ Summit both your implementation and report in KLMS.

#### 6.3. Programming Language to Use

* Python 3.7-10.

#### 6.4. Formats of Input and Output

* Follow DIMACS input/output requirements. You can learn about these requirements at the following URL: [http://www.satcompetition.org/2009/format-benchmarks2009.html](http://www.satcompetition.org/2009/format-benchmarks2009.html). This is the format used in the SAT competition. 
* Assume that the input is always in CNF format.

#### 6.5. Input Interface

The main file of your solver should be named as follows:

* solvepy3.py 

We plan to write a script that runs your solver with a cnf formula stored in a file (according to DIMACS format). The script searches for the solvepy3.py file in your submission, and runs something like

* python3 solvepy3.py "testn.cnf" --- when solvepy3.py is found.

Here "testn.cnf" is just an example name of a file containing a cnf formula in DIMACS format. Of course, different test cases will use different names.

#### 6.6. Output Interface

The output should specify SATISFIABLE/UNSATISFIABLE using s and give a partial assignment using v. So, if your solver is run

```
python3 solvepy3.py "test1.cnf"
```

but "test1.cnf" is unsatisfiable and your solver finds this out, it should return

```
s UNSATISFIABLE
```

in the standard output. On the other hand, if your solver is run

```
python3 solvepy3.py "test2.cnf"
```

but "test2.cnf" is satisfiable and your solver finds a satisfying partial assignment (2, 5, -7) meaning that variables 2 and 5 have the value 1 and the variable 7 has the value -1 in the found partial assignment, then your solver should return

```
s SATISFIABLE
v 2 5 -7 0
```

Here 0 indicates the end of the found partial assignment. The description of a found partial assignment can be across multiple lines. For instance, in the above case, the solver may return

```
s SATISFIABLE
v 2 5
v -7 0
```

#### 6.7. What to Submit in KLMS?

A zip file named "dpll.zip" containing two files:

* Source code of your implementation. Make sure that you follow the specifications described above. We plan to write a script that compiles and runs your code on some test cases automatically. Locate a solvepy*.py file on the root of the zip file.
* A report on your implementation, its design decision, and the rationale behind or justification of the decision. The report must be written by a word processor and submitted in a pdf format. (Its file name doesn't matter.) 
The report should be at most 4 pages without including the bibliography and figures.

#### 6.8. Test Cases

The following webpages contain benchmark problems in DIMACS format: 

* [https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html) and 
* [http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html](http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html). 

Those problems have a little bit different format described in the DIMACS format above; clause can be expressed on several lines, ill-formatted end lines. Therefore, you may need to modify your code or the problems to test them. However, the test cases for grading will strictly obey the DIMACS format above.  In the course webpage, we uploaded a zip file that contains some test cases we used before. To see the file, follow the below link:

* [https://github.com/hongseok-yang/logic23/blob/master/Others/Test_Case.zip](https://github.com/hongseok-yang/logic23/blob/master/Others/Test_Case.zip).

If you implemented the DPLL algorithm in the lecture correctly, then your code will return a result in 1 minute for every cases in the above zip file (tested in i7 7700HQ). Note that these cases are just examples, not necessarily ones that we will use to test your code for marking; we will certainly try new test cases with various difficulty. Thus, even when your code finds a right answer to every provided case within 1 minute, it may perform badly on the real test cases, and fail to get good marks.


#### 6.9. Final Remark

Make sure that your implementation handles corner cases correctly. There will be a timeout for each test case to check that you implemented the DPLL algorithms in the lecture properly. Finally, start this programming project as early as possible.
