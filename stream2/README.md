# Stream Manager 使用手册

基于 FFmpeg 的 HLS 直播流管理工具。

## 前置条件

- 已安装 [FFmpeg](https://ffmpeg.org/) 并加入系统 PATH
- 视频源文件为 MP4 格式，放在 `media/` 目录下
- Gateway 服务已启动（端口 8080），用于提供 HLS 文件访问

## 目录结构

```
stream2/
├── stream_manager.py   # 流管理脚本
├── media/              # 视频源文件（放入 stream1.mp4, stream2.mp4 ...）
└── .pids/              # 运行时自动创建，存储进程 PID

gateway/hls/            # HLS 输出（自动创建）
├── stream1.m3u8        # 播放列表
└── stream1_00000000.ts # TS 分片（自动滚动，保留最近 5 个）
```

## 命令

### 启动流

```bash
python stream_manager.py start-stream <名称>
```

`<名称>` 对应 `media/<名称>.mp4` 文件。

示例：
```bash
python stream_manager.py start-stream stream1
```

启动后输出：
```
直播流 stream1 已启动 (PID: 12345) -> hls/stream1.m3u8
```

### 停止流

```bash
python stream_manager.py stop-stream <名称>
```

停止流并自动清理对应的 m3u8 和 ts 文件。

### 查看运行中的流

```bash
python stream_manager.py list
```

## 播放地址

流启动后，通过以下地址播放：

```
http://localhost:8080/hls/<名称>.m3u8
```

示例：`http://localhost:8080/hls/stream1.m3u8`

支持浏览器（需 hls.js）和 VLC 播放器。

## 参数说明

在 `stream_manager.py` 顶部可调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SEGLENT` | 10 | 每个 TS 分片时长（秒） |
| `NUMSEGS` | 5 | 播放列表中保留的分片数量 |

## 常见问题

**Q: 启动报错 "找不到视频源文件"**
A: 确认 `media/<名称>.mp4` 文件存在。

**Q: 启动报错 "已在运行"**
A: 先执行 `stop-stream` 停止，或手动删除 `.pids/<名称>.pid`。

**Q: 播放卡住**
A: 确认 gateway 已重启（修改了 HLS HTTP 头后需要重启 gateway）。
