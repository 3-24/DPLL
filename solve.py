import sys
from copy import copy

def parse_problem(filename):
    with open(filename) as f:
        lines = f.readlines()

    for i in range(len(lines) - 1):
        if lines[i] == "%\n" and lines[i + 1] == "0\n":
            lines = lines[:i]
            break

    clauses = []
    for line in lines:
        if line[0] == "c":  # comment
            continue
        if line[0] == "p":
            toks = line.split()
            assert toks[1] == "cnf"
            assert len(toks) == 4
            num_vars, num_clauses = map(int, (toks[2], toks[3]))
        else:
            toks = list(map(int, line.split()))
            assert toks[-1] == 0
            toks.pop()
            clauses.append(Clause.default_clause(toks))

    assert num_clauses == len(clauses)

    return clauses, num_vars


class Solution:
    def __init__(self, sat, sol=None):
        self.sat = sat
        self.sol = sol

    def __repr__(self):
        if self.sat:
            first_line = "s SATISFIABLE\n"
            L = ["v"]
            for s in self.sol:
                L.append(str(s))
            L.append("0")
            return first_line + " ".join(L)
        else:
            return "s UNSATISFIABLE"


class Clause:
    def __init__(
        self, inner=None, undecided=None, true=None, false=None, watched_literals=None
    ):
        self.inner = inner if inner is not None else set()
        self.undecided = undecided if undecided is not None else set()
        self.true = true if true is not None else set()
        self.false = false if false is not None else set()
        self.watched_literals = watched_literals if watched_literals is not None else set()

    @classmethod
    def default_clause(cls, iterable):
        clause = cls(inner=set(iterable), undecided=set(iterable))

        if len(clause.undecided) <= 2:
            clause.watched_literals = copy(clause.undecided)
        else:
            it = iter(clause.undecided)
            clause.watched_literals = set((next(it), next(it)))

        return clause

    def __repr__(self):
        return "{" + ", ".join(
            map(lambda i: f"*{i}{'=T' if i in self.true else ''}{'=F' if i in self.false else ''}", self.inner)
            ) + "}"

    def get(self):
        return next(iter(self.undecided))

    def disassign(self, literal):
        assert(literal in self.true ^ literal in self.false)
        self.true.discard(literal)
        self.false.discard(literal)
        self.undecided.add(literal)

    def empty(self):
        return len(self.inner) == 0

    def exist(self, var):
        return (var in self.inner) or (-var in self.inner)

    def is_true(self):
        return len(self.true) >= 1

    def is_false(self):
        return len(self.false) == len(self.inner)

    def is_unit(self):
        return len(self.true) == 0 and len(self.undecided) == 1

    def resolvent(self, var, clause):
        new_inner = set(self.inner).union(set(clause.inner))
        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(inner=new_inner)          # Will assign undecided / false later


class DPLL:
    def __init__(self, clauses, nvars):
        self.clauses = clauses
        self.assignment = []
        self.vmap = set()
        self.updates = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.watched_literal_to_clause = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.literal_to_clause = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.unit = []  # unit clauses
        self.update_watch_queue = []

        for i, clause in enumerate(clauses):
            if clause.is_unit():
                self.unit.append((i, False))
            for literal in clause.inner:
                self.literal_to_clause[literal].add(i)
            for literal in clause.watched_literals:
                self.watched_literal_to_clause[literal].add(i)

    def value(self, literal):
        if literal in self.vmap:
            return True
        elif -literal in self.vmap:
            return False
        else:
            return None
    
    def update_literal(self, i, literal, val):
        clause: Clause = self.clauses[i]
        clause.undecided.remove(literal)
        if val:
            clause.true.add(literal)
        else:
            clause.false.add(literal)
        
        if literal in clause.watched_literals:
            clause.watched_literals.remove(literal)
            self.watched_literal_to_clause[literal].remove(i)
            self.update_watch_queue.append(i)
            
    
    def update_watched_literal(self):
        while (len(self.update_watch_queue) != 0):
            i = self.update_watch_queue.pop()
            clause: Clause = self.clauses[i]
            for literal in copy(clause.undecided):
                if literal in clause.watched_literals:
                    continue
                new_val = self.value(literal)
                if new_val is None:
                    clause.watched_literals.add(literal)
                    self.watched_literal_to_clause[literal].add(i)
                    return None
                elif new_val is False:
                    clause.undecided.remove(literal)
                    clause.false.add(literal)
                else:
                    assert(False)
            
            if clause.is_unit():
                self.unit.append((i, False))

    def unit_prop(self):
        while (len(self.unit) > 0):
            i, decision = self.unit.pop()
            clause = self.clauses[i]
            if len(clause.false) != 1:
                continue
            elif clause.is_true():
                continue
            
            literal = clause.get()
            assert(not (-literal in self.vmap))
            self.vmap.add(literal)
            self.assignment.append((literal, None if decision else i))
            
            for j in self.literal_to_clause[literal]:
                self.update_literal(j, literal, True)
            
            for j in copy(self.watched_literal_to_clause[-literal]):
                false_clause: Clause = self.clauses[j]
                self.update_literal(j, -literal, False)
                if false_clause.is_false():
                    self.unit.clear()
                    return j
                if false_clause.is_unit():
                    self.unit.append((j, False))
            
            self.update_watched_literal()

        return None
    
    
    def satisfied(self):
        for clause in self.clauses:
            if not clause.is_true():
                return False
        return True

    def learn_clause(self, conflict_clause: Clause):
        learned_clause: Clause = conflict_clause
        for var, idx in self.assignment.__reversed__():
            if idx is None:  # Decision assignment
                continue
            if not learned_clause.exist(var):
                continue
            else:  # Implied assignment with var
                # print(f"Learning iter: {learned_clause}, {self.clauses[idx]}")
                learned_clause = learned_clause.resolvent(var, self.clauses[idx])

        n = len(self.clauses)

        for literal in learned_clause.inner:
            self.literal_to_clause[literal].add(n)
            self.updates[literal].add(n)
            assert(self.map_literal(literal) is False)
            learned_clause.false.add(literal)

        self.clauses.append(learned_clause)

        return learned_clause

    def backtrack(self, learned_clause: Clause):
        while True:
            literal, _ = self.assignment.pop()
            self.vmap.remove(literal)

            while len(self.updates[literal]) != 0:
                i = self.updates[literal].pop()
                clause: Clause = self.clauses[i]
                clause.disassign(literal)
                if len(clause.watched_literals) < 2:
                    clause.watched_literals.add(literal)
                    self.watched_literal_to_clause[literal].add(i)

            while len(self.updates[-literal]) != 0:
                i = self.updates[-literal].pop()
                clause: Clause = self.clauses[i]
                clause.disassign(-literal)
                if len(clause.watched_literals) < 2:
                    clause.watched_literals.add(-literal)
                    self.watched_literal_to_clause[-literal].add(i)

            if learned_clause.exist(literal):
                break

    def decision(self):
        for i, clause in enumerate(self.clauses):
            if not clause.is_true():
                literal = clause.get()
                self.vmap.add(literal)
                self.unit.append((i, True))
                break

    def run(self):
        preprocess = True
        while True:
            print(self.unit)
            #print(f"Current Solution: {self.vmap}")
            #print(f"Assignments: {self.assignment}")
            
            conflict = self.unit_prop()
            print(f"Clauses: {self.clauses}")
            input()
            
            if preprocess:
                if conflict is not None:
                    return Solution(False)
                preprocess = False

            if self.satisfied():
                return Solution(True, self.vmap)

            if conflict is not None:
                assert(self.clauses[conflict].is_false())
                learned_clause = self.learn_clause(self.clauses[conflict])
                #print(f"Learned {self.clauses[conflict]} -> {learned_clause}")
                if learned_clause.empty():
                    return Solution(False)
                self.backtrack(learned_clause)
                #print(f"Backtrack {learned_clause}")
                assert learned_clause.is_unit()
                self.unit.append((len(self.clauses)-1, False))
            else:
                self.decision()


if __name__ == "__main__":
    dpll = DPLL(*parse_problem(sys.argv[1]))
    result = dpll.run()
    print(result)
