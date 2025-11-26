# Hexza — Made By Hexzo Lonely
## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Running a Script](#running-a-script)
  - [Interactive REPL](#interactive-repl)
  - [Package Management](#package-management)
  - [Web Server Mode](#web-server-mode)
- [Language Guide](#language-guide)
  - [Variables and Data Types](#variables-and-data-types)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Classes](#classes)
  - [Imports](#imports)
  - [Error Handling](#error-handling)
  - [Built-in Functions](#built-in-functions)
- [Example Script](#example-script)
- [Security](#security)
- [Contributing](#contributing)

## Features

*   **Multi-Language Interop**: Natively import and use packages from Python's `pip` and JavaScript's `npm` in the same script.
*   **Simple Syntax**: A clean, readable syntax that will feel familiar to users of Python, JavaScript, and C-like languages.
*   **Built-in Package Manager**: Install dependencies for your scripts directly from the command line.
*   **Interactive REPL**: Experiment with the language and test code snippets on the fly.
*   **Web Framework**: Define simple API endpoints directly within your Hexza script.
*   **Cross-Platform**: Installer and interpreter support for Windows and Linux.

## Prerequisites

*   **Python 3.10+**: Required for the interpreter.
*   **Node.js** (Optional): Required for using JavaScript (`npm`) modules.

## Installation

1.  Ensure Python 3.10 or higher is installed and available in your system's PATH.
2.  Clone this repository.
3.  From the project's root directory, run the installer:

    ```sh
    python install.py
    ```

The installer copies the interpreter to a user-local directory (`%LOCALAPPDATA%` on Windows, `~/.local/lib` on Linux) and adds a launcher script to a `bin` directory that is added to your user's PATH.

After installation, you may need to **open a new terminal session** for the `hexza` command to be recognized.

### Uninstalling

To remove Hexza from your system, run the installer with the `--uninstall` flag:

```sh
python install.py --uninstall
```

## Usage

### Running a Script

To execute a Hexza script file (e.g., `myscript.hxza`):

```sh
hexza myscript.hxza
```

### Interactive REPL

Start an interactive "Read-Eval-Print Loop" by running `hexza` with no arguments. This is great for quick tests and exploration.

```sh
hexza
Hexza v0.1 - (type 'exit' to quit)
hexza> print("Hello, World!")
Hello, World!
hexza>
```

### Package Management

Hexza can manage its own set of `pip` and `npm` packages, which are tracked in the `.hexza_packages/registry.json` file.

*   **Install a Python package:**

    ```sh
    hexza --install numpy
    ```

*   **Install a JavaScript package:** (Requires Node.js)

    ```sh
    hexza --install axios --npm
    ```

*   **List installed packages:**

    ```sh
    hexza --list
    ```

### Web Server Mode

If your script defines an API, you can run it as a web server using the `--web` flag.

```sh
hexza your_api_script.hxza --web --port 8080
```

## Language Guide

### Variables and Data Types

Variables are assigned with `=`. The syntax is dynamic and types are inferred.

```hxza
my_number = 42
my_string = "Hello, Hexza!"
my_bool = true
my_list = [1, 2, "three", false]
my_object = { "key": "value", "another": 123 }
nothing = null
```

### Control Flow

**If/Else/Elseif:**
```hxza
if (x > 10) {
    print("x is large")
} elseif (x > 5) {
    print("x is medium")
} else {
    print("x is small")
}
```

**While Loop:**
```hxza
i = 0
while (i < 5) {
    print(i)
    i = i + 1
}
```

**For Loops:**
Hexza supports both C-style `for` loops and `for-in` loops for iteration.
```hxza
// C-style
for (j = 0; j < 3; j = j + 1) {
    print(j)
}

// For-in
my_list = ["a", "b", "c"]
for (item in my_list) {
    print(item)
}
```

### Functions

Define functions with the `func` keyword.

```hxza
func greet(name) {
    return "Hello, " + name
}

message = greet("World")
print(message)
```

### Classes

Hexza supports basic class definitions with `class`, instantiation with `new`, and member access with `this`.

```hxza
class Greeter {
    func __init__(greeting) {
        this.greeting = greeting
    }

    func say_hello(name) {
        print(this.greeting + ", " + name)
    }
}

g = new Greeter("Welcome")
g.say_hello("developer")

// this code is bug is can't fix it becousi am too lazy
```

### Imports

Import Python and JavaScript modules using the `import` statement. The second argument (`py` or `js`) specifies the module type.

```hxza
import "numpy", py as np
import "axios", js as http

arr = np.array([1, 2, 3])
print(np.sum(arr)) // 6

resp = http.get("https://httpbin.org/get")
print(resp.status) // 200
```

### Error Handling

Use `try`/`catch` blocks to handle potential errors.

```hxza
try {
    throw("Something went wrong!")
} catch (e) {
    print("Caught an error:", e)
}
```

### Built-in Functions

Hexza provides a set of useful built-in functions, including:
`print()`, `say()`, `len()`, `range()`, `str()`, `int()`, `float()`, `bool()`, `list()`, `dict()`, `type()`, `abs()`, `min()`, `max()`, `sum()`, `round()`.

## Example Script

This script demonstrates fetching data with a JS library and processing it with a Python library.

```hxza
import "axios", js as ax
import "numpy", py as np

func main() {
    print("--- Running JS (axios) ---")
    resp = ax.get("https://httpbin.org/get") 
    print("Axios response status:", resp.status)

    print("--- Running PY (numpy) ---")
    my_array = np.array([10, 20, 30, 40])
    total = np.sum(my_array)
    print("Numpy calculated sum:", total)
}

main()
```

## Security

**Warning**: Hexza does not provide any sandboxing. It executes Python and JavaScript code with the same permissions as the user running the interpreter. **Do not run untrusted Hexza scripts.**

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

Your Contribution Is Very Usefull for me becouse i dont have any team
- Hexzo