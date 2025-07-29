import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

export class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  getBaseUrl() {
    return this.client.defaults.baseURL;
  }

  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        if (error.response) {
          const status = error.response.status;
          const message = error.response.data?.message || error.response.data?.detail || '请求失败';
          
          switch (status) {
            case 401:
              console.error('未授权访问');
              break;
            case 403:
              console.error('禁止访问');
              break;
            case 404:
              console.error('资源不存在');
              break;
            default:
              console.error('请求失败:', message);
          }
          
          return Promise.reject(new Error(message));
        }
        
        if (error.request) {
          return Promise.reject(new Error('网络连接失败'));
        }
        
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    return this.client.get<any, T>(url, config);
  }

  async post<T>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> {
    return this.client.post<any, T>(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> {
    return this.client.put<any, T>(url, data, config);
  }

  async delete<T>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    return this.client.delete<any, T>(url, config);
  }

  async upload(url: string, files: File[], config?: InternalAxiosRequestConfig): Promise<any> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await this.client.post(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data'
      }
    });

    return response.data;
  }
}

export const apiService = new ApiService();