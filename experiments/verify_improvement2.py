"""
Verify more bottleneck improvements
"""
import pyprofiler

print("=" * 80)
print("Test 3: Matrix Operations - BEFORE")
print("=" * 80)

code_before = '''
def multiply_matrices(a, b):
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(b[0])):
            sum_val = 0
            for k in range(len(b)):
                sum_val += a[i][k] * b[k][j]
            row.append(sum_val)
        result.append(row)
    return result

def create_matrix(n, m):
    return [[i*j for j in range(m)] for i in range(n)]

# Create and multiply 5x5 matrices
mat1 = create_matrix(5, 5)
mat2 = create_matrix(5, 5)
for _ in range(10):
    multiply_matrices(mat1, mat2)
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("Test 3: Matrix Operations - AFTER (using list comprehension)")
print("=" * 80)

code_after = '''
def multiply_matrices_optimized(a, b):
    # Optimized with list comprehension and zip
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))]
            for i in range(len(a))]

def create_matrix(n, m):
    return [[i*j for j in range(m)] for i in range(n)]

# Create and multiply 5x5 matrices
mat1 = create_matrix(5, 5)
mat2 = create_matrix(5, 5)
for _ in range(10):
    multiply_matrices_optimized(mat1, mat2)
'''

pyprofiler.run(code_after)
