import sys
from copy import copy

Debug = False

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

    def disassign(self, literal):
        self.true.discard(literal)
        self.false.discard(literal)
        self.undecided.add(literal)

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
        def process(i):
            s = ""
            if i in self.watched_literals:
                s += "*"
            s += str(i)
            if i in self.true:
                s += "=T"
            elif i in self.false:
                s += "=F"
            return s

        return "{" + ", ".join(map(process, self.inner)) + "}"

    def is_false(self):
        return len(self) == 0

    def is_unit(self):
        return len(self) == 1

    def resolvent(self, var, clause):
        new_inner = set(self.inner).union(set(clause.inner))
        new_inner.remove(var)
        new_inner.remove(-var)
        return Clause(inner=new_inner)


class DPLL:
    def __init__(self, clauses, nvars):
        self.clauses = clauses
        self.assignment = []
        self.vmap = {}
        self.time = {"learn": 0, "satisfy_check": 0, "propagate": 0}
        self.watcher = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.updates = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.literals = {literal: set() for literal in range(-nvars - 1, nvars + 1)}
        self.unit = []  # unit clauses used in preprocessing

        for i, clause in enumerate(clauses):
            if clause.is_unit():
                self.unit.append(i)
            for literal in clause.inner:
                self.literals[literal].add(i)
            for literal in clause.watched_literals:
                self.watcher[literal].add(i)

    def map_literal(self, literal):
        var = abs(literal)
        if not var in self.vmap:
            return None
        else:
            val = self.vmap[var]
            return val if literal > 0 else (not val)

    def update_literal(self, i, literal, value):
        clause: Clause = self.clauses[i]
        clause.undecided.remove(literal)
        if value:
            clause.true.add(literal)
        else:
            clause.false.add(literal)
        self.updates[literal].add(i)
        if literal in clause.watched_literals:
            clause.watched_literals.remove(literal)
            self.watcher[literal].remove(i)
            
            # Decide new watched literal
            for undecided_literal in copy(clause.undecided):
                if undecided_literal in clause.watched_literals:
                    continue
                val = self.map_literal(undecided_literal)
                # Lazy undecided
                if val is None:
                    clause.watched_literals.add(undecided_literal)
                    self.watcher[undecided_literal].add(i)
                    return None  # Exit normally
                else:
                    assert(val is False)
                    # This is not watched literal
                    clause.undecided.remove(undecided_literal)
                    clause.false.add(literal)

    def unit_prop(self, decision=False):
        while (len(self.unit) > 0):
            i = self.unit.pop()
            clause = self.clauses[i]
            literal = clause.get()
            var, value = (literal, True) if literal > 0 else (-literal, False)
            
            if var in self.vmap:
                assert(var == self.vmap[var])
                self.update_literal(i, literal, self.vmap[var])
                continue

            self.vmap[var] = value
            self.assignment.append((var, None if decision else i))
            
            for j in self.literals[literal]:
                true_clause: Clause = self.clauses[j]
                if true_clause.satisfied():
                    continue
                self.update_literal(j, literal, True)
            
            for j in copy(self.watcher[-literal]):
                false_clause: Clause = self.clauses[j]
                if false_clause.satisfied():
                    continue
                self.update_literal(j, -literal, False)
                if false_clause.satisfied():
                    continue
                if false_clause.is_false():
                    self.unit.clear()
                    return j
                if false_clause.is_unit():
                    self.unit.append(j)

        return None

    def satisfied(self):
        for clause in self.clauses:
            if not clause.satisfied():
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
                if Debug:
                    print(f"Learning iter: {learned_clause}, {self.clauses[idx]}")
                learned_clause = learned_clause.resolvent(var, self.clauses[idx])

        n = len(self.clauses)

        for literal in learned_clause.inner:
            self.literals[literal].add(n)
            self.updates[literal].add(n)
            assert(self.map_literal(literal) is False)
            learned_clause.false.add(literal)

        self.clauses.append(learned_clause)

        return learned_clause

    def backtrack(self, learned_clause: Clause):
        while True:
            var, _ = self.assignment.pop()
            del self.vmap[var]

            while len(self.updates[var]) != 0:
                i = self.updates[var].pop()
                clause: Clause = self.clauses[i]
                clause.disassign(var)
                if len(clause.watched_literals) < 2:
                    clause.watched_literals.add(var)
                    self.watcher[var].add(i)

            while len(self.updates[-var]) != 0:
                i = self.updates[-var].pop()
                clause: Clause = self.clauses[i]
                clause.disassign(-var)
                if len(clause.watched_literals) < 2:
                    clause.watched_literals.add(-var)
                    self.watcher[-var].add(i)

            if learned_clause.exist(var):
                break

    def decision(self):
        for i, clause in enumerate(self.clauses):
            if not clause.satisfied():
                literal = clause.get()
                self.update_literal(i, literal, True)
                break

    def run(self):
        preprocess = True
        while True:
            if Debug:
                print(f"Clauses: {self.clauses}")
                print(f"Current Solution: {self.vmap}")
                print(f"Assignments: {self.assignment}")
            
            conflict = self.unit_prop()
            if preprocess:
                if conflict is not None:
                    return Solution(False)
                preprocess = False

            if self.satisfied():
                return Solution(True, self.vmap)

            if conflict is not None:
                assert(self.clauses[conflict].is_false())
                learned_clause = self.learn_clause(self.clauses[conflict])
                if Debug:
                    print(f"Learned {self.clauses[conflict]} -> {learned_clause}")
                if learned_clause.empty():
                    return Solution(False)
                self.backtrack(learned_clause)
                if Debug:
                    print(f"Backtrack {learned_clause}")
                assert learned_clause.is_unit()
                self.unit.append(len(self.clauses)-1)
            else:
                self.decision()


if __name__ == "__main__":
    dpll = DPLL(*parse_problem(sys.argv[1]))
    result = dpll.run()
    print(result)
