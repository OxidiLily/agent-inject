#!/usr/bin/env python3
"""Install the explicitly requested tools on Windows, Linux, or macOS."""
import os, platform, shutil, subprocess, sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
SKILL_URL = "https://raw.githubusercontent.com/decolua/9router/refs/heads/master/skills/9router/SKILL.md"

def run(args):
    print("[run]", " ".join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True)

def install_rtk():
    osname = platform.system()
    if osname == "Windows":
        if not shutil.which("winget"): raise RuntimeError("winget unavailable; install RTK manually from https://github.com/rtk-ai/rtk")
        listed = subprocess.run(["winget", "list", "--id", "rtk-ai.rtk", "--exact"], capture_output=True, text=True)
        if listed.returncode != 0 or "rtk-ai.rtk" not in listed.stdout:
            run(["winget", "install", "--id", "rtk-ai.rtk", "--exact", "--accept-source-agreements", "--accept-package-agreements"])
        else: print("[ok] RTK already installed via winget")
        candidates = [Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links/rtk.exe", Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages"]
        for candidate in candidates:
            if candidate.is_file(): os.environ["PATH"] = str(candidate.parent) + os.pathsep + os.environ["PATH"]
            elif candidate.is_dir():
                for exe in candidate.glob("*/rtk.exe"):
                    os.environ["PATH"] = str(exe.parent) + os.pathsep + os.environ["PATH"]
    elif shutil.which("brew"):
        if subprocess.run(["brew", "list", "--versions", "rtk"],capture_output=True).returncode: run(["brew", "install", "rtk"])
        else: print("[ok] RTK already installed via Homebrew")
    else:
        raise RuntimeError("Homebrew unavailable; install RTK using official instructions: https://github.com/rtk-ai/rtk")
    if shutil.which("rtk"):
        run(["rtk", "--version"]); run(["rtk", "gain"])
    else: print("[warn] RTK installed but unavailable in PATH; restart terminal before rerunning")


def install_uv():
    if shutil.which("uv"): return
    if platform.system() == "Windows" and shutil.which("winget"):
        listed=subprocess.run(["winget","list","--id","astral-sh.uv","--exact"],capture_output=True,text=True)
        if listed.returncode != 0 or "astral-sh.uv" not in listed.stdout: run(["winget", "install", "--id=astral-sh.uv", "-e", "--accept-source-agreements", "--accept-package-agreements"])
    elif platform.system() in {"Linux", "Darwin"} and shutil.which("brew"):
        if subprocess.run(["brew","list","--versions","uv"],capture_output=True).returncode: run(["brew", "install", "uv"])
    else:
        raise RuntimeError("uv unavailable; follow official setup https://docs.astral.sh/uv/getting-started/installation/ then rerun")
    if not shutil.which("uv"):
        local=Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Links/uv.exe"
        if local.is_file(): os.environ["PATH"] = str(local.parent) + os.pathsep + os.environ["PATH"]
    if not shutil.which("uv"): raise RuntimeError("uv installed but unavailable in PATH; restart terminal and rerun")


def install_python_tools():
    install_uv()
    if not shutil.which("python") and not shutil.which("python3"):
        raise RuntimeError("Python 3.10+ unavailable; install Python, then rerun")
    py = shutil.which("python") or shutil.which("python3")
    run([py, "-c", "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ required'"])
    run(["uv", "tool", "install", "--upgrade", "--force", "browser-use"])
    if shutil.which("browser-use"):
        run(["browser-use", "--help"]); run(["browser-use", "skill", "install"])
    else: print("[warn] browser-use installed; reopen terminal to refresh PATH")
    run(["uv", "tool", "install", "--force", "https://github.com/Panniantong/Agent-Reach/releases/latest/download/agent-reach.zip"])
    if shutil.which("agent-reach"):
        run(["agent-reach", "setup"]); run(["agent-reach", "channels"])
    else: print("[warn] agent-reach installed; reopen terminal and run agent-reach setup")


def install_9router_skill():
    target = ROOT / "Skills" / "9router" / "SKILL.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(SKILL_URL, timeout=30) as response: content = response.read()
    if not content.startswith(b"---") or b"name: 9router" not in content: raise RuntimeError("Upstream 9Router skill failed validation")
    target.write_bytes(content)
    print(f"[ok] 9Router skill: {target}")


def main():
    print(f"Platform: {platform.system()} / {platform.machine()}")
    if platform.system() not in {"Windows", "Linux", "Darwin"}: raise RuntimeError("Unsupported operating system")
    install_rtk(); install_python_tools(); install_9router_skill()
    print("[ok] All requested install steps completed; restart agent sessions if needed")






if __name__ == "__main__":
    try: main()
    except (subprocess.CalledProcessError,OSError,RuntimeError) as exc: print(f"[failed] {exc}",file=sys.stderr); sys.exit(1)
