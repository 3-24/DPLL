import sys
from copy import copy
import time

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
            clauses.append(Clause(toks))

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
            for k, v in self.sol.items():
                if v:
                    s = ""
                else:
                    s = "-"
                L.append(s + str(k))
            L.append("0")
            return first_line + " ".join(L)
        else:
            return "s UNSATISFIABLE"


class Clause:
    def __init__(self, iterable):
        self.inner = set(iterable)
        self.undecided = set(iterable)
        self.false = set()
        self.true = set()

    def get(self):
        return next(iter(self.undecided))

    def assign(self, var, value):
        if var in self.inner:
            self.undecided.remove(var)
            if value:
                self.true.add(var)
            else:
                self.false.add(var)
        if -var in self.inner:
            self.undecided.remove(-var)
            if value:
                self.false.add(-var)
            else:
                self.true.add(-var)

    def disassign(self, var, value):
        if value == True:
            if var in self.true:
                self.true.remove(var)
                self.undecided.add(var)
            if -var in self.false:
                self.false.remove(-var)
                self.undecided.add(-var)
        else:
            if var in self.false:
                self.false.remove(var)
                self.undecided.add(var)
            if -var in self.true:
                self.true.remove(-var)
                self.undecided.add(-var)

    def empty(self):
        return len(self.inner) == 0

    def exist(self, var):
        return (var in self.inner) or (-var in self.inner)

    def satisfied(self):
        return len(self.true) >= 1

    def __len__(self):
        assert not self.satisfied()
        return len(self.undecided)

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
        self.positive_clauses = {var: set() for var in range(1, nvars + 1)}
        self.negative_clauses = {var: set() for var in range(1, nvars + 1)}
        self.time = {"learn": 0, "satisfy_check": 0, "propagate": 0}

        for i, clause in enumerate(clauses):
            for literal in clause.inner:
                if literal > 0:
                    self.positive_clauses[literal].add(i)
                else:
                    self.negative_clauses[-literal].add(i)

    def propagate(self, var, value, associated_clause=None):
        if var in self.vmap:
            return None  # Already propagated

        self.vmap[var] = value
        self.assignment.append((var, associated_clause))

        true_clauses = (
            self.positive_clauses[var] if value else self.negative_clauses[var]
        )

        for i in true_clauses:
            clause = self.clauses[i]
            clause.assign(var, value)

        false_clauses = (
            self.negative_clauses[var] if value else self.positive_clauses[var]
        )

        for i in false_clauses:
            clause = self.clauses[i]
            clause.assign(var, value)

            if clause.satisfied():
                continue

            if clause.is_false():
                return i

            elif clause.is_unit():
                literal = clause.get()
                nvar = abs(literal)
                if literal > 0:
                    conflict = self.propagate(nvar, True, i)
                else:
                    conflict = self.propagate(nvar, False, i)
                if conflict is not None:
                    return conflict

        return None

    def preprocess(self):
        for i, clause in enumerate(self.clauses):
            if clause.satisfied():
                continue
            if clause.is_false():
                return False
            if clause.is_unit():
                literal = clause.get()
                var = abs(literal)
                if literal > 0:
                    if self.propagate(var, True, i) is not None:
                        return False
                else:
                    if self.propagate(var, False, i) is not None:
                        return False

        return True

    def satisfied(self):
        for clause in self.clauses:
            if not clause.satisfied():
                return False
        return True

    def learn_clause(self, conflict_clause: Clause):
        learned_clause = Clause(copy(conflict_clause.inner))
        for var, idx in self.assignment.__reversed__():
            if idx is None:  # Decision assignment
                continue
            if not learned_clause.exist(var):
                continue
            else:  # Implied assignment with var
                learned_clause = learned_clause.resolvent(var, self.clauses[idx])

        for literal in learned_clause.inner:
            var = abs(literal)
            if literal > 0:
                self.positive_clauses[var].add(len(self.clauses))
            else:
                self.negative_clauses[var].add(len(self.clauses))

            learned_clause.assign(var, self.vmap[var])

        self.clauses.append(learned_clause)

        return learned_clause

    def backtrack(self, learned_clause: Clause):
        while True:
            var, _ = self.assignment.pop()
            value = self.vmap[var]
            del self.vmap[var]

            for i in self.negative_clauses[var]:
                affected_clause: Clause = self.clauses[i]
                affected_clause.disassign(var, value)

            for i in self.positive_clauses[var]:
                affected_clause: Clause = self.clauses[i]
                affected_clause.disassign(var, value)

            if learned_clause.exist(var):
                break

    def decision(self):
        for clause in self.clauses:
            if not clause.satisfied():
                literal = clause.get()
                var = abs(literal)
                start = time.time()
                conflict = self.propagate(var, True if literal > 0 else False, None)
                end = time.time()
                self.time["propagate"] += end - start
                return conflict

    def run(self):
        if not self.preprocess():
            return Solution(False)

        conflict = None

        while True:
            start = time.time()
            if self.satisfied():
                return Solution(True, self.vmap)
            end = time.time()

            self.time["satisfy_check"] += end - start
            

            if conflict is not None:
                start = time.time()
                learned_clause = self.learn_clause(self.clauses[conflict])
                if learned_clause.empty():
                    return Solution(False)
                self.backtrack(learned_clause)
                end = time.time()
                self.time["learn"] += end - start
                assert learned_clause.is_unit()
                literal = learned_clause.get()
                var = abs(literal)
                start = time.time()
                if literal > 0:
                    conflict = self.propagate(var, True, len(self.clauses) - 1)
                else:
                    conflict = self.propagate(var, False, len(self.clauses) - 1)
                end = time.time()
                self.time["propagate"] += end - start
            else:
                conflict = self.decision()


if __name__ == "__main__":
    dpll = DPLL(*parse_problem(sys.argv[1]))
    result = dpll.run()
    print(result)
