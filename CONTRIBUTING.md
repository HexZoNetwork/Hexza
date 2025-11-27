# Contributing to Hexza

Thank you for your interest in contributing to Hexza! This document provides guidelines for contributing to this open-source universal programming language.

## Mission

**Everything Can Be Dreamed Can Be Built - SFFF (Simple, Fast, Flexible, Free)**

## Code of Conduct

Be respectful, constructive, and collaborative. We're building something amazing together!

## How to Contribute

### 1. Pick a Task from ROADMAP.md

We organize tasks by priority:
- **P1 (Critical)** - Core functionality, highest impact
- **P2 (High)** - Important for production readiness
- **P3 (Medium)** - Nice-to-have features

Start with P1 tasks for maximum impact!

### 2. Development Setup

```bash
# Clone the repository
git clone https://github.com/hexzo/hexza.git
cd hexza

# Install development dependencies
python install.py

# Run tests
python hexza.py test.hxza
```

### 3. Making Changes

1. **Create a branch** for your feature/fix
   ```bash
   git checkout -b feature/bytecode-vm
   ```

2. **Make your changes** to the codebase
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation

3. **Test your changes**
   ```bash
   python hexza.py test.hxza
   python hexza.py --version
   ```

4. **Commit your changes**
   ```bash
   git commit -m "Add bytecode interpreter foundation"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/bytecode-vm
   ```

### 4. Code Style

- **Python code**: Follow PEP 8 where reasonable
- **Hexza code**: Follow examples in `tutorial.md`
- **Keep it simple**: SFFF principle applies to code too!

## Priority Areas for Contribution

### Phase 1: Core Performance (P1 Critical)

**Most Impactful Right Now:**

1. **Bytecode Interpreter**
   - Design bytecode instruction set
   - Implement bytecode compiler
   - Build bytecode VM
   - Target: 10x speed improvement

2. **Error Reporting**
   - Add line/column tracking
   - Show code snippets in errors
   - Add helpful suggestions
   - Improve stack traces

3. **Async Runtime**
   - Implement event loop
   - Make async/await functional
   - Add coroutine scheduling

4. **JIT Compiler**
   - LLVM integration research
   - Hot-path detection
   - Native code generation

### Phase 2: Native Compilation (P1 Critical)

1. **LLVM Backend**
   - AST to LLVM IR translation
   - Optimization passes
   - Native code generation

2. **FFI (Foreign Function Interface)**
   - C header parser
   - Safe foreign calls
   - Type marshalling

### Phase 3: Ecosystem

1. **Full-Stack Web Framework**
2. **Package Manager Improvements**
3. **Testing Framework**
4. **Code Formatter/Linter**

## Project Structure

```
hexza/
├── hexza.py           # Main interpreter
├── install.py         # Installer script
├── README.md          # Project overview
├── syntax.md          # Language reference
├── tutorial.md        # Learning guide
├── api.md             # Standard library API
├── ROADMAP.md         # Development plan
├── LICENSE            # MIT License
├── CONTRIBUTING.md    # This file
└── test.hxza          # Test suite
```

## Testing Guidelines

All contributions should:
- Not break existing tests
- Add new tests for new features
- Run `python hexza.py test.hxza` successfully

## Documentation

When adding features:
- Update `syntax.md` for new syntax
- Update `api.md` for new APIs
- Add examples to `tutorial.md`
- Update `README.md` if needed

## Pull Request Process

1. **Describe your changes** clearly
2. **Link to related issues** or roadmap items
3. **Include test results**
4. **Update documentation**
5. **Be patient** - we'll review as soon as possible!

## Questions?

- Create an issue for discussion
- Tag it with appropriate labels (P1, P2, P3)
- Reference ROADMAP.md for context

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Part of Hexza history!

## Development Priorities

### Immediate (This Quarter)

- [ ] Bytecode Interpreter
- [ ] Error Reporting System
- [ ] Async Runtime Implementation

### Next Quarter

- [ ] JIT Compiler (LLVM)
- [ ] Optional Type System
- [ ] LLVM Backend

### Long Term

- [ ] Full OS Development Support
- [ ] GPU Acceleration
- [ ] Game Engine Module

---

**Everything Can Be Dreamed Can Be Built!**

Thank you for contributing to Hexza! Together we're building the universal programming language that can truly do anything.

SFFF - Simple, Fast, Flexible, Free 🚀
