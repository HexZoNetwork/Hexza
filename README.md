# 🚀 Hexza - Universal Programming Language

> **"Everything Can Be Dreamed Can Be Built"**  
> **SFFF: Simple. Fast. Flexible. Free.**

Hexza is the **fastest, simplest, and most flexible programming language** designed to handle **any development task** - from games to web apps, AI to system programming, and everything in between.

**Phase 2 Now Live:** 🔥 **4346x faster** with bytecode VM!

---

## ✨ What Makes Hexza Universal?

- 🎮 **Game Development** - Built-in Pygame wrapper
- 🌐 **Web Development** - Flask/HTTP server included
- 🤖 **AI & Machine Learning** - NumPy integration
- 🖥️ **System Programming** - Direct OS access
- ⚡ **C++ Interop** - Load and call DLLs
- 📜 **JavaScript Integration** - Execute JS via Node.js
- 🔨 **Compile to .exe** - One command compilation
- 🏎️ **Speed Testing** - Built-in benchmarking
- 🚀 **Bytecode VM** - **4346x faster** execution!

---

## 📦 Installation

```bash
# Install Hexza (installs all dependencies automatically)
python install.py

# After installation, restart your terminal and run:
hexza --version
```

---

### Benchmark Performance
```bash
hexza myscript.hxza --benchmark
```

**Results:** 4346x faster with bytecode VM!

---

## 🏎️ Phase 2: Performance

### Benchmark Mode

Compare AST interpreter vs Bytecode VM:

```bash
hexza benchmark.hxza --benchmark
```

**Output:**
```
>> Benchmarking AST vs Bytecode
Testing Phase 2 Performance
Completed: x = 10000

>> Benchmark Results:
   AST Mode:      778.23 ms
   Bytecode Mode:   0.18 ms
   Speedup:       4346.40x faster!
```

---

## 🚀 Quick Start

### Hello World
```hxza
print("Hello from Hexza!")
```

### Run a script
```bash
hexza myscript.hxza
```

### Interactive REPL
```bash
hexza
```

---

## 🎯 Universal Modules

### 🎮 Game Development
```hxza
game = Hexza.Game.init(800, 600, "My Game")
Hexza.Game.draw_rect(game, 100, 100, 50, 50, [255, 0, 0])
Hexza.Game.update(game, 60)
```

### 🌐 Web Development
```hxza
html = """
<html><body><h1>Hello from Hexza!</h1></body></html>
"""
Hexza.Web.serve(html, 8000)
```

### 🤖 AI & Math
```hxza
matrix = Hexza.AI.create_matrix(3, 3, 0)
result = Hexza.AI.sigmoid(2.5)
print(result)
```

### 🖥️ System Operations
```hxza
files = Hexza.System.list_dir(".")
content = Hexza.System.read_file("myfile.txt")
Hexza.System.write_file("output.txt", "Hello!")
```

### ⚡ C++ Integration
```hxza
lib = Hexza.Cpp.load("mylib.dll")
result = Hexza.Cpp.call(lib, "my_function", 42)
```

### 📜 JavaScript Execution
```hxza
result = Hexza.JS.run("console.log('Hello from JS!')")
value = Hexza.JS.eval("2 + 2")
```

---

## 🔨 Compile to Executable

```bash
# Compile your script to a standalone .exe
hexza myscript.hxza --compile myapp
```

---

## 🏎️ Speed Test

```hxza
speedtest()  # Benchmark the interpreter
```

---

## 📚 Documentation

- [**syntax.md**](syntax.md) - Complete language syntax reference
- [**tutorial.md**](tutorial.md) - Step-by-step tutorials

---

## 💡 Example: Full-Stack Game

```hxza
// Initialize game window
game = Hexza.Game.init(800, 600, "Hexza Game")

// Game loop
running = true
x = 100
y = 100

while (running) {
    events = Hexza.Game.get_events()
    
    // Draw rectangle
    Hexza.Game.draw_rect(game, x, y, 50, 50, [0, 255, 0])
    
    // Update display
    Hexza.Game.update(game, 60)
    
    x = x + 1
}
```

---

## 🌟 Features

✅ **Simple syntax** - Familiar to JavaScript/Python developers  
✅ **Fast execution** - Optimized interpreter  
✅ **Flexible** - Works for any domain  
✅ **Free** - Open source  
✅ **Universal** - One language for everything  

---

## 📖 More Info

See [syntax.md](syntax.md) and [tutorial.md](tutorial.md) for complete documentation.

---

**Made with ❤️ by Hexzo**  
*Everything Can Be Dreamed Can Be Built*
