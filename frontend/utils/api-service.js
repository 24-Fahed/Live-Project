/**
 * 统一API服务层
 * 封装所有后端接口调用，支持环境切换和错误处理
 * 
 * 💡 快速切换提示：
 * 要在模拟服务器和真实服务器之间切换，请修改 config/server-mode.js 文件中的 USE_MOCK_SERVER 配置
 */

import apiInterceptor from './api-interceptor.js';
import { API_BASE_URL } from '@/config/server-mode.js';

// 从配置文件获取当前服务器地址
// 注意：这里使用固定地址，因为 uni-app 可能不支持动态 require
// 如需切换，请修改 config/server-mode.js 后重新编译
const currentUrl = API_BASE_URL;

// 内联配置，避免导入问题
const API_CONFIG = {
  development: {
    local: currentUrl,
    original: currentUrl,
    swagger: currentUrl,
    ngrok: currentUrl,
    backend: currentUrl,
    current: currentUrl
  },
  testing: {
    local: currentUrl,
    ngrok: currentUrl,
    backend: currentUrl,
    current: currentUrl
  },
  production: {
    local: currentUrl,
    ngrok: currentUrl,
    backend: currentUrl,
    current: currentUrl
  }
};

const getCurrentEnv = () => {
  return process.env.NODE_ENV || 'development';
};

const getCurrentConfig = () => {
  const env = getCurrentEnv();
  return API_CONFIG[env] || API_CONFIG.development;
};

class ApiService {
  constructor() {
    this.config = getCurrentConfig();
    // 强制使用 API_BASE_URL，确保使用配置文件中的地址
    this.baseURL = API_BASE_URL || this.config.current || 'http://192.168.31.249:8081';
    this.timeout = 10000; // 10秒超时
    
    // 调试日志：显示初始化的服务器地址
    if (typeof console !== 'undefined') {
      console.log('🔧 ApiService 初始化');
      console.log('📡 API_BASE_URL:', API_BASE_URL);
      console.log('📡 this.baseURL:', this.baseURL);
    }
  }

  /**
   * 更新API配置
   * @param {string} serverUrl - 新的服务器地址
   */
  updateConfig(serverUrl) {
    // 如果传入的是空值，使用配置文件中的默认地址
    this.baseURL = serverUrl || API_BASE_URL || 'http://192.168.31.249:8081';
    
    // 调试日志
    if (typeof console !== 'undefined') {
      console.log('🔧 ApiService.updateConfig 被调用');
      console.log('📡 新地址:', this.baseURL);
    }
  }

  /**
   * 通用请求方法
   * @param {Object} options - 请求配置
   * @returns {Promise} 请求结果
   */
  async request(options) {
    const {
      url,
      method = 'GET',
      data = null,
      headers = {},
      timeout = this.timeout
    } = options;

    // 构建完整URL
    // 确保使用最新的 baseURL（如果被 updateConfig 更新过）
    const baseUrl = this.baseURL || API_BASE_URL || 'http://192.168.31.249:8081';
    const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
    
    // 调试日志（开发环境）
    if (process.env.NODE_ENV === 'development' && typeof console !== 'undefined') {
      console.log(`📤 API请求: ${method} ${fullUrl}`);
    }

    // 获取 token（从本地存储）
    let authToken = null;
    try {
      // 优先使用 uni.getStorageSync（适用于小程序和 APP）
      if (typeof uni !== 'undefined' && uni.getStorageSync) {
        authToken = uni.getStorageSync('authToken');
      }
      // 如果 uni 不可用，尝试使用 localStorage（适用于 H5）
      if (!authToken && typeof localStorage !== 'undefined') {
        authToken = localStorage.getItem('authToken');
      }
    } catch (error) {
      // 获取 token 失败，忽略
      console.log('获取 token 失败:', error);
    }
    
    // 调试日志：显示是否找到 token
    if (typeof console !== 'undefined' && process.env.NODE_ENV === 'development') {
      if (authToken) {
        console.log('✅ 已找到认证 token，将添加到请求头');
      } else {
        console.log('⚠️  未找到认证 token');
      }
    }

    // 默认请求头
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...headers
    };
    
    // 如果存在 token，添加到请求头
    if (authToken) {
      defaultHeaders['Authorization'] = `Bearer ${authToken}`;
    }

    // 构建请求配置
    const requestConfig = {
      url: fullUrl,
      method: method.toUpperCase(),
      header: defaultHeaders,
      timeout,
      dataType: 'json' // 明确指定数据类型
    };

    // 🔧 对于POST请求，确保数据正确序列化
    if (method.toUpperCase() === 'POST' && data) {
      // 在微信小程序中，uni.request 会自动序列化对象为 JSON
      // 但为了确保一致性，我们显式处理
      requestConfig.data = data;
      
      // 调试：记录POST请求的完整数据
      console.log('📤 [POST请求] 发送的数据:', JSON.stringify(data, null, 2));
      console.log('📤 [POST请求] 数据类型:', typeof data);
      console.log('📤 [POST请求] Content-Type:', defaultHeaders['Content-Type']);
    } else {
      requestConfig.data = data;
    }

    // 使用拦截器处理请求
    return await apiInterceptor.requestWithRetry(async (config) => {
      const response = await uni.request(config);

      // 检查响应状态
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return response.data;
      } else {
        // 详细记录错误信息
        console.error('❌ API请求失败:', {
          url: fullUrl,
          method: method,
          statusCode: response.statusCode,
          response: response.data,
          responseString: JSON.stringify(response.data, null, 2),
          headers: response.header || response.headers
        });
        
        const error = new Error(`HTTP ${response.statusCode}: ${response.data?.message || response.data || '请求失败'}`);
        error.statusCode = response.statusCode;
        error.response = response.data;
        error.url = fullUrl;
        error.method = method;
        throw error;
      }
    }, requestConfig);
  }

  /**
   * 错误处理
   * @param {Error} error - 错误对象
   * @returns {string} 错误信息
   */
  handleError(error) {
    // 检查状态码
    if (error.statusCode === 403) {
      return '服务器拒绝请求（403），可能是权限或CORS配置问题。请检查服务器配置。';
    } else if (error.statusCode === 401) {
      return '未授权（401），请先登录';
    } else if (error.statusCode === 404) {
      return '接口不存在（404），请检查API地址';
    } else if (error.statusCode === 500) {
      return '服务器内部错误（500），请稍后重试';
    }
    
    // 检查错误消息
    if (error.message.includes('timeout')) {
      return '请求超时，请检查网络连接';
    } else if (error.message.includes('network')) {
      return '网络连接失败，请检查网络设置';
    } else if (error.message.includes('403')) {
      return '服务器拒绝请求（403），可能是权限或CORS配置问题';
    } else if (error.message.includes('404')) {
      return '接口不存在，请检查API地址';
    } else if (error.message.includes('500')) {
      return '服务器内部错误，请稍后重试';
    } else {
      return error.message || '请求失败，请稍后重试';
    }
  }

  // ==================== 投票系统接口 ====================

  /**
   * 获取票数统计
   * @param {string} streamId - 直播流ID（必需）
   * @returns {Promise<Object>} 票数数据
   */
  async getVotes(streamId) {
    if (!streamId) {
      throw new Error('获取票数必须指定直播流ID (streamId)');
    }
    const url = `/api/v1/votes?stream_id=${streamId}`;
    return await this.request({
      url,
      method: 'GET'
    });
  }

  async getVote(streamId = null) {
    const url = streamId ? `/api/v1/votes?stream_id=${streamId}` : '/api/v1/votes';
    return await this.request({
      url,
      method: 'GET'
    });
  }

  /**
   * 用户投票
   * @param {string} side - 投票方 ('left' 或 'right')
   * @param {number} votes - 投票数量，默认10
   * @param {string} streamId - 直播流ID（必需，用于指定投票所属的直播流）
   * @returns {Promise<Object>} 投票结果
   */
  async userVote(side, votes = 10, streamId = null) {
    if (!side || !['left', 'right'].includes(side)) {
      throw new Error('投票方必须是 "left" 或 "right"');
    }

    // 🔧 验证 streamId 是否提供（投票必须指定直播流）
    if (!streamId) {
      throw new Error('投票必须指定直播流ID (streamId)');
    }

    // 确保 votes 是整数且在有效范围内
    // 注意：由于服务器要求总和为100，单方票数最大为100
    const voteCount = parseInt(votes, 10);
    if (isNaN(voteCount) || voteCount < 0 || voteCount > 100) {
      throw new Error('投票数量必须在 0-100 之间（总和必须为100）');
    }

    // 尝试从本地存储获取用户ID（如果存在）
    let userId = null;
    try {
      if (typeof uni !== 'undefined' && uni.getStorageSync) {
        const currentUser = uni.getStorageSync('currentUser');
        if (currentUser && currentUser.id) {
          userId = currentUser.id;
        }
      } else if (typeof localStorage !== 'undefined') {
        const currentUserStr = localStorage.getItem('currentUser');
        if (currentUserStr) {
          try {
            const currentUser = JSON.parse(currentUserStr);
            if (currentUser && currentUser.id) {
              userId = currentUser.id;
            }
          } catch (e) {
            // 解析失败，忽略
          }
        }
      }
    } catch (error) {
      // 获取用户ID失败，忽略
    }

    // 服务器期望的格式：{ leftVotes: number, rightVotes: number }
    // 服务器要求：leftVotes + rightVotes 必须等于 100
    // 根据 side 参数设置对应的票数，另一方的票数 = 100 - 当前票数
    const totalRequired = 100;
    let leftVotes, rightVotes;
    
    if (side === 'left') {
      // 投正方：leftVotes = voteCount, rightVotes = 100 - voteCount
      leftVotes = voteCount;
      rightVotes = totalRequired - voteCount;
    } else {
      // 投反方：rightVotes = voteCount, leftVotes = 100 - voteCount
      rightVotes = voteCount;
      leftVotes = totalRequired - voteCount;
    }
    
    // 确保票数在有效范围内
    if (leftVotes < 0 || leftVotes > totalRequired || rightVotes < 0 || rightVotes > totalRequired) {
      throw new Error(`投票数量无效：单方票数必须在 0-100 之间，总和必须为 ${totalRequired}`);
    }
    
    const requestData = {
      leftVotes: leftVotes,
      rightVotes: rightVotes
    };

    // 如果找到用户ID，添加到请求中
    if (userId) {
      requestData.userId = String(userId);
    }

    // 🔧 streamId 是必需的，必须添加到请求中
    // 注意：如果 streamId 为空，上面的验证应该已经抛出错误
    requestData.streamId = streamId;

    console.log('📤 投票请求数据 (服务器格式):', JSON.stringify(requestData, null, 2));
    console.log('📤 原始参数:', { side, votes: voteCount });

    try {
      // 🔧 后端API期望数据包装在 request 字段中
      // 根据错误信息 "body -> request: Field required"，后端明确需要 request 字段
    const requestBody = {
      request: {
        ...requestData,
        stream_id: requestData.streamId || streamId
      }
    };
      
      console.log('📤 最终发送的请求体:', JSON.stringify(requestBody, null, 2));
      
      const response = await this.request({
        url: '/api/v1/user-vote',
        method: 'POST',
        data: requestBody
      });
      try {
        const totals = await this.getVote(streamId);
        return totals;
      } catch (e0) {
        try {
          const totalsV1 = await this.getVotes(streamId);
          return totalsV1;
        } catch (e1) {
          return response;
        }
      }
    } catch (error) {
      // 详细记录错误信息
      console.error('❌ 投票请求失败详细信息:', {
        statusCode: error.statusCode,
        message: error.message,
        response: error.response,
        url: error.url,
        requestData: requestData
      });
      
      // 如果服务器返回了错误消息，在控制台详细显示
      if (error.response && error.response.message) {
        console.error('📋 服务器错误消息:', error.response.message);
        console.error('📋 服务器完整响应:', JSON.stringify(error.response, null, 2));
      }
      
      throw error;
    }
  }

  /**
   * 直接按分布投票（left/right 和为100）
   */
  async userVoteDistribution(leftVotes, rightVotes, streamId, userId = null) {
    if (typeof leftVotes !== 'number' || typeof rightVotes !== 'number') {
      throw new Error('leftVotes/rightVotes 必须是数字');
    }
    const total = Math.round(leftVotes) + Math.round(rightVotes);
    if (total !== 100) {
      throw new Error('投票总和必须为100');
    }
    if (!streamId) {
      throw new Error('投票必须指定直播流ID (streamId)');
    }
    
    // 获取用户ID（如果没有传入）
    if (!userId) {
      try {
        if (typeof uni !== 'undefined' && uni.getStorageSync) {
          const currentUser = uni.getStorageSync('currentUser');
          if (currentUser && currentUser.id) {
            userId = currentUser.id;
          }
        }
      } catch (e) {
        console.warn('⚠️ 无法获取本地存储的用户ID:', e);
      }
    }
    
    // 如果仍然没有 userId，使用 'guest'
    if (!userId) {
      userId = 'guest';
    }
    
    // 尝试多种请求格式和路径组合
    const testConfigs = [
      {
        name: '格式1-v1路径（直接格式）',
        url: '/api/v1/user-vote',
        data: {
          leftVotes: Math.round(leftVotes),
          rightVotes: Math.round(rightVotes),
          streamId: streamId,
          stream_id: streamId,
          userId: userId,
          user_id: userId
        }
      },
      {
        name: '格式2-v1路径（包装格式）',
        url: '/api/v1/user-vote',
        data: {
          request: {
            leftVotes: Math.round(leftVotes),
            rightVotes: Math.round(rightVotes),
            streamId: streamId,
            stream_id: streamId,
            userId: userId,
            user_id: userId
          }
        }
      },
      {
        name: '格式3-非v1路径（直接格式）',
        url: '/api/user-vote',
        data: {
          leftVotes: Math.round(leftVotes),
          rightVotes: Math.round(rightVotes),
          streamId: streamId,
          stream_id: streamId,
          userId: userId,
          user_id: userId
        }
      },
      {
        name: '格式4-非v1路径（包装格式）',
        url: '/api/user-vote',
        data: {
          request: {
            leftVotes: Math.round(leftVotes),
            rightVotes: Math.round(rightVotes),
            streamId: streamId,
            stream_id: streamId,
            userId: userId,
            user_id: userId
          }
        }
      }
    ];
    
    console.log('🔍 投票请求诊断信息:');
    console.log('  streamId:', streamId);
    console.log('  userId:', userId);
    console.log('  leftVotes:', Math.round(leftVotes));
    console.log('  rightVotes:', Math.round(rightVotes));
    console.log('  测试配置总数:', testConfigs.length);
    
    // 逐个尝试不同的格式
    for (let i = 0; i < testConfigs.length; i++) {
      const config = testConfigs[i];
      try {
        console.log(`📤 [${i + 1}/${testConfigs.length}] 尝试 ${config.name}`);
        console.log('   URL:', config.url);
        console.log('   Data:', JSON.stringify(config.data, null, 2));
        
        const response = await this.request({
          url: config.url,
          method: 'POST',
          data: config.data
        });
        
        console.log(`✅ ${config.name} 成功！返回数据:`, response);
        
        // 成功后尝试获取更新后的投票总数
        try {
          const totals = await this.getVote(streamId);
          return totals;
        } catch (e0) {
          try {
            const totalsV1 = await this.getVotes(streamId);
            return totalsV1;
          } catch (e1) {
            return response;
          }
        }
      } catch (error) {
        console.error(`❌ ${config.name} 失败:`, {
          statusCode: error.statusCode,
          message: error.message,
          response: error.response
        });
        
        // 继续尝试下一个格式
        if (i === testConfigs.length - 1) {
          // 最后一个配置也失败了
          console.error('🔍 所有格式都失败了！完整错误信息:', {
            statusCode: error.statusCode,
            message: error.message,
            response: error.response,
            url: error.url,
            allAttempts: testConfigs.map(c => c.name)
          });
          throw error;
        }
      }
    }
  }

  // ==================== AI内容接口 ====================

  /**
   * 获取AI识别内容
   * @param {string} streamId - 直播流ID（可选，不传则使用全局辩题）
   * @returns {Promise<Object>} AI内容列表
   */
  async getAiContent(streamId = null) {
    const url = streamId 
      ? `/api/v1/ai-content?stream_id=${streamId}`
      : '/api/v1/ai-content';
    return await this.request({
      url,
      method: 'GET'
    });
  }

  // ==================== 评论系统接口 ====================

  /**
   * 添加评论
   * @param {string} contentId - 内容ID（UUID字符串）
   * @param {string} text - 评论内容
   * @param {string} user - 用户名，默认"匿名用户"
   * @param {string} avatar - 用户头像，默认"👤"
   * @returns {Promise<Object>} 评论结果
   */
  async addComment(contentId, text, user = '匿名用户', avatar = '👤') {
    if (!contentId || !text) {
      throw new Error('内容ID和评论内容不能为空');
    }

    return await this.request({
      url: '/api/v1/comment',
      method: 'POST',
      data: {
        contentId: String(contentId), // 确保是字符串
        text: text.trim(),
        user: user.trim() || '匿名用户',
        avatar: avatar || '👤'
      }
    });
  }

  /**
   * 点赞功能
   * @param {string} contentId - 内容ID（UUID字符串）
   * @param {string} commentId - 评论ID（UUID字符串，可选，不传则点赞内容）
   * @returns {Promise<Object>} 点赞结果
   */
  async like(contentId, commentId = null) {
    if (!contentId) {
      throw new Error('内容ID不能为空');
    }

    const data = {
      contentId: String(contentId) // 确保是字符串
    };

    if (commentId !== null && commentId !== undefined) {
      data.commentId = String(commentId); // 确保是字符串
    }

    return await this.request({
      url: '/api/v1/like',
      method: 'POST',
      data
    });
  }

  /**
   * 删除评论
   * @param {string} contentId - 内容ID（UUID字符串）
   * @param {string} commentId - 评论ID（UUID字符串）
   * @returns {Promise<Object>} 删除结果
   */
  async deleteComment(contentId, commentId) {
    if (!contentId || !commentId) {
      throw new Error('内容ID和评论ID不能为空');
    }

    return await this.request({
      url: `/api/v1/comment/${commentId}`,
      method: 'DELETE',
      data: {
        contentId: String(contentId) // 确保是字符串
      }
    });
  }

  // ==================== 辩题管理接口 ====================

  /**
   * 获取辩题信息
   * @param {string} streamId - 直播流ID（可选，不传则使用全局辩题）
   * @returns {Promise<Object>} 辩题数据
   */
  async getDebateTopic(streamId = null) {
    const url = streamId 
      ? `/api/v1/debate-topic?stream_id=${streamId}`
      : '/api/v1/debate-topic';
    const response = await this.request({
      url,
      method: 'GET'
    });
    
    // 处理响应格式，确保兼容不同的响应格式
    let debateData = null;
    
    // 处理响应格式：{success: true, data: {...}} 或直接返回数据
    if (response && response.success && response.data) {
      debateData = response.data;
    } else if (response && response.data) {
      debateData = response.data;
    } else if (response && typeof response === 'object' && !response.success) {
      // 直接返回数据对象
      debateData = response;
    } else {
      // 如果响应格式不符合预期，返回 null
      console.warn('⚠️ 辩题响应格式不符合预期:', response);
      return null;
    }
    
    // 统一字段名称，兼容 leftPosition/rightPosition 和 leftSide/rightSide
    if (debateData) {
      // 如果后端返回的是 leftPosition/rightPosition，转换为 leftSide/rightSide
      if (debateData.leftPosition && !debateData.leftSide) {
        debateData.leftSide = debateData.leftPosition;
      }
      if (debateData.rightPosition && !debateData.rightSide) {
        debateData.rightSide = debateData.rightPosition;
      }
      
      // 返回统一格式
      return {
        success: true,
        data: {
          id: debateData.id || null,
          title: debateData.title || '',
          description: debateData.description || '',
          leftSide: debateData.leftSide || debateData.leftPosition || '',
          rightSide: debateData.rightSide || debateData.rightPosition || '',
          leftPosition: debateData.leftPosition || debateData.leftSide || '',
          rightPosition: debateData.rightPosition || debateData.rightSide || ''
        }
      };
    }
    
    return null;
  }

  /**
   * 查询用户投票状态
   * @param {string} streamId - 直播流ID（必需）
   * @returns {Promise<Object>} 用户投票数据
   */
  async getUserVotes(streamId) {
    if (!streamId) {
      throw new Error('查询用户投票状态必须指定直播流ID (streamId)');
    }
    
    // 获取当前用户ID
    let userId = null;
    try {
      if (typeof uni !== 'undefined' && uni.getStorageSync) {
        const currentUser = uni.getStorageSync('currentUser');
        if (currentUser && currentUser.id) {
          userId = currentUser.id;
        }
      } else if (typeof localStorage !== 'undefined') {
        const currentUserStr = localStorage.getItem('currentUser');
        if (currentUserStr) {
          try {
            const currentUser = JSON.parse(currentUserStr);
            if (currentUser && currentUser.id) {
              userId = currentUser.id;
            }
          } catch (e) {
            // 解析失败，忽略
          }
        }
      }
    } catch (error) {
      // 获取用户ID失败，忽略
    }
    
    if (!userId) {
      throw new Error('用户未登录，无法获取投票记录');
    }
    
    const url = `/api/v1/user-votes?stream_id=${streamId}&user_id=${userId}`;
    const response = await this.request({ url, method: 'GET' });
    if (response && response.success && response.data) {
      return response.data;
    }
    return response;
  }

  // ==================== 工具方法 ====================

  /**
   * 测试API连接
   * @param {string} streamId - 直播流ID（可选，如果提供则测试投票API，否则仅测试基础连接）
   * @returns {Promise<boolean>} 连接是否成功
   */
  async testConnection(streamId = null) {
    try {
      // 如果提供了 streamId，测试投票API
      if (streamId) {
        await this.getVotes(streamId);
      } else {
        // 如果没有提供 streamId，尝试使用 getDashboard 测试连接
        // 或者简单地测试 baseURL 是否可访问
        // 这里我们使用一个简单的请求来测试连接
        // 注意：如果后端有健康检查端点，可以使用它
        await this.request({
          url: '/api/admin/live/status',
          method: 'GET'
        });
      }
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * 获取当前配置信息
   * @returns {Object} 当前配置
   */
  getCurrentConfig() {
    return {
      baseURL: this.baseURL,
      timeout: this.timeout,
      config: this.config
    };
  }

  /**
   * 切换API服务器
   * @param {string} serverType - 服务器类型
   * @returns {string|null} 新的服务器地址
   */
  switchApiServer(serverType) {
    const env = getCurrentEnv();
    const config = API_CONFIG[env];
    
    if (config && config[serverType]) {
      config.current = config[serverType];
      this.baseURL = config[serverType];
      return config[serverType];
    } else {
      return null;
    }
  }

  /**
   * 获取当前服务器信息
   * @returns {Object} 服务器信息
   */
  getCurrentServerInfo() {
    const config = getCurrentConfig();
    const availableServers = Object.keys(config).filter(key => key !== 'current');
    
    return {
      current: config.current,
      environment: getCurrentEnv(),
      available: availableServers.map(type => ({
        type,
        url: config[type]
      }))
    };
  }

  /**
   * 获取当前直播状态
   * @returns {Promise<Object>} { isLive, streamUrl, ... }
   */
  async getLiveStatus() {
    return this.request({ url: '/api/admin/live/status', method: 'GET' });
  }

  /**
   * 获取数据概览（包含直播状态）
   * @param {string|null} streamId - 可选，指定要查询的直播流ID。如果提供，则查询该流的Dashboard；否则查询默认Dashboard
   * @returns {Promise<Object>} { isLive, liveStreamUrl, totalUsers, activeUsers, ... }
   */
  async getDashboard(streamId = null) {
    // 如果提供了 streamId，使用带参数的API查询特定流的Dashboard
    const url = streamId 
      ? `/api/v1/admin/dashboard?stream_id=${streamId}`
      : '/api/admin/dashboard';
    const response = await this.request({ url, method: 'GET' });
    // 如果返回的是包装格式 { success: true, data: {...} }，提取 data 字段
    if (response && response.success && response.data) {
      return response.data;
    }
    // 如果直接返回数据，直接返回
    return response;
  }

  /**
   * 控制直播（用户直接控制）
   * @param {string} action - 'start' 或 'stop'
   * @param {string} streamId - 可选的直播流ID，不传则使用默认启用的直播流
   * @returns {Promise<Object>} 操作结果
   */
  async controlLive(action, streamId = null) {
    if (!action || !['start', 'stop'].includes(action)) {
      throw new Error('action 必须是 "start" 或 "stop"');
    }

    const data = { action };
    if (streamId) {
      data.streamId = streamId;
    }

    return this.request({
      url: '/api/live/control',
      method: 'POST',
      data
    });
  }

  /**
   * 开始直播（用户直接调用）
   * @param {string} streamId - 可选的直播流ID
   * @returns {Promise<Object>} 操作结果
   */
  async startLive(streamId = null) {
    return this.controlLive('start', streamId);
  }

  /**
   * 停止直播（用户直接调用）
   * @returns {Promise<Object>} 操作结果
   */
  async stopLive() {
    return this.controlLive('stop');
  }

  /**
   * 获取直播流列表
   * @returns {Promise<Array>} 直播流列表
   */
  async getStreamsList() {
    const response = await this.request({ url: '/api/v1/admin/streams', method: 'GET' });
    // 处理多种可能的响应格式
    // 格式1: {success: true, data: {streams: [...], total: 5}}
    if (response && response.success && response.data && Array.isArray(response.data.streams)) {
      return response.data.streams;
    }
    // 格式2: {success: true, data: [...]} (直接是数组)
    if (response && response.success && Array.isArray(response.data)) {
      return response.data;
    }
    // 格式3: 直接返回数组
    if (Array.isArray(response)) {
      return response;
    }
    // 格式4: {streams: [...]}
    if (response && Array.isArray(response.streams)) {
      return response.streams;
    }
    // 格式5: 直接返回数据对象
    if (response && response.data && Array.isArray(response.data)) {
      return response.data;
    }
    console.warn('⚠️ 无法解析直播流列表响应格式:', response);
    return [];
  }

  /**
   * 获取指定直播流的投票统计
   * @param {string} streamId - 直播流ID（可选）
   * @returns {Promise<Object>} 投票统计数据
   */
  async getVotesStatistics(streamId = null) {
    const url = streamId 
      ? `/api/v1/admin/votes/statistics?stream_id=${streamId}`
      : '/api/v1/admin/votes/statistics';
    const response = await this.request({ url, method: 'GET' });
    if (response && response.success && response.data) {
      return response.data;
    }
    return response;
  }

  /**
   * 获取 WebSocket URL
   * @returns {string} WebSocket连接地址
   */
  getWebSocketUrl() {
    const baseUrl = this.baseURL || API_BASE_URL || 'http://192.168.31.249:8081';
    const wsProtocol = baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = baseUrl.replace(/^https?:\/\//, '');
    // WebSocket 路径是 /ws（不是 /api/v1/ws）
    return `${wsProtocol}://${wsHost}/ws`;
  }

  /**
   * 获取RTMP转HLS播放地址
   * @param {string} roomName - 房间名称/流名称
   * @returns {Promise<Object>} HLS播放地址等信息
   */
  async getRtmpToHlsUrls(roomName) {
    if (!roomName) {
      throw new Error('房间名称不能为空');
    }

    try {
      const response = await this.request({
        url: `/api/admin/rtmp/urls?room_name=${encodeURIComponent(roomName)}`,
        method: 'GET'
      });

      if (response && response.success && response.data) {
        console.log('✅ [RTMP转HLS] API返回数据:', {
          room_name: response.data.room_name,
          push_url: response.data.push_url,
          play_flv: response.data.play_flv,
          play_hls: response.data.play_hls
        });
        return response.data; // { push_url, play_flv, play_hls }
      }

      console.warn('⚠️ [RTMP转HLS] API返回格式异常:', response);
      return response;
    } catch (error) {
      console.error('获取RTMP转HLS地址失败:', error);
      throw error;
    }
  }

  /**
   * 从流URL中提取房间名（用于RTMP转HLS）
   * @param {string} streamUrl - 流地址
   * @returns {string|null} 房间名
   */
  extractRoomNameFromUrl(streamUrl) {
    if (!streamUrl) return null;

    try {
      // RTMP格式: rtmp://server:port/app/room_name
      // HLS格式: http://server:port/app/room_name.m3u8
      // FLV格式: http://server:port/app/room_name.flv
      
      // 移除协议前缀
      let path = streamUrl.replace(/^[a-zA-Z]+:\/\//, '');
      
      // 移除服务器地址和端口
      const parts = path.split('/');
      if (parts.length < 3) return null;
      
      // 获取最后一部分（房间名）
      let roomName = parts[parts.length - 1];
      
      // 移除文件扩展名
      roomName = roomName.replace(/\.(m3u8|flv|mp4)$/, '');
      
      return roomName || null;
    } catch (error) {
      console.error('解析房间名失败:', error);
      return null;
    }
  }

  /**
   * 智能转换流地址为HLS格式（如果需要）
   * @param {string} streamUrl - 原始流地址
   * @param {string} streamName - 流名称（可选）
   * @returns {Promise<string>} HLS播放地址
   */
  async convertToHlsIfNeeded(streamUrl, streamName = null) {
    if (!streamUrl) {
      throw new Error('流地址不能为空');
    }

    // 如果已经是HLS格式，直接返回
    if (streamUrl.includes('.m3u8')) {
      console.log('✅ 流地址已经是HLS格式，无需转换:', streamUrl);
      return streamUrl;
    }

    // 如果是RTMP或FLV格式，需要转换为FLV（HTTP协议支持）
    if (streamUrl.startsWith('rtmp://') || streamUrl.includes('.flv')) {
      console.log('🔄 检测到RTMP/FLV格式流，正在获取FLV地址...');

      // 提取房间名
      const roomName = streamName || this.extractRoomNameFromUrl(streamUrl);

      if (!roomName) {
        console.error('❌ 无法从URL中提取房间名:', streamUrl);
        throw new Error('无法解析流地址，请提供房间名');
      }

      try {
        // 调用API获取播放地址
        console.log('🔍 [FLV转换] 正在调用API，房间名:', roomName);
        const urls = await this.getRtmpToHlsUrls(roomName);

        console.log('📦 [FLV转换] API返回结果:', JSON.stringify(urls, null, 2));

        // 优先使用HLS格式（虽然需要HTTPS，但原生video组件支持好）
        if (urls && urls.play_hls) {
          console.log('✅ [HLS转换] 成功获取HLS地址:', urls.play_hls);

          // 修正 localhost 为真实服务器 IP
          let hlsUrl = urls.play_hls;

          // 1. 替换 localhost 为真实 IP
          if (hlsUrl.includes('localhost')) {
            // 从当前 API_BASE_URL 提取服务器 IP
            const apiBaseUrl = this.baseURL || API_BASE_URL;
            const serverIpMatch = apiBaseUrl.match(/https?:\/\/([^:\/]+)/);
            const serverIp = serverIpMatch ? serverIpMatch[1] : '192.168.31.189';

            hlsUrl = hlsUrl.replace('localhost', serverIp);
            console.log('🔄 [HLS转换] 已修正 localhost 为真实IP:', hlsUrl);
          }

          // 2. 直接使用原始SRS地址（避免代理兼容性问题）
          // 暂时移除代理，直接使用原始SRS地址测试
          if (hlsUrl.includes('192.168.31.189:8086')) {
            console.log('🔄 [HLS转换] 使用原始SRS地址（不使用代理）:', {
              原始地址: hlsUrl,
              说明: '直接使用SRS服务器，避免代理转发的兼容性问题'
            });
          }

          console.log('📺 [HLS转换] 最终HLS地址:', hlsUrl);
          console.log('📺 [转换完成] 流地址信息:', {
            push_url: urls.push_url,
            play_flv: urls.play_flv,
            play_hls: hlsUrl,
            格式: 'HLS (原生video组件支持更好)'
          });
          return hlsUrl;
        } else if (urls && urls.play_flv) {
          // 备选方案：如果没有HLS，使用FLV
          console.warn('⚠️ [HLS转换] 无法获取HLS地址，使用FLV作为备选');
          let flvUrl = urls.play_flv;

          // 同样的修正逻辑
          if (flvUrl.includes('localhost')) {
            const apiBaseUrl = this.baseURL || API_BASE_URL;
            const serverIpMatch = apiBaseUrl.match(/https?:\/\/([^:\/]+)/);
            const serverIp = serverIpMatch ? serverIpMatch[1] : '192.168.31.189';
            flvUrl = flvUrl.replace('localhost', serverIp);
          }

          if (flvUrl.includes('192.168.31.189:8086')) {
            console.log('🔄 [FLV备选] 使用原始SRS地址（不使用代理）:', flvUrl);
          }

          console.log('📺 [FLV备选] 最终FLV地址:', flvUrl);
          return flvUrl;
        } else {
          console.error('❌ [FLV转换] API返回数据中没有FLV或HLS地址, 完整响应:', urls);
          throw new Error('无法获取播放地址');
        }
      } catch (error) {
        console.error('❌ [FLV转换] 转换失败:', {
          error: error.message,
          stack: error.stack,
          roomName: roomName
        });
        throw new Error(`获取播放地址失败: ${error.message}`);
      }
    }

    // 其他格式，尝试直接返回（可能是HTTP-FLV等）
    console.log('⚠️ 未知格式的流地址，直接返回:', streamUrl);
    return streamUrl;
  }
}

// 创建单例实例
const apiService = new ApiService();

export default apiService;
