#!/usr/bin/env python3
"""HLS HTTPS 服务器控制脚本。

用法:
    python -m app.subsystems.hls.script.hls_server start     # 启动服务器（阻塞运行）
    python -m app.subsystems.hls.script.hls_server status    # 查看状态
"""

import sys
import signal
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.subsystems.hls import hls_server
from app.subsystems.hls.config import CERT_DIR, CERT_FILE

# PID 文件路径
PID_FILE = Path(CERT_DIR).parent / "hls_server.pid"


def save_pid() -> None:
    """保存当前进程 PID。"""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(sys.modules["os"].getpid()))


def remove_pid() -> None:
    """删除 PID 文件。"""
    if PID_FILE.exists():
        PID_FILE.unlink()


def is_running() -> bool:
    """检查服务器是否正在运行。"""
    if not PID_FILE.exists():
        return False

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # 检查进程是否存在
        import os
        try:
            os.kill(pid, 0)  # 发送空信号检查进程
            return True
        except OSError:
            # 进程不存在，清理 PID 文件
            remove_pid()
            return False
    except (ValueError, FileNotFoundError):
        return False


def cmd_start() -> None:
    """启动服务器（阻塞运行，Ctrl+C 停止）。"""
    if is_running():
        print("HLS 服务器已在运行中")
        return

    print("正在启动 HLS 服务器...")

    # 保存 PID
    save_pid()

    # 注册退出时清理 PID
    def cleanup(signum=None, frame=None):
        remove_pid()
        if signum is not None:
            print("\nHLS 服务器已停止")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # 阻塞式启动
    try:
        hls_server.start()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        remove_pid()
        print(f"启动失败: {e}")
        sys.exit(1)


def cmd_status() -> None:
    """查看状态。"""
    if is_running():
        print("✓ HLS 服务器运行中")
        try:
            with open(PID_FILE, "r") as f:
                pid = f.read().strip()
            print(f"  PID: {pid}")
        except:
            pass
    else:
        print("✗ HLS 服务器未运行")


def main() -> None:
    if len(sys.argv) < 2:
        print("HLS HTTPS 服务器控制脚本")
        print()
        print("用法:")
        print("  python -m app.subsystems.hls.script.hls_server start   # 启动服务器")
        print("  python -m app.subsystems.hls.script.hls_server status  # 查看状态")
        print()
        print("注意: start 命令会阻塞运行，使用 Ctrl+C 停止服务器")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "start":
        cmd_start()
    elif command == "status":
        cmd_status()
    else:
        print(f"未知命令: {command}")
        print("可用命令: start, status")
        sys.exit(1)


if __name__ == "__main__":
    main()
