import sys
from copy import deepcopy

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
    
    assert(num_clauses == len(clauses))

    return clauses, num_vars

class Solution:
    def __init__(self, sat, sol=None):
        self.sat = sat
        self.sol = sol
    
    def __repr__(self):
        if self.sat:
            first_line = "s SATISFIABLE\n"
            L = ["v"]
            for (k, v) in self.sol.items():
                if v:
                    s = ""
                else:
                    s = "-"
                L.append(s + str(k))
            L.append("0")
            return first_line + ' '.join(L)
        else:
            return "s UNSATISFIABLE"

class Assignment:
    def __init__(self, var, implied, associated_clause=None):
        self.var = var
        self.implied = implied      # or decided
        self.associated_clause = None

class Clause:
    def __init__(self, iterable):
        self.inner = {var: None for var in iterable}
        self.undecided = set(iterable)
        self.count_true = 0
        self.count_false = 0
    
    def get(self):
        return iter(self.undecided).next()

    def assign(self, var, value):
        if var in self.inner:
            self.undecided.remove(var)
            self.inner[var] = value
            if value:
                self.count_true += 1
            else:
                self.count_false += 1
        elif -var in self.inner:
            self.undecided.remove(-var)
            self.inner[-var] = not value
            if not value:
                self.count_true += 1
            else:
                self.count_false += 1

    def is_satisfied(self):
        return self.count_true >= 1

    def __len__(self):
        assert(not self.satisfied())
        return len(self.inner) - self.count_false
    
    def __repr__(self):
        return repr(self.inner)

    def is_false(self):
        return len(self) == 0

    def is_unit(self):
        return len(self) == 1

    def resolvent(self, var, clause):
        new_inner = set(self.inner).union(set(clause.inner))
        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(new_inner)

class DPLL:
    def __init__(self, clauses, nvars):
        self.clauses = clauses
        self.assignment = []
        self.vmap = {}
        self.positive_clauses = {var: set() for var in range(1, nvars+1)}
        self.negative_clauses = {var: set() for var in range(1, nvars+1)}
        
        for i, clause in enumerate(clauses):
            for literal in clause:
                if literal > 0:
                    self.positive_clauses[literal].add(i)
                else:
                    self.negative_clauses[literal].add(i)
    
    def propagate(self, var, value, record=True):
        if var in self.vmap:
            if self.vmap[var] != value:
                return False
        
        self.vmap[var] = value

        #satisfied_clauses = pclauses if self.vmap[var] else nclauses
        target = self.negative_clauses[var] \
            if value else self.positive_clauses[var]

        for i in target:
            clause = self.clauses[i]
            clause.assign(var, value)
            if clause.is_unit():
                literal = clause.get()
                nvar = abs(literal)
                if literal > 0:
                    return self.propagate(nvar, True, record)
                else:
                    return self.propagate(nvar, False, record)
        
        return True
            
            

    def preprocess(self):
        for clause in self.clauses:
            if clause.is_satisfied():
                continue
            if clause.is_unit():
                literal = clause.get()
                var = abs(literal)
                if literal > 0:
                    if not self.propagate(var, True, record=False):
                        return False
                else:
                    if not self.propagate(var, False, record=False):
                        return False

        return True

    def satisfied(self):
        

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
    
    def decision(self):
        p = abs(self.reduced_clauses[0][1].get())
        self.assign(p, True, -1)

    def run(self):
        if not self.preprocess():
            return Solution(False)
        
        while True:
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


if __name__ == "__main__":
    dpll = DPLL(*parse_problem(sys.argv[1]))
    result = dpll.run()
    if result.sat:
        assert(dpll.verify())
    print(result)