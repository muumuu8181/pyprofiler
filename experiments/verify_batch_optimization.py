"""
Verify improvements for Tests 11-20
"""
import pyprofiler

print("=" * 80)
print("Test 16: String Concatenation - BEFORE")
print("=" * 80)

code_before = '''
def concat_strings(strings):
    result = ''
    for s in strings:
        result += s
    return result

def join_strings(strings):
    return ''.join(strings)

strings = [f'string_{i} ' * 10 for i in range(100)]

concat_strings(strings)
join_strings(strings)
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("Test 16: String Concatenation - AFTER (use join only)")
print("=" * 80)

code_after = '''
def join_strings_optimized(strings):
    return ''.join(strings)

strings = [f'string_{i} ' * 10 for i in range(100)]

# Use only the faster method
for _ in range(2):  # Run twice to match original workload
    join_strings_optimized(strings)
'''

pyprofiler.run(code_after)
