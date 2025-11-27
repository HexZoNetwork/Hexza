# Hexza Tutorials

## Table of Contents
- [Tutorial 1: Your First Hexza Program](#tutorial-1-your-first-hexza-program)
- [Tutorial 2: Building a Simple Game](#tutorial-2-building-a-simple-game)
- [Tutorial 3: Creating a Web Server](#tutorial-3-creating-a-web-server)
- [Tutorial 4: AI with Hexza](#tutorial-4-ai-with-hexza)
- [Tutorial 5: Using C++ Libraries](#tutorial-5-using-c-libraries)
- [Tutorial 6: JavaScript Integration](#tutorial-6-javascript-integration)
- [Tutorial 7: Compiling to Executable](#tutorial-7-compiling-to-executable)

---

## Tutorial 1: Your First Hexza Program

### Step 1: Create a file
Create a new file called `hello.hxza`:

```hxza
print("Hello, World!")
print("Hexza is awesome!")

// Variables
name = "Developer"
print("Welcome, " + name)

// Math
x = 10
y = 20
print("Sum: " + str(x + y))
```

### Step 2: Run it
```bash
hexza hello.hxza
```

### Expected Output:
```
Hello, World!
Hexza is awesome!
Welcome, Developer
Sum: 30
```

---

## Tutorial 2: Building a Simple Game

Create `game.hxza`:

```hxza
// Initialize game
game = Hexza.Game.init(800, 600, "My Hexza Game")

// Game state
x = 400
y = 300
speed = 5
running = true

// Game loop
while (running) {
    // Get events
    events = Hexza.Game.get_events()
    
    // Move square
    x = x + speed
    if (x > 750 or x < 0) {
        speed = -speed
    }
    
    // Clear and draw
    Hexza.Game.draw_rect(game, 0, 0, 800, 600, [0, 0, 0])  // Background
    Hexza.Game.draw_rect(game, x, y, 50, 50, [255, 0, 0])  // Red square
    
    // Update display
    Hexza.Game.update(game, 60)
}
```

Run it:
```bash
hexza game.hxza
```

**Note:** Make sure pygame is installed: `hexza --install pygame`

---

## Tutorial 3: Creating a Web Server

### Simple HTML Server

Create `web_server.hxza`:

```hxza
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Hexza Web App</title>
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
        }
        h1 { font-size: 48px; }
    </style>
</head>
<body>
    <h1>🚀 Hexza Web Server</h1>
    <p>Everything Can Be Dreamed Can Be Built</p>
</body>
</html>
"""

print("Starting web server...")
Hexza.Web.serve(html_content, 8000)
```

Run it:
```bash
hexza web_server.hxza
```

Visit: http://localhost:8000

---

## Tutorial 4: AI with Hexza

Create `ai_demo.hxza`:

```hxza
// Create matrices
print("Creating matrices...")
matrix_a = Hexza.AI.create_matrix(2, 2, 1)
matrix_b = Hexza.AI.create_matrix(2, 2, 2)

print("Matrix A (2x2, filled with 1):")
print(matrix_a)

print("Matrix B (2x2, filled with 2):")
print(matrix_b)

// Matrix multiplication
print("Multiplying matrices...")
result = Hexza.AI.matrix_mult(matrix_a, matrix_b)
print("Result:")
print(result)

// Sigmoid activation
value = 2.5
print("Sigmoid(" + str(value) + ") = " + str(Hexza.AI.sigmoid(value)))
```

Run it:
```bash
hexza ai_demo.hxza
```

**Note:** Install numpy: `hexza --install numpy`

---

## Tutorial 5: Using C++ Libraries

### Creating a C++ DLL (Example)

First, create a simple C++ file `mylib.cpp`:

```cpp
extern "C" {
    int add(int a, int b) {
        return a + b;
    }
}
```

Compile it:
```bash
# Windows
g++ -shared -o mylib.dll mylib.cpp

# Linux
g++ -shared -fPIC -o mylib.so mylib.cpp
```

### Using it in Hexza

Create `cpp_demo.hxza`:

```hxza
// Load C++ library
lib = Hexza.Cpp.load("mylib.dll")  // or "mylib.so" on Linux

// Call C++ function
result = Hexza.Cpp.call(lib, "add", 15, 27)
print("15 + 27 = " + str(result))
```

Run it:
```bash
hexza cpp_demo.hxza
```

---

## Tutorial 6: JavaScript Integration

Create `js_demo.hxza`:

```hxza
// Run JavaScript code
print("Running JavaScript...")

js_code = """
const result = 10 * 5;
console.log(result);
"""

output = Hexza.JS.run(js_code)
print("JS Output: " + output)

// Evaluate JS expression
value = Hexza.JS.eval("Math.sqrt(16)")
print("Square root of 16: " + value)
```

Run it:
```bash
hexza js_demo.hxza
```

**Note:** Requires Node.js installed

---

## Tutorial 7: Compiling to Executable

### Step 1: Create your script

Create `myapp.hxza`:

```hxza
print("Welcome to My Hexza App!")
print("This is a compiled executable")

name = "User"
print("Hello, " + name)

// Run speed test
speedtest()
```

### Step 2: Compile it

```bash
hexza myapp.hxza --compile myapp
```

### Step 3: Run the executable

```bash
# Windows
myapp.exe

# Linux
./myapp
```

**Note:** PyInstaller must be installed: `hexza --install pyinstaller`

---

## Tutorial 8: Complete System Automation

Create `automation.hxza`:

```hxza
print("🤖 Hexza Automation Script")

// List files in current directory
files = Hexza.System.list_dir(".")
print("Files in current directory:")
for (file in files) {
    print("  - " + file)
}

// Read a file
content = Hexza.System.read_file("README.md")
lines = len(content)
print("README.md has " + str(lines) + " characters")

// Write a file
Hexza.System.write_file("output.txt", "Created by Hexza!")
print("Created output.txt")

// Run a system command
result = Hexza.System.run("echo Hello from system!")
print("Command output: " + result.stdout)
```

Run it:
```bash
hexza automation.hxza
```

---

## Next Steps

- Read the [syntax.md](syntax.md) for complete language reference
- Explore the universal modules
- Build your own projects!

**Everything Can Be Dreamed Can Be Built - SFFF**
