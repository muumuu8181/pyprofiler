"""
Verify bottleneck improvements
This tests whether fixing the identified bottlenecks actually improves performance
"""
import pyprofiler
import time

print("=" * 80)
print("BEFORE: Using filter + lambda (slow)")
print("=" * 80)

code_before = '''
def filter_method(n):
    return list(filter(lambda x: x % 2 == 0, map(lambda x: x**2, range(n))))

def loop_method(n):
    result = []
    for x in range(n):
        if x % 2 == 0:
            result.append(x**2)
    return result

def list_comp_method(n):
    return [x**2 for x in range(n) if x % 2 == 0]

# Run slow version
for _ in range(5):
    filter_method(1000)
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("AFTER: Using list comprehension (fast)")
print("=" * 80)

code_after = '''
def list_comp_method(n):
    return [x**2 for x in range(n) if x % 2 == 0]

# Run fast version
for _ in range(5):
    list_comp_method(1000)
'''

pyprofiler.run(code_after)
