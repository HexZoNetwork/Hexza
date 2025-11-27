# Hexza Standard Library API Reference

> **Version:** 1.0  
> **Everything Can Be Dreamed Can Be Built - SFFF**

This document provides complete API documentation for all Hexza standard library modules.

---

## Table of Contents

1. [Built-in Functions](#built-in-functions)
2. [Hexza.Game - Game Development](#hexzagame)
3. [Hexza.Web - Web Development](#hexzaweb)
4. [Hexza.AI - AI & Machine Learning](#hexzaai)
5. [Hexza.System - System Operations](#hexzasystem)
6. [Hexza.Cpp - C++ Interoperability](#hexzacpp)
7. [Hexza.JS - JavaScript Integration](#hexzajs)

---

## Built-in Functions

### Core Functions

#### `print(...args)`
Print values to console.

```hxza
print("Hello")
print("Value:", 42)
```

#### `len(obj)`
Get length of array, string, or object.

```hxza
len([1, 2, 3])  // 3
len("hello")    // 5
```

#### `range(start, end?, step?)`
Generate a range of numbers.

```hxza
range(5)         // [0, 1, 2, 3, 4]
range(1, 5)      // [1, 2, 3, 4]
range(0, 10, 2)  // [0, 2, 4, 6, 8]
```

### Type Conversion

#### `str(obj)` → string
Convert to string.

#### `int(obj)` → integer
Convert to integer.

#### `float(obj)` → float
Convert to floating point.

#### `bool(obj)` → boolean
Convert to boolean.

#### `list(obj)` → array
Convert to array.

#### `dict(obj)` → object
Convert to object/dictionary.

#### `type(obj)` → string
Get type name.

```hxza
type(42)        // "int"
type("hello")   // "str"
type([1,2,3])  // "list"
```

### Math Functions

#### `abs(x)` → number
Absolute value.

```hxza
abs(-5)  // 5
```

#### `min(...args)` → number
Minimum value.

```hxza
min(3, 1, 4, 1, 5)  // 1
```

#### `max(...args)` → number
Maximum value.

```hxza
max(3, 1, 4, 1, 5)  // 5
```

#### `sum(iterable)` → number
Sum of values.

```hxza
sum([1, 2, 3, 4])  // 10
```

#### `round(x, ndigits?)` → number
Round to n digits.

```hxza
round(3.14159, 2)  // 3.14
```

### Performance

#### `speedtest(iterations?)`
Benchmark interpreter performance.

```hxza
speedtest()           // Default 1M iterations
speedtest(100000)     // Custom iterations
```

**Returns:** dict with timing results
```hxza
{
    "iterations": 1000000,
    "arithmetic_ms": 162.29,
    "function_ms": 2.3,
    "list_ms": 1.25,
    "total_ms": 165.84
}
```

---

## Hexza.Game

Game development module powered by Pygame.

### Installation
```bash
hexza --install pygame
```

### Functions

#### `Hexza.Game.init(width, height, title)` → game
Initialize game window.

**Parameters:**
- `width` (int) - Window width in pixels
- `height` (int) - Window height in pixels
- `title` (string) - Window title

**Returns:** Game object with screen, pygame, clock

```hxza
game = Hexza.Game.init(800, 600, "My Game")
```

#### `Hexza.Game.draw_rect(game, x, y, w, h, color)`
Draw a rectangle.

**Parameters:**
- `game` - Game object from init()
- `x` (int) - X position
- `y` (int) - Y position
- `w` (int) - Width
- `h` (int) - Height
- `color` (array) - RGB color [r, g, b]

```hxza
Hexza.Game.draw_rect(game, 100, 100, 50, 50, [255, 0, 0])  // Red square
```

#### `Hexza.Game.update(game, fps)`
Update display and tick clock.

**Parameters:**
- `game` - Game object
- `fps` (int) - Target frames per second

```hxza
Hexza.Game.update(game, 60)  // 60 FPS
```

#### `Hexza.Game.get_events()` → array
Get input events.

**Returns:** Array of Pygame events

```hxza
events = Hexza.Game.get_events()
for (event in events) {
    // Handle event
}
```

### Example: Simple Game

```hxza
game = Hexza.Game.init(800, 600, "Hexza Game")
x = 100
running = true

while (running) {
    events = Hexza.Game.get_events()
    
    // Clear screen (black background)
    Hexza.Game.draw_rect(game, 0, 0, 800, 600, [0, 0, 0])
    
    // Draw moving rect
    Hexza.Game.draw_rect(game, x, 100, 50, 50, [0, 255, 0])
    
    Hexza.Game.update(game, 60)
    x = x + 2
}
```

---

## Hexza.Web

Web development module with HTTP server and client.

### Installation
```bash
hexza --install flask
```

### Functions

#### `Hexza.Web.serve(html_content, port?)` 
Serve HTML/CSS content.

**Parameters:**
- `html_content` (string) - HTML to serve
- `port` (int, optional) - Port number (default: 8000)

```hxza
html = """
<!DOCTYPE html>
<html>
<head><title>Hexza Web</title></head>
<body>
    <h1>Hello from Hexza!</h1>
</body>
</html>
"""

Hexza.Web.serve(html, 8000)
```

#### `Hexza.Web.fetch(url, method?, data?)` → string
HTTP client request.

**Parameters:**
- `url` (string) - URL to fetch
- `method` (string, optional) - HTTP method (default: "GET")
- `data` (object, optional) - Request body data

**Returns:** Response body as string

```hxza
// GET request
response = Hexza.Web.fetch("https://api.example.com/data")

// POST request
response = Hexza.Web.fetch(
    "https://api.example.com/create",
    "POST",
    {"name": "Hexza"}
)
```

### Example: Web Server

```hxza
html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 50px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Hexza Web Framework</h1>
    <p>Simple. Fast. Flexible. Free.</p>
</body>
</html>
"""

Hexza.Web.serve(html, 8080)
```

---

## Hexza.AI

AI and machine learning module powered by NumPy.

### Installation
```bash
hexza --install numpy
```

### Functions

#### `Hexza.AI.create_matrix(rows, cols, fill)` → matrix
Create a matrix filled with a value.

**Parameters:**
- `rows` (int) - Number of rows
- `cols` (int) - Number of columns
- `fill` (number) - Fill value

**Returns:** NumPy array (or nested list if NumPy not installed)

```hxza
matrix = Hexza.AI.create_matrix(3, 3, 0)
// [[0, 0, 0],
//  [0, 0, 0],
//  [0, 0, 0]]
```

#### `Hexza.AI.matrix_mult(a, b)` → matrix
Matrix multiplication.

**Parameters:**
- `a` (matrix) - First matrix
- `b` (matrix) - Second matrix

**Returns:** Product matrix

```hxza
a = Hexza.AI.create_matrix(2, 2, 1)
b = Hexza.AI.create_matrix(2, 2, 2)
result = Hexza.AI.matrix_mult(a, b)
```

#### `Hexza.AI.sigmoid(x)` → number
Sigmoid activation function.

**Parameters:**
- `x` (number) - Input value

**Returns:** Sigmoid of x: 1 / (1 + e^(-x))

```hxza
Hexza.AI.sigmoid(0)     // 0.5
Hexza.AI.sigmoid(2.5)   // 0.924
Hexza.AI.sigmoid(-2.5)  // 0.076
```

### Example: Neural Network Math

```hxza
// Create weight matrix
weights = Hexza.AI.create_matrix(3, 2, 0.5)

// Create input
input = Hexza.AI.create_matrix(2, 1, 1.0)

// Forward pass
output = Hexza.AI.matrix_mult(weights, input)

// Apply activation
for (i = 0; i < len(output); i = i + 1) {
    activated = Hexza.AI.sigmoid(output[i][0])
    print("Neuron " + str(i) + ": " + str(activated))
}
```

---

## Hexza.System

System operations module for OS interaction.

### Functions

#### `Hexza.System.run(command)` → object
Execute system command.

**Parameters:**
- `command` (string) - Shell command to execute

**Returns:** Object with stdout, stderr, code

```hxza
result = Hexza.System.run("echo Hello")
print(result.stdout)  // "Hello\n"
print(result.code)    // 0
```

#### `Hexza.System.read_file(path)` → string
Read file contents.

**Parameters:**
- `path` (string) - File path

**Returns:** File contents as string

```hxza
content = Hexza.System.read_file("data.txt")
print(content)
```

#### `Hexza.System.write_file(path, content)` → boolean
Write file contents.

**Parameters:**
- `path` (string) - File path
- `content` (string) - Content to write

**Returns:** true on success, error message on failure

```hxza
Hexza.System.write_file("output.txt", "Hello from Hexza!")
```

#### `Hexza.System.list_dir(path?)` → array
List directory contents.

**Parameters:**
- `path` (string, optional) - Directory path (default: ".")

**Returns:** Array of filenames

```hxza
files = Hexza.System.list_dir(".")
for (file in files) {
    print(file)
}
```

### Example: File Processing

```hxza
// Read input
data = Hexza.System.read_file("input.txt")

// Process
processed = data + "\nProcessed by Hexza!"

// Write output
Hexza.System.write_file("output.txt", processed)

// List results
files = Hexza.System.list_dir(".")
print("Files created:")
for (file in files) {
    if (file == "output.txt") {
        print("  ✓ " + file)
    }
}
```

---

## Hexza.Cpp

C++ DLL/shared library loader for native interop.

### Functions

#### `Hexza.Cpp.load(library_path)` → library
Load C++ library.

**Parameters:**
- `library_path` (string) - Path to .dll (Windows) or .so (Linux)

**Returns:** Library object

```hxza
lib = Hexza.Cpp.load("mylib.dll")
```

#### `Hexza.Cpp.call(lib, function_name, ...args)` → any
Call C++ function.

**Parameters:**
- `lib` - Library object from load()
- `function_name` (string) - Function name
- `...args` - Function arguments

**Returns:** Function return value

```hxza
result = Hexza.Cpp.call(lib, "add", 10, 20)
print(result)  // 30
```

### Example: Using C++ Library

**C++ Library (mymath.cpp):**
```cpp
extern "C" {
    int add(int a, int b) {
        return a + b;
    }
    
    double sqrt(double x) {
        return ::sqrt(x);
    }
}
```

**Compile:**
```bash
# Windows
g++ -shared -o mymath.dll mymath.cpp

# Linux
g++ -shared -fPIC -o mymath.so mymath.cpp
```

**Hexza Code:**
```hxza
lib = Hexza.Cpp.load("mymath.dll")

sum = Hexza.Cpp.call(lib, "add", 15, 27)
print("15 + 27 = " + str(sum))

root = Hexza.Cpp.call(lib, "sqrt", 16.0)
print("sqrt(16) = " + str(root))
```

---

## Hexza.JS

JavaScript execution via Node.js.

### Requirements
Node.js must be installed.

### Functions

#### `Hexza.JS.run(js_code)` → string
Execute JavaScript code.

**Parameters:**
- `js_code` (string) - JavaScript code to execute

**Returns:** Console output as string

```hxza
output = Hexza.JS.run("console.log('Hello from JS!')")
print(output)  // "Hello from JS!"
```

#### `Hexza.JS.eval(js_expression)` → string
Evaluate JavaScript expression.

**Parameters:**
- `js_expression` (string) - JavaScript expression

**Returns:** Expression result as string

```hxza
result = Hexza.JS.eval("2 + 2")
print(result)  // "4"

result = Hexza.JS.eval("Math.sqrt(16)")
print(result)  // "4"
```

### Example: JavaScript Integration

```hxza
// Run JS calculations
js_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(sum);
"""

result = Hexza.JS.run(js_code)
print("Sum from JS: " + result)

// Use JS Math
pi = Hexza.JS.eval("Math.PI")
print("Pi: " + pi)

sin_val = Hexza.JS.eval("Math.sin(Math.PI / 2)")
print("sin(π/2): " + sin_val)
```

---

## Error Handling

All modules can raise errors. Use try-catch:

```hxza
try {
    lib = Hexza.Cpp.load("missing.dll")
} catch (error) {
    print("Error: " + error)
}
```

---

## Module Availability

Check if modules are available:

```hxza
print("Game module: " + type(Hexza.Game))
print("Web module: " + type(Hexza.Web))
print("AI module: " + type(Hexza.AI))
```

---

## Best Practices

### 1. Error Handling
Always wrap external operations in try-catch:

```hxza
try {
    content = Hexza.System.read_file("data.txt")
} catch (error) {
    print("Failed to read file: " + error)
    content = ""
}
```

### 2. Resource Cleanup
Close resources when done:

```hxza
// Web server will block, so use Ctrl+C to stop
Hexza.Web.serve(html, 8000)
```

### 3. Type Checking
Check types before operations:

```hxza
if (type(value) == "int") {
    result = value * 2
}
```

---

## Performance Tips

1. **Use speedtest()** to benchmark your code
2. **Batch operations** when using AI module
3. **Cache results** of expensive computations
4. **Pre-allocate** large arrays when possible

```hxza
// Good: Pre-allocate
matrix = Hexza.AI.create_matrix(1000, 1000, 0)

// Bad: Grow dynamically
arr = []
for (i = 0; i < 1000000; i = i + 1) {
    arr.append(i)  // Slow!
}
```

---

**For complete language syntax, see [syntax.md](syntax.md)**  
**For tutorials, see [tutorial.md](tutorial.md)**  
**For development roadmap, see [ROADMAP.md](ROADMAP.md)**

**Everything Can Be Dreamed Can Be Built - SFFF**
