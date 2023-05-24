print("\n")
print("hello world!")

import subprocess
print("\nRunning test.h to check if it works...")

#use this pattern to get a dashing output for sequences
output = subprocess.call(['sh', './test.sh'])

print(f"The output of calling test.sh is {output}")

print("\nTesting if Concrete-ML was properly installed...")

import sys
from concrete.ml.sklearn import LogisticRegression

print('LogisticRegression' in sys.modules)