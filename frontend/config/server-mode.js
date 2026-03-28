/**
 * ????????
 * ???????????????????????????
 *
 * HBuilderX / uni-app ???????
 * 1. ?????????????? -> ????????? localhost:8080
 * 2. ?? uni-app script `mp-weixin-device` -> ???????????
 * 3. ?? uni-app script `mp-weixin-ip-debug` -> ???? IP ????
 * 4. ?? uni-app script `mp-weixin-ip-release` -> ???? IP ????
 */

// ==================== ???????? ====================

// ?? Docker / ???????????????????????
export const LOCAL_SERVER_URL = 'http://localhost:8080';

// ??????????????????????????
export const REAL_DEVICE_SERVER_URL = 'http://192.168.137.1:8080';

// ?? IP ?? / ???????????????? HTTP ??
export const PUBLIC_IP_SERVER_URL = 'http://106.14.254.19:8080';

// ????????????
export const MIDDLEWARE_SERVER_URL = PUBLIC_IP_SERVER_URL;
export const REAL_SERVER_URL = PUBLIC_IP_SERVER_URL;

// ??????????????? mock?????????
export const USE_MOCK_SERVER = false;

const REAL_WECHAT_CONFIG = {
  appid: 'wx655ac081a77374a7',
  secret: 'c0933eeb17faa6b8b3e74d2c9a405d3a'
};

const SERVER_PROFILES = {
  local: {
    key: 'local',
    label: '?????',
    url: LOCAL_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  device: {
    key: 'device',
    label: '???????',
    url: REAL_DEVICE_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  ipDebug: {
    key: 'ipDebug',
    label: '?? IP ??',
    url: PUBLIC_IP_SERVER_URL,
    wechat: { useMock: false, ...REAL_WECHAT_CONFIG }
  },
  ipRelease: {
    key: 'ipRelease',
    label: '?? IP ??',
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
  console.log('============================');
  console.log('LIVE Frontend Runtime Config');
  console.log('============================');
  console.log('Mode:', config.mode);
  console.log('Label:', config.label);
  console.log('URL:', config.url);
  console.log('WeChat AppID:', config.wechat.appid);
  console.log('============================');
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
