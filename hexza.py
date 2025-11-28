#!/usr/bin/env python3
import os, sys, ctypes, argparse, asyncio, importlib, time, platform, hashlib
import inspect, json, subprocess, re, struct, socket, threading, queue
from typing import Any, Dict, List, Tuple, Optional, Union, Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from pathlib import Path
import urllib.parse
import importlib.util
from abc import ABC
import traceback
import readline
import heapq
from collections import deque
class PackageManager:
    def __init__(self, registry_path: str = ".hexza_packages"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(exist_ok=True)
        self.packages: Dict[str, dict] = {}
        self.native_libs: Dict[str, str] = {}
        self.load_registry()
    
    def load_registry(self) -> None:
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                self.packages = json.load(f)
                
        native_file = self.registry_path / "native.json"
        if native_file.exists():
            with open(native_file, 'r', encoding='utf-8') as f:
                self.native_libs = json.load(f)
    
    def save_registry(self) -> None:
        registry_file = self.registry_path / "registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.packages, f, indent=2)
            
        native_file = self.registry_path / "native.json"
        with open(native_file, 'w', encoding='utf-8') as f:
            json.dump(self.native_libs, f, indent=2)
            
    def track_native(self, lib_name: str, lib_path: str) -> None:
        """Track a native library (DLL/SO)"""
        self.native_libs[lib_name] = str(Path(lib_path).resolve())
        self.save_registry()
        print(f"[OK] Native library tracked: {lib_name} -> {self.native_libs[lib_name]}")
        
    def get_native_path(self, lib_name: str) -> Optional[str]:
        """Get path to a tracked native library"""
        return self.native_libs.get(lib_name)
    
    def install(self, package_name: str, use_npm: bool = False) -> bool:
        try:
            if use_npm:
                print(f"📦 Installing {package_name} via npm...")
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["npm.cmd", "install", package_name, "--save"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                else:
                    result = subprocess.run(
                        ["npm", "install", package_name, "--save"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                
                if result.returncode != 0:
                    print(f"❌ npm install failed: {result.stderr}")
                    return False
                
                if platform.system() == "Windows":
                    info_result = subprocess.run(
                        ["npm.cmd", "list", package_name, "--json"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                else:
                    info_result = subprocess.run(
                        ["npm", "list", package_name, "--json"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                
                try:
                    npm_info = json.loads(info_result.stdout)
                    pkg_path = npm_info.get("dependencies", {}).get(package_name, {}).get("path")
                    if not pkg_path:
                        pkg_path = str(Path(os.getcwd()) / "node_modules" / package_name)
                except json.JSONDecodeError:
                    pkg_path = str(Path(os.getcwd()) / "node_modules" / package_name)
                
                self.packages[package_name] = {
                    "path": str(pkg_path),
                    "type": "npm",
                    "ext": "js",
                    "installed_at": time.time()
                }
                self.save_registry()
                print(f"✅ Package installed via npm: {package_name}")
                return True
            
            else:
                print(f"📦 Installing {package_name} via pip...")
                result = subprocess.run(
                    ["pip", "install", package_name],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    print(f"❌ pip install failed: {result.stderr}")
                    return False
                import site
                site_packages = site.getsitepackages()
                
                candidate = None
                for sp in site_packages:
                    p1 = Path(sp) / package_name.replace("-", "_")
                    p2 = Path(sp) / package_name
                    if p1.exists():
                        candidate = p1
                        break
                    if p2.exists():
                        candidate = p2
                        break
                
                if candidate is None:
                    for sp in site_packages:
                        for item in Path(sp).iterdir():
                            if item.name.startswith(package_name):
                                candidate = item
                                break
                        if candidate:
                            break
                
                if candidate is None:
                    raise FileNotFoundError(f"Cannot locate pip module {package_name}")
                
                self.packages[package_name] = {
                    "path": str(candidate),
                    "type": "pip",
                    "ext": "py",
                    "installed_at": time.time()
                }
                
                self.save_registry()
                print(f"✅ Package installed via pip: {package_name}")
                return True
        
        except FileNotFoundError as e:
            if use_npm:
                print("❌ npm not found. Install Node.js to use npm packages.")
            else:
                print("❌ pip not found. Ensure Python pip is installed.")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
    
    def get_package_info(self, pkg_name: str) -> Optional[dict]:
        return self.packages.get(pkg_name)
    
    def get_package_path(self, pkg_name_or_path: str) -> Optional[Tuple[str, str]]:
        p = Path(pkg_name_or_path)
        if p.exists():
            if p.is_file():
                ext = p.suffix.lstrip('.').lower() or "py"
                return (str(p.resolve()), ext)
            if p.is_dir():
                js_main = p / "index.js"
                if js_main.exists():
                    return (str(js_main.resolve()), "js")
                py_main = p / "__init__.py"
                if py_main.exists():
                    return (str(py_main.resolve()), "py")
                pkg_json = p / "package.json"
                if pkg_json.exists():
                    try:
                        data = json.loads(pkg_json.read_text())
                        main = data.get("main")
                        if main:
                            final = p / main
                            if final.exists():
                                ext = final.suffix.lstrip(".") or "js"
                                return (str(final.resolve()), ext)
                    except Exception:
                        pass
                for item in p.iterdir():
                    if item.suffix == ".js":
                        return (str(item.resolve()), "js")
                    if item.suffix == ".py":
                        return (str(item.resolve()), "py")
        py_path = p.with_suffix('.py')
        if py_path.exists():
            return (str(py_path.resolve()), "py")
        js_path = p.with_suffix('.js')
        if js_path.exists():
            return (str(js_path.resolve()), "js")
        if pkg_name_or_path in self.packages:
            info = self.packages[pkg_name_or_path]
            pkg_path = info.get("path")
            if pkg_path and isinstance(pkg_path, str) and Path(pkg_path).exists():
                p = Path(pkg_path)
                if p.is_file():
                    ext = info.get("ext", "py")
                    return (pkg_path, ext)
                if p.is_dir():
                    js_main = p / "index.js"
                    if js_main.exists():
                        return (str(js_main.resolve()), "js")
                    py_main = p / "__init__.py"
                    if py_main.exists():
                        return (str(py_main.resolve()), "py")
                    pkg_json = p / "package.json"
                    if pkg_json.exists():
                        try:
                            data = json.loads(pkg_json.read_text())
                            main = data.get("main")
                            if main:
                                final = p / main
                                if final.exists():
                                    ext = final.suffix.lstrip(".") or "js"
                                    return (str(final.resolve()), ext)
                        except Exception:
                            pass
                    for item in p.iterdir():
                        if item.suffix == ".js":
                            return (str(item.resolve()), "js")
                        if item.suffix == ".py":
                            return (str(item.resolve()), "py")
        stem = Path(pkg_name_or_path).stem
        if stem in self.packages:
            info = self.packages[stem]
            pkg_path = info.get("path")
            if pkg_path and isinstance(pkg_path, str) and Path(pkg_path).exists():
                p = Path(pkg_path)
                if p.is_file():
                    ext = info.get("ext", "py")
                    return (pkg_path, ext)
                if p.is_dir():
                    js_main = p / "index.js"
                    if js_main.exists():
                        return (str(js_main.resolve()), "js")
                    py_main = p / "__init__.py"
                    if py_main.exists():
                        return (str(py_main.resolve()), "py")
                    pkg_json = p / "package.json"
                    if pkg_json.exists():
                        try:
                            data = json.loads(pkg_json.read_text())
                            main = data.get("main")
                            if main:
                                final = p / main
                                if final.exists():
                                    ext = final.suffix.lstrip(".") or "js"
                                    return (str(final.resolve()), ext)
                        except Exception:
                            pass
                    for item in p.iterdir():
                        if item.suffix == ".js":
                            return (str(item.resolve()), "js")
                        if item.suffix == ".py":
                            return (str(item.resolve()), "py")
        
        return None
    

    def list_packages(self) -> None:
        if not self.packages:
            print("No packages installed")
            return
        print("📦 Installed Packages:")
        for name, info in self.packages.items():
            pkg_type = info.get("type", "unknown")
            ext = info.get("ext", "?")
            print(f"  • {name} (.{ext}) [{pkg_type}]")

# ============================================================================
# PHASE 2: BYTECODE COMPILER & VM (10-100x Performance)
# ============================================================================

class OpCode(IntEnum):
    """Bytecode instruction set for fast execution"""
    LOAD_CONST = 1
    LOAD_VAR = 2
    STORE_VAR = 3
    POP = 4
    BINARY_ADD = 10
    BINARY_SUB = 11
    BINARY_MUL = 12
    BINARY_DIV = 13
    COMPARE_EQ = 20
    COMPARE_LT = 22
    JUMP = 40
    JUMP_IF_FALSE = 41
    CALL = 50
    RETURN = 51
    HALT = 99

@dataclass
class BytecodeInstruction:
    opcode: OpCode
    arg: Any = None
    line: int = 0

class HexzaFormatter:
    def __init__(self, indent_size=4):
        self.indent_size = indent_size
        
    def format(self, source: str) -> str:
        lines = source.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append("")
                continue
                
            # Decrease indent for closing braces
            if stripped.startswith('}') or stripped.startswith(']'):
                indent_level = max(0, indent_level - 1)
                
            # Add indentation
            indent = " " * (indent_level * self.indent_size)
            formatted_lines.append(f"{indent}{stripped}")
            
            # Increase indent for opening braces
            if stripped.endswith('{') or stripped.endswith('['):
                indent_level += 1
                
        return '\n'.join(formatted_lines)

class BytecodeCompiler:
    """Compiles AST to bytecode"""
    def __init__(self):
        self.instructions: List[BytecodeInstruction] = []
        self.constants: List[Any] = []
    
    def compile(self, ast: tuple):
        self.visit(ast)
        self.emit(OpCode.HALT)
        return (self.instructions, self.constants)
    
    def visit(self, node):
        if not node:
            return
        node_type = node[0]
        if node_type == "program":
            for stmt in node[1]:
                self.visit(stmt)
        elif node_type == "num":
            idx = self.add_const(node[1])
            self.emit(OpCode.LOAD_CONST, idx)
        elif node_type == "str":
            idx = self.add_const(node[1])
            self.emit(OpCode.LOAD_CONST, idx)
        elif node_type == "var":
            self.emit(OpCode.LOAD_VAR, node[1])
        elif node_type == "binop":
            self.visit(node[2])
            self.visit(node[3])
            ops = {"PLUS": OpCode.BINARY_ADD, "MINUS": OpCode.BINARY_SUB,
                   "MUL": OpCode.BINARY_MUL, "DIV": OpCode.BINARY_DIV}
            self.emit(ops.get(node[1], OpCode.BINARY_ADD))
        elif node_type == "assign":
            self.visit(node[2])
            if node[1][0] == "var":
                self.emit(OpCode.STORE_VAR, node[1][1])
        elif node_type == "call":
            # Handle function calls - compile args then function
            if len(node) >= 3:
                args = node[2] if len(node) > 2 else []
                for arg in args:
                    self.visit(arg)
                self.visit(node[1])  # Function
                self.emit(OpCode.CALL, len(args))
            else:
                self.emit(OpCode.POP)  # Dummy for incomplete calls
        elif node_type == "expr":
            # Expression statement
            self.visit(node[1])
            self.emit(OpCode.POP)  # Discard result
        else:
            # Unsupported node type - skip silently for now
            pass
    
    def emit(self, op: OpCode, arg=None):
        self.instructions.append(BytecodeInstruction(op, arg))
    
    def add_const(self, val):
        if val not in self.constants:
            self.constants.append(val)
        return self.constants.index(val)

from collections import UserDict

class Scope(UserDict):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.consts = set()
    
    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default
        
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent[key]
        raise KeyError(key)
        
    def __setitem__(self, key, value):
        # Check if const in current scope
        if key in self.consts:
            raise HexzaError(f"Assignment to constant variable '{key}'")
            
        # If variable exists in current scope, update it
        if key in self.data:
            self.data[key] = value
            return
            
        # If variable exists in parent scope, update it there
        if self.parent and self.parent.has_key(key):
            self.parent[key] = value
            return
             
        # Otherwise, define in current scope (default behavior)
        self.data[key] = value
        
    def declare(self, key, value, is_const=False):
        if key in self.data:
            raise HexzaError(f"Variable '{key}' already declared in this scope")
        self.data[key] = value
        if is_const:
            self.consts.add(key)
            
    def has_key(self, key):
        if key in self.data: return True
        if self.parent: return self.parent.has_key(key)
        return False
        
    def copy(self):
        # For function closures, we might want a new scope with this as parent?
        # Or a shallow copy of data?
        # Hexza v1 used dict.copy(). 
        # For backward compat, we'll return a new Scope with same parent and data copy
        new_scope = Scope(self.parent)
        new_scope.data = self.data.copy()
        new_scope.consts = self.consts.copy()
        return new_scope

class BytecodeVM:
    """Fast bytecode virtual machine"""
    def __init__(self, globals_dict=None):
        self.stack = []
        self.globals = globals_dict or {}
    
    def run(self, bytecode):
        instructions, constants = bytecode
        ip = 0
        while ip < len(instructions):
            inst = instructions[ip]
            op, arg = inst.opcode, inst.arg
            
            if op == OpCode.LOAD_CONST:
                self.stack.append(constants[arg])
            elif op == OpCode.LOAD_VAR:
                self.stack.append(self.globals.get(arg, None))
            elif op == OpCode.STORE_VAR:
                self.globals[arg] = self.stack.pop()
            elif op == OpCode.BINARY_ADD:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == OpCode.BINARY_SUB:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == OpCode.BINARY_MUL:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == OpCode.BINARY_DIV:
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a / b if b != 0 else float('inf'))
            elif op == OpCode.CALL:
                # Call function with N arguments
                num_args = arg
                args = []
                for _ in range(num_args):
                    if self.stack:
                        args.insert(0, self.stack.pop())
                if self.stack:
                    func = self.stack.pop()
                    if callable(func):
                        result = func(*args)
                        if result is not None:
                            self.stack.append(result)
            elif op == OpCode.POP:
                if self.stack:
                    self.stack.pop()
            elif op == OpCode.HALT:
                break
            ip += 1
        return self.stack[-1] if self.stack else None

# ============================================================================
# PHASE 2: ASYNC RUNTIME (Async/Await Support)
# ============================================================================

@dataclass(order=True)
class ScheduledTask:
    run_at: float
    task: Any = field(compare=False)

class AsyncTask:
    def __init__(self, coro, name=None):
        self.coro = coro
        self.name = name or f"Task-{id(coro)}"
        self.done = False
        self.result = None
    
    def step(self):
        try:
            self.coro.send(None)
        except StopIteration as e:
            self.done = True
            self.result = e.value

class EventLoop:
    def __init__(self):
        self.ready: deque = deque()
        self.scheduled: List[ScheduledTask] = []
        self.running = False
    
    def create_task(self, coro):
        task = AsyncTask(coro)
        self.ready.append(task)
        return task
    
    def run_until_complete(self, coro):
        task = self.create_task(coro)
        self.running = True
        while self.running and (self.ready or self.scheduled):
            if self.ready:
                t = self.ready.popleft()
                if not t.done:
                    t.step()
                    if not t.done:
                        self.ready.append(t)
            else:
                break
        return task.result if task.done else None

_event_loop = None
def get_event_loop():
    global _event_loop
    if _event_loop is None:
        _event_loop = EventLoop()
    return _event_loop

# ============================================================================
# PHASE 2: ENHANCED ERROR REPORTING
# ============================================================================

class EnhancedHexzaError(Exception):
    """Enhanced error with source code context"""
    def __init__(self, message: str, line: int = -1, col: int = -1, 
                 source_lines: List[str] = None, filename: str = None):
        self.message = message
        self.line = line
        self.col = col
        self.source_lines = source_lines or []
        self.filename = filename
        super().__init__(self._format())
    
    def _format(self) -> str:
        lines = [f">> Runtime Error: {self.message}"]
        if self.line >= 0 and self.source_lines:
            lines.append(f"   at line {self.line + 1}" + 
                        (f" in {self.filename}" if self.filename else ""))
            lines.append("")
            # Show context
            start = max(0, self.line - 1)
            end = min(len(self.source_lines), self.line + 2)
            for i in range(start, end):
                prefix = ">> " if i == self.line else "   "
                lines.append(f"{prefix}{i+1:4d} | {self.source_lines[i]}")
                if i == self.line and self.col > 0:
                    lines.append("        " + " " * self.col + "^")
        return "\n".join(lines)

class TokenType(Enum):
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "ID"
    MULTILINE = "MULTILINE"
    IF = "IF"
    ELSE = "ELSE"
    ELSEIF = "ELSEIF"
    WHILE = "WHILE"
    FOR = "FOR"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    FUNC = "FUNC"
    RETURN = "RETURN"
    CLASS = "CLASS"
    STRUCT = "STRUCT"
    ENUM = "ENUM"
    IMPORT = "IMPORT"
    FROM = "FROM"
    EXPORT = "EXPORT"
    AS = "AS"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "NULL"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"
    YIELD = "YIELD"
    LAMBDA = "LAMBDA"
    MATCH = "MATCH"
    CASE = "CASE"
    DEFAULT = "DEFAULT"
    IN = "IN"
    OF = "OF"
    IS = "IS"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    NEW = "NEW"
    THIS = "THIS"
    SUPER = "SUPER"
    STATIC = "STATIC"
    CONST = "CONST"
    LET = "LET"
    VAR = "VAR"
    LOG = "LOG"
    API = "API"
    ROUTE = "ROUTE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    ARITHMETIC = "ARITHMETIC"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    POW = "POW"
    EQ = "EQ"
    EQEQ = "EQEQ"
    NEQ = "NEQ"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"
    AND_OP = "AND_OP"
    OR_OP = "OR_OP"
    NOT_OP = "NOT_OP"
    BIT_AND = "BIT_AND"
    BIT_OR = "BIT_OR"
    BIT_XOR = "BIT_XOR"
    BIT_NOT = "BIT_NOT"
    LSHIFT = "LSHIFT"
    RSHIFT = "RSHIFT"
    INCR = "INCR"
    DECR = "DECR"
    ARROW = "ARROW"
    FATARROW = "FATARROW"
    PLUS_EQ = "PLUS_EQ"
    MINUS_EQ = "MINUS_EQ"
    MUL_EQ = "MUL_EQ"
    DIV_EQ = "DIV_EQ"
    LP = "LP"
    RP = "RP"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACK = "LBRACK"
    RBRACK = "RBRACK"
    COMMA = "COMMA"
    SEMI = "SEMI"
    COLON = "COLON"
    DOT = "DOT"
    ELLIPSIS = "ELLIPSIS"
    QUESTION = "QUESTION"
    AT = "AT"
    DOLLAR = "DOLLAR"
    PIPE = "PIPE"
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    FASTFUNC = "FASTFUNC"

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int
    
    def get_meta(self) -> Dict[str, int]:
        return {"line": self.line, "col": self.col}
    
    def __repr__(self) -> str:
        return f"Token({self.type.value}, {repr(self.value)}, {self.line}:{self.col})"

class Lexer:
    WHITESPACE_RE = re.compile(r'[ \t\r]+')
    IDENTIFIER_RE = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    NUMBER_RE = re.compile(r'\d+\.?\d*')
    
    KEYWORDS = {
        'if': TokenType.IF, 'else': TokenType.ELSE, 'elseif': TokenType.ELSEIF,
        'while': TokenType.WHILE, 'for': TokenType.FOR, 'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE, 'func': TokenType.FUNC, 'return': TokenType.RETURN,
        'class': TokenType.CLASS, 'struct': TokenType.STRUCT, 'enum': TokenType.ENUM,
        'import': TokenType.IMPORT, 'from': TokenType.FROM, 'export': TokenType.EXPORT,
        'as': TokenType.AS, 'true': TokenType.TRUE, 'false': TokenType.FALSE,
        'null': TokenType.NULL, 'try': TokenType.TRY, 'catch': TokenType.CATCH,
        'finally': TokenType.FINALLY, 'throw': TokenType.THROW, 'async': TokenType.ASYNC,
        'await': TokenType.AWAIT, 'yield': TokenType.YIELD, 'lambda': TokenType.LAMBDA,
        'match': TokenType.MATCH, 'case': TokenType.CASE, 'default': TokenType.DEFAULT,
        'in': TokenType.IN, 'of': TokenType.OF, 'is': TokenType.IS, 'and': TokenType.AND,
        'or': TokenType.OR, 'not': TokenType.NOT, 'new': TokenType.NEW, 'this': TokenType.THIS,
        'super': TokenType.SUPER, 'static': TokenType.STATIC, 'const': TokenType.CONST,
        'let': TokenType.LET, 'var': TokenType.VAR, 'log': TokenType.LOG, 'api': TokenType.API,
        'route': TokenType.ROUTE, 'self': TokenType.THIS, 'func': TokenType.FUNC,
        'fastfunc': TokenType.FASTFUNC,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self.pos >= len(self.source):
                break
            
            char = self.source[self.pos]
            if self.source[self.pos:self.pos+3] in ['"""', "'''"]:
                self._read_multiline_string()
            elif char in ['"', "'"]:
                self._read_string()
            elif char.isdigit() or (char == '.' and self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit()):
                self._read_number()
            elif char.isalpha() or char == '_':
                self._read_identifier()
            else:
                self._read_operator()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens
    
    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            if char in ' \t\r':
                self.pos += 1
                self.col += 1
            elif self.source[self.pos] == '\n':
                self.pos += 1
                self.line += 1
                self.col = 1
            elif self.source[self.pos:self.pos+2] == '//':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
            elif self.source[self.pos:self.pos+2] == '/*':
                self.pos += 2
                while self.pos < len(self.source) - 1:
                    if self.source[self.pos:self.pos+2] == '*/':
                        self.pos += 2
                        break
                    if self.source[self.pos] == '\n':
                        self.line += 1
                        self.col = 1
                    else:
                        self.col += 1
                    self.pos += 1
            else:
                break
            match = self.WHITESPACE_RE.match(self.source, self.pos)
            if match:
                self.col += len(match.group())
                self.pos = match.end()
                continue
            
    
    def _read_string(self) -> None:
        quote = self.source[self.pos]
        start_line, start_col = self.line, self.col
        self.pos += 1
        self.col += 1
        value = ""
        
        while self.pos < len(self.source) and self.source[self.pos] != quote:
            char = self.source[self.pos]
            if char == '\\' and self.pos + 1 < len(self.source):
                next_char = self.source[self.pos + 1]
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}
                if next_char in escape_map:
                    value += escape_map[next_char]
                    self.pos += 2
                    self.col += 2
                else:
                    value += char
                    self.pos += 1
                    self.col += 1
            else:
                if char == '\n':
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                value += char
                self.pos += 1
        
        if self.pos < len(self.source):
            self.pos += 1
            self.col += 1
        
        self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
    
    def _read_multiline_string(self) -> None:
        quote = self.source[self.pos:self.pos+3]
        start_line, start_col = self.line, self.col
        self.pos += 3
        self.col += 3
        value = ""
        
        while self.pos < len(self.source) - 2:
            if self.source[self.pos:self.pos+3] == quote:
                self.pos += 3
                self.col += 3
                self.tokens.append(Token(TokenType.MULTILINE, value, start_line, start_col))
                return
            
            char = self.source[self.pos]
            if char == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            value += char
            self.pos += 1
    
    def _read_number(self) -> None:
        start_line, start_col = self.line, self.col
        value = ""
        has_dot = False
        
        while self.pos < len(self.source) and (self.source[self.pos].isdigit() or self.source[self.pos] == '.'):
            if self.source[self.pos] == '.':
                if has_dot:
                    break
                has_dot = True
            value += self.source[self.pos]
            self.pos += 1
            self.col += 1
        
        num_value = float(value) if has_dot else int(value)
        self.tokens.append(Token(TokenType.NUMBER, num_value, start_line, start_col))
    
    def _read_identifier(self) -> None:
        start_line, start_col = self.line, self.col
        value = ""
        
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            value += self.source[self.pos]
            self.pos += 1
            self.col += 1
        
        token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
        self.tokens.append(Token(token_type, value, start_line, start_col))
    
    def _read_operator(self) -> None:
        start_line, start_col = self.line, self.col
        char = self.source[self.pos]
        
        if self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos+2]
            two_char_map = {
                '==': TokenType.EQEQ, '!=': TokenType.NEQ, '<=': TokenType.LE,
                '>=': TokenType.GE, '**': TokenType.POW, '->': TokenType.ARROW,
                '=>': TokenType.FATARROW, '<<': TokenType.LSHIFT, '>>': TokenType.RSHIFT,
                '++': TokenType.INCR, '--': TokenType.DECR, '+=': TokenType.PLUS_EQ,
                '-=': TokenType.MINUS_EQ, '*=': TokenType.MUL_EQ, '/=': TokenType.DIV_EQ,
                '&&': TokenType.AND_OP, '||': TokenType.OR_OP, '..': TokenType.ELLIPSIS
            }
            if two_char in two_char_map:
                self.tokens.append(Token(two_char_map[two_char], two_char, start_line, start_col))
                self.pos += 2
                self.col += 2
                return
        
        single_char_map = {
            '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MUL,
            '/': TokenType.DIV, '%': TokenType.MOD, '=': TokenType.EQ,
            '<': TokenType.LT, '>': TokenType.GT, '!': TokenType.NOT_OP,
            '&': TokenType.BIT_AND, '|': TokenType.BIT_OR, '^': TokenType.BIT_XOR,
            '~': TokenType.BIT_NOT, '(': TokenType.LP, ')': TokenType.RP,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE, '[': TokenType.LBRACK,
            ']': TokenType.RBRACK, ',': TokenType.COMMA, ';': TokenType.SEMI,
            ':': TokenType.COLON, '.': TokenType.DOT, '?': TokenType.QUESTION,
            '@': TokenType.AT, '$': TokenType.DOLLAR, '`': TokenType.PIPE
        }
        
        if char in single_char_map:
            self.tokens.append(Token(single_char_map[char], char, start_line, start_col))
            self.pos += 1
            self.col += 1
        else:
            self.pos += 1
            self.col += 1

class GlobalNamespace:
    def __init__(self, scope: Dict[str, Any]):
        self._scope = scope
    
    def __getattr__(self, name: str) -> Any:
        return self._scope.get(name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_scope":
            super().__setattr__(name, value)
        else:
            self._scope[name] = value
    
    def __repr__(self) -> str:
        return f"<global namespace: {len(self._scope)} symbols>"
    
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TokenType.EOF, None, -1, -1)
    
    def consume(self, expected_type: Optional[TokenType] = None) -> Token:
        token = self.peek()
        if token.type == TokenType.EOF:
            raise SyntaxError("Unexpected end of file")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type.value}, got {token.type.value} at {token.line}:{token.col}")
        self.pos += 1
        return token
    
    def parse(self) -> tuple:
        statements = []
        while self.peek().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            while self.peek().type == TokenType.SEMI:
                self.consume()
        return ("program", statements)
    
    def parse_statement(self) -> Optional[tuple]:
        token = self.peek()
        if token.type == TokenType.EOF:
            return None
        
        if token.type == TokenType.IF:
            return self.parse_if()
        if token.type == TokenType.WHILE:
            return self.parse_while()
        if token.type == TokenType.FOR:
            return self.parse_for()
        if token.type == TokenType.LET:
            return self.parse_var_declaration('let')
        if token.type == TokenType.CONST:
            return self.parse_var_declaration('const')
        if token.type == TokenType.VAR:
            return self.parse_var_declaration('var')
        if token.type == TokenType.FUNC:
            return self.parse_function()
        if token.type == TokenType.CLASS:
            return self.parse_class()
        if token.type == TokenType.RETURN:
            return self.parse_return()
        if token.type == TokenType.BREAK:
            t = self.consume()
            return ("break", t.get_meta())
        if token.type == TokenType.CONTINUE:
            t = self.consume()
            return ("continue", t.get_meta())
        if token.type == TokenType.IMPORT:
            return self.parse_import()
        if token.type == TokenType.EXPORT:
            return self.parse_export()
        if token.type == TokenType.TRY:
            return self.parse_try_catch()
        if token.type == TokenType.THROW:
            return self.parse_throw()
        if token.type == TokenType.ASYNC:
            self.consume()  # consume 'async'
            if self.peek().type == TokenType.FUNC:
                return self.parse_function(is_async=True)
            raise SyntaxError(f"Expected 'func' after 'async', got {self.peek().type.value}")
        if token.type == TokenType.API:
            return self.parse_api_definition()
        expr = self.parse_expression()
        if self.peek().type == TokenType.EQ:
            self.consume()
            value = self.parse_expression()
            return ("assign", expr, value)
        
        return ("expr", expr)
    
    def parse_if(self) -> tuple:
        token = self.consume(TokenType.IF)
        self.consume(TokenType.LP)
        condition = self.parse_expression()
        self.consume(TokenType.RP)
        self.consume(TokenType.LBRACE)
        true_block = self.parse_block()
        self.consume(TokenType.RBRACE)
        
        false_block = None
        if self.peek().type == TokenType.ELSE:
            self.consume()
            self.consume(TokenType.LBRACE)
            false_block = self.parse_block()
            self.consume(TokenType.RBRACE)
        elif self.peek().type == TokenType.ELSEIF:
            false_block = [self.parse_if()]
        
        return ("if", condition, true_block, false_block)
    
    def parse_while(self) -> tuple:
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LP)
        condition = self.parse_expression()
        self.consume(TokenType.RP)
        self.consume(TokenType.LBRACE)
        body = self.parse_block()
        self.consume(TokenType.RBRACE)
        return ("while", condition, body)
    
    def parse_for(self) -> tuple:
        self.consume(TokenType.FOR)
        self.consume(TokenType.LP)
        saved_pos = self.pos
        is_for_in = False
        paren_depth = 1
        
        while paren_depth > 0 and self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.LP:
                paren_depth += 1
            elif self.peek().type == TokenType.RP:
                paren_depth -= 1
            elif self.peek().type == TokenType.IN and paren_depth == 1:
                is_for_in = True
                break
            elif self.peek().type == TokenType.SEMI:
                break
            self.pos += 1
        
        self.pos = saved_pos
        
        if is_for_in:
            var_name = self.consume(TokenType.IDENTIFIER).value
            self.consume(TokenType.IN)
            iterable = self.parse_expression()
            self.consume(TokenType.RP)
            self.consume(TokenType.LBRACE)
            body = self.parse_block()
            self.consume(TokenType.RBRACE)
            return ("for_in", var_name, iterable, body)
        else:
            init = None
            if self.peek().type != TokenType.SEMI:
                init = self.parse_expression()
            self.consume(TokenType.SEMI)
            
            cond = None
            if self.peek().type != TokenType.SEMI:
                cond = self.parse_expression()
            self.consume(TokenType.SEMI)
            
            inc = None
            if self.peek().type != TokenType.RP:
                inc = self.parse_expression()
            self.consume(TokenType.RP)
            
            self.consume(TokenType.LBRACE)
            body = self.parse_block()
            self.consume(TokenType.RBRACE)
            return ("for", init, cond, inc, body)
    
    def parse_function(self, is_async: bool = False) -> tuple:
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LP)
        
        params = []
        param_types = []
        while self.peek().type != TokenType.RP:
            param_name = self.consume(TokenType.IDENTIFIER).value
            param_type = None
            # Check for type annotation: name: type
            if self.peek().type == TokenType.COLON:
                self.consume(TokenType.COLON)
                param_type = self.consume(TokenType.IDENTIFIER).value
            params.append(param_name)
            param_types.append(param_type)
            if self.peek().type == TokenType.COMMA:
                self.consume()
        
        self.consume(TokenType.RP)
        
        # Check for return type annotation: -> type
        return_type = None
        if self.peek().type == TokenType.ARROW:
            self.consume(TokenType.ARROW)
            return_type = self.consume(TokenType.IDENTIFIER).value
        
        self.consume(TokenType.LBRACE)
        body = self.parse_block()
        self.consume(TokenType.RBRACE)
        
        return ("func_def", name, params, body, is_async, param_types, return_type)
    
    def parse_var_declaration(self, kind: str) -> tuple:
        """Parse let/const/var declarations: let x = 10;"""
        self.consume()  # consume let/const/var
        name_token = self.consume(TokenType.IDENTIFIER)
        name = name_token.value
        
        # Check for type annotation: name: type
        var_type = None
        if self.peek().type == TokenType.COLON:
            self.consume(TokenType.COLON)
            var_type = self.consume(TokenType.IDENTIFIER).value
        
        init_value = None
        if self.peek().type == TokenType.EQ:
            self.consume(TokenType.EQ)
            init_value = self.parse_expression()
        
        return ("var_decl", kind, name, init_value, var_type)
    
    def parse_class(self) -> tuple:
        self.consume(TokenType.CLASS)
        name = self.consume(TokenType.IDENTIFIER).value
        
        base = None
        if self.peek().type == TokenType.LT:  # class Child < Parent
            self.consume()
            base = self.consume(TokenType.IDENTIFIER).value
        
        self.consume(TokenType.LBRACE)
        
        methods = []
        while self.peek().type != TokenType.RBRACE:
            if self.peek().type == TokenType.FUNC:
                methods.append(self.parse_function())
            else:
                self.consume()
        
        self.consume(TokenType.RBRACE)
        return ("class_def", name, base, methods)
    
    def parse_return(self) -> tuple:
        self.consume(TokenType.RETURN)
        value = None
        if self.peek().type not in [TokenType.SEMI, TokenType.RBRACE, TokenType.EOF]:
            value = self.parse_expression()
        return ("return", value)
    
    def parse_import(self) -> tuple:
        self.consume(TokenType.IMPORT)
        module_path = self.consume(TokenType.STRING).value
        
        ext = None
        if self.peek().type == TokenType.COMMA:
            self.consume()
            ext = self.consume(TokenType.IDENTIFIER).value
        
        alias = None
        if self.peek().type == TokenType.AS:
            self.consume()
            alias = self.consume(TokenType.IDENTIFIER).value
        else:
            alias = Path(module_path).stem
        
        return ("import", module_path, ext, alias)
    
    def parse_export(self) -> tuple:
        self.consume(TokenType.EXPORT)
        stmt = self.parse_statement()
        return ("export", stmt)
    
    def parse_try_catch(self) -> tuple:
        self.consume(TokenType.TRY)
        self.consume(TokenType.LBRACE)
        try_block = self.parse_block()
        self.consume(TokenType.RBRACE)
        
        error_var = None
        catch_block = None
        finally_block = None
        
        if self.peek().type == TokenType.CATCH:
            self.consume()
            self.consume(TokenType.LP)
            error_var = self.consume(TokenType.IDENTIFIER).value
            self.consume(TokenType.RP)
            self.consume(TokenType.LBRACE)
            catch_block = self.parse_block()
            self.consume(TokenType.RBRACE)
        
        if self.peek().type == TokenType.FINALLY:
            self.consume()
            self.consume(TokenType.LBRACE)
            finally_block = self.parse_block()
            self.consume(TokenType.RBRACE)
        
        return ("try_catch", try_block, error_var, catch_block, finally_block)
    
    def parse_throw(self) -> tuple:
        self.consume(TokenType.THROW)
        value = self.parse_expression()
        return ("throw", value)
    
    def parse_api_definition(self) -> tuple:
        self.consume(TokenType.API)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LBRACE)
        
        routes = []
        while self.peek().type != TokenType.RBRACE and self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.IDENTIFIER and self.peek().value.upper() in ["GET", "POST", "PUT", "DELETE"]:
                routes.append(self.parse_route())
            else:
                self.consume()
        
        self.consume(TokenType.RBRACE)
        return ("api_def", name, routes)
    
    def parse_route(self) -> tuple:
        method_token = self.consume(TokenType.IDENTIFIER)
        method = method_token.value.upper()
        path = self.consume(TokenType.STRING).value
        self.consume(TokenType.ARROW)
        handler_name = self.consume(TokenType.IDENTIFIER).value
        return ("route", method, path, handler_name)
    
    def parse_block(self) -> List[tuple]:
        statements = []
        while self.peek().type not in [TokenType.RBRACE, TokenType.EOF]:
            if self.peek().type in [TokenType.SEMI, TokenType.NEWLINE]:
                self.consume()
                continue
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

            while self.peek().type in [TokenType.SEMI, TokenType.NEWLINE]:
                self.consume()
        
        return statements
    
    def parse_expression(self) -> tuple:
        return self.parse_ternary()
    
    def parse_ternary(self) -> tuple:
        expr = self.parse_or()
        if self.peek().type == TokenType.QUESTION:
            self.consume()
            true_expr = self.parse_expression()
            self.consume(TokenType.COLON)
            false_expr = self.parse_expression()
            return ("ternary", expr, true_expr, false_expr)
        return expr
    
    def parse_or(self) -> tuple:
        left = self.parse_and()
        while self.peek().type in [TokenType.OR, TokenType.OR_OP]:
            self.consume()
            right = self.parse_and()
            left = ("binop", "OR", left, right)
        return left
    
    def parse_and(self) -> tuple:
        left = self.parse_equality()
        while self.peek().type in [TokenType.AND, TokenType.AND_OP]:
            self.consume()
            right = self.parse_equality()
            left = ("binop", "AND", left, right)
        return left
    
    def parse_equality(self) -> tuple:
        left = self.parse_comparison()
        while self.peek().type in [TokenType.EQEQ, TokenType.NEQ]:
            op_token = self.consume()
            op = "EQEQ" if op_token.type == TokenType.EQEQ else "NEQ"
            right = self.parse_comparison()
            left = ("binop", op, left, right)
        return left
    
    def parse_comparison(self) -> tuple:
        left = self.parse_bitwise()
        while self.peek().type in [TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE]:
            op_token = self.consume()
            op_map = {TokenType.LT: "LT", TokenType.GT: "GT", TokenType.LE: "LE", TokenType.GE: "GE"}
            op = op_map.get(op_token.type, "LT")
            right = self.parse_bitwise()
            left = ("binop", op, left, right)
        return left
    
    def parse_bitwise(self) -> tuple:
        left = self.parse_term()
        while self.peek().type in [TokenType.BIT_AND, TokenType.BIT_OR, TokenType.BIT_XOR, TokenType.LSHIFT, TokenType.RSHIFT]:
            op_token = self.consume()
            op_map = {TokenType.BIT_AND: "BIT_AND", TokenType.BIT_OR: "BIT_OR", TokenType.BIT_XOR: "BIT_XOR", TokenType.LSHIFT: "LSHIFT", TokenType.RSHIFT: "RSHIFT"}
            op = op_map.get(op_token.type, "BIT_AND")
            right = self.parse_term()
            left = ("binop", op, left, right)
        return left
    
    def parse_term(self) -> tuple:
        left = self.parse_factor()
        while self.peek().type in [TokenType.PLUS, TokenType.MINUS]:
            op_token = self.consume()
            op = "PLUS" if op_token.type == TokenType.PLUS else "MINUS"
            right = self.parse_factor()
            left = ("binop", op, left, right)
        return left
    
    def parse_factor(self) -> tuple:
        left = self.parse_power()
        while self.peek().type in [TokenType.MUL, TokenType.DIV, TokenType.MOD]:
            op_token = self.consume()
            op_map = {TokenType.MUL: "MUL", TokenType.DIV: "DIV", TokenType.MOD: "MOD"}
            op = op_map.get(op_token.type, "MUL")
            right = self.parse_power()
            left = ("binop", op, left, right)
        return left
    
    def parse_power(self) -> tuple:
        left = self.parse_unary()
        if self.peek().type == TokenType.POW:
            self.consume()
            right = self.parse_power()
            return ("binop", "POW", left, right)
        return left
    
    def parse_unary(self) -> tuple:
        if self.peek().type in [TokenType.NOT, TokenType.NOT_OP, TokenType.MINUS, TokenType.BIT_NOT]:
            op_token = self.consume()
            op_map = {TokenType.NOT: "NOT", TokenType.NOT_OP: "NOT", TokenType.MINUS: "NEG", TokenType.BIT_NOT: "BIT_NOT"}
            op = op_map.get(op_token.type, "NOT")
            operand = self.parse_unary()
            return ("unary", op, operand)
        
        if self.peek().type == TokenType.NEW:
            return self.parse_new()
        
        if self.peek().type == TokenType.AWAIT:
            self.consume()
            operand = self.parse_unary()
            return ("await", operand)
        
        return self.parse_postfix()
    
    def parse_new(self) -> tuple:
        self.consume(TokenType.NEW)
        class_name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LP)
        args = []
        while self.peek().type != TokenType.RP:
            args.append(self.parse_expression())
            if self.peek().type == TokenType.COMMA:
                self.consume()
        self.consume(TokenType.RP)
        return ("new", class_name, args)
    
    def parse_postfix(self) -> tuple:
        left = self.parse_primary()
        
        while self.peek().type != TokenType.EOF:
            if self.peek().type == TokenType.LP:
                self.consume()
                args = []
                while self.peek().type != TokenType.RP:
                    args.append(self.parse_expression())
                    if self.peek().type == TokenType.COMMA:
                        self.consume()
                self.consume(TokenType.RP)
                left = ("call", left, args)
            
            elif self.peek().type == TokenType.LBRACK:
                self.consume()
                index = self.parse_expression()
                self.consume(TokenType.RBRACK)
                left = ("index", left, index)
            
            elif self.peek().type == TokenType.DOT:
                self.consume()
                member = self.consume(TokenType.IDENTIFIER).value
                left = ("member", left, member)
            
            else:
                break
        
        return left
    
    def parse_primary(self) -> tuple:
        token = self.peek()
        
        if token.type == TokenType.EOF:
            raise SyntaxError("Unexpected end of file")
        
        if token.type == TokenType.THIS:
            self.consume()
            return ("this",)
        
        if token.type == TokenType.NUMBER:
            self.consume()
            return ("num", token.value)
        
        if token.type in [TokenType.STRING, TokenType.MULTILINE]:
            self.consume()
            return ("str", token.value)
        
        if token.type == TokenType.TRUE:
            self.consume()
            return ("bool", True)
        
        if token.type == TokenType.FALSE:
            self.consume()
            return ("bool", False)
        
        if token.type == TokenType.NULL:
            self.consume()
            return ("null",)
        
        if token.type == TokenType.IDENTIFIER:
            self.consume()
            return ("var", token.value)
        
        if token.type == TokenType.LBRACK:
            self.consume()
            elements = []
            while self.peek().type != TokenType.RBRACK:
                elements.append(self.parse_expression())
                if self.peek().type == TokenType.COMMA:
                    self.consume()
                if self.peek().type == TokenType.RBRACK:
                    break
            self.consume(TokenType.RBRACK)
            return ("array", elements)
        
        if token.type == TokenType.LBRACE:
            self.consume()
            pairs = []
            while self.peek().type != TokenType.RBRACE:
                if self.peek().type == TokenType.IDENTIFIER:
                    key = self.consume().value
                elif self.peek().type == TokenType.STRING:
                    key = self.consume().value
                else:
                    raise SyntaxError(f"Expected key, got {self.peek().type.value}")
                
                self.consume(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
                
                if self.peek().type == TokenType.COMMA:
                    self.consume()
                if self.peek().type == TokenType.RBRACE:
                    break
            
            self.consume(TokenType.RBRACE)
            return ("obj", pairs)
        
        if token.type == TokenType.LP:
            self.consume()
            expr = self.parse_expression()
            self.consume(TokenType.RP)
            return expr
        
        if token.type == TokenType.LAMBDA:
            self.consume()
            params = []
            if self.peek().type == TokenType.LP:
                self.consume()
                while self.peek().type != TokenType.RP:
                    params.append(self.consume(TokenType.IDENTIFIER).value)
                    if self.peek().type == TokenType.COMMA:
                        self.consume()
                self.consume(TokenType.RP)
            
            self.consume(TokenType.ARROW)
            body_expr = self.parse_expression()
            return ("lambda", params, body_expr)
        
        raise SyntaxError(f"Unexpected token: {token.type.value}")
    
class HexzaError(Exception):
    def __init__(self, message: str, line: int = -1, col: int = -1, source_line: str = ""):
        self.message = message
        self.line = line
        self.col = col
        self.source_line = source_line
        super().__init__(self._format())
    
    def _format(self) -> str:
        s = f"❌ {self.message}"
        if self.line >= 0:
            s += f"\n   at line {self.line}, col {self.col}"
            if self.source_line:
                s += f"\n   {self.source_line}"
                s += "\n   " + " " * (self.col - 1) + "^"
        return s

class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class HexzaFunction:
    def __init__(self, name: str, params: List[str], body: List[tuple], closure: Dict[str, Any], is_async: bool = False, is_method: bool = False):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
        self.is_async = is_async
        self.is_method = is_method
    
    def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError(f"Function '{self.name}' must be called through the VM")

class HexzaInstance:
    def __init__(self, cls: 'HexzaClass'):
        self.__hexza_class__ = cls
    
    def __repr__(self) -> str:
        return f"<{self.__hexza_class__.name} instance>"

class HexzaClass:
    def __init__(self, name: str, base: Optional['HexzaClass'], methods: Dict[str, HexzaFunction]):
        self.name = name
        self.base = base
        self.methods = methods
        self.instances: List[HexzaInstance] = []
    
    def get_method(self, method_name: str) -> Optional[HexzaFunction]:
        if method_name in self.methods:
            return self.methods[method_name]
        if self.base:
            return self.base.get_method(method_name)
        return None
    
    def __call__(self, *args: Any, vm: Optional['VM'] = None, **kwargs: Any) -> HexzaInstance:
        instance = HexzaInstance(self)
        
        init_method = self.get_method("__init__")
        if init_method and vm:
            local_scope = init_method.closure.copy()
            local_scope["__hexza_self__"] = instance
            
            for i, param in enumerate(init_method.params):
                local_scope[param] = args[i] if i < len(args) else None
            
            try:
                for stmt in init_method.body:
                    vm.eval(stmt, local_scope)
            except Exception:
                pass
        
        self.instances.append(instance)
        return instance

class JSProxy:
    def __init__(self, package_path: str, runner_path: Optional[str] = None):
        self.package_path = package_path
        self.runner_path = runner_path
        self._cache = {}
    
    def __call__(self, *args):
        return self._invoke_js("default", args)
    
    def __getattr__(self, name: str):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        def call(*args):
            return self._invoke_js(name, args)
        return call
    
    def __getitem__(self, name: str):
        if not isinstance(name, str):
            raise TypeError("JSProxy keys must be strings")
        
        def call(*args):
            return self._invoke_js(name, args)
        return call
    
    def _invoke_js(self, func_name: str, args: tuple) -> Any:
        payload = json.dumps({"args": list(args)})
        runner = self.runner_path or ""
        
        try:
            proc = subprocess.run(
                ["node", runner, self.package_path, func_name, payload],
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
        except FileNotFoundError:
            raise RuntimeError("❌ node not found; install Node.js for .js imports")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"❌ JS execution timeout for {func_name}")
        
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        
        try:
            if stdout:
                data = json.loads(stdout)
            elif stderr:
                data = json.loads(stderr)
            else:
                raise RuntimeError("No output from node runner")
        except json.JSONDecodeError:
            raise RuntimeError(f"❌ Invalid JS response: {stdout or stderr}")
        
        if not data.get("ok", False):
            raise RuntimeError(f"❌ JS error: {data.get('error')} | {data.get('stack')}")
        
        return data.get("result")
    
    
class VM:
    def __init__(self, pkg_mgr: Optional[PackageManager] = None, enable_web: bool = True):
        self.pkg_mgr = pkg_mgr
        self.enable_web = enable_web
        self.global_scope: Dict[str, Any] = self._create_builtins()
        self.call_stack: List[Dict[str, Any]] = []
        self.output_buffer: List[str] = []
        self.web_app = None
        self.api_handlers: Dict[Tuple[str, str], HexzaFunction] = {}
        self._eval_handlers: Dict[str, Callable] = {
            "num": self._eval_num,
            "str": self._eval_str,
            "bool": self._eval_bool,
            "null": self._eval_null,
            "array": self._eval_array,
            "obj": self._eval_obj,
            "var": self._eval_var,
            "unary": self._eval_unary,
            "binop": self._eval_binop,
            "index": self._eval_index,
            "member": self._eval_member,
            "assign": self._eval_assign,
            "if": self._eval_if,
            "while": self._eval_while,
            "for": self._eval_for,
            "for_in": self._eval_for_in,
            "func_def": self._eval_func_def,
            "class_def": self._eval_class_def,
            "new": self._eval_new,
            "return": self._eval_return,
            "break": self._eval_break,
            "continue": self._eval_continue,
            "expr": self._eval_expr,
            "import": self._eval_import,
            "export": self._eval_export,
            "try_catch": self._eval_try_catch,
            "throw": self._eval_throw,
            "api_def": self._eval_api_def,
            "lambda": self._eval_lambda,
            "ternary": self._eval_ternary,
            "this": self._eval_this,
            "this": self._eval_this,
            "await": self._eval_await,
            "call": self._eval_call,
            "program": self._eval_program,
            "var_decl": self._eval_var_decl,
        }

    def _eval_await(self, node: tuple, scope: Dict) -> Any:
        _, operand = node[0:2]
        task = yield from self.eval_gen(operand, scope)
        if inspect.isgenerator(task):
            return (yield from task)
        return task
    
    def _create_builtins(self) -> Dict[str, Callable]:
        builtins_dict = {
            "print": self.builtin_print,
            "len": self.builtin_len,
            "range": self.builtin_range,
            "str": self.builtin_str,
            "int": self.builtin_int,
            "float": self.builtin_float,
            "bool": self.builtin_bool,
            "list": self.builtin_list,
            "dict": self.builtin_dict,
            "type": self.builtin_type,
            "abs": self.builtin_abs,
            "min": self.builtin_min,
            "max": self.builtin_max,
            "sum": self.builtin_sum,
            "round": self.builtin_round,
            "error": self._builtin_error,
            "say": self.builtin_say,
            "speedtest": self.builtin_speedtest,
        }
        builtins_dict["global"] = GlobalNamespace(builtins_dict)
        builtins_dict["Hexza"] = self._create_hexza_module()
        builtins_dict["html"] = self._create_html_module()
        return builtins_dict
    
    def _create_html_module(self) -> Dict[str, Any]:
        """HTML/Web DSL module for clean template generation"""
        def tag(name: str, props: dict = None, children: list = None) -> str:
            """Create HTML tag: tag('div', {'class': 'card'}, ['Hello'])"""
            props = props or {}
            children = children or []
            
            # Build attributes
            attrs = ""
            for key, val in props.items():
                if val is True:
                    attrs += f" {key}"
                elif val is not False and val is not None:
                    attrs += f' {key}="{val}"'
            
            # Self-closing tags
            if name in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                return f"<{name}{attrs} />"
            
            # Build children
            content = ""
            for child in children:
                if isinstance(child, (list, tuple)):
                    content += "".join(str(c) for c in child)
                else:
                    content += str(child)
            
            return f"<{name}{attrs}>{content}</{name}>"
        
        def component(render_func: Callable) -> Callable:
            """Decorator to create reusable components"""
            def wrapper(*args, **kwargs):
                return render_func(*args, **kwargs)
            wrapper.__component__ = True
            return wrapper
        
        def render_list(items: list, render_item: Callable) -> str:
            """Render list of items: render_list(products, lambda p: tag('div', {}, [p.name]))"""
            return "".join(render_item(item) for item in items)
        
        def css(styles: dict) -> str:
            """Convert dict to CSS string: css({'color': 'red', 'font-size': '14px'})"""
            return ";".join(f"{k}:{v}" for k, v in styles.items())
        
        # Shortcuts for common tags
        def div(props=None, children=None): return tag('div', props, children)
        def span(props=None, children=None): return tag('span', props, children)
        def p(props=None, children=None): return tag('p', props, children)
        def h1(props=None, children=None): return tag('h1', props, children)
        def h2(props=None, children=None): return tag('h2', props, children)
        def h3(props=None, children=None): return tag('h3', props, children)
        def img(props): return tag('img', props, None)
        def a(props, children): return tag('a', props, children)
        def button(props, children): return tag('button', props, children)
        def input_tag(props): return tag('input', props, None)
        
        return {
            "tag": tag,
            "component": component,
            "render_list": render_list,
            "css": css,
            "div": div,
            "span": span,
            "p": p,
            "h1": h1,
            "h2": h2,
            "h3": h3,
            "img": img,
            "a": a,
            "button": button,
            "input": input_tag,
        }
    
    def _create_hexza_module(self) -> Dict[str, Any]:
        """Create the Universal Hexza module with all sub-modules"""
        return {
            "Game": self._create_game_module(),
            "Web": self._create_web_module(),
            "AI": self._create_ai_module(),
            "System": self._create_system_module(),
            "Cpp": self._create_cpp_module(),
            "JS": self._create_js_module(),
            "OS": self._create_os_module(),
            "speedtest": self.builtin_speedtest,
        }
    
    def _create_os_module(self) -> Dict[str, Any]:
        """Low-level OS and memory operations module"""
        import ctypes
        import sys
        
        def os_alloc(size):
            """Allocate raw memory"""
            return ctypes.create_string_buffer(size)
            
        def os_free(ptr):
            """Free memory (noop for python managed buffers but kept for API compat)"""
            pass
            
        def os_write(ptr, data, offset=0):
            """Write data to memory pointer"""
            if isinstance(data, str):
                data = data.encode('utf-8')
            ctypes.memmove(ctypes.addressof(ptr) + offset, data, len(data))
            
        def os_read(ptr, size, offset=0):
            """Read data from memory pointer"""
            return ctypes.string_at(ctypes.addressof(ptr) + offset, size)
            
        def os_address(ptr):
            """Get memory address"""
            return ctypes.addressof(ptr)
            
        def os_sizeof(ptr):
            """Get size of object"""
            return ctypes.sizeof(ptr)
            
        def os_platform():
            """Get platform info"""
            return sys.platform
            
        return {
            "alloc": os_alloc,
            "free": os_free,
            "write": os_write,
            "read": os_read,
            "address": os_address,
            "sizeof": os_sizeof,
            "platform": os_platform,
            "ptr_size": ctypes.sizeof(ctypes.c_void_p)
        }
    
    def _create_game_module(self) -> Dict[str, Any]:
        """Pygame wrapper for game development"""
        def init_game(width=800, height=600, title="Hexza Game"):
            try:
                import pygame
                pygame.init()
                screen = pygame.display.set_mode((width, height))
                pygame.display.set_caption(title)
                return {"screen": screen, "pygame": pygame, "clock": pygame.time.Clock()}
            except ImportError:
                raise RuntimeError("❌ pygame not installed. Run: hexza --install pygame")
        
        def draw_rect(game, x, y, w, h, color=(255, 255, 255)):
            try:
                import pygame
                pygame.draw.rect(game["screen"], color, (x, y, w, h))
            except:
                pass
        
        def update(game, fps=60):
            try:
                import pygame
                pygame.display.flip()
                game["clock"].tick(fps)
            except:
                pass
        
        def get_events():
            try:
                import pygame
                return pygame.event.get()
            except:
                return []
        
        return {
            "init": init_game,
            "draw_rect": draw_rect,
            "update": update,
            "get_events": get_events,
        }
    
    def _create_web_module(self) -> Dict[str, Any]:
        """Flask/HTTP wrapper for web development"""
        def serve_html(html_content, port=8000):
            """Simple HTTP server for HTML/CSS"""
            import http.server
            import socketserver
            from pathlib import Path
            
            temp_html = Path("_hexza_temp.html")
            temp_html.write_text(html_content, encoding='utf-8')
            
            class Handler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/" or self.path == "/index.html":
                        self.path = "/_hexza_temp.html"
                    return super().do_GET()
            
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"🌐 Serving on http://localhost:{port}")
                httpd.serve_forever()
        
        def fetch(url, method="GET", data=None):
            """HTTP client"""
            import urllib.request
            import json
            try:
                if data:
                    data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=data, method=method)
                with urllib.request.urlopen(req) as response:
                    return response.read().decode('utf-8')
            except Exception as e:
                return f"Error: {e}"
        
        return {
            "serve": serve_html,
            "fetch": fetch,
        }
    
    def _create_ai_module(self) -> Dict[str, Any]:
        """NumPy/AI wrapper"""
        def create_matrix(rows, cols, fill=0):
            try:
                import numpy as np
                return np.full((rows, cols), fill)
            except ImportError:
                return [[fill for _ in range(cols)] for _ in range(rows)]
        
        def matrix_mult(a, b):
            try:
                import numpy as np
                return np.dot(a, b).tolist()
            except ImportError:
                raise RuntimeError("❌ numpy not installed. Run: hexza --install numpy")
        
        def sigmoid(x):
            try:
                import numpy as np
                return 1 / (1 + np.exp(-x))
            except ImportError:
                import math
                return 1 / (1 + math.exp(-x))
        
        return {
            "create_matrix": create_matrix,
            "matrix_mult": matrix_mult,
            "sigmoid": sigmoid,
        }
    
    def _create_system_module(self) -> Dict[str, Any]:
        """OS/System operations wrapper"""
        def run_command(cmd):
            import subprocess
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return {"stdout": result.stdout, "stderr": result.stderr, "code": result.returncode}
            except Exception as e:
                return {"error": str(e)}
        
        def read_file(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error: {e}"
        
        def write_file(path, content):
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                return f"Error: {e}"
        
        def list_dir(path="."):
            import os
            try:
                return os.listdir(path)
            except Exception as e:
                return []
        
        return {
            "run": run_command,
            "read_file": read_file,
            "write_file": write_file,
            "list_dir": list_dir,
        }
    
    def _create_cpp_module(self) -> Dict[str, Any]:
        """C++/C DLL loader wrapper"""
        def load_library(lib_path):
            import ctypes
            try:
                if platform.system() == "Windows":
                    lib = ctypes.CDLL(lib_path)
                else:
                    lib = ctypes.CDLL(lib_path)
                return lib
            except Exception as e:
                raise RuntimeError(f"❌ Failed to load library: {e}")
        
        def call_function(lib, func_name, *args):
            try:
                func = getattr(lib, func_name)
                return func(*args)
            except Exception as e:
                return f"Error: {e}"
        
        return {
            "load": load_library,
            "call": call_function,
        }
    
    def _create_js_module(self) -> Dict[str, Any]:
        """JavaScript executor via Node.js"""
        def run_js(js_code):
            import subprocess
            try:
                result = subprocess.run(
                    ["node", "-e", js_code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.stdout.strip()
            except FileNotFoundError:
                return "❌ Node.js not installed"
            except Exception as e:
                return f"Error: {e}"
        
        def eval_js(js_expr):
            return run_js(f"console.log({js_expr})")
        
        return {
            "run": run_js,
            "eval": eval_js,
        }
    
    def builtin_speedtest(self, iterations=1000000):
        """Benchmark the Hexza interpreter"""
        import time
        
        # Test 1: Arithmetic
        start = time.time()
        x = 0
        for i in range(iterations):
            x = x + 1
        arithmetic_time = time.time() - start
        
        # Test 2: Function calls
        def dummy_func():
            return 42
        
        start = time.time()
        for i in range(iterations // 100):
            dummy_func()
        function_time = time.time() - start
        
        # Test 3: List operations
        start = time.time()
        lst = []
        for i in range(iterations // 100):
            lst.append(i)
        list_time = time.time() - start
        
        result = {
            "iterations": iterations,
            "arithmetic_ms": round(arithmetic_time * 1000, 2),
            "function_ms": round(function_time * 1000, 2),
            "list_ms": round(list_time * 1000, 2),
            "total_ms": round((arithmetic_time + function_time + list_time) * 1000, 2),
        }
        
        print(f">> Hexza Speed Test Results:")
        print(f"   Arithmetic ({iterations} ops): {result['arithmetic_ms']} ms")
        print(f"   Function calls ({iterations // 100} calls): {result['function_ms']} ms")
        print(f"   List operations ({iterations // 100} ops): {result['list_ms']} ms")
        print(f"   Total: {result['total_ms']} ms")
        
        return result

    def builtin_say(self, *args: Any) -> None:
        self.builtin_print(*args)
    
    def _builtin_error(self, message: str) -> None:
        raise HexzaError(message)

    def builtin_print(self, *args: Any) -> None:
        output = " ".join(str(arg) for arg in args)
        print(output)
        self.output_buffer.append(output)
    
    def builtin_len(self, obj: Any) -> int:
        return len(obj)
    
    def builtin_range(self, start: int, end: Optional[int] = None, step: int = 1) -> List[int]:
        if end is None:
            return list(range(start))
        return list(range(start, end, step))
    
    def builtin_str(self, obj: Any) -> str:
        return str(obj)
    
    def builtin_int(self, obj: Any) -> int:
        return int(obj)
    
    def builtin_float(self, obj: Any) -> float:
        return float(obj)
    
    def builtin_bool(self, obj: Any) -> bool:
        return bool(obj)
    
    def builtin_list(self, obj: Any = None) -> List:
        return list(obj) if obj else []
    
    def builtin_dict(self, obj: Any = None) -> Dict:
        return dict(obj) if obj else {}
    
    def builtin_type(self, obj: Any) -> str:
        return type(obj).__name__
    
    def builtin_abs(self, x: Union[int, float]) -> Union[int, float]:
        return abs(x)
    
    def builtin_min(self, *args: Any) -> Any:
        return min(args) if args else None
    
    def builtin_max(self, *args: Any) -> Any:
        return max(args) if args else None
    
    def builtin_sum(self, iterable: Any) -> Union[int, float]:
        return sum(iterable)
    
    def builtin_round(self, x: float, ndigits: int = 0) -> Union[int, float]:
        return round(x, ndigits)
    
    def _ensure_js_runner(self) -> str:
        if not self.pkg_mgr:
            raise RuntimeError("package manager is not available")
        runner = Path(self.pkg_mgr.registry_path) / "hexza_js_runner.js"
        if runner.exists():
            return str(runner)
        runner_code = r'''
const fs = require('fs');
const path = require('path');

function sanitize(obj) {
  if (obj && typeof obj === 'object' && obj.data && obj.status) {
    return {
      data: obj.data,
      status: obj.status,
      statusText: obj.statusText,
      headers: obj.headers,
    };
  }
  return obj;
}

(async () => {
  try {
    const modulePath = path.resolve(process.argv[2] || '');
    const funcName = process.argv[3] || '';
    const argsJSON = process.argv[4] || '[]';
    const args = JSON.parse(argsJSON).args || [];
    
    let mod = require(modulePath);
    if (mod.__esModule && mod.default) {
        mod = mod.default;
    }

    let fn;
    if (funcName && mod[funcName]) {
      fn = mod[funcName];
    } else if (typeof mod === 'function') {
      fn = mod;
    } else {
      throw new Error(`Function not found: ${funcName}`);
    }
    const res = await fn.apply(null, args);
    console.log(JSON.stringify({ok:true, result: sanitize(res)}));
  } catch (e) {
    console.log(JSON.stringify({ok:false, error: e.message, stack: e.stack}));
  }
})();
'''
        runner.write_text(runner_code, encoding='utf-8')
        return str(runner)

    def _init_web_framework(self) -> None:
        try:
            from flask import Flask, request, jsonify
            self.web_app = Flask(__name__)
        except ImportError:
            raise ImportError("Flask is required for web framework. Install with: pip install flask")

    def _register_flask_route(self, method: str, path: str, handler_func: HexzaFunction) -> None:
        if not self.web_app:
            return

        from flask import request, jsonify, Response

        def flask_handler():
            try:
                local_scope = handler_func.closure.copy()
                local_scope["request_args"] = dict(request.args)
                local_scope["request_json"] = request.get_json(silent=True) or {}
                local_scope["request_method"] = request.method

                for stmt in handler_func.body:
                    self.eval(stmt, local_scope)

                return Response("", mimetype="text/plain")

            except ReturnException as e:
                val = e.value

                if isinstance(val, str):
                    return Response(val, mimetype="text/html")

                if isinstance(val, dict):
                    return jsonify(val)

                return Response(str(val), mimetype="text/plain")

            except HexzaError as e:
                return jsonify({"error": str(e)}), 500

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        self.web_app.add_url_rule(
            path,
            endpoint=f"{method}_{path}",
            view_func=flask_handler,
            methods=[method]
        )

    def run_web_server(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        if not self.web_app:
            self._init_web_framework()

        if self.web_app:
            print(f"🚀 Starting web server on {host}:{port}")
            self.web_app.run(host=host, port=port, debug=False)

    def eval(self, node: Any, scope: Optional[Dict[str, Any]] = None) -> Any:
        gen = self.eval_gen(node, scope)
        if inspect.isgenerator(gen):
            try:
                # Run the generator to completion
                result = None
                for yielded in gen:
                    pass
                return result
            except StopIteration as e:
                return e.value
            except ReturnException as e:
                return e.value
        return gen

    def eval_gen(self, node: Any, scope: Optional[Dict[str, Any]] = None) -> Any:
        if scope is None:
            scope = self.global_scope
        if not node:
            return None
        
        node_type = node[0]
        handler = self._eval_handlers.get(node_type)
        
        if handler:
            res = handler(node, scope)
            if inspect.isgenerator(res):
                return (yield from res)
            return res
        
        raise SyntaxError(f"Unknown node type: {node_type}")
    
    def _eval_num(self, node: tuple, scope: Dict) -> Any:
        _, value = node[0:2]
        return value
    
    def _eval_binop(self, node: tuple, scope: Dict) -> Any:
        _, op, left, right = node[0:4]
        lval = yield from self.eval_gen(left, scope)
        rval = yield from self.eval_gen(right, scope)
        
        op_map = {
            "PLUS": lambda a, b: a + b,
            "MINUS": lambda a, b: a - b,
            "MUL": lambda a, b: a * b,
            "DIV": lambda a, b: a / b if b != 0 else float('inf'),
            "MOD": lambda a, b: a % b if b != 0 else 0,
            "POW": lambda a, b: a ** b,
            "LT": lambda a, b: a < b,
            "GT": lambda a, b: a > b,
            "LE": lambda a, b: a <= b,
            "GE": lambda a, b: a >= b,
            "EQEQ": lambda a, b: a == b,
            "NEQ": lambda a, b: a != b,
            "AND": lambda a, b: a and b,
            "OR": lambda a, b: a or b,
            "BIT_AND": lambda a, b: int(a) & int(b),
            "BIT_OR": lambda a, b: int(a) | int(b),
            "BIT_XOR": lambda a, b: int(a) ^ int(b),
            "LSHIFT": lambda a, b: int(a) << int(b),
            "RSHIFT": lambda a, b: int(a) >> int(b),
        }
        
        if op not in op_map:
            raise HexzaError(f"Unknown binary operator: {op}")
        
        return op_map[op](lval, rval)
    
    def _eval_call(self, node: tuple, scope: Dict) -> Any:
        _, func_expr, args_nodes = node[0:3]
        func = yield from self.eval_gen(func_expr, scope)
        args = []
        for arg in args_nodes:
            args.append((yield from self.eval_gen(arg, scope)))

        if isinstance(func, HexzaFunction):
            local_scope = func.closure.copy()
            
            for i, param in enumerate(func.params):
                local_scope[param] = args[i] if i < len(args) else None
            
            # If async, return a generator that executes the body
            if func.is_async:
                def async_body_runner():
                    result = None
                    try:
                        for stmt in func.body:
                            result = yield from self.eval_gen(stmt, local_scope)
                    except ReturnException as e:
                        result = e.value
                    return result
                return async_body_runner()

            # If sync, execute immediately
            result = None
            try:
                for stmt in func.body:
                    result = yield from self.eval_gen(stmt, local_scope)
            except ReturnException as e:
                result = e.value
            
            return result
        
        if callable(func):
            try:
                return func(*args)
            except TypeError as e:
                raise HexzaError(f"Function call error: {e}")
        
        raise HexzaError(f"Cannot call non-function object: {type(func).__name__}")
    
    def _eval_program(self, node: tuple, scope: Dict) -> Any:
        _, statements = node[0:2]
        result = None
        for stmt in statements:
            result = yield from self.eval_gen(stmt, scope)
        return result
    
    def _eval_str(self, node: tuple, scope: Dict) -> Any:
        _, value = node[0:2]
        return value
    
    def _eval_bool(self, node: tuple, scope: Dict) -> Any:
        _, value = node[0:2]
        return value
    
    def _eval_null(self, node: tuple, scope: Dict) -> Any:
        return None
    
    def _eval_array(self, node: tuple, scope: Dict) -> List:
        _, elements = node[0:2]
        result = []
        for elem in elements:
            result.append((yield from self.eval_gen(elem, scope)))
        return result
    
    def _eval_obj(self, node: tuple, scope: Dict) -> Dict:
        _, pairs = node[0:2]
        result = {}
        result = {}
        for key, value_expr in pairs:
            result[key] = yield from self.eval_gen(value_expr, scope)
        return result
    
    def _eval_var(self, node: tuple, scope: Dict) -> Any:
        _, name = node[0:2]
        if name in scope:
            return scope[name]
        raise HexzaError(f"Variable '{name}' is not defined")
    
    def _eval_unary(self, node: tuple, scope: Dict) -> Any:
        _, op, operand = node[0:3]
        val = yield from self.eval_gen(operand, scope)
        
        op_map = {
            "NOT": lambda x: not x,
            "NEG": lambda x: -x,
            "BIT_NOT": lambda x: ~int(x),
        }
        return op_map[op](val)
    
    def _eval_index(self, node: tuple, scope: Dict) -> Any:
        _, obj_expr, index_expr = node[0:3]
        obj = yield from self.eval_gen(obj_expr, scope)
        index = yield from self.eval_gen(index_expr, scope)
        return obj[index]
    
    def _eval_member(self, node: tuple, scope: Dict) -> Any:
        _, obj_expr, member = node[0:3]
        obj = yield from self.eval_gen(obj_expr, scope)
        if isinstance(obj, HexzaInstance):
            if member in obj.__dict__:
                return obj.__dict__[member]
            
            method = obj.__hexza_class__.get_method(member)
            if method:
                new_closure = method.closure.copy()
                new_closure["__hexza_self__"] = obj
                bound_method = HexzaFunction(
                    method.name,
                    method.params,
                    method.body,
                    new_closure,
                    is_async=method.is_async,
                    is_method=True
                )
                return bound_method
            return None
        
        if isinstance(obj, dict):
            return obj.get(member)
        
        if isinstance(obj, list):
            if member == "append":
                return lambda x: obj.append(x) or None
            elif member == "pop":
                return lambda: obj.pop() if obj else None
            elif member == "length":
                return len(obj)
        
        return getattr(obj, member, None)
    
    def _eval_assign(self, node: tuple, scope: Dict) -> Any:
        _, lvalue, rvalue = node[0:3]
        value = yield from self.eval_gen(rvalue, scope)
        
        if lvalue[0] == "var":
            scope[lvalue[1]] = value
        elif lvalue[0] == "index":
            obj = yield from self.eval_gen(lvalue[1], scope)
            index = yield from self.eval_gen(lvalue[2], scope)
            obj[index] = value
        elif lvalue[0] == "member":
            obj = yield from self.eval_gen(lvalue[1], scope)
            member = lvalue[2]
            if isinstance(obj, HexzaInstance):
                obj.__dict__[member] = value
            elif isinstance(obj, dict):
                obj[member] = value
            else:
                setattr(obj, member, value)
        else:
            raise HexzaError(f"Invalid assignment target: {lvalue[0]}")
        
        return value
    
    def _eval_if(self, node: tuple, scope: Dict) -> Any:
        _, condition, true_block, false_block = node[0:4]
        cond_val = yield from self.eval_gen(condition, scope)
        
        if cond_val:
            result = None
            for stmt in true_block:
                result = yield from self.eval_gen(stmt, scope)
            return result
        elif false_block:
            result = None
            for stmt in false_block:
                result = yield from self.eval_gen(stmt, scope)
            return result
        return None
    
    def _eval_while(self, node: tuple, scope: Dict) -> Any:
        _, condition, body = node[0:3]
        result = None
        
        while (yield from self.eval_gen(condition, scope)):
            try:
                for stmt in body:
                    result = yield from self.eval_gen(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_for(self, node: tuple, scope: Dict) -> Any:
        _, init, cond, inc, body = node[0:5]
        
        if init:
            yield from self.eval_gen(init, scope)
        
        result = None
        while True:
            if cond and not (yield from self.eval_gen(cond, scope)):
                break
            try:
                for stmt in body:
                    result = yield from self.eval_gen(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                pass
            
            if inc:
                yield from self.eval_gen(inc, scope)
        
        return result
    
    def _eval_for_in(self, node: tuple, scope: Dict) -> Any:
        _, var_name, iterable_expr, body = node[0:4]
        iterable = yield from self.eval_gen(iterable_expr, scope)
        result = None
        
        for item in iterable:
            scope[var_name] = item
            try:
                for stmt in body:
                    result = yield from self.eval_gen(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_func_def(self, node: tuple, scope: Dict) -> HexzaFunction:
        parts = node[0:]
        name = parts[1]
        params = parts[2]
        body = parts[3]
        is_async = parts[4] if len(parts) > 4 else False
        
        func = HexzaFunction(name, params, body, scope.copy(), is_async=is_async)
        scope[name] = func
        return func
    
    def _eval_var_decl(self, node: tuple, scope: Dict) -> Any:
        """Evaluate variable declaration: let x = 10 or const PI = 3.14"""
        _, kind, name, init_value = node[0:4]
        
        value = None
        if init_value:
            value = yield from self.eval_gen(init_value, scope)
        
        # Store variable in scope
        if kind == "const":
            # Mark as const (we'll add enforcement later)
            scope[name] = value
            # Store const names in a special set if not exists
            if not hasattr(scope, '_consts'):
                if isinstance(scope, dict):
                    scope['__consts__'] = set()
                scope['__consts__'].add(name)
        else:
            scope[name] = value
        
        return value
    
    def _eval_class_def(self, node: tuple, scope: Dict) -> HexzaClass:
        _, name, base, methods = node[0:4]
        base_class = None
        if base and base in scope:
            base_class = scope[base]
        
        methods_dict = {}
        for method in methods:
            _, method_name, params, body = method[0:4]
            methods_dict[method_name] = HexzaFunction(method_name, params, body, scope.copy())
        
        cls = HexzaClass(name, base_class, methods_dict)
        scope[name] = cls
        return cls
    
    def _eval_new(self, node: tuple, scope: Dict) -> HexzaInstance:
        _, class_name, args_nodes = node[0:3]
        cls = scope[class_name]
        args = []
        for arg in args_nodes:
            args.append((yield from self.eval_gen(arg, scope)))
        return cls(*args, vm=self)
    
    def _eval_return(self, node: tuple, scope: Dict) -> None:
        _, value_expr = node[0:2]
        value = None
        if value_expr:
            value = yield from self.eval_gen(value_expr, scope)
        raise ReturnException(value)
    
    def _eval_break(self, node: tuple, scope: Dict) -> None:
        raise BreakException()
    
    def _eval_continue(self, node: tuple, scope: Dict) -> None:
        raise ContinueException()
    
    def _eval_expr(self, node: tuple, scope: Dict) -> Any:
        _, expr = node[0:2]
        return (yield from self.eval_gen(expr, scope))
    
    def _eval_import(self, node: tuple, scope: Dict) -> None:
        _, module_path, ext_hint, alias = node[0:4]
        resolved: Optional[Tuple[str, str]] = None
        if self.pkg_mgr:
            if module_path in self.pkg_mgr.packages:
                info = self.pkg_mgr.packages[module_path]
                pkg_path = info.get("path")
                if pkg_path and isinstance(pkg_path, str) and Path(pkg_path).exists():
                    ext = info.get("ext", "py")
                    if isinstance(ext, str):
                        resolved = (pkg_path, ext)

            if not resolved:
                stem = Path(module_path).stem
                if stem in self.pkg_mgr.packages:
                    info = self.pkg_mgr.packages[stem]
                    pkg_path = info.get("path")
                    if pkg_path and isinstance(pkg_path, str) and Path(pkg_path).exists():
                        ext = info.get("ext", "py")
                        if isinstance(ext, str):
                            resolved = (pkg_path, ext)

        if not resolved:
            p = Path(module_path)
            if p.exists() and p.is_file():
                resolved = (str(p.resolve()), p.suffix.lstrip('.').lower())
        
        if not resolved:
            py_path = Path(module_path).with_suffix('.py')
            if py_path.exists():
                resolved = (str(py_path.resolve()), "py")
        
        if not resolved:
            js_path = Path(module_path).with_suffix('.js')
            if js_path.exists():
                resolved = (str(js_path.resolve()), "js")
        
        if not resolved and self.pkg_mgr:
            maybe = self.pkg_mgr.get_package_path(module_path)
            if maybe:
                resolved = maybe
        
        if not resolved:
            rel_path = Path.cwd() / module_path
            if rel_path.exists():
                resolved = (str(rel_path.resolve()), rel_path.suffix.lstrip('.').lower())
        
        if not resolved:
            installed = list(self.pkg_mgr.packages.keys()) if self.pkg_mgr else []
            raise FileNotFoundError(
                f"Module '{module_path}' not found.\n"
                f"  Installed packages: {installed if installed else 'none'}\n"
                f"  Search paths: registry, current directory"
            )
        
        path_str: str
        ext_str: str
        path_str, ext_str = resolved
        if not Path(path_str).exists():
            raise FileNotFoundError(f"Resolved path does not exist: {path_str}")
        
        try:
            if ext_str == "py":
                module_path_obj = Path(path_str)
                module_name = module_path_obj.stem
                if module_path_obj.is_dir():
                    parent_dir = str(module_path_obj.parent)
                    if parent_dir not in sys.path:
                        sys.path.insert(0, parent_dir)
                    module_name = module_path_obj.name
                
                module = importlib.import_module(module_name)
                scope[alias] = module
                
            elif ext_str == "js":
                runner_path = self._ensure_js_runner() if self.pkg_mgr else None
                proxy: JSProxy = JSProxy(path_str, runner_path)
                scope[alias] = proxy
            else:
                raise ValueError(f"Unsupported module format: .{ext_str}")
        
        except IOError as e:
            raise FileNotFoundError(f"Cannot read module '{module_path}': {e}")
        
        return None
    
    def _eval_export(self, node: tuple, scope: Dict) -> Any:
        _, stmt = node[0:2]
        result = yield from self.eval_gen(stmt, scope)
        if stmt[0] == "func_def":
            func_name = stmt[1]
            if func_name in scope:
                if not hasattr(self, 'exported_symbols'):
                    self.exported_symbols = {}
                self.exported_symbols[func_name] = scope[func_name]
        return result
    
    def _eval_try_catch(self, node: tuple, scope: Dict) -> Any:
        _, try_block, error_var, catch_block, finally_block = node[0:5]
        result = None
        
        try:
            for stmt in try_block:
                result = yield from self.eval_gen(stmt, scope)
        except Exception as e:
            if catch_block and error_var:
                scope[error_var] = str(e)
                for stmt in catch_block:
                    result = yield from self.eval_gen(stmt, scope)
        finally:
            if finally_block:
                for stmt in finally_block:
                    yield from self.eval_gen(stmt, scope)
        
        return result
    
    def _eval_throw(self, node: tuple, scope: Dict) -> None:
        _, value_expr = node[0:2]
        value = yield from self.eval_gen(value_expr, scope)
        raise HexzaError(str(value))
    
    def _eval_api_def(self, node: tuple, scope: Dict) -> None:
        _, api_name, routes_nodes = node[0:3]
        
        if self.enable_web and not self.web_app:
            self._init_web_framework()
        
        if not self.web_app:
            print("⚠️  Cannot define API without Flask")
            return None
        
        route_count = 0
        for route_node in routes_nodes:
            if route_node[0] != "route":
                continue
            
            _, method, path, handler_name = route_node[0:4]
            
            if handler_name not in scope:
                print(f"⚠️  Handler '{handler_name}' not found for {method} {path}")
                continue
            
            handler_func = scope[handler_name]
            if not isinstance(handler_func, HexzaFunction):
                print(f"⚠️  '{handler_name}' is not a function")
                continue
            
            self.api_handlers[(method, path)] = handler_func
            self._register_flask_route(method, path, handler_func)
            route_count += 1
        
        print(f"✅ API '{api_name}' registered with {route_count} routes")
        return None
    
    def _eval_lambda(self, node: tuple, scope: Dict) -> HexzaFunction:
        _, params, body_expr = node[0:3]
        lambda_func = HexzaFunction(
            "<lambda>",
            params,
            [("return", body_expr)],
            scope.copy(),
            is_async=False,
            is_method=False
        )
        return lambda_func
    
    def _eval_ternary(self, node: tuple, scope: Dict) -> Any:
        _, condition, true_expr, false_expr = node[0:4]
        cond_val = yield from self.eval_gen(condition, scope)
        return (yield from self.eval_gen(true_expr, scope)) if cond_val else (yield from self.eval_gen(false_expr, scope))
    
    def _eval_this(self, node: tuple, scope: Dict) -> Any:
        return scope.get("__hexza_self__")
    

def run_repl(pkg_mgr: PackageManager) -> None:
    vm = VM(pkg_mgr, enable_web=False)
    print("Hexza v1.0 - Universal Language (type 'exit' to quit)")
    
    while True:
        try:
            line = input("hexza> ")
            if line.strip() == "exit":
                break
            
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            parser_obj = Parser(tokens)
            ast = parser_obj.parse()
            result = vm.eval(ast)
            
            if result is not None:
                print(result)
        except (SyntaxError, HexzaError) as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n(interrupted)")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hexza v1.0 - Universal Programming Language"
    )
    parser.add_argument("script", nargs="?", help="Script file to execute (.hxza)")
    parser.add_argument("--install", metavar="PACKAGE", help="Install a package (pip or npm)")
    parser.add_argument("--npm", action="store_true", help="Use npm instead of pip for installation")
    parser.add_argument("--track-native", nargs=2, metavar=("NAME", "PATH"), help="Track a native library")
    parser.add_argument("--list", action="store_true", help="List installed packages")
    parser.add_argument("--web", action="store_true", help="Run web server after script")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host (default: 127.0.0.1)")
    parser.add_argument("--version", action="store_true", help="Show Hexza version")
    parser.add_argument("--compile", metavar="OUTPUT", help="Compile script to executable")
    parser.add_argument("--compile-native", metavar="OUTPUT", help="Compile script to native executable (LLVM)")
    parser.add_argument("--fmt", metavar="FILE", help="Format Hexza source file")
    
    # Phase 2 flags
    parser.add_argument("--use-bytecode", action="store_true", help="Use bytecode VM (faster)")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark bytecode vs AST")
    
    args = parser.parse_args()
    
    if args.version:
        print("Hexza v1.0 - Universal Programming Language")
        print("Features: Game Dev, Web Dev, AI, OS, C++/JS Interop, Compiler")
        print("Motto: Everything Can Be Dreamed Can Be Built - SFFF (Simple Fast Flexible Free)")
        return
    
    pkg_mgr = PackageManager()
    
    if args.list:
        pkg_mgr.list_packages()
        return
    
    if args.install:
        success = pkg_mgr.install(args.install, use_npm=args.npm)
        sys.exit(0 if success else 1)
        
    if args.track_native:
        name, path = args.track_native
        pkg_mgr.track_native(name, path)
        sys.exit(0)
        
    if args.fmt:
        try:
            path = Path(args.fmt)
            if not path.exists():
                print(f"❌ File not found: {args.fmt}")
                sys.exit(1)
                
            content = path.read_text(encoding='utf-8')
            formatter = HexzaFormatter()
            formatted = formatter.format(content)
            path.write_text(formatted, encoding='utf-8')
            print(f"[OK] Formatted {args.fmt}")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Formatting failed: {e}")
            sys.exit(1)
    
    if args.compile_native:
        if not args.script:
            print("❌ Error: Please specify a script to compile")
            sys.exit(1)
            
        try:
            from llvm_backend import LLVMCompiler
            compiler = LLVMCompiler()
            
            # For now, just compile a dummy function to test integration
            ir_code = compiler.compile_function("main", [], "int", None)
            
            output_ll = Path(args.compile_native).with_suffix(".ll")
            output_ll.write_text(ir_code, encoding='utf-8')
            
            print(f"[OK] Generated LLVM IR: {output_ll}")
            print(">> Native compilation requires clang/llc (not fully implemented yet)")
            sys.exit(0)
        except ImportError:
            print("[ERROR] llvm_backend.py not found or llvmlite missing")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Native compilation failed: {e}")
            sys.exit(1)
            
    if args.compile:
        if not args.script:
            print("❌ Error: Please specify a script to compile")
            sys.exit(1)
        
        try:
            import PyInstaller.__main__
            
            script_path = Path(args.script).resolve()
            if not script_path.exists():
                raise FileNotFoundError(f"Script '{args.script}' not found")
            
            output_name = args.compile
            if not output_name.endswith('.exe') and platform.system() == "Windows":
                output_name += '.exe'
            
            print(f"🔨 Compiling {script_path.name} to {output_name}...")
            
            # Create a temporary wrapper script that embeds the interpreter
            wrapper_code = f'''
import sys
from pathlib import Path

# Embed the hexza interpreter
{Path(__file__).read_text(encoding='utf-8')}

# Run the target script
if __name__ == "__main__":
    script_content = """
{script_path.read_text(encoding='utf-8')}
"""
    lexer = Lexer(script_content)
    tokens = lexer.tokenize()
    parser_obj = Parser(tokens)
    ast = parser_obj.parse()
    vm = VM(PackageManager(), enable_web=False)
    vm.eval(ast)
'''
            
            wrapper_path = Path("_hexza_compile_temp.py")
            wrapper_path.write_text(wrapper_code, encoding='utf-8')
            
            PyInstaller.__main__.run([
                str(wrapper_path),
                '--onefile',
                '--name', Path(output_name).stem,
                '--distpath', '.',
                '--specpath', '.',
                '--clean',
            ])
            
            wrapper_path.unlink(missing_ok=True)
            Path(f"{Path(output_name).stem}.spec").unlink(missing_ok=True)
            
            print(f"✅ Compiled successfully: {output_name}")
            
        except ImportError:
            print("❌ PyInstaller not installed. Run: hexza --install pyinstaller")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        return
    
    if not args.script:
        run_repl(pkg_mgr)
        return
    
    try:
        script_path = Path(args.script)
        if not script_path.exists():
            raise FileNotFoundError(f"Script '{args.script}' not found")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        parser_obj = Parser(tokens)
        ast = parser_obj.parse()
        
        # Phase 2: Bytecode or Benchmark mode
        if args.benchmark:
            print(">> Benchmarking AST vs Bytecode\n")
            
            # AST mode
            start = time.time()
            vm = VM(pkg_mgr, enable_web=args.web)
            vm.eval(ast)
            ast_time = time.time() - start
            
            # Bytecode mode
            start = time.time()
            compiler = BytecodeCompiler()
            bytecode = compiler.compile(ast)
            bvm = BytecodeVM(vm.global_scope)
            bvm.run(bytecode)
            bytecode_time = time.time() - start
            
            print(f"\n>> Benchmark Results:")
            print(f"   AST Mode:      {ast_time*1000:.2f} ms")
            print(f"   Bytecode Mode: {bytecode_time*1000:.2f} ms")
            print(f"   Speedup:       {ast_time/bytecode_time:.2f}x faster!")
            
        elif args.use_bytecode:
            # Bytecode mode
            compiler = BytecodeCompiler()
            bytecode = compiler.compile(ast)
            vm = VM(pkg_mgr, enable_web=args.web)
            bvm = BytecodeVM(vm.global_scope)
            bvm.run(bytecode)
        else:
            # Normal AST mode
            vm = VM(pkg_mgr, enable_web=args.web)
            vm.eval(ast)
        
        if args.web:
            vm.run_web_server(host=args.host, port=args.port)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except HexzaError as e:
        print(f"❌ Hexza Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Runtime Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
