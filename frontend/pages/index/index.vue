<template>
	<view class="container">
		<!-- 背景装饰 -->
		<view class="background-decoration">
			<view class="deco-shape deco-circle-1"></view>
			<view class="deco-shape deco-circle-2"></view>
			<view class="deco-shape deco-square-1"></view>
			<view class="deco-shape deco-triangle-1"></view>
		</view>

	<!-- 不规则装饰图标 -->
	<view class="irregular-icons">
		<image src="/static/home/guangbo-bangong.png" class="icon-1"></image>
		<image src="/static/home/kidaha-.png" class="icon-2"></image>
	</view>

	<!-- 主内容区域 -->
	<view class="content-wrapper">
		<!-- 顶部标题区 -->
		<view class="header-section">
			<view class="pop-title">
				<text class="title-main">辩论 LIVE</text>
				<text class="title-sub">思维竞技场</text>
			</view>
			<view class="pop-badge">I CAN I BB</view>
		</view>

			<!-- 中间内容区 -->
			<view class="middle-section">
				<view class="pop-window">
					<view class="window-header"></view>
					<view class="window-content">
					<!-- 左侧图标 -->
					<view class="character-area">
						<image src="/static/home/quweichahuaqueshengye.png" class="icon-image"></image>
					</view>

						<!-- 右侧文本区 -->
						<view class="text-area">
							<text class="main-text">思维碰撞</text>
							<text class="sub-text">观看精彩辩论</text>
						</view>
					</view>
				</view>
			</view>

			<!-- 登录按钮区 -->
			<view class="button-section">
				<view class="login-button" @click="handleLogin">
					<text class="button-text">一键闪电登录</text>
				</view>
			</view>

			<!-- 底部信息 -->
			<view class="footer-info">
				<text class="info-text">登录即同意参与思维竞技</text>
			</view>
		</view>

		<!-- Loading 遮罩 -->
		<view class="loading-overlay" v-if="isLoading">
			<view class="loading-container">
				<view class="loading-spinner"></view>
				<text class="loading-text">闪电登录中...</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { API_BASE_URL } from '@/config/server-mode.js'
	export default {
		data() {
			return {
				isLoading: false,
				userInfo: null,
				hasUserInfo: false
			}
		},
	onLoad() {
		// 页面加载完成，检查登录状态
		this.checkLoginStatus()
	},
	onUnload() {
		// 页面卸载
	},
	methods: {
		initLoadingLottie() {
			// 暂时空实现，避免报错
		    console.log('initLoadingLottie方法没有实现，这是一个占位函数')
		},
		
		async handleLogin() {
		try {
			console.log('开始登录流程')
			
			// 显示 Loading 动画
			this.isLoading = true
			
			// 初始化 Loading 动画
			this.$nextTick(() => {
				this.initLoadingLottie()
			})

			// 获取用户授权 → 执行微信登录
			const userInfoRes = await this.getUserProfile()
			await this.performWechatLogin(userInfoRes)
		} catch (error) {
			console.error('登录处理失败:', error)
			this.isLoading = false
			uni.showToast({
				title: error.message || '登录失败',
				icon: 'none',
				duration: 2000
			})
		}
	},
	
	// ⚡ 临时方案：跳过微信登录，直接进入
	async bypassWechatLogin() {
		try {
			console.log('⚡ 临时方案：跳过微信登录，直接进入小程序')
			
			// 生成临时用户信息
			const tempUserInfo = {
				nickName: '测试用户_' + Math.floor(Math.random() * 10000),
				avatarUrl: '/static/iconfont/blue-user.png'
			}
			
			console.log('生成临时用户信息:', tempUserInfo)
			
			// 保存到本地存储
			this.userInfo = tempUserInfo
			this.hasUserInfo = true
			uni.setStorageSync('userInfo', tempUserInfo)
			uni.setStorageSync('loginCode', 'temp_bypass_code')
			
			// 延迟后跳转到直播选择页
			setTimeout(() => {
				this.isLoading = false
				uni.redirectTo({
					url: '/pages/live-select/live-select'
				})
			}, 1500)
		} catch (error) {
			console.error('临时登录失败:', error)
			this.isLoading = false
			throw error
		}
	},
	
	// 检查登录状态
	checkLoginStatus() {
			// 检查本地存储的用户信息
			const userInfo = uni.getStorageSync('userInfo')
			if (userInfo) {
				this.userInfo = userInfo
				this.hasUserInfo = true
				console.log('已登录用户:', userInfo)
			}
		},
		
		// 执行微信登录
		async performWechatLogin(userInfoRes) {
			try {
				console.log('开始微信登录流程...')
				console.log('运行环境:', this.getPlatform())
				
				let serverRes
				let loginCode
				let currentUserInfo
				
				// 检测运行环境
				const platform = this.getPlatform()
				
			// #ifdef MP-WEIXIN
			// 微信小程序环境：使用完整的微信登录流程
			// 1. 静默登录获取 code
			const loginRes = await this.wxLogin()
			console.log('微信登录结果:', loginRes)
			
			// 📋 打印获取到的 Code
			console.log('%c═══════════════════════════════════════', 'color: #4CAF50; font-weight: bold; font-size: 14px;')
			console.log('%c 微信登录凭证 CODE 已获取 ', 'background: #4CAF50; color: white; font-weight: bold; padding: 5px 10px; border-radius: 3px;')
			console.log('%c═══════════════════════════════════════', 'color: #4CAF50; font-weight: bold; font-size: 14px;')
				console.log('%c Code:', 'color: #FF6B9D; font-weight: bold; font-size: 14px;', loginRes.code)
				console.log('%c 请立即复制此 Code 进行测试:', 'color: #FF0000; font-weight: bold; font-size: 16px;')
				console.log('%c', 'color: #FF0000; font-weight: bold; font-size: 14px;', loginRes.code)
			console.log('%c 完整 Code:', 'color: #2196F3; font-weight: bold; font-size: 12px;', loginRes.code)
			console.log('%c═══════════════════════════════════════', 'color: #4CAF50; font-weight: bold; font-size: 14px;')
			
			if (!loginRes.code) {
				throw new Error('获取微信登录 code 失败')
			}
			
			console.log('用户信息:', userInfoRes)
				
				// 2. 发送到服务器验证
				serverRes = await this.sendToServer({
					code: loginRes.code,
					userInfo: userInfoRes.userInfo,
					encryptedData: userInfoRes.encryptedData,
					iv: userInfoRes.iv
				})
				
				// 3. 保存登录信息
				loginCode = loginRes.code
				currentUserInfo = userInfoRes.userInfo
				
				console.log('登录成功:', userInfoRes.userInfo)
				
				// #endif
			
			// 保存用户信息到本地（仅微信小程序环境）
			// #ifdef MP-WEIXIN
			this.userInfo = currentUserInfo
			this.hasUserInfo = true
			uni.setStorageSync('userInfo', currentUserInfo)
			uni.setStorageSync('loginCode', loginCode)
			
			// 保存 token 和用户信息
			if (serverRes?.data?.token) {
				uni.setStorageSync('authToken', serverRes.data.token);
			}
			if (serverRes?.data?.userId) {
				uni.setStorageSync('userId', serverRes.data.userId);
			}
			if (serverRes?.data?.user) {
				uni.setStorageSync('currentUser', serverRes.data.user);
			}
			
			console.log('登录成功，用户信息已保存')
			console.log('TODO: 添加JWT验证在网关中')
			console.log('✅ Token:', serverRes?.data?.token ? '已保存' : '未找到')
			
			// 5. 跳转到直播选择页
			setTimeout(() => {
				this.isLoading = false
				uni.redirectTo({
					url: '/pages/live-select/live-select'
				})
			}, 1000)
			// #endif
			
			// #ifndef MP-WEIXIN
			// H5或其他环境：无法获取真实微信 code，提示用户
			console.error('⚠️  当前不在微信小程序环境，无法获取真实的微信登录 code')
			
			this.isLoading = false
			uni.showToast({
				title: '微信登录功能仅在微信小程序环境中可用，请在微信小程序中打开此应用',
				icon: 'none',
				duration: 3000
			})
			// #endif
				
			} catch (error) {
				console.error('微信登录失败:', error)
				this.isLoading = false
				
				// 显示错误提示
				uni.showToast({
					title: error.message || '登录失败，请重试',
					icon: 'none',
					duration: 2000
				})
			}
		},
		
		// 获取运行平台
		getPlatform() {
			// #ifdef MP-WEIXIN
			return 'mp-weixin'
			// #endif
			
			// #ifdef H5
			return 'h5'
			// #endif
			
			// #ifdef APP-PLUS
			return 'app'
			// #endif
			
			return 'unknown'
		},
		
		// 微信静默登录
		wxLogin() {
			return new Promise((resolve, reject) => {
				uni.login({
					provider: 'weixin',
					success: (res) => {
						console.log('微信登录成功:', res)
						resolve(res)
					},
					fail: (err) => {
						console.error('微信登录失败:', err)
						reject(new Error('微信登录失败'))
					}
				})
			})
		},
		
		// 获取用户信息（需要用户授权）
		getUserProfile() {
			return new Promise((resolve, reject) => {
				// #ifdef MP-WEIXIN
				// 微信小程序环境：调用真实的授权接口
				uni.getUserProfile({
					desc: '用于完善个人辩论档案',
					success: (res) => {
						console.log('获取用户信息成功:', res)
						resolve(res)
					},
					fail: (err) => {
						console.error('获取用户信息失败:', err)
						// 如果用户拒绝授权，使用默认信息
						if (err.errMsg.includes('deny')) {
							resolve({
								userInfo: {
									nickName: '微信用户',
									avatarUrl: '/static/logo.png'
								},
								encryptedData: '',
								iv: ''
							})
						} else {
							reject(new Error('获取用户信息失败'))
						}
					}
				})
				// #endif
				
				// #ifndef MP-WEIXIN
				// H5或其他环境：直接返回默认信息（不需要授权）
				console.log('当前不在微信小程序环境，使用默认用户信息')
				resolve({
					userInfo: {
						nickName: '用户' + Math.floor(Math.random() * 1000),
						avatarUrl: '/static/logo.png'
					},
					encryptedData: '',
					iv: ''
				})
				// #endif
			})
		},
		
		// 发送登录信息到服务器
		async sendToServer(loginData) {
			try {
				console.log('发送登录数据到服务器')
				console.log('Code (前15位):', loginData.code?.substring(0, 15) + '...')
				console.log('UserInfo:', loginData.userInfo?.nickName)
				
			// 使用配置的API地址（强制使用本地服务器）
			const apiBaseURL = API_BASE_URL || 'http://192.168.31.249:8081';
			
			// 调试日志：显示使用的服务器地址
			console.log('📡 API_BASE_URL 值:', API_BASE_URL);
			console.log('📡 实际使用的服务器地址:', apiBaseURL);
			console.log('📡 完整请求URL:', `${apiBaseURL}/api/wechat-login`);
				
				const response = await uni.request({
					url: `${apiBaseURL}/api/wechat-login`,
					method: 'POST',
					data: loginData,
					header: {
						'Content-Type': 'application/json'
					},
					timeout: 30000 // 增加超时时间到 30 秒，因为需要代理到后端服务器
				})
				
				console.log('服务器响应状态:', response.statusCode)
				console.log('服务器响应数据:', response.data)
				
				if (response.statusCode === 200 && response.data && response.data.success) {
					// 保存 token 到本地存储
					const token = response.data.data?.token;
					if (token) {
						uni.setStorageSync('authToken', token);
						console.log('✅ Token 已保存到本地存储');
					}
					return response.data
				} else {
					// 提取错误信息
					const errorMsg = response.data?.message || '服务器验证失败'
					throw new Error(errorMsg)
				}
				
			} catch (error) {
				console.error('服务器验证失败:', error)
				
				// 如果是网络错误，提供备用方案
				if (error.errMsg && error.errMsg.includes('timeout')) {
					throw new Error('网络超时，请检查网络连接')
				} else if (error.errMsg && error.errMsg.includes('fail')) {
					throw new Error('网络连接失败，请检查网络设置')
				} else {
					throw new Error(error.message || '服务器验证失败')
				}
			}
		},
		
		// 退出登录
		logout() {
			uni.showModal({
				title: '确认退出',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 清除本地存储
						uni.removeStorageSync('userInfo')
						uni.removeStorageSync('loginCode')
						
						// 重置状态
						this.userInfo = null
						this.hasUserInfo = false
						
						uni.showToast({
							title: '已退出登录',
							icon: 'success'
						})
					}
				}
			})
		},
		
		}
	}
</script>

<style>
	.container {
		height: 100vh;
		background: #FFEB3B;
		padding: 0;
		position: relative;
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		overflow: hidden;
	}

	/* 背景装饰 */
	.background-decoration {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		left: 0;
		z-index: 1;
		pointer-events: none;
	}

	.deco-shape {
		position: absolute;
		opacity: 0.12;
		border: 8rpx solid;
	}

	.deco-circle-1 {
		width: 300rpx;
		height: 300rpx;
		border-radius: 50%;
		top: -100rpx;
		left: -100rpx;
		border-color: #FF0000;
		animation: floatDecoration 8s ease-in-out infinite;
	}

	.deco-circle-2 {
		width: 250rpx;
		height: 250rpx;
		border-radius: 50%;
		bottom: -80rpx;
		right: -80rpx;
		border-color: #0066FF;
		animation: floatDecoration 10s ease-in-out infinite reverse;
	}

	.deco-square-1 {
		width: 200rpx;
		height: 200rpx;
		top: 50%;
		right: 10%;
		border-color: #FFEB3B;
		animation: rotateDecoration 15s linear infinite;
	}

	.deco-triangle-1 {
		width: 0;
		height: 0;
		border-left: 100rpx solid transparent;
		border-right: 100rpx solid transparent;
		border-bottom: 173rpx solid #FF0000;
		top: 20%;
		left: 5%;
		opacity: 0.08;
		animation: floatDecoration 12s ease-in-out infinite;
	}

	@keyframes floatDecoration {
		0%, 100% { transform: translateY(0) rotate(0deg); }
		50% { transform: translateY(-20rpx) rotate(180deg); }
	}

	@keyframes rotateDecoration {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	/* 内容包装 */
	.content-wrapper {
		position: relative;
		z-index: 10;
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40rpx 20rpx;
		gap: 40rpx;
	}

	/* 顶部标题区 */
	.header-section {
		position: relative;
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20rpx;
	}

	.pop-title {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8rpx;
		background: #FFFFFF;
		padding: 30rpx 50rpx;
		border-radius: 20rpx;
		border: 8rpx solid #FF0000;
		box-shadow: 12rpx 12rpx 0 #0066FF, -4rpx -4rpx 0 #FF0000;
	}

	.title-main {
		font-size: 80rpx;
		font-weight: 900;
		color: #FF0000;
		letter-spacing: 4rpx;
		text-shadow: none;
	}

	.title-sub {
		font-size: 32rpx;
		font-weight: 700;
		color: #0066FF;
		letter-spacing: 2rpx;
		text-shadow: none;
	}

	.pop-badge {
		font-size: 28rpx;
		font-weight: 900;
		color: #FFFFFF;
		background: #FF0000;
		padding: 12rpx 30rpx;
		border-radius: 40rpx;
		border: 4rpx solid #0066FF;
		box-shadow: 6rpx 6rpx 0 #FFEB3B;
		letter-spacing: 2rpx;
	}

	/* 中间内容区 */
	.middle-section {
		width: 100%;
		max-width: 600rpx;
		display: flex;
		justify-content: center;
	}

	.pop-window {
		width: 100%;
		background: #FFFFFF;
		border: 8rpx solid #0066FF;
		border-radius: 20rpx;
		overflow: hidden;
		box-shadow: 16rpx 16rpx 0 #FF0000, -6rpx -6rpx 0 #FFEB3B;
	}

	.window-header {
		height: 40rpx;
		background: #0066FF;
		display: flex;
		align-items: center;
		padding: 0 20rpx;
		gap: 12rpx;
	}

	.window-header::before {
		content: '';
		width: 20rpx;
		height: 20rpx;
		background: #FFFFFF;
		border-radius: 50%;
		box-shadow: 30rpx 0 0 #FFFFFF, 60rpx 0 0 #FFFFFF;
	}

	.window-content {
		padding: 40rpx;
		display: flex;
		align-items: center;
		gap: 30rpx;
		min-height: 280rpx;
	}

	.character-area {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.icon-image {
		width: 140rpx;
		height: 140rpx;
		animation: iconBounce 3s ease-in-out infinite;
	}

	@keyframes iconBounce {
		0%, 100% { transform: scale(1) rotate(0deg); }
		25% { transform: scale(1.1) rotate(-5deg); }
		50% { transform: scale(1) rotate(0deg); }
		75% { transform: scale(1.05) rotate(5deg); }
	}

	.text-area {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 16rpx;
	}

	.main-text {
		font-size: 48rpx;
		font-weight: 900;
		color: #FF0000;
		letter-spacing: 3rpx;
		text-shadow: none;
	}

	.sub-text {
		font-size: 36rpx;
		font-weight: 800;
		color: #0066FF;
		letter-spacing: 2rpx;
		text-shadow: none;
	}

	/* 按钮区 */
	.button-section {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	.login-button {
		background: #FF0000;
		border: 6rpx solid #0066FF;
		border-radius: 50rpx;
		padding: 24rpx 60rpx;
		font-size: 36rpx;
		font-weight: 900;
		transition: all 0.3s ease;
		box-shadow: 10rpx 10rpx 0 #FFEB3B;
		cursor: pointer;
	}

	.login-button:active {
		transform: scale(0.95);
		box-shadow: 4rpx 4rpx 0 #FFEB3B;
	}

	.button-text {
		color: #FFFFFF;
		font-weight: 900;
		text-shadow: none;
		letter-spacing: 2rpx;
	}

	/* 底部信息 */
	.footer-info {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 20rpx;
	}

	.info-text {
		font-size: 24rpx;
		color: #000;
		font-weight: 700;
		background: #FFFFFF;
		padding: 12rpx 30rpx;
		border-radius: 40rpx;
		border: 3rpx solid #FF0000;
		text-shadow: none;
	}

	.info-buttons {
		display: flex;
		gap: 20rpx;
		flex-wrap: wrap;
		justify-content: center;
	}

	.info-btn {
		padding: 16rpx 40rpx;
		border-radius: 40rpx;
		border: 4rpx solid;
		font-size: 24rpx;
		font-weight: 800;
		transition: all 0.3s ease;
		cursor: pointer;
	}

	.btn-primary {
		background: #0066FF;
		border-color: #FF0000;
		color: #FFFFFF;
		box-shadow: 6rpx 6rpx 0 #FFEB3B;
	}

	.btn-primary:active {
		transform: scale(0.95);
		box-shadow: 2rpx 2rpx 0 #FFEB3B;
	}

	.btn-secondary {
		background: #FFEB3B;
		border-color: #FF0000;
		color: #000;
		box-shadow: 6rpx 6rpx 0 #0066FF;
	}

	.btn-secondary:active {
		transform: scale(0.95);
		box-shadow: 2rpx 2rpx 0 #0066FF;
	}

	/* Loading 遮罩 */
	.loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(255, 255, 255, 0.95);
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
		backdrop-filter: blur(4rpx);
	}

	.loading-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 30rpx;
	}

	.loading-spinner {
		width: 100rpx;
		height: 100rpx;
		border: 8rpx solid #FFEB3B;
		border-top: 8rpx solid #FF0000;
		border-right: 8rpx solid #0066FF;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}

	.loading-text {
		font-size: 32rpx;
		font-weight: 800;
		color: #FF0000;
		letter-spacing: 2rpx;
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.7; }
		50% { opacity: 1; }
	}

	/* 不规则装饰图标 */
	.irregular-icons {
		position: absolute;
		width: 100%;
		height: 100%;
		z-index: 20;
		pointer-events: none;
	}

	.icon-1 {
		position: absolute;
		width: 200rpx;
		height: 200rpx;
		top: 10%;
		left: 5%;
		opacity: 0.85;
		transform: rotate(-25deg) scaleX(-1);
		filter: drop-shadow(0 4rpx 8rpx rgba(255, 0, 0, 0.3));
		animation: floatIcon1 4s ease-in-out infinite;
	}

	.icon-2 {
		position: absolute;
		width: 220rpx;
		height: 220rpx;
		bottom: 15%;
		right: 2%;
		opacity: 0.8;
		transform: rotate(35deg) scaleY(-1);
		filter: drop-shadow(0 6rpx 12rpx rgba(0, 102, 255, 0.3));
		animation: floatIcon2 5s ease-in-out infinite;
	}

	.icon-3 {
		position: absolute;
		width: 100rpx;
		height: 100rpx;
		top: 55%;
		right: 12%;
		opacity: 0.6;
		transform: rotate(45deg);
		filter: drop-shadow(0 4rpx 10rpx rgba(255, 235, 59, 0.4));
		animation: floatIcon3 3.5s ease-in-out infinite;
	}

	@keyframes floatIcon1 {
		0%, 100% { transform: rotate(-25deg) scaleX(-1) translateY(0) translateX(0); }
		25% { transform: rotate(-25deg) scaleX(-1) translateY(-10rpx) translateX(8rpx); }
		50% { transform: rotate(-25deg) scaleX(-1) translateY(15rpx) translateX(-5rpx); }
		75% { transform: rotate(-25deg) scaleX(-1) translateY(-8rpx) translateX(-10rpx); }
	}

	@keyframes floatIcon2 {
		0%, 100% { transform: rotate(35deg) scaleY(-1) translateY(0) translateX(0); }
		33% { transform: rotate(35deg) scaleY(-1) translateY(12rpx) translateX(-8rpx); }
		66% { transform: rotate(35deg) scaleY(-1) translateY(-15rpx) translateX(10rpx); }
	}

	@keyframes floatIcon3 {
		0%, 100% { transform: rotate(45deg) translateY(0); }
		50% { transform: rotate(45deg) translateY(-20rpx); }
	}
</style>
