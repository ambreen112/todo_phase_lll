// Frontend TypeScript type definitions.

export type TaskPriority = "low" | "medium" | "high" | "LOW" | "MEDIUM" | "HIGH";
export type TaskRecurrence = "none" | "daily" | "weekly" | "monthly" | "NONE" | "DAILY" | "WEEKLY" | "MONTHLY";

export interface User {
  id: string;
  email: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: TaskPriority;
  tags: string[] | null;
  due_date: string | null;
  recurrence: TaskRecurrence;
  parent_id: string | null;
  deleted_at: string | null;
  deletion_reason: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
  // Computed fields from backend
  is_overdue: boolean;
  is_due_today: boolean;
  is_recurring: boolean;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  recurrence?: TaskRecurrence;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: TaskPriority;
  tags?: string[];
  due_date?: string;
  recurrence?: TaskRecurrence;
}

export interface TaskDelete {
  deletion_reason: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
}

export interface SignupRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  overdue_count: number;
  due_today_count: number;
}

export interface DeletedTaskListResponse {
  tasks: Task[];
  total: number;
}

export interface ErrorResponse {
  detail: string;
}

export interface TaskFilters {
  completed?: boolean;
  priority?: TaskPriority;
  tag?: string;
  due_status?: "overdue" | "due_today" | "future";
  search?: string;
  sort_by?: "created_at" | "due_date" | "priority" | "title";
  sort_order?: "asc" | "desc";
}

// Chat types
export interface ChatMessage {
  id?: string;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp?: string;
}

export interface ToolCall {
  tool_name: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown> | null;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

export interface ChatResponse {
  success: boolean;
  conversation_id: string;
  agent_response: string;
  tool_calls: ToolCall[];
  messages: ChatMessage[];
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationsListResponse {
  conversations: Conversation[];
}

export interface ConversationMessagesResponse {
  conversation_id: string;
  messages: ChatMessage[];
}
