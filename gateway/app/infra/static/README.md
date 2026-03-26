# 静态资源管理

## 设计模式：注册表模式（Registry）

将所有静态资源挂载集中在一个注册表中管理，新增挂载只改注册表，main.py 不感知变化。

## 接入方式

在 `config.py` 的 `_MOUNTS` 列表中添加一行：

```python
_MOUNTS: list[tuple[str, str, bool]] = [
    # (挂载路径, 目录, html模式)
    ("/admin", "admin", True),        # 后台管理页面
    ("/hls", "static/hls", False),    # 示例：HLS 资源
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| 挂载路径 | str | URL 前缀 |
| 目录 | str | 相对于网关根目录的文件夹路径 |
| html模式 | bool | `True` 访问路径自动返回 `index.html` |

## 行为

- 目录存在 → 挂载成功
- 目录不存在 → 跳过，不影响启动
- 重复路径 → FastAPI 抛出异常

## 当前挂载

| 路径 | 目录 | 说明 |
|------|------|------|
| `/admin` | `admin/` | 后台管理页面 |

## 依赖

`aiofiles` — FastAPI StaticFiles 的异步文件 IO 依赖。
