import sys
try:
    from llvmlite import ir
    import llvmlite.binding as llvm
except ImportError:
    print("❌ llvmlite not found. Run: hexza --install llvmlite")
    # Mock for development if not installed
    class MockIR:
        def Module(self, name): return MockModule(name)
        def FunctionType(self, ret, args): return "func_type"
        def Function(self, module, ftype, name): return MockFunction(name)
        def IntType(self, bits): return "int_type"
        def Constant(self, type, val): return f"const({val})"
        def IRBuilder(self, block): return MockBuilder()
        
    class MockModule:
        def __init__(self, name): self.name = name
        def __str__(self): return f"; ModuleID = '{self.name}'\n"
        
    class MockFunction:
        def __init__(self, name): self.name = name
        def append_basic_block(self, name): return name
        
    class MockBuilder:
        def ret(self, val): pass
        
    ir = MockIR()

class LLVMCompiler:
    def __init__(self):
        self.module = ir.Module("hexza_module")
        self.builder = None
        self.functions = {}
        self._init_llvm()
        
    def _init_llvm(self):
        try:
            llvm.initialize()
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except:
            pass

    def compile_function(self, name, arg_types, ret_type, body_ast):
        """Compile a simple function to LLVM IR"""
        # Create function type (assuming int32 for now)
        func_type = ir.FunctionType(ir.IntType(32), [])
        func = ir.Function(self.module, func_type, name=name)
        
        # Create entry block
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        # Simple return 0 for now
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        
        return str(self.module)

    def get_ir(self):
        return str(self.module)
