from pathlib import Path
from solve import *
import time
import sys

def add_time(a, b):
    if a is None:
        return b
    else:
        c = {}
        for k in b:
            c[k] = a[k] + b[k]
        return c

bench_dir = Path(sys.argv[1])

total_time = None

start = time.time()
for file in bench_dir.iterdir():
    print(file)
    dpll = DPLL(*parse_problem(file))
    result = dpll.run()
    total_time = add_time(total_time, dpll.time)
    print(result)

end = time.time()
print(end-start)
print(total_time)