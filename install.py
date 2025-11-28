#!/usr/bin/env python3
import sys, subprocess, os, shutil, stat, json, ctypes

APP_NAME="Hexza"
SCRIPT_NAME="hexza.py"

def safe_copy(src,dst):
    os.makedirs(os.path.dirname(dst),exist_ok=True)
    shutil.copy2(src,dst)

def broadcast_env_update():
    HWND_BROADCAST=0xFFFF
    WM_SETTINGCHANGE=0x001A
    SMTO_ABORTIFHUNG=0x0002
    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST,WM_SETTINGCHANGE,0,"Environment",SMTO_ABORTIFHUNG,5000,None)

def add_to_path_windows(p):
    import winreg
    try:
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Environment",0,winreg.KEY_READ|winreg.KEY_WRITE)
        try:
            cur,_=winreg.QueryValueEx(k,"Path")
        except FileNotFoundError:
            cur=""
        items=[x for x in cur.split(';') if x]
        if p.rstrip("\\") in [x.rstrip("\\") for x in items]:
            print("[OK] PATH entry exists")
        else:
            items.append(p)
            winreg.SetValueEx(k,"Path",0,winreg.REG_EXPAND_SZ,';'.join(items))
            print("[OK] Added to PATH")
        broadcast_env_update()
        return True
    except:
        print("[ERROR] PATH update failed")
        return False

def remove_from_path_windows(p):
    import winreg
    try:
        k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Environment",0,winreg.KEY_READ|winreg.KEY_WRITE)
        cur,_=winreg.QueryValueEx(k,"Path")
        new=';'.join([x for x in cur.split(';') if x.rstrip('\\')!=p.rstrip('\\')])
        winreg.SetValueEx(k,"Path",0,winreg.REG_EXPAND_SZ,new)
        broadcast_env_update()
        print("[OK] PATH cleaned")
    except: pass

def install_windows():
    print(f"\n--- Installing {APP_NAME} on Windows ---")

    base = os.getenv("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    root = os.path.join(base, APP_NAME)
    bind = os.path.join(root, "bin")
    os.makedirs(bind, exist_ok=True)
    src_main = os.path.join(os.path.dirname(__file__), SCRIPT_NAME)
    dst_main = os.path.join(bind, SCRIPT_NAME)
    safe_copy(src_main, dst_main)
    src_llvm = os.path.join(os.path.dirname(__file__), "llvm_backend.py")
    dst_llvm = os.path.join(bind, "llvm_backend.py")
    safe_copy(src_llvm, dst_llvm)
    launcher = os.path.join(bind, f"{APP_NAME.lower()}.bat")
    with open(launcher, "w", encoding="utf-8") as f:
        f.write(f'@echo off\r\npython "{dst_main}" %*\r\n')

    add_to_path_windows(bind)

    print("\n[INFO] Installation finished.")
    print(f"Run:  {APP_NAME.lower()}")

def uninstall_windows():
    print(f"\n--- Uninstalling {APP_NAME} on Windows ---")
    base=os.getenv('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'),'AppData','Local')
    root=os.path.join(base,APP_NAME)
    bind=os.path.join(root,'bin')
    remove_from_path_windows(bind)
    if os.path.exists(root): shutil.rmtree(root,ignore_errors=True)
    print("[OK] Removed installation directory")

def install_linux():
    print(f"\n--- Installing {APP_NAME} on Linux ---")
    lib=os.path.expanduser(f"~/.local/lib/{APP_NAME.lower()}")
    bind=os.path.expanduser("~/.local/bin")
    os.makedirs(lib,exist_ok=True)
    os.makedirs(bind,exist_ok=True)
    src=os.path.join(os.path.dirname(__file__),SCRIPT_NAME)
    dst=os.path.join(lib,SCRIPT_NAME)
    safe_copy(src,dst)

    execp=os.path.join(bind,APP_NAME.lower())
    with open(execp,"w") as f:
        f.write(
            f"#!/usr/bin/env python3\n"
            f"import os,sys\n"
            f"p=os.path.expanduser('~/.local/lib/{APP_NAME.lower()}/{SCRIPT_NAME}')\n"
            f"os.execv(sys.executable,[sys.executable,p]+sys.argv[1:])\n"
        )
    
    # Make executable
    os.chmod(execp, os.stat(execp).st_mode | stat.S_IEXEC)

    print("\n[INFO] Installation finished.")
    print(f"Run:  {APP_NAME.lower()}")

def uninstall_linux():
    print(f"\n--- Uninstalling {APP_NAME} on Linux ---")
    lib=os.path.expanduser(f"~/.local/lib/{APP_NAME.lower()}")
    bind=os.path.expanduser("~/.local/bin")
    execp=os.path.join(bind,APP_NAME.lower())
    if os.path.exists(execp): os.remove(execp)
    if os.path.exists(lib): shutil.rmtree(lib,ignore_errors=True)
    print("[OK] Uninstalled")

def install_dependencies():
    """Install optional dependencies for Hexza universal features"""
    print("\n--- Installing Dependencies ---")
    dependencies = [
        ("pygame", "Game Development"),
        ("flask", "Web Development"),
        ("numpy", "AI & Math"),
        ("pyinstaller", "Executable Compiler"),
    ]
    
    for package, purpose in dependencies:
        try:
            print(f"📦 Installing {package} ({purpose})...")
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"   ✅ {package} installed")
            else:
                print(f"   ⚠️  {package} failed (optional)")
        except Exception as e:
            print(f"   ⚠️  {package} failed: {e} (optional)")
    
    print("\n[INFO] Dependency installation complete (optional packages)")

def check(cmd, label):
    try:
        subprocess.run(cmd,capture_output=True,check=True)
        print(f"[OK] {label}")
    except:
        print(f"[X] Missing {label}")

def main():
    args=sys.argv[1:]
    
    # Check for flags
    no_modules = "--nomodule" in args
    uninstall = "--uninstall" in args
    
    if uninstall:
        if sys.platform=="win32": 
            uninstall_windows()
        elif sys.platform.startswith("linux"): 
            uninstall_linux()
        else:
            print("[ERROR] Only Linux + Windows supported")
        return

    if not (sys.version_info.major==3 and sys.version_info.minor>=10):
        print("[ERROR] Python 3.10+ required")
        sys.exit(1)

    check(["node","--version"],"Node.js (optional)")

    if sys.platform=="win32":
        install_windows()
        if not no_modules:
            install_dependencies()
        else:
            print("\n[INFO] Skipping module installation (--nomodule)")
    elif sys.platform.startswith("linux"):
        install_linux()
        if not no_modules:
            install_dependencies()
        else:
            print("\n[INFO] Skipping module installation (--nomodule)")
    else:
        print("[ERROR] Unsupported OS")
        sys.exit(1)

if __name__=="__main__":
    main()