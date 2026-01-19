"""
Verify dictionary operations improvement
"""
import pyprofiler

print("=" * 80)
print("Test 4: Dictionary Operations - BEFORE (inefficient)")
print("=" * 80)

code_before = '''
def find_duplicates(items):
    seen = {}
    duplicates = []
    for item in items:
        key = item['name']
        if key in seen:
            duplicates.append(item)
        else:
            seen[key] = True
    return duplicates

def build_lookup(data):
    lookup = {}
    for item in data:
        key = item['id']
        lookup[key] = item
    return lookup

# Create sample data and process
data = [{'id': i, 'name': f'item_{i % 100}'} for i in range(1000)]
build_lookup(data)
find_duplicates(data)
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("Test 4: Dictionary Operations - AFTER (optimized)")
print("=" * 80)

code_after = '''
def find_duplicates_optimized(items):
    seen = set()
    duplicates = []
    for item in items:
        key = item['name']
        if key in seen:
            duplicates.append(item)
        else:
            seen.add(key)
    return duplicates

def build_lookup_optimized(data):
    return {item['id']: item for item in data}

# Create sample data and process
data = [{'id': i, 'name': f'item_{i % 100}'} for i in range(1000)]
build_lookup_optimized(data)
find_duplicates_optimized(data)
'''

pyprofiler.run(code_after)
