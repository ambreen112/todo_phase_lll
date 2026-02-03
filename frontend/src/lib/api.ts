// API client utility for backend communication.

import axios, { AxiosInstance, AxiosError } from "axios";
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskDelete,
  TaskListResponse,
  DeletedTaskListResponse,
  TaskFilters,
  AuthResponse,
  SignupRequest,
  LoginRequest,
  ErrorResponse,
  ChatRequest,
  ChatResponse,
  ConversationsListResponse,
  ConversationMessagesResponse,
} from "@/types";

import {
  MOCK_TASKS,
  MOCK_DELETED_TASKS,
  getMockTaskListResponse,
  getMockDeletedTaskListResponse,
  MOCK_USER_ID,
} from "./mock-data";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "true";

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;
  private useMock: boolean = USE_MOCK;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        // Double check token from storage if current token is null
        if (!this.token) {
          const storedToken = getStoredToken();
          if (storedToken) {
            this.token = storedToken;
          }
        }

        if (this.token) {
          // Use .set() if available, otherwise fallback to direct assignment
          if (typeof config.headers.set === "function") {
            config.headers.set("Authorization", `Bearer ${this.token}`);
          } else {
            (config.headers as any).Authorization = `Bearer ${this.token}`;
          }
        } else {
          // Check if it's a protected route and we're missing a token
          const isAuthRoute = config.url?.startsWith("/auth/");
          if (!isAuthRoute && process.env.NODE_ENV === "development") {
            console.warn(`Protected request to ${config.url} made without auth token`);
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorResponse>) => {
        if (error.response?.status === 401) {
          // Clear token and redirect to login
          this.clearToken();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string | null) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  // Authentication
  async signup(request: SignupRequest): Promise<AuthResponse> {
    if (this.useMock) {
      return {
        access_token: "mock-jwt-token",
        token_type: "bearer",
        user_id: MOCK_USER_ID,
        email: request.email,
      };
    }
    const response = await this.client.post<AuthResponse>("/auth/signup", request);
    return response.data;
  }

  async login(request: LoginRequest): Promise<AuthResponse> {
    if (this.useMock) {
      return {
        access_token: "mock-jwt-token",
        token_type: "bearer",
        user_id: MOCK_USER_ID,
        email: request.email,
      };
    }
    const response = await this.client.post<AuthResponse>("/auth/login", request);
    return response.data;
  }

  // Tasks - List with filters
  async getTasks(userId: string, filters?: TaskFilters): Promise<TaskListResponse> {
    if (this.useMock) {
      // Simulate network delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      let tasks = [...MOCK_TASKS];

      // Basic filtering for mock
      if (filters) {
        if (filters.search) {
          const search = filters.search.toLowerCase();
          tasks = tasks.filter(t =>
            t.title.toLowerCase().includes(search) ||
            (t.description && t.description.toLowerCase().includes(search))
          );
        }
        if (filters.priority) {
          tasks = tasks.filter(t => t.priority === filters.priority);
        }
        if (filters.completed !== undefined) {
          tasks = tasks.filter(t => t.completed === filters.completed);
        }
        // Sorting
        if (filters.sort_by) {
          tasks.sort((a, b) => {
            let valA: any = a[filters.sort_by as keyof Task];
            let valB: any = b[filters.sort_by as keyof Task];

            if (filters.sort_by === 'priority') {
              const priorityWeight: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1, high: 3, medium: 2, low: 1 };
              valA = priorityWeight[a.priority] || 0;
              valB = priorityWeight[b.priority] || 0;
            } else if (filters.sort_by === 'due_date' || filters.sort_by === 'created_at') {
                 // Handle null dates (sort them last)
                 if (!valA) return 1;
                 if (!valB) return -1;
            }

            if (valA < valB) return filters.sort_order === 'asc' ? -1 : 1;
            if (valA > valB) return filters.sort_order === 'asc' ? 1 : -1;
            return 0;
          });
        }
      }

      return {
        tasks,
        total: tasks.length,
        overdue_count: tasks.filter(t => t.is_overdue && !t.completed).length,
        due_today_count: tasks.filter(t => t.is_due_today && !t.completed).length
      };
    }

    const params: Record<string, any> = {};

    if (filters?.completed !== undefined) {
      params.completed = filters.completed;
    }
    if (filters?.priority) {
      params.priority = filters.priority.toUpperCase();
    }
    if (filters?.tag) {
      params.tag = filters.tag;
    }
    if (filters?.due_status) {
      params.due_status = filters.due_status;
    }
    if (filters?.search) {
      params.search = filters.search;
    }
    if (filters?.sort_by) {
      params.sort_by = filters.sort_by;
    }
    if (filters?.sort_order) {
      params.sort_order = filters.sort_order;
    }

    const response = await this.client.get<TaskListResponse>(`/api/${userId}/tasks`, {
      params,
    });
    return response.data;
  }

  // Get deleted tasks
  async getDeletedTasks(userId: string): Promise<DeletedTaskListResponse> {
    if (this.useMock) {
      return getMockDeletedTaskListResponse();
    }
    const response = await this.client.get<DeletedTaskListResponse>(
      `/api/${userId}/tasks/deleted`
    );
    return response.data;
  }

  async getTask(userId: string, taskId: string): Promise<Task> {
    if (this.useMock) {
      const task = MOCK_TASKS.find(t => t.id === taskId);
      if (!task) throw new Error("Task not found");
      return task;
    }
    const response = await this.client.get<Task>(
      `/api/${userId}/tasks/${taskId}`
    );
    return response.data;
  }

  async createTask(userId: string, task: TaskCreate): Promise<Task> {
    if (this.useMock) {
      // Create a mock task
      const newTask: Task = {
        id: `task-${Date.now()}`,
        title: task.title,
        description: task.description || null,
        completed: false,
        priority: task.priority || "medium",
        tags: task.tags || [],
        due_date: task.due_date || null,
        recurrence: task.recurrence || "none",
        parent_id: null,
        deleted_at: null,
        deletion_reason: null,
        owner_id: userId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_overdue: false,
        is_due_today: false,
        is_recurring: task.recurrence !== "none"
      };

      // Add to mock array in memory (won't persist across page reloads in this simple implementation)
      MOCK_TASKS.unshift(newTask);
      return newTask;
    }
    const response = await this.client.post<Task>(`/api/${userId}/tasks`, task);
    return response.data;
  }

  async updateTask(
    userId: string,
    taskId: string,
    task: TaskUpdate
  ): Promise<Task> {
    if (this.useMock) {
      const existingIndex = MOCK_TASKS.findIndex(t => t.id === taskId);
      if (existingIndex === -1) throw new Error("Task not found");

      const updatedTask = { ...MOCK_TASKS[existingIndex], ...task, updated_at: new Date().toISOString() };

      // Update derived fields
      if (task.due_date || task.completed !== undefined) {
        const d = task.due_date ? new Date(task.due_date) : (updatedTask.due_date ? new Date(updatedTask.due_date) : null);
        const isCompleted = task.completed !== undefined ? task.completed : updatedTask.completed;

        if (d) {
           const now = new Date();
           const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
           const dueDay = new Date(d.getFullYear(), d.getMonth(), d.getDate());

           updatedTask.is_overdue = d < now && !isCompleted;
           updatedTask.is_due_today = dueDay.getTime() === today.getTime() && !isCompleted;
        }
      }

      MOCK_TASKS[existingIndex] = updatedTask as Task;
      return updatedTask as Task;
    }
    const response = await this.client.put<Task>(
      `/api/${userId}/tasks/${taskId}`,
      task
    );
    return response.data;
  }

  async deleteTask(userId: string, taskId: string, reason: string): Promise<void> {
    if (this.useMock) {
      const existingIndex = MOCK_TASKS.findIndex(t => t.id === taskId);
      if (existingIndex !== -1) {
        const task = MOCK_TASKS[existingIndex];
        MOCK_TASKS.splice(existingIndex, 1);
        MOCK_DELETED_TASKS.push({
          ...task,
          deleted_at: new Date().toISOString(),
          deletion_reason: reason
        });
      }
      return;
    }
    await this.client.delete(`/api/${userId}/tasks/${taskId}`, {
      data: { deletion_reason: reason },
    });
  }

  async restoreTask(userId: string, taskId: string): Promise<Task> {
    if (this.useMock) {
      const existingIndex = MOCK_DELETED_TASKS.findIndex(t => t.id === taskId);
      if (existingIndex === -1) throw new Error("Task not found in deleted items");

      const task = MOCK_DELETED_TASKS[existingIndex];
      MOCK_DELETED_TASKS.splice(existingIndex, 1);

      const restoredTask = {
        ...task,
        deleted_at: null,
        deletion_reason: null,
        updated_at: new Date().toISOString()
      };

      MOCK_TASKS.unshift(restoredTask);
      return restoredTask;
    }
    const response = await this.client.post<Task>(
      `/api/${userId}/tasks/${taskId}/restore`
    );
    return response.data;
  }

  async toggleComplete(userId: string, taskId: string): Promise<Task> {
    if (this.useMock) {
      const existingIndex = MOCK_TASKS.findIndex(t => t.id === taskId);
      if (existingIndex === -1) throw new Error("Task not found");

      const task = MOCK_TASKS[existingIndex];
      const updatedTask = {
        ...task,
        completed: !task.completed,
        updated_at: new Date().toISOString()
      };

      MOCK_TASKS[existingIndex] = updatedTask;
      return updatedTask;
    }
    const response = await this.client.patch<Task>(
      `/api/${userId}/tasks/${taskId}/complete`
    );
    return response.data;
  }

  // Chat API methods
  async sendChatMessage(userId: string, request: ChatRequest): Promise<ChatResponse> {
    if (this.useMock) {
      // Mock chat response
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return {
        success: true,
        conversation_id: request.conversation_id || `conv-${Date.now()}`,
        agent_response: `I received your message: "${request.message}". This is a mock response. In production, I would help you manage your tasks using natural language.`,
        tool_calls: [],
        messages: [
          {
            role: "user",
            content: request.message,
            timestamp: new Date().toISOString()
          },
          {
            role: "assistant",
            content: `I received your message: "${request.message}". This is a mock response. In production, I would help you manage your tasks using natural language.`,
            timestamp: new Date().toISOString()
          }
        ]
      };
    }
    const response = await this.client.post<ChatResponse>(
      `/api/${userId}/chat`,
      request
    );
    return response.data;
  }

  async getConversations(userId: string): Promise<ConversationsListResponse> {
    if (this.useMock) {
      return { conversations: [] };
    }
    const response = await this.client.get<ConversationsListResponse>(
      `/api/${userId}/conversations`
    );
    return response.data;
  }

  async getConversationMessages(userId: string, conversationId: string): Promise<ConversationMessagesResponse> {
    if (this.useMock) {
      return {
        conversation_id: conversationId,
        messages: []
      };
    }
    const response = await this.client.get<ConversationMessagesResponse>(
      `/api/${userId}/conversations/${conversationId}/messages`
    );
    return response.data;
  }
}

// Singleton instance
export const api = new ApiClient();

// Helper functions for localStorage
export const getStoredToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
};

export const setStoredToken = (token: string): void => {
  if (typeof window === "undefined") return;
  localStorage.setItem("auth_token", token);
};

export const clearStoredToken = (): void => {
  if (typeof window === "undefined") return;
  localStorage.removeItem("auth_token");
};
