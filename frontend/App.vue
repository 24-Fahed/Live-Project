<script>
	import wsSingleton from '@/utils/ws-singleton.js';

	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
			wsSingleton.disconnect();
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import "node_modules/vant-weapp/dist/common/index.wxss";
	/* 全局引入IconFont */
	@import "static/iconfont/iconfont.css";
	/* 引入uni-icons CSS */
	@import "node_modules/@dcloudio/uni-ui/lib/uni-icons/uniicons.css";
</style>
