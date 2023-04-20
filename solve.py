import sys
from copy import deepcopy
import random

def parse_problem(filename):
    with open(filename) as f:
        lines = f.readlines()
    
    for i in range(len(lines)-1):
        if lines[i] == "%\n" and lines[i+1] == "0\n":
            lines = lines[:i]
            break

    clauses = []
    for line in lines:
        if (line[0] == "c"): # comment
            continue
        if (line[0] == "p"):
            toks = line.split()
            assert (toks[1] == "cnf")
            assert (len(toks) == 4)
            num_vars, num_clauses = toks[2], toks[3]
        else:
            toks = list(map(int, line.split()))
            assert (toks[-1] == 0)
            toks.pop()
            clauses.append(Clause(toks))
    
    return clauses

class Clause:
    def __init__(self, iterable):
        self.inner = set(iterable)
        self.inner_abs = set(map(abs, iterable))
    
    def get(self):
        return next(iter(self.inner))

    def exist(self, variable):
        return abs(variable) in self.inner_abs

    def remove(self, var):
        self.inner.remove(var)
        if not -var in self.inner:
            self.inner_abs.remove(abs(var))
    
    def set_satisfied(self):
        self.inner = None
        self.inner_abs = None

    def satisfied(self):
        return self.inner is None

    def update(self, map_var):
        if self.satisfied():
            return
        for var in self.inner.copy():
            if var < 0:
                neg = True
                avar = -var
            else:
                neg = False
                avar = var
            
            if avar in map_var:
                if map_var[avar] == neg:                            # False Literal
                    self.remove(var)
                else:
                    self.set_satisfied()
            
            if self.satisfied():
                return

    def __len__(self):
        return len(self.inner)
    
    def __repr__(self):
        return repr(self.inner)

    def is_false(self):
        return len(self) == 0

    def is_unit(self):
        return len(self) == 1

    def resolvent(self, var, clause):
        new_inner = self.inner.union(clause.inner)

        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(new_inner)

class DPLL:
    def __init__(self, clauses):
        self.clauses = clauses
        self.assignment = []
        self.map_var = {}
        self.reduced_clauses = None
    
    def assign(self, var, value, related_clause):
        self.assignment.append((var, value, related_clause))
        self.map_var[var] = value

    def unit_prop(self):
        reduced_clauses = list(enumerate(deepcopy(self.clauses)))
        
        while True:
            updated = False
            for (i, clause) in reduced_clauses:
                clause.update(self.map_var)

                if clause.satisfied():
                    continue
                
                if clause.is_unit():
                    literal = clause.get()
                    if literal > 0:
                        self.assign(literal, True, i)
                    else:
                        self.assign(-literal, False, i)
                    updated = True
                    clause.set_satisfied()
            
            if not updated:
                break
        
        self.reduced_clauses = list(filter(lambda t: not t[1].satisfied(), reduced_clauses))
        return

    def satisfied(self):
        return len(self.reduced_clauses) == 0

    def conflict(self):
        for j, clause in self.reduced_clauses:
            if (clause.is_false()):
                return j
        return None

    def learn_clause(self, conflict_clause):
        learned_clause = conflict_clause
        for (var, _, idx) in self.assignment.__reversed__():
            if not learned_clause.exist(var):
                continue
            if idx == -1:             # Decision assignment
                continue
            else:                     # Implied assignment with var
                learned_clause = learned_clause.resolvent(var, self.clauses[idx])
        return learned_clause
    
    def backtrack(self, learned_clause):
        while True:
            var, _1, _2 = self.assignment.pop()
            del self.map_var[var]
            if learned_clause.exist(var):
                break
    
    # Heuristic to decide most popular variable
    def decision(self):
        _, clause = random.choice(self.reduced_clauses)
        self.assign(abs(clause.get()), True, -1)

    def run(self):
        while True:
            self.unit_prop()
            if self.satisfied():
                return Solution(True, self.map_var)

            if (i:=self.conflict()) is not None:
                learned_clause = self.learn_clause(self.clauses[i])
                if learned_clause.is_false():
                    return Solution(False)
                self.backtrack(learned_clause)
                self.clauses.append(learned_clause)
            else:
                self.decision()
            
            del self.reduced_clauses
    
    def verify(self):
        self.unit_prop()
        return self.satisfied()

class Solution:
    def __init__(self, sat, sol=None):
        self.sat = sat
        self.sol = sol
    
    def __repr__(self):
        if self.sat:
            L = ["v"]
            for (k, v) in self.sol.items():
                if v:
                    s = ""
                else:
                    s = "-"
                L.append(s + str(k))
            L.append("0")
            return ' '.join(L)
        else:
            return "UNSATISFIABLE"


if __name__ == "__main__":
    clauses = parse_problem(sys.argv[1])
    dpll = DPLL(clauses)
    result = dpll.run()
    if result.sat:
        assert(dpll.verify())
    print(result)