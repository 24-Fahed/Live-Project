"""历史 HLS 演示配置。

当前项目已经不再依赖独立的 HLS 演示子系统，但保留这份配置是为了：
- 兼容旧版本代码与历史文档
- 方便回看早期演示实现

新版本的媒体播放应以 SRS + 网关代理方案为准。
"""

from pathlib import Path


# 旧版示例中存放 HLS 文件的本地目录。
HLS_DIR = Path("runtime/hls")

# 演示视频源路径，仅用于早期样例或回溯历史逻辑。
DEMO_VIDEO = Path("stream/stream-001.mp4")
