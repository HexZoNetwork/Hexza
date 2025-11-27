# Hexza Language Syntax Reference

## Table of Contents
- [Variables](#variables)
- [Data Types](#data-types)
- [Operators](#operators)
- [Control Flow](#control-flow)
- [Functions](#functions)
- [Classes](#classes)
- [Imports](#imports)
- [Error Handling](#error-handling)
- [Built-in Functions](#built-in-functions)
- [Universal Modules](#universal-modules)

---

## Variables

Variables are dynamically typed and declared with assignment:

```hxza
x = 10
name = "Hexza"
list = [1, 2, 3]
obj = { "key": "value" }
```

### Variable Types
- `let`, `var`, `const` - All work the same (syntactic sugar)

---

## Data Types

### Numbers
```hxza
integer = 42
float = 3.14
```

### Strings
```hxza
single = 'Hello'
double = "World"
multiline = """
This is a
multiline string
"""
```

### Booleans
```hxza
flag = true
flag2 = false
```

### Null
```hxza
nothing = null
```

### Arrays
```hxza
arr = [1, 2, 3, "four"]
arr[0]  // 1
```

### Objects
```hxza
person = {
    "name": "Hexza",
    "age": 1
}
person.name  // "Hexza"
```

---

## Operators

### Arithmetic
```hxza
+  // Addition
-  // Subtraction
*  // Multiplication
/  // Division
%  // Modulo
** // Power
```

### Comparison
```hxza
==  // Equal
!=  // Not equal
<   // Less than
>   // Greater than
<=  // Less than or equal
>=  // Greater than or equal
```

### Logical
```hxza
&&  or  and  // Logical AND
||  or  or   // Logical OR
!   or  not  // Logical NOT
```

### Bitwise
```hxza
&   // Bitwise AND
|   // Bitwise OR
^   // Bitwise XOR
~   // Bitwise NOT
<<  // Left shift
>>  // Right shift
```

### Assignment
```hxza
=    // Assign
+=   // Add and assign
-=   // Subtract and assign
*=   // Multiply and assign
/=   // Divide and assign
```

---

## Control Flow

### If-Else
```hxza
if (condition) {
    // code
} elseif (condition2) {
    // code
} else {
    // code
}
```

### Ternary
```hxza
result = condition ? true_value : false_value
```

### While Loop
```hxza
while (condition) {
    // code
    break     // Exit loop
    continue  // Skip to next iteration
}
```

### For Loop (C-style)
```hxza
for (i = 0; i < 10; i = i + 1) {
    print(i)
}
```

### For-In Loop
```hxza
arr = [1, 2, 3]
for (item in arr) {
    print(item)
}
```

### Match (Switch)
```hxza
match (value) {
    case 1: print("One")
    case 2: print("Two")
    default: print("Other")
}
```

---

## Functions

### Basic Function
```hxza
func add(a, b) {
    return a + b
}

result = add(5, 3)
```

### Lambda
```hxza
square = lambda(x) -> x * x
print(square(5))  // 25
```

### Async Functions
```hxza
async func fetchData() {
    data = await someAsyncCall()
    return data
}
```

---

## Classes

### Class Definition
```hxza
class Person {
    func __init__(name, age) {
        this.name = name
        this.age = age
    }
    
    func greet() {
        print("Hello, I'm " + this.name)
    }
}
```

### Instantiation
```hxza
person = new Person("Alice", 25)
person.greet()
```

### Inheritance
```hxza
class Employee < Person {
    func __init__(name, age, company) {
        super.__init__(name, age)
        this.company = company
    }
}
```

---

## Imports

### Import Python Modules
```hxza
import "numpy", py as np
arr = np.array([1, 2, 3])
```

### Import JavaScript Modules
```hxza
import "axios", js as http
response = http.get("https://api.example.com")
```

### Import Local Files
```hxza
import "mymodule.hxza" as mymod
```

---

## Error Handling

### Try-Catch-Finally
```hxza
try {
    risky_operation()
} catch (error) {
    print("Error: " + error)
} finally {
    cleanup()
}
```

### Throw
```hxza
throw "Something went wrong!"
```

---

## Built-in Functions

```hxza
print(...)       // Print to console
len(obj)         // Get length
range(n)         // Generate range
str(obj)         // Convert to string
int(obj)         // Convert to integer
float(obj)       // Convert to float
bool(obj)        // Convert to boolean
list(obj)        // Convert to list
dict(obj)        // Convert to dictionary
type(obj)        // Get type name
abs(x)           // Absolute value
min(...)         // Minimum value
max(...)         // Maximum value
sum(iterable)    // Sum of values
round(x, n)      // Round number
speedtest()      // Run speed benchmark
```

---

## Universal Modules

### Hexza.Game (Pygame)
```hxza  
game = Hexza.Game.init(width, height, title)
Hexza.Game.draw_rect(game, x, y, w, h, color)
Hexza.Game.update(game, fps)
events = Hexza.Game.get_events()
```

### Hexza.Web (Flask/HTTP)
```hxza
Hexza.Web.serve(html_content, port)
response = Hexza.Web.fetch(url, method, data)
```

### Hexza.AI (NumPy)
```hxza
matrix = Hexza.AI.create_matrix(rows, cols, fill)
result = Hexza.AI.matrix_mult(a, b)
value = Hexza.AI.sigmoid(x)
```

### Hexza.System (OS)
```hxza
result = Hexza.System.run(command)
content = Hexza.System.read_file(path)
Hexza.System.write_file(path, content)
files = Hexza.System.list_dir(path)
```

### Hexza.Cpp (C++ DLL Loader)
```hxza
lib = Hexza.Cpp.load(library_path)
result = Hexza.Cpp.call(lib, function_name, ...args)
```

### Hexza.JS (JavaScript Executor)
```hxza
output = Hexza.JS.run(js_code)
result = Hexza.JS.eval(js_expression)
```

---

## Comments

```hxza
// Single line comment

/* Multi-line
   comment */
```

---

**Everything Can Be Dreamed Can Be Built**
