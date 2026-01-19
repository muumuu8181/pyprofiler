"""
Verify Test 17: Logging Overhead Optimization
"""
import pyprofiler

print("=" * 80)
print("Test 17: Logging - BEFORE (always log)")
print("=" * 80)

code_before = '''
class Logger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        import time
        timestamp = time.time()
        self.logs.append(f'{timestamp}: {message}')

    def log_debug(self, message):
        self.log(f'[DEBUG] {message}')

    def log_info(self, message):
        self.log(f'[INFO] {message}')

    def log_warning(self, message):
        self.log(f'[WARN] {message}')

logger = Logger()
for i in range(100):
    logger.log_debug(f'Debug message {i}')

for i in range(50):
    logger.log_info(f'Info message {i}')

for i in range(10):
    logger.log_warning(f'Warning message {i}')
'''

pyprofiler.run(code_before)

print("\n" + "=" * 80)
print("Test 17: Logging - AFTER (with level filtering)")
print("=" * 80)

code_after = '''
class OptimizedLogger:
    def __init__(self, level='INFO'):
        self.logs = []
        self.level = level
        self.levels = {'DEBUG': 0, 'INFO': 1, 'WARN': 2}

    def log(self, message, level='INFO'):
        if self.levels[level] >= self.levels[self.level]:
            import time
            timestamp = time.time()
            self.logs.append(f'{timestamp}: {message}')

    def log_debug(self, message):
        self.log(f'[DEBUG] {message}', 'DEBUG')

    def log_info(self, message):
        self.log(f'[INFO] {message}', 'INFO')

    def log_warning(self, message):
        self.log(f'[WARN] {message}', 'WARN')

logger = OptimizedLogger(level='INFO')  # Skip DEBUG logs
for i in range(100):
    logger.log_debug(f'Debug message {i}')  # These will be skipped

for i in range(50):
    logger.log_info(f'Info message {i}')

for i in range(10):
    logger.log_warning(f'Warning message {i}')
'''

pyprofiler.run(code_after)
