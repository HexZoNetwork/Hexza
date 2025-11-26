#!/usr/bin/env python3
import os, sys, ctypes, argparse, asyncio, importlib, time, platform, hashlib
import inspect, json, subprocess, re, struct, socket, threading, queue
from typing import Any, Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import urllib.parse
import importlib.util
from abc import ABC
import traceback
import readline
class PackageManager:
    def __init__(self, registry_path: str = ".hexza_packages"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(exist_ok=True)
        self.packages: Dict[str, dict] = {}
        self.load_registry()
    
    def load_registry(self) -> None:
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                self.packages = json.load(f)
    
    def save_registry(self) -> None:
        registry_file = self.registry_path / "registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.packages, f, indent=2)
    
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
    
    def parse_function(self) -> tuple:
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.LP)
        
        params = []
        while self.peek().type != TokenType.RP:
            params.append(self.consume(TokenType.IDENTIFIER).value)
            if self.peek().type == TokenType.COMMA:
                self.consume()
        
        self.consume(TokenType.RP)
        self.consume(TokenType.LBRACE)
        body = self.parse_block()
        self.consume(TokenType.RBRACE)
        
        return ("func_def", name, params, body)
    
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
            "await": self._eval_await,
            "call": self._eval_call,
            "program": self._eval_program,
        }
    
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
        }
        builtins_dict["global"] = GlobalNamespace(builtins_dict)
        return builtins_dict

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
        
        from flask import request, jsonify
        
        def flask_handler():
            try:
                local_scope = handler_func.closure.copy()
                local_scope["request_args"] = dict(request.args)
                local_scope["request_json"] = request.get_json(silent=True) or {}
                local_scope["request_method"] = request.method
                for stmt in handler_func.body:
                    self.eval(stmt, local_scope)
                
                return jsonify({"status": "ok"}), 200
            
            except ReturnException as e:
                return jsonify({"result": e.value}), 200
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
        if scope is None:
            scope = self.global_scope
        
        if not node:
            return None
        
        node_type = node[0]
        handler = self._eval_handlers.get(node_type)
        
        if handler:
            return handler(node, scope)
        
        raise SyntaxError(f"Unknown node type: {node_type}")
    
    def _eval_num(self, node: tuple, scope: Dict) -> Any:
        _, value = node[0:2]
        return value
    
    def _eval_binop(self, node: tuple, scope: Dict) -> Any:
        _, op, left, right = node[0:4]
        lval = self.eval(left, scope)
        rval = self.eval(right, scope)
        
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
        func = self.eval(func_expr, scope)
        args = [self.eval(arg, scope) for arg in args_nodes]

        if isinstance(func, HexzaFunction):
            local_scope = func.closure.copy()
            
            for i, param in enumerate(func.params):
                local_scope[param] = args[i] if i < len(args) else None
            
            result = None
            try:
                for stmt in func.body:
                    result = self.eval(stmt, local_scope)
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
            result = self.eval(stmt, scope)
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
        return [self.eval(elem, scope) for elem in elements]
    
    def _eval_obj(self, node: tuple, scope: Dict) -> Dict:
        _, pairs = node[0:2]
        result = {}
        for key, value_expr in pairs:
            result[key] = self.eval(value_expr, scope)
        return result
    
    def _eval_var(self, node: tuple, scope: Dict) -> Any:
        _, name = node[0:2]
        if name in scope:
            return scope[name]
        raise HexzaError(f"Variable '{name}' is not defined")
    
    def _eval_unary(self, node: tuple, scope: Dict) -> Any:
        _, op, operand = node[0:3]
        val = self.eval(operand, scope)
        
        op_map = {
            "NOT": lambda x: not x,
            "NEG": lambda x: -x,
            "BIT_NOT": lambda x: ~int(x),
        }
        return op_map[op](val)
    
    def _eval_index(self, node: tuple, scope: Dict) -> Any:
        _, obj_expr, index_expr = node[0:3]
        obj = self.eval(obj_expr, scope)
        index = self.eval(index_expr, scope)
        return obj[index]
    
    def _eval_member(self, node: tuple, scope: Dict) -> Any:
        _, obj_expr, member = node[0:3]
        obj = self.eval(obj_expr, scope)
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
        value = self.eval(rvalue, scope)
        
        if lvalue[0] == "var":
            scope[lvalue[1]] = value
        elif lvalue[0] == "index":
            obj = self.eval(lvalue[1], scope)
            index = self.eval(lvalue[2], scope)
            obj[index] = value
        elif lvalue[0] == "member":
            obj = self.eval(lvalue[1], scope)
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
        cond_val = self.eval(condition, scope)
        
        if cond_val:
            result = None
            for stmt in true_block:
                result = self.eval(stmt, scope)
            return result
        elif false_block:
            result = None
            for stmt in false_block:
                result = self.eval(stmt, scope)
            return result
        return None
    
    def _eval_while(self, node: tuple, scope: Dict) -> Any:
        _, condition, body = node[0:3]
        result = None
        
        while self.eval(condition, scope):
            try:
                for stmt in body:
                    result = self.eval(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_for(self, node: tuple, scope: Dict) -> Any:
        _, init, cond, inc, body = node[0:5]
        
        if init:
            self.eval(init, scope)
        
        result = None
        while True:
            if cond and not self.eval(cond, scope):
                break
            try:
                for stmt in body:
                    result = self.eval(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                pass
            
            if inc:
                self.eval(inc, scope)
        
        return result
    
    def _eval_for_in(self, node: tuple, scope: Dict) -> Any:
        _, var_name, iterable_expr, body = node[0:4]
        iterable = self.eval(iterable_expr, scope)
        result = None
        
        for item in iterable:
            scope[var_name] = item
            try:
                for stmt in body:
                    result = self.eval(stmt, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_func_def(self, node: tuple, scope: Dict) -> HexzaFunction:
        _, name, params, body = node[0:4]
        func = HexzaFunction(name, params, body, scope.copy())
        scope[name] = func
        return func
    
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
        args = [self.eval(arg, scope) for arg in args_nodes]
        return cls(*args, vm=self)
    
    def _eval_return(self, node: tuple, scope: Dict) -> None:
        _, value_expr = node[0:2]
        value = None
        if value_expr:
            value = self.eval(value_expr, scope)
        raise ReturnException(value)
    
    def _eval_break(self, node: tuple, scope: Dict) -> None:
        raise BreakException()
    
    def _eval_continue(self, node: tuple, scope: Dict) -> None:
        raise ContinueException()
    
    def _eval_expr(self, node: tuple, scope: Dict) -> Any:
        _, expr = node[0:2]
        return self.eval(expr, scope)
    
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
        result = self.eval(stmt, scope)
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
                result = self.eval(stmt, scope)
        except Exception as e:
            if catch_block and error_var:
                scope[error_var] = str(e)
                for stmt in catch_block:
                    result = self.eval(stmt, scope)
        finally:
            if finally_block:
                for stmt in finally_block:
                    self.eval(stmt, scope)
        
        return result
    
    def _eval_throw(self, node: tuple, scope: Dict) -> None:
        _, value_expr = node[0:2]
        value = self.eval(value_expr, scope)
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
        cond_val = self.eval(condition, scope)
        return self.eval(true_expr, scope) if cond_val else self.eval(false_expr, scope)
    
    def _eval_this(self, node: tuple, scope: Dict) -> Any:
        return scope.get("__hexza_self__")
    
    def _eval_await(self, node: tuple, scope: Dict) -> Any:
        _, expr = node[0:2]
        return self.eval(expr, scope)
def run_repl(pkg_mgr: PackageManager) -> None:
    vm = VM(pkg_mgr, enable_web=False)
    print("Hexza v0.1 - (type 'exit' to quit)")
    
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
        description="Hexza v0.1 - Beta Lang"
    )
    parser.add_argument("script", nargs="?", help="Script file to execute (.hxza)")
    parser.add_argument("--install", metavar="PACKAGE", help="Install a package (pip or npm)")
    parser.add_argument("--npm", action="store_true", help="Use npm instead of pip for installation")
    parser.add_argument("--list", action="store_true", help="List installed packages")
    parser.add_argument("--web", action="store_true", help="Run web server after script")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host (default: 127.0.0.1)")
    parser.add_argument("--version", action="store_true", help="Show Hexza version")
    
    args = parser.parse_args()
    
    if args.version:
        print("Hexza v0.1 - Beta Lang")
        print("Features: Any")
        return
    
    pkg_mgr = PackageManager()
    
    if args.list:
        pkg_mgr.list_packages()
        return
    
    if args.install:
        success = pkg_mgr.install(args.install, use_npm=args.npm)
        sys.exit(0 if success else 1)
    
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
    main()
