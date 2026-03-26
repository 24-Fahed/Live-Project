import uuid
from datetime import datetime, timedelta, timezone


class MockRepository:
    """直播子系统 Mock 数据仓库，原型阶段使用内存存储。

    所有业务域的数据存储和 CRUD 操作集中在此文件中。
    未来替换为 MySQL 实现时，只需创建 MysqlRepository 实现相同接口，
    并修改 repository/__init__.py 的导入即可。
    """

    def __init__(self):
        # ---- 流管理 ----
        self._streams: list[dict] = [
            {
                "id": "stream-001",
                "name": "辩论直播场A",
                "url": "http://example.com/live/stream-a.m3u8",
                "type": "hls",
                "description": "第一场辩论直播",
                "enabled": True,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": "stream-002",
                "name": "辩论直播场B",
                "url": "http://example.com/live/stream-b.m3u8",
                "type": "hls",
                "description": "第二场辩论直播",
                "enabled": True,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
        ]

        # ---- 直播状态 ----
        self._live_statuses: dict[str, dict] = {}

        # ---- 辩题管理 ----
        self._debates: dict[str, dict] = {
            "debate-001": {
                "id": "debate-001",
                "title": "如果有一个能一键消除痛苦的按钮，你会按吗？",
                "description": "关于痛苦、成长与人性选择的深度辩论",
                "leftSide": "会按",
                "rightSide": "不会按",
                "isActive": True,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
            "debate-002": {
                "id": "debate-002",
                "title": "人工智能是否应该拥有创作版权？",
                "description": "科技发展与知识产权保护的辩论",
                "leftSide": "应该拥有",
                "rightSide": "不应该拥有",
                "isActive": True,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
        }
        self._stream_debate_map: dict[str, str] = {
            "stream-001": "debate-001",
            "stream-002": "debate-002",
        }

        # ---- 投票 ----
        self._votes: dict[str, dict] = {
            "default": {"leftVotes": 0, "rightVotes": 0},
        }
        self._vote_backups: list[dict] = []
        self._vote_snapshots: dict[str, list[dict]] = {}

        # ---- 评委 ----
        self._judges: dict[str, list[dict]] = {}

        # ---- 辩论流程 ----
        self._debate_flows: dict[str, dict] = {}
        self._debate_flow_states: dict[str, dict] = {}

        # ---- AI 内容 ----
        self._ai_contents: dict[str, list[dict]] = {}

        # ---- AI 状态 ----
        self._ai_statuses: dict[str, dict] = {}

        # ---- 用户 ----
        self._users: list[dict] = [
            {
                "userId": "user-001",
                "nickname": "辩论爱好者",
                "avatar": "",
                "joinTime": "2024-01-15T10:30:00+00:00",
            },
            {
                "userId": "user-002",
                "nickname": "理性思考者",
                "avatar": "",
                "joinTime": "2024-02-20T14:00:00+00:00",
            },
            {
                "userId": "user-003",
                "nickname": "旁观者小明",
                "avatar": "",
                "joinTime": "2024-03-10T08:45:00+00:00",
            },
        ]

    # ========== 流管理 ==========

    def list_streams(self) -> list[dict]:
        return self._streams

    def get_stream(self, stream_id: str) -> dict | None:
        for s in self._streams:
            if s["id"] == stream_id:
                return s
        return None

    def create_stream(self, name: str, url: str, type_: str, description: str) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        stream = {
            "id": str(uuid.uuid4()),
            "name": name,
            "url": url,
            "type": type_,
            "description": description,
            "enabled": True,
            "createdAt": now,
            "updatedAt": now,
        }
        self._streams.append(stream)
        return stream

    def update_stream(self, stream_id: str, **kwargs) -> dict | None:
        stream = self.get_stream(stream_id)
        if not stream:
            return None
        for k, v in kwargs.items():
            if v is not None and k in stream:
                stream[k] = v
        stream["updatedAt"] = datetime.now(timezone.utc).isoformat()
        return stream

    def delete_stream(self, stream_id: str) -> dict | None:
        stream = self.get_stream(stream_id)
        if not stream:
            return None
        self._streams.remove(stream)
        return stream

    # ========== 直播状态 ==========

    def get_live_status(self, stream_id: str) -> dict:
        return self._live_statuses.get(stream_id, {
            "isLive": False,
            "streamId": stream_id,
            "liveId": None,
            "startTime": None,
            "streamUrl": None,
        })

    def start_live(self, stream_id: str) -> dict:
        stream = self.get_stream(stream_id)
        status = {
            "isLive": True,
            "streamId": stream_id,
            "liveId": str(uuid.uuid4()),
            "startTime": datetime.now(timezone.utc).isoformat(),
            "streamUrl": stream["url"] if stream else "",
        }
        self._live_statuses[stream_id] = status
        return status

    def stop_live(self, stream_id: str) -> dict:
        prev = self._live_statuses.get(stream_id, {})
        status = {
            "isLive": False,
            "streamId": stream_id,
            "liveId": None,
            "startTime": None,
            "streamUrl": None,
            "stoppedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._live_statuses[stream_id] = status
        return {**prev, "stoppedAt": status["stoppedAt"]}

    # ========== 投票 ==========

    def _record_vote_snapshot(self, stream_id: str, left: int, right: int, active_users: int = 0):
        """记录一次投票变更快照，用于统计图表。"""
        if stream_id not in self._vote_snapshots:
            self._vote_snapshots[stream_id] = []
        self._vote_snapshots[stream_id].append({
            "time": datetime.now(timezone.utc).isoformat(),
            "leftVotes": left,
            "rightVotes": right,
            "total": left + right,
            "activeUsers": active_users,
        })

    def get_votes(self, stream_id: str = "default") -> dict:
        if stream_id not in self._votes:
            self._votes[stream_id] = {"leftVotes": 0, "rightVotes": 0}
        return self._votes[stream_id]

    def set_votes(self, stream_id: str, left: int, right: int, active_users: int = 0) -> dict:
        self._votes[stream_id] = {"leftVotes": left, "rightVotes": right}
        self._record_vote_snapshot(stream_id, left, right, active_users)
        return self._votes[stream_id]

    def add_votes(self, stream_id: str, left_delta: int, right_delta: int, active_users: int = 0) -> dict:
        current = self.get_votes(stream_id)
        current["leftVotes"] += left_delta
        current["rightVotes"] += right_delta
        self._record_vote_snapshot(stream_id, current["leftVotes"], current["rightVotes"], active_users)
        return current

    def reset_votes(self, stream_id: str, reset_to: dict | None = None, save_backup: bool = True, active_users: int = 0) -> dict:
        left = reset_to.get("leftVotes", 0) if reset_to else 0
        right = reset_to.get("rightVotes", 0) if reset_to else 0
        if save_backup:
            current = self.get_votes(stream_id)
            self._vote_backups.append({
                "streamId": stream_id,
                "leftVotes": current["leftVotes"],
                "rightVotes": current["rightVotes"],
                "resetTo": {"leftVotes": left, "rightVotes": right},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        self._votes[stream_id] = {"leftVotes": left, "rightVotes": right}
        self._record_vote_snapshot(stream_id, left, right, active_users)
        return self._votes[stream_id]

    def get_vote_snapshots(self, stream_id: str, since: datetime | None = None) -> list[dict]:
        """获取指定流的投票快照，可按时间过滤。"""
        snapshots = list(self._vote_snapshots.get(stream_id, []))
        if since:
            snapshots = [s for s in snapshots if datetime.fromisoformat(s["time"]) >= since]
        return snapshots

    def list_vote_backups(self) -> list[dict]:
        return list(reversed(self._vote_backups))

    # ========== 辩题管理 ==========

    def get_debate(self, stream_id: str) -> dict | None:
        debate_id = self._stream_debate_map.get(stream_id)
        if debate_id:
            return self._debates.get(debate_id)
        return None

    def get_debate_by_id(self, debate_id: str) -> dict | None:
        return self._debates.get(debate_id)

    def create_debate(self, title: str, description: str, left: str, right: str, is_active: bool) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        debate_id = str(uuid.uuid4())
        debate = {
            "id": debate_id,
            "title": title,
            "description": description,
            "leftSide": left,
            "rightSide": right,
            "isActive": is_active,
            "createdAt": now,
            "updatedAt": now,
        }
        self._debates[debate_id] = debate
        return debate

    def update_debate(self, debate_id: str, **kwargs) -> dict | None:
        debate = self._debates.get(debate_id)
        if not debate:
            return None
        # 字段映射：前端 leftPosition/rightPosition → 存储 leftSide/rightSide
        if "leftPosition" in kwargs and kwargs["leftPosition"] is not None:
            kwargs["leftSide"] = kwargs.pop("leftPosition")
        if "rightPosition" in kwargs and kwargs["rightPosition"] is not None:
            kwargs["rightSide"] = kwargs.pop("rightPosition")
        for k, v in kwargs.items():
            if v is not None and k in debate:
                debate[k] = v
        debate["updatedAt"] = datetime.now(timezone.utc).isoformat()
        return debate

    def associate_debate(self, stream_id: str, debate_id: str) -> bool:
        if debate_id not in self._debates:
            return False
        self._stream_debate_map[stream_id] = debate_id
        return True

    def remove_debate(self, stream_id: str) -> bool:
        return self._stream_debate_map.pop(stream_id, None) is not None

    # ========== 用户 ==========

    def list_users(self) -> list[dict]:
        return [
            {"id": u["userId"], "userId": u["userId"], "nickname": u["nickname"], "avatarUrl": u["avatar"], "joinTime": u["joinTime"]}
            for u in self._users
        ]

    def get_user(self, user_id: str) -> dict | None:
        for u in self._users:
            if u["userId"] == user_id:
                return u
        return None

    # ========== 评委 ==========

    def get_judges(self, stream_id: str) -> list[dict]:
        if stream_id not in self._judges:
            self._judges[stream_id] = [
                {"id": "judge-1", "name": "评委一", "role": "主评委", "avatar": "./assets/images/judges/osmanthus.jpg", "votes": 0},
                {"id": "judge-2", "name": "评委二", "role": "嘉宾评委", "avatar": "./assets/images/judges/osmanthus.jpg", "votes": 0},
                {"id": "judge-3", "name": "评委三", "role": "嘉宾评委", "avatar": "./assets/images/judges/osmanthus.jpg", "votes": 0},
            ]
        return self._judges[stream_id]

    def set_judges(self, stream_id: str, judges: list[dict]) -> list[dict]:
        self._judges[stream_id] = judges
        return judges

    # ========== 辩论流程 ==========

    _DEFAULT_SEGMENTS = [
        {"name": "正方发言", "duration": 180, "side": "left"},
        {"name": "反方质问", "duration": 120, "side": "right"},
        {"name": "反方发言", "duration": 180, "side": "right"},
        {"name": "正方质问", "duration": 120, "side": "left"},
        {"name": "自由辩论", "duration": 300, "side": "both"},
        {"name": "正方总结", "duration": 120, "side": "left"},
        {"name": "反方总结", "duration": 120, "side": "right"},
    ]

    def get_debate_flow(self, stream_id: str) -> dict:
        if stream_id not in self._debate_flows:
            self._debate_flows[stream_id] = {"segments": [s.copy() for s in self._DEFAULT_SEGMENTS]}
        return self._debate_flows[stream_id]

    def set_debate_flow(self, stream_id: str, segments: list[dict]) -> list[dict]:
        self._debate_flows[stream_id] = {"segments": segments}
        return segments

    def get_debate_flow_state(self, stream_id: str) -> dict:
        return self._debate_flow_states.get(stream_id, {
            "status": "idle",
            "currentSegmentIndex": 0,
            "remainingSeconds": 0,
        })

    def update_debate_flow_state(self, stream_id: str, **kwargs) -> dict:
        state = self.get_debate_flow_state(stream_id)
        state.update(kwargs)
        self._debate_flow_states[stream_id] = state
        return state

    # ========== AI 内容 ==========

    def _ensure_ai_stream(self, stream_id: str):
        if stream_id not in self._ai_contents:
            self._ai_contents[stream_id] = []

    def list_ai_contents(self, stream_id: str) -> list[dict]:
        self._ensure_ai_stream(stream_id)
        return self._ai_contents[stream_id]

    def list_ai_contents_admin(self, page: int = 1, page_size: int = 20, stream_id: str | None = None) -> dict:
        all_items: list[dict] = []
        if stream_id:
            all_items = list(self._ai_contents.get(stream_id, []))
        else:
            for items in self._ai_contents.values():
                all_items.extend(items)
        all_items.sort(key=lambda x: x["timestamp"], reverse=True)
        total = len(all_items)
        start = (page - 1) * page_size
        return {"total": total, "page": page, "pageSize": page_size, "items": all_items[start:start + page_size]}

    def get_ai_content(self, content_id: str) -> dict | None:
        for items in self._ai_contents.values():
            for item in items:
                if item["id"] == content_id:
                    return item
        return None

    def create_ai_content(self, stream_id: str, content: str, side: str, confidence: float) -> dict:
        self._ensure_ai_stream(stream_id)
        item = {
            "id": str(uuid.uuid4()),
            "streamId": stream_id,
            "content": content,
            "side": side,
            "position": side,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "comments": [],
            "statistics": {"views": 0, "likes": 0, "comments": 0},
        }
        self._ai_contents[stream_id].append(item)
        return item

    def delete_ai_content(self, content_id: str) -> dict | None:
        for stream_id, items in self._ai_contents.items():
            for i, item in enumerate(items):
                if item["id"] == content_id:
                    items.pop(i)
                    return item
        return None

    def list_ai_comments(self, content_id: str) -> list[dict]:
        item = self.get_ai_content(content_id)
        if not item:
            return []
        return item.get("comments", [])

    def delete_ai_comment(self, content_id: str, comment_id: str) -> dict | None:
        item = self.get_ai_content(content_id)
        if not item:
            return None
        comments = item.get("comments", [])
        for i, comment in enumerate(comments):
            if comment["id"] == comment_id:
                comments.pop(i)
                # 更新评论计数
                stats = item.get("statistics", {})
                stats["comments"] = max(0, stats.get("comments", 0) - 1)
                return comment
        return None

    def add_ai_comment(self, content_id: str, text: str, user: str, avatar: str) -> dict | None:
        """添加评论到 AI 内容。"""
        item = self.get_ai_content(content_id)
        if not item:
            return None
        if "comments" not in item:
            item["comments"] = []
        comment = {
            "id": str(uuid.uuid4()),
            "text": text,
            "user": user,
            "avatar": avatar,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "likes": 0,
        }
        item["comments"].append(comment)
        # 更新评论计数
        stats = item.get("statistics", {})
        stats["comments"] = stats.get("comments", 0) + 1
        return comment

    def add_ai_like(self, content_id: str, comment_id: str | None = None) -> dict | None:
        """点赞 AI 内容或评论。"""
        item = self.get_ai_content(content_id)
        if not item:
            return None

        # 更新点赞计数
        stats = item.get("statistics", {})
        if comment_id:
            # 点赞评论
            comments = item.get("comments", [])
            for comment in comments:
                if comment["id"] == comment_id:
                    comment["likes"] = comment.get("likes", 0) + 1
                    return comment
            return None
        else:
            # 点赞内容
            stats["likes"] = stats.get("likes", 0) + 1
            return item

    # ========== AI 状态 ==========

    def get_ai_status(self, stream_id: str) -> dict:
        return self._ai_statuses.get(stream_id, {
            "status": "stopped",
            "streamId": stream_id,
        })

    def set_ai_status(self, stream_id: str, status: str, **extra) -> dict:
        entry = {"status": status, "streamId": stream_id, **extra}
        self._ai_statuses[stream_id] = entry
        return entry

    # ========== 用户 ==========

    def get_or_create_user(self, user_id: str, nickname: str = "", avatar: str = "") -> dict:
        user = self.get_user(user_id)
        if user:
            # 更新昵称和头像（用户可能在微信修改了资料）
            if nickname:
                user["nickname"] = nickname
            if avatar:
                user["avatar"] = avatar
            return user
        now = datetime.now(timezone.utc).isoformat()
        user = {
            "userId": user_id,
            "nickname": nickname,
            "avatar": avatar,
            "joinTime": now,
        }
        self._users.append(user)
        return user
