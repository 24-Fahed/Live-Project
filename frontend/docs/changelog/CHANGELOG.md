# 前端修改日志

## 2026-03-17

### 1. 配置修改：前端API地址指向本地网关

**文件**: `config/server-mode.js`

**修改内容**:
```javascript
// 修改前
export const API_BASE_URL = REAL_SERVER_URL;

// 修改后
export const API_BASE_URL = LOCAL_SERVER_URL;
```

**修改原因**: 让小程序的API流量全部走本地网关(localhost:8080)，便于本地开发和Mock数据测试。

**修改人**: Claude Code

---

### 2. Bug修复：微信小程序刷新按钮无法点击

**文件**: `pages/live-select/live-select.vue`

**修改内容**:
```css
/* 修改前 */
.footer-section {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    padding: 20rpx;
    background: #FFEB3B;
    border-top: 6rpx solid #FF0000;
    display: flex;
    justify-content: center;
    /* 无 z-index */
}

/* 修改后 */
.footer-section {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    padding: 20rpx;
    background: #FFEB3B;
    border-top: 6rpx solid #FF0000;
    display: flex;
    justify-content: center;
    z-index: 100;
}
```

**修改原因**:
- `footer-section` 原来没有设置 `z-index`
- `live-list-section` (scroll-view) 设置了 `z-index: 10`
- 在微信小程序中，没有 `z-index` 的 fixed 元素可能被 scroll-view 遮挡
- 添加 `z-index: 100` 确保按钮层级高于 scroll-view，可正常点击

**修改人**: Claude Code

---

## 文件夹说明

`frontend/docs/changelog/` 用于存放前端代码修改的留档日志。
