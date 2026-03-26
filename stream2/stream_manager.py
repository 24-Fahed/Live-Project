import sys
import os
import subprocess
import signal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
HLS_BASE_DIR = os.path.join(os.path.dirname(BASE_DIR), "docker", "hls-data")
PID_DIR = os.path.join(BASE_DIR, ".pids")

SEGLENT = 10
NUMSEGS = 5


def get_pid_path(name):
    os.makedirs(PID_DIR, exist_ok=True)
    return os.path.join(PID_DIR, f"{name}.pid")


def start_stream(name):
    mp4 = os.path.join(MEDIA_DIR, f"{name}.mp4")
    if not os.path.isfile(mp4):
        print(f"错误: 找不到视频源文件 {mp4}")
        sys.exit(1)

    pid_path = get_pid_path(name)
    if os.path.exists(pid_path):
        print(f"错误: 流 {name} 已在运行（pid 文件: {pid_path}），请先 stop")
        sys.exit(1)

    hls_dir = os.path.join(HLS_BASE_DIR, name)
    os.makedirs(hls_dir, exist_ok=True)

    m3u8_path = os.path.join(hls_dir, f"{name}.m3u8")
    ts_pattern = os.path.join(hls_dir, f"{name}_%08d.ts")

    cmd = [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", mp4,
        "-c:v", "copy",
        "-c:a", "copy",
        "-fflags", "+genpts",
        "-f", "hls",
        "-hls_time", str(SEGLENT),
        "-hls_list_size", str(NUMSEGS),
        "-hls_flags", "delete_segments+append_list",
        "-hls_segment_filename", ts_pattern,
        m3u8_path,
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    with open(pid_path, "w") as f:
        f.write(str(proc.pid))

    print(f"直播流 {name} 已启动 (PID: {proc.pid}) -> hls/{name}/{name}.m3u8")


def stop_stream(name):
    pid_path = get_pid_path(name)
    if not os.path.exists(pid_path):
        print(f"错误: 流 {name} 未在运行")
        sys.exit(1)

    with open(pid_path) as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    os.remove(pid_path)

    # 清理 HLS 文件
    hls_dir = os.path.join(HLS_BASE_DIR, name)
    if os.path.isdir(hls_dir):
        for f in os.listdir(hls_dir):
            try:
                os.remove(os.path.join(hls_dir, f))
            except PermissionError:
                pass
        try:
            os.rmdir(hls_dir)
        except OSError:
            pass

    print(f"直播流 {name} 已停止并删除 (PID: {pid})")


def list_streams():
    os.makedirs(PID_DIR, exist_ok=True)
    found = False
    for f in os.listdir(PID_DIR):
        if f.endswith(".pid"):
            name = f[:-4]
            pid_path = os.path.join(PID_DIR, f)
            with open(pid_path) as pf:
                pid = pf.read().strip()
            try:
                os.kill(int(pid), 0)
                print(f"  {name}  (PID: {pid})")
                found = True
            except ProcessLookupError:
                os.remove(pid_path)
    if not found:
        print("当前没有活跃的直播流")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print(f"  python {os.path.basename(__file__)} start-stream <名称>")
        print(f"  python {os.path.basename(__file__)} stop-stream <名称>")
        print(f"  python {os.path.basename(__file__)} list")
        sys.exit(1)

    action = sys.argv[1]

    if action == "start-stream":
        if len(sys.argv) < 3:
            print("错误: 请指定流名称")
            sys.exit(1)
        start_stream(sys.argv[2])
    elif action == "stop-stream":
        if len(sys.argv) < 3:
            print("错误: 请指定流名称")
            sys.exit(1)
        stop_stream(sys.argv[2])
    elif action == "list":
        list_streams()
    else:
        print(f"未知命令: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
