import sys
from copy import deepcopy

def unit_propagation(clauses, assignment, map_var):
    reduced_clauses = list(enumerate(clauses))
    
    while True:
        updated = False
        for (i, clause) in reduced_clauses:
            if clause is None:
                continue

            satisfied = False
            for var in clause.inner:
                if var < 0:
                    neg = True
                    avar = -var
                else:
                    neg = False
                    avar = var
                
                if avar in map_var:
                    if map_var[avar] ^ neg:                         # False Literal
                        clause.inner.remove(var)
                    else:
                        reduced_clauses[i] = (i, None)                   # Satisfied clause
                        satisfied = True
                        break
            
            if satisfied:
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
                reduced_clauses[i] = (i, None)
        
        if not updated:
            break
    return reduced_clauses
            

class Clause:
    def __init__(self, iterable):
        self.inner = set(iterable)
        self.inner_abs = set(map(abs, iterable))
    
    def get(self):
        return next(iter(self.inner))

    def exist(self, variable):
        return abs(variable) in self.inner_abs

    def __len__(self):
        return len(self.inner)
    
    def __repr__(self):
        return repr(self.inner)

    def resolvent(self, var, clause):
        new_inner = self.inner.union(clause.inner)
        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(new_inner)
        
        

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    

    # [{1, 2,}, {2, 3}, ...]
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
    
    assignment = []
    map_var = {}
    
    while True:
        # [(1, {1, 2}), (3, {2, 3}), ...]
        reduced_clauses = unit_propagation(clauses, assignment, map_var)
        print(reduced_clauses)
        print(assignment)
        input()
        if reduced_clauses == []:
            print(assignment)
            exit()
        
        i = None
        for i, clause in reduced_clauses:
            if (len(clause) == 0):                  
                break
        
        if i is not None:               # Conflict!
            conflict_clause = clauses[i]
            for (var, val, idx) in assignment.__reversed__():
                if not conflict_clause.exist(var):
                    continue
                if idx == -1:             # Decision assignment
                    continue
                else:
                    conflict_clause = conflict_clause.resolvant(var, clauses[idx])

            j = len(assignment)
            for var, _1, _2 in assignment.__reversed__():
                del map_var[var]
                if conflict_clause.exist(var):
                    break
                j -= 1
            assignment = assignment[:j]
            clauses.append(conflict_clause)
        else:
            # Use a decision strategy to determine a new assignment p |-> b
            p = abs(reduced_clauses[0].get())
            assignment.append((p, True, -1))           # -1 Means represents assignment is decided.
            map_var[p] = True