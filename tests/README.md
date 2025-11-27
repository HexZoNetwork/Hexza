# Hexza Test Suite

Comprehensive test suite for Hexza Universal Programming Language.

## Test Coverage

- ✅ **test_basics.hxza** - Basic language features (variables, arrays, objects)
- ✅ **test_web.hxza** - Web development (Hexza.Web module)
- ✅ **test_ai.hxza** - AI & machine learning (Hexza.AI module)
- ✅ **test_game.hxza** - Game development (Hexza.Game module)
- ✅ **test_system.hxza** - System operations (Hexza.System module)
- ✅ **test_performance.hxza** - Performance benchmarks

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Individual Test
```bash
hexza tests/test_basics.hxza
hexza tests/test_web.hxza
hexza tests/test_ai.hxza
```

### Run with Benchmark
```bash
hexza tests/test_performance.hxza --benchmark
```

## Expected Output

```
🚀 Hexza Test Suite
Found 6 tests

Test 1: Basic Features
...
✅ Test 1 Passed!

Test 2: Web Development
...
✅ Test 2 Passed!

...

🎉 ALL TESTS PASSED!
```

## Adding New Tests

1. Create file in `tests/` directory: `test_feature.hxza`
2. Follow naming convention: `test_*.hxza`
3. Include pass/fail indicators
4. Run `python run_tests.py`

---

**Everything Can Be Dreamed Can Be Built - SFFF**
