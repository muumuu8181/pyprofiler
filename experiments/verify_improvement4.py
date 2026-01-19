"""
Verify sorting algorithms improvement
"""
import pyprofiler

print("=" * 80)
print("Test 7: Sorting - BEFORE (bubble sort - slow)")
print("=" * 80)

code_before = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test sorting
data = list(range(50, 0, -1))
for _ in range(10):
    bubble_sort(data.copy())
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("Test 7: Sorting - AFTER (using built-in sort - fast)")
print("=" * 80)

code_after = '''
def builtin_sort(arr):
    return sorted(arr)

# Test sorting
data = list(range(50, 0, -1))
for _ in range(10):
    builtin_sort(data.copy())
'''

pyprofiler.run(code_after)
