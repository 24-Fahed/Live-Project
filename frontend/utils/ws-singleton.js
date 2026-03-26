import apiService from './api-service.js';

/**
 * WebSocket 全局单例
 *
 * 管理唯一的 WebSocket 连接，多个页面通过 subscribe/unsubscribe 共享同一连接，
 * 页面切换时仅取消/重新订阅，底层连接不断开。
 *
 * @example
 * import wsSingleton from '@/utils/ws-singleton.js';
 *
 * // 订阅
 * const subId = wsSingleton.subscribe(
 *     (msg) => console.log(msg),
 *     {
 *         onOpen: () => console.log('已连接'),
 *         onClose: () => console.log('已断开'),
 *     }
 * );
 *
 * // 发送
 * wsSingleton.send({ type: 'register', clientType: 'miniprogram' });
 *
 * // 取消订阅
 * wsSingleton.unsubscribe(subId);
 *
 * // 彻底关闭（App 退出时）
 * await wsSingleton.disconnect();
 */
class WebSocketSingleton {
	constructor() {
		/** @type {UniApp.SocketTask|null} uni.connectSocket 返回的任务实例 */
		this.socketTask = null;

		/** @type {Map<number, {onMessage: Function, onOpen?: Function, onClose?: Function}>} 订阅者列表 */
		this._subscribers = new Map();

		/** @type {number} 下一个订阅 ID */
		this._nextId = 0;

		/** @type {boolean} 当前连接是否处于打开状态 */
		this.connected = false;

		/** @type {boolean} 是否为主动关闭（主动关闭时不触发重连） */
		this.intentionalClose = false;

		/** @type {number|null} 心跳定时器 */
		this.heartbeatTimer = null;

		/** @type {number|null} 重连定时器 */
		this.reconnectTimer = null;

		/** @type {number} 当前连续重连次数 */
		this.reconnectAttempts = 0;

		/** @type {number} 最大连续重连次数 */
		this.maxReconnectAttempts = 5;
	}

	/**
	 * 获取当前连接状态
	 * @returns {boolean} 是否已连接
	 */
	get isConnected() { return this.connected; }

	/**
	 * 订阅 WebSocket 消息
	 *
	 * 首次订阅时自动建立连接；若已连接，立即触发 onOpen 回调。
	 *
	 * @param {Function} onMessage - 收到消息时的回调，参数为解析后的 JSON 对象
	 * @param {Object} [callbacks] - 可选的生命周期回调
	 * @param {Function} [callbacks.onOpen] - 连接建立时的回调
	 * @param {Function} [callbacks.onClose] - 连接断开时的回调
	 * @returns {number} 订阅 ID，用于后续取消订阅
	 */
	subscribe(onMessage, { onOpen, onClose } = {}) {
		const id = ++this._nextId;
		this._subscribers.set(id, { onMessage, onOpen, onClose });
		console.log('[WS-Singleton] subscribe, id=' + id + ', subscribers=' + this._subscribers.size);
		if (!this.socketTask) {
			this._connect();
		} else if (this.connected && onOpen) {
			onOpen();
		}
		return id;
	}

	/**
	 * 取消订阅
	 *
	 * 触发订阅者的 onClose 回调，并从订阅者列表中移除。
	 * 不会关闭底层 WebSocket 连接（除非所有订阅者都已取消）。
	 *
	 * @param {number} id - subscribe() 返回的订阅 ID
	 */
	unsubscribe(id) {
		const sub = this._subscribers.get(id);
		if (sub) {
			console.log('[WS-Singleton] unsubscribe, id=' + id);
			if (sub.onClose) sub.onClose();
			this._subscribers.delete(id);
		}
	}

	/**
	 * 通过 WebSocket 发送消息
	 *
	 * 仅在连接已建立时发送。对象会自动序列化为 JSON 字符串。
	 *
	 * @param {Object|string} data - 要发送的数据，对象将自动 JSON.stringify
	 */
	send(data) {
		if (this.socketTask && this.connected) {
			this.socketTask.send({
				data: typeof data === 'string' ? data : JSON.stringify(data),
			});
		}
	}

	/**
	 * 彻底关闭 WebSocket 连接
	 *
	 * 停止心跳和重连，通知并清空所有订阅者，关闭底层连接。
	 * 仅用于 App 退出等全局场景，页面切换应使用 unsubscribe()。
	 *
	 * @returns {Promise<void>} 连接关闭完成后 resolve，最多等待 3 秒超时
	 */
	disconnect() {
		this.intentionalClose = true;
		this._stopHeartbeat();
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		this.reconnectAttempts = 0;

		// 通知所有订阅者关闭
		this._subscribers.forEach((sub) => {
			if (sub.onClose) sub.onClose();
		});
		this._subscribers.clear();

		if (this.socketTask) {
			const task = this.socketTask;
			this.socketTask = null;
			this.connected = false;
			return new Promise((resolve) => {
				const timer = setTimeout(resolve, 3000);
				task.close({
					success: () => { clearTimeout(timer); resolve(); },
					fail: () => { clearTimeout(timer); resolve(); }
				});
			});
		}
		this.connected = false;
		return Promise.resolve();
	}

	// ==================== 内部方法 ====================

	/**
	 * 建立 WebSocket 连接
	 * @private
	 */
	_connect() {
		this.intentionalClose = false;
		try {
			const wsUrl = apiService.getWebSocketUrl();
			console.log('[WS-Singleton] connecting to ' + wsUrl);

			this.socketTask = uni.connectSocket({
				url: wsUrl,
				success: () => console.log('[WS-Singleton] connect request sent'),
				fail: () => this._scheduleReconnect()
			});

			this.socketTask.onOpen(() => {
				console.log('[WS-Singleton] connected');
				this.connected = true;
				this.reconnectAttempts = 0;
				this._startHeartbeat();
				// 通知所有订阅者 onOpen
				this._subscribers.forEach((sub) => {
					if (sub.onOpen) sub.onOpen();
				});
			});

			this.socketTask.onMessage((event) => {
				try {
					const message = JSON.parse(event.data);
					// pong 由单例内部消费，不分发给订阅者
					if (message.type === 'pong') return;
					// 分发到所有订阅者
					this._subscribers.forEach((sub) => {
						if (sub.onMessage) sub.onMessage(message);
					});
				} catch (error) {
					console.error('[WS-Singleton] parse error:', error);
				}
			});

			this.socketTask.onClose(() => {
				console.log('[WS-Singleton] closed');
				this._stopHeartbeat();
				this.connected = false;
				this.socketTask = null;

				if (this.intentionalClose) return;
				this._scheduleReconnect();
				// 通知所有订阅者 onClose
				this._subscribers.forEach((sub) => {
					if (sub.onClose) sub.onClose();
				});
			});

			this.socketTask.onError(() => {
				console.log('[WS-Singleton] error');
				this._stopHeartbeat();
				this.connected = false;
				this.socketTask = null;

				if (this.intentionalClose) return;
				this._scheduleReconnect();
				// 通知所有订阅者 onClose
				this._subscribers.forEach((sub) => {
					if (sub.onClose) sub.onClose();
				});
			});
		} catch (error) {
			console.error('[WS-Singleton] connect error:', error);
			this._scheduleReconnect();
		}
	}

	/**
	 * 启动心跳定时器，每 30 秒发送一次 ping
	 * @private
	 */
	_startHeartbeat() {
		this._stopHeartbeat();
		this.heartbeatTimer = setInterval(() => {
			this.send({ type: 'ping' });
		}, 30000);
	}

	/**
	 * 停止心跳定时器
	 * @private
	 */
	_stopHeartbeat() {
		if (this.heartbeatTimer) {
			clearInterval(this.heartbeatTimer);
			this.heartbeatTimer = null;
		}
	}

	/**
	 * 安排一次自动重连（指数退避策略）
	 *
	 * 延迟序列：2s → 4s → 8s → 16s → 30s（封顶）
	 * 达到 maxReconnectAttempts（5 次）后停止重连。
	 *
	 * @private
	 */
	_scheduleReconnect() {
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			console.log('[WS-Singleton] max reconnect attempts reached (' + this.maxReconnectAttempts + ')');
			return;
		}
		this.reconnectAttempts++;
		const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
		console.log('[WS-Singleton] reconnecting in ' + delay + 'ms (attempt ' + this.reconnectAttempts + ')');
		this.reconnectTimer = setTimeout(() => {
			this.reconnectTimer = null;
			this._connect();
		}, delay);
	}
}

export default new WebSocketSingleton();
