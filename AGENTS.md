# Review Guidelines

## Code Review Standards

### Security (P0)
- SQL injection vulnerabilities
- Authentication/authorization bypass
- Sensitive data exposure

### Correctness (P0)
- Logic errors that affect core functionality
- Off-by-one errors
- Null pointer/None reference errors

### Performance (P1)
- O(n²) or worse algorithms where O(n) is possible
- Memory leaks
- Inefficient data structures

### Code Quality (P1)
- **PEP 8 violations are P1** (spacing, naming, line length)
- Missing error handling
- Code duplication (DRY violations)
- Missing input validation

### Documentation (P2)
- Missing docstrings for public functions/classes
- **Typos in documentation are P1**

### Best Practices (P1)
- Using deprecated APIs
- Not following language idioms
- Missing logging for critical operations
