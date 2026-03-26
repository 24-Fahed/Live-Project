# 日志工具

## 设计模式

外观模式（Facade）。封装 Loguru 配置细节，对外暴露统一的 `logger` 实例。

## 构件

| 文件 | 职责 |
|------|------|
| `logger.py` | 配置 Loguru 输出格式，导出全局 `logger` 实例 |

## 接口

```python
from app.utils.logger.logger import logger

logger.info("消息", extra={"module": "vote", "stream_id": "room-1"})
logger.error("错误", extra={"module": "ws"})
logger.warning("警告")
```

## 输出格式

```
2026-03-24 23:06:40.778 | INFO    | module:function:line | 消息
```

## 使用方式

业务代码直接导入 `logger`，不感知 Loguru 配置。推荐通过 `extra` 参数传递模块名和上下文。
