import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  User,
  Document,
  ChatSession,
  ChatMessage,
  UserSettings,
  QuestionRequest,
  QuestionResponse,
  ProcessingStatus,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.token = localStorage.getItem('token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('token');
  }

  getToken(): string | null {
    return this.token;
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await this.api.post('/users/', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/users/me');
    return response.data;
  }

  // Document endpoints
  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getDocuments(skip = 0, limit = 100): Promise<Document[]> {
    const response = await this.api.get('/documents/', {
      params: { skip, limit },
    });
    return response.data;
  }

  async getDocument(documentId: string): Promise<Document> {
    const response = await this.api.get(`/documents/${documentId}`);
    return response.data;
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.api.delete(`/documents/${documentId}`);
  }

  async processDocument(documentId: string): Promise<any> {
    const response = await this.api.post(`/documents/${documentId}/process`);
    return response.data;
  }

  async getProcessingStatus(documentId: string): Promise<ProcessingStatus> {
    const response = await this.api.get(`/documents/${documentId}/status`);
    return response.data;
  }

  async processAllDocuments(): Promise<any> {
    const response = await this.api.post('/documents/process-all');
    return response.data;
  }

  // Chat endpoints
  async askQuestion(request: QuestionRequest): Promise<QuestionResponse> {
    const response = await this.api.post('/chat/ask', request);
    return response.data;
  }

  async getChatSessions(skip = 0, limit = 100, activeOnly = true): Promise<ChatSession[]> {
    const response = await this.api.get('/chat/sessions', {
      params: { skip, limit, active_only: activeOnly },
    });
    return response.data;
  }

  async createChatSession(title?: string, documentFilter?: string[]): Promise<ChatSession> {
    const response = await this.api.post('/chat/sessions', {
      title,
      document_filter: documentFilter || [],
    });
    return response.data;
  }

  async getChatSession(sessionId: string): Promise<ChatSession> {
    const response = await this.api.get(`/chat/sessions/${sessionId}`);
    return response.data;
  }

  async deleteChatSession(sessionId: string): Promise<void> {
    await this.api.delete(`/chat/sessions/${sessionId}`);
  }

  async getSessionMessages(sessionId: string, skip = 0, limit = 100): Promise<ChatMessage[]> {
    const response = await this.api.get(`/chat/sessions/${sessionId}/messages`, {
      params: { skip, limit },
    });
    return response.data;
  }

  async getConversationHistory(sessionId: string, limit = 50): Promise<any> {
    const response = await this.api.get(`/chat/sessions/${sessionId}/history`, {
      params: { limit },
    });
    return response.data;
  }

  async getQuestionSuggestions(documentIds?: string[], limit = 5): Promise<string[]> {
    const response = await this.api.get('/chat/suggestions', {
      params: { document_ids: documentIds, limit },
    });
    return response.data.suggestions;
  }

  // Settings endpoints
  async getUserSettings(): Promise<UserSettings> {
    const response = await this.api.get('/settings/');
    return response.data;
  }

  async updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await this.api.put('/settings/', settings);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; environment: string }> {
    const response = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/health`);
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;