/**
 * 前端运行模式配置
 * 只通过配置切换小程序连接地址，不改页面业务代码。
 */

// 本地模拟器
export const LOCAL_SERVER_URL = 'http://localhost:8080';

// 真机局域网调试
export const REAL_DEVICE_SERVER_URL = 'http://192.168.137.1:8080';

// 公网 IP 调试 / 上线
export const PUBLIC_IP_SERVER_URL = 'http://106.14.254.19:8080';

// 兼容旧代码
export const MIDDLEWARE_SERVER_URL = PUBLIC_IP_SERVER_URL;
export const REAL_SERVER_URL = PUBLIC_IP_SERVER_URL;
export const USE_MOCK_SERVER = false;

const REAL_WECHAT_CONFIG = {
  appid: 'wx655ac081a77374a7',
  secret: 'c0933eeb17faa6b8b3e74d2c9a405d3a'
};

const SERVER_PROFILES = {
  local: {
    key: 'local',
    label: '本地模拟器',
    url: LOCAL_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  device: {
    key: 'device',
    label: '真机局域网调试',
    url: REAL_DEVICE_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  ipDebug: {
    key: 'ipDebug',
    label: '公网 IP 调试',
    url: PUBLIC_IP_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  ipRelease: {
    key: 'ipRelease',
    label: '公网 IP 上线',
    url: PUBLIC_IP_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  }
};

const resolveProfileKey = () => {
  let key = 'local';

  // #ifdef MP-WEIXIN-DEVICE
  key = 'device';
  // #endif

  // #ifdef MP-WEIXIN-IP-DEBUG
  key = 'ipDebug';
  // #endif

  // #ifdef MP-WEIXIN-IP-RELEASE
  key = 'ipRelease';
  // #endif

  return key;
};

export const CURRENT_SERVER_PROFILE = SERVER_PROFILES[resolveProfileKey()];
export const CURRENT_RUNTIME_MODE = CURRENT_SERVER_PROFILE.key;
export const API_BASE_URL = CURRENT_SERVER_PROFILE.url;

export const getCurrentServerConfig = () => ({
  mode: CURRENT_SERVER_PROFILE.key,
  label: CURRENT_SERVER_PROFILE.label,
  url: CURRENT_SERVER_PROFILE.url,
  host: CURRENT_SERVER_PROFILE.url.replace(/^https?:\/\//, '').split(':')[0],
  port: CURRENT_SERVER_PROFILE.url.split(':').pop(),
  wechat: CURRENT_SERVER_PROFILE.wechat
});

export const printConfig = () => {
  const config = getCurrentServerConfig();
  console.log('LIVE Frontend Runtime Config');
  console.log('Mode:', config.mode);
  console.log('Label:', config.label);
  console.log('URL:', config.url);
};

export default {
  USE_MOCK_SERVER,
  LOCAL_SERVER_URL,
  REAL_DEVICE_SERVER_URL,
  PUBLIC_IP_SERVER_URL,
  MIDDLEWARE_SERVER_URL,
  REAL_SERVER_URL,
  API_BASE_URL,
  CURRENT_RUNTIME_MODE,
  CURRENT_SERVER_PROFILE,
  getCurrentServerConfig,
  printConfig
};
