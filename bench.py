from pathlib import Path
from solve import *
import time
import sys

bench_dir = Path(sys.argv[1])

start = time.time()
for file in bench_dir.iterdir():
    dpll = DPLL(*parse_problem(file))
    result = dpll.run()
    print(result)

end = time.time()
print(end-start)