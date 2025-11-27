# Hexza Change Log

All notable changes to Hexza will be documented in this file.

## [2.0.0] - 2025-11-27 - Phase 2 Release 🚀

### Added - Performance & Compilation Features

**Bytecode Compiler & VM:**
- ✅ Complete bytecode instruction set (25 opcodes)
- ✅ BytecodeCompiler - AST → Bytecode translation
- ✅ BytecodeVM - Stack-based execution engine
- ✅ `--benchmark` flag - Compare AST vs Bytecode performance
- ✅ **RESULT: 4346x faster** on computation-heavy code!

**Async Runtime:**
- ✅ EventLoop implementation
- ✅ AsyncTask and coroutine support
- ✅ ScheduledTask for time-based execution
- ✅ Foundation for async/await

**Enhanced Error Reporting:**
- ✅ EnhancedHexzaError with source context
- ✅ Line/column tracking
- ✅ Error highlighting with ^
- ✅ Code snippets in error messages

**Benchmark Results:**
```
Simple Loop (10k iterations):
  AST Mode:      778.23 ms
  Bytecode Mode:   0.18 ms
  Speedup:       4346.40x faster!
```

### Status
- Bytecode VM: Experimental (works great for simple scripts)
- Benchmark mode: Production ready
- Async runtime: Foundation complete

## [1.0.0] - 2025-11-27

### Added - Universal Language Features 🚀

**Core Modules:**
- ✅ `Hexza.Game` - Game development with Pygame integration
- ✅ `Hexza.Web` - Web development with Flask/HTTP server
- ✅ `Hexza.AI` - AI/ML with NumPy matrix operations
- ✅ `Hexza.System` - System operations (file I/O, commands)
- ✅ `Hexza.Cpp` - C++ DLL/library loader for native interop
- ✅ `Hexza.JS` - JavaScript execution via Node.js

**Features:**
- ✅ Compiler command (`--compile`) to generate executables
- ✅ Speed testing with `speedtest()` function
- ✅ Package manager with pip/npm integration
- ✅ Automatic dependency installation

**Documentation:**
- ✅ README.md - Universal language overview
- ✅ syntax.md - Complete language reference
- ✅ tutorial.md - 8 hands-on tutorials
- ✅ api.md - Standard library API documentation
- ✅ ROADMAP.md - Development roadmap with priorities
- ✅ LICENSE - MIT License
- ✅ CONTRIBUTING.md - Contribution guidelines
- ✅ CONTRIBUTORS.md - Contributor recognition

**Installer:**
- ✅ Windows installation support
- ✅ Linux installation support
- ✅ Automatic dependency installation (pygame, flask, numpy, pyinstaller)

### Philosophy

**SFFF - Simple, Fast, Flexible, Free**
- Simple: Clean syntax, easy to learn
- Fast: Optimized for performance
- Flexible: Universal - works for any domain
- Free: Open source MIT license

**Mission:** Everything Can Be Dreamed Can Be Built

---

## [Planned] - Future Releases

### [2.0.0] - Phase 1: Performance

**P1 Critical:**
- [ ] Bytecode Interpreter (10-100x faster)
- [ ] JIT Compiler (LLVM integration)
- [ ] Async Runtime (functional async/await)
- [ ] Error Reporting (rich error messages)

**P2 High:**
- [ ] Green Threads/Fibers
- [ ] Reference Counting
- [ ] Optional Static Types

### [3.0.0] - Phase 2: Native Compilation

**P1 Critical:**
- [ ] LLVM Backend
- [ ] Advanced FFI
- [ ] True native compilation

**P2 High:**
- [ ] Full-stack web framework
- [ ] Advanced package manager

### [4.0.0] - Phase 3: Universal Ecosystem

**Planned:**
- [ ] OS development module
- [ ] GPU acceleration
- [ ] Game engine abstraction
- [ ] IDE/Language server

---

## Version History

- **1.0.0** (2025-11-27) - Universal Language Release
  - First stable release with universal modules
  - Complete documentation suite
  - Open source under MIT license

---

**Everything Can Be Dreamed Can Be Built - SFFF** 🚀
