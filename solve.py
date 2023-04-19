import sys
from copy import deepcopy

def parse_problem(filename):
    with open(filename) as f:
        lines = f.readlines()
    
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

def unit_propagation(clauses, assignment, map_var):
    reduced_clauses = list(enumerate(deepcopy(clauses)))
    
    while True:
        updated = False
        for (i, clause) in reduced_clauses:
            clause.update(map_var)

            if clause.satisfied():
                continue
            
            if len(clause) == 1:
                literal = clause.get()
                if literal > 0:
                    var = literal
                    assignment.append((var, True, i))
                    map_var[var] = True
                else:
                    var = -literal
                    assignment.append((var, False, i))
                    map_var[var] = False
                
                updated = True
                clause.set_satisfied()
        
        if not updated:
            break
    
    return list(filter(lambda t: not t[1].satisfied(), reduced_clauses))

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

    def resolvent(self, var, clause):
        new_inner = self.inner.union(clause.inner)
        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(new_inner)
        
def reduced_assertion(reduced_clauses, map_var):
    for (_, c) in reduced_clauses:
        for var in map_var:
            if c.exist(var):
                return False
    return True

if __name__ == "__main__":
    clauses = parse_problem(sys.argv[1])
    assignment = []
    map_var = {}
    
    while True:
        reduced_clauses = unit_propagation(clauses, assignment, map_var)
        print(len(map_var))
        assert(reduced_assertion(reduced_clauses, map_var))
        
        if reduced_clauses == []:
            print(map_var)
            sol = ' '.join(map(lambda item: str(item[0] if item[1] else -item[0]), map_var.items()))
            print("v " + sol)
            exit()
        
        i = None
        for j, clause in reduced_clauses:
            if (clause.is_false()):
                i = j
                break
        
        if i is not None:               # Conflict!
            conflict_clause = clauses[i]
            for (var, val, idx) in assignment.__reversed__():
                if not conflict_clause.exist(var):
                    continue
                if idx == -1:             # Decision assignment
                    continue
                else:
                    conflict_clause = conflict_clause.resolvent(var, clauses[idx])

            if conflict_clause.is_false():
                print("UNSATISFIABLE")
                exit()
            j = len(assignment)
            for var, _1, _2 in assignment.__reversed__():
                del map_var[var]
                j -= 1
                if conflict_clause.exist(var):
                    break
            assignment = assignment[:j]
            clauses.append(conflict_clause)
        else:
            # Use a decision strategy to determine a new assignment p |-> b
            p = abs(reduced_clauses[0][1].get())
            assignment.append((p, True, -1))           # -1 represents assignment is decided.
            map_var[p] = True