from pathlib import Path
from solve import *
import time

bench_dir = Path("./uf20-91")

start = time.time()
for file in bench_dir.iterdir():
    clauses = parse_problem(file)
    dpll = DPLL(clauses)
    result = dpll.run()
    print(result)

end = time.time()
print(end-start)