import { Task, TaskListResponse, DeletedTaskListResponse } from '@/types';

const now = new Date();
const tomorrow = new Date(now);
tomorrow.setDate(now.getDate() + 1);
const yesterday = new Date(now);
yesterday.setDate(now.getDate() - 1);
const nextWeek = new Date(now);
nextWeek.setDate(now.getDate() + 7);

export const MOCK_USER_ID = "mock-user-123";

export const MOCK_TASKS: Task[] = [
  {
    id: "task-1",
    title: "Complete project documentation",
    description: "Write detailed documentation for the frontend architecture and API integration.",
    completed: false,
    priority: "high",
    tags: ["work", "docs"],
    due_date: tomorrow.toISOString(),
    recurrence: "none",
    parent_id: null,
    deleted_at: null,
    deletion_reason: null,
    owner_id: MOCK_USER_ID,
    created_at: yesterday.toISOString(),
    updated_at: yesterday.toISOString(),
    is_overdue: false,
    is_due_today: false,
    is_recurring: false
  },
  {
    id: "task-2",
    title: "Review pull requests",
    description: "Check pending PRs for the authentication flow.",
    completed: true,
    priority: "medium",
    tags: ["work", "dev"],
    due_date: yesterday.toISOString(),
    recurrence: "daily",
    parent_id: null,
    deleted_at: null,
    deletion_reason: null,
    owner_id: MOCK_USER_ID,
    created_at: yesterday.toISOString(),
    updated_at: now.toISOString(),
    is_overdue: true,
    is_due_today: false,
    is_recurring: true
  },
  {
    id: "task-3",
    title: "Buy groceries",
    description: "Milk, eggs, bread, and coffee.",
    completed: false,
    priority: "low",
    tags: ["personal"],
    due_date: nextWeek.toISOString(),
    recurrence: "weekly",
    parent_id: null,
    deleted_at: null,
    deletion_reason: null,
    owner_id: MOCK_USER_ID,
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
    is_overdue: false,
    is_due_today: false,
    is_recurring: true
  },
  {
    id: "task-4",
    title: "Urgent bug fix",
    description: "Fix the critical crash on the payment page.",
    completed: false,
    priority: "high",
    tags: ["work", "bug"],
    due_date: now.toISOString(),
    recurrence: "none",
    parent_id: null,
    deleted_at: null,
    deletion_reason: null,
    owner_id: MOCK_USER_ID,
    created_at: now.toISOString(),
    updated_at: now.toISOString(),
    is_overdue: false,
    is_due_today: true,
    is_recurring: false
  }
];

export const MOCK_DELETED_TASKS: Task[] = [
  {
    id: "task-deleted-1",
    title: "Old recurring meeting",
    description: "Weekly standup that is no longer happening",
    completed: false,
    priority: "low",
    tags: ["work", "meeting"],
    due_date: yesterday.toISOString(),
    recurrence: "weekly",
    parent_id: null,
    deleted_at: now.toISOString(),
    deletion_reason: "Meeting cancelled permanently",
    owner_id: MOCK_USER_ID,
    created_at: yesterday.toISOString(),
    updated_at: now.toISOString(),
    is_overdue: false,
    is_due_today: false,
    is_recurring: true
  }
];

export const getMockTaskListResponse = (): TaskListResponse => {
  return {
    tasks: MOCK_TASKS,
    total: MOCK_TASKS.length,
    overdue_count: MOCK_TASKS.filter(t => t.is_overdue && !t.completed).length,
    due_today_count: MOCK_TASKS.filter(t => t.is_due_today && !t.completed).length
  };
};

export const getMockDeletedTaskListResponse = (): DeletedTaskListResponse => {
  return {
    tasks: MOCK_DELETED_TASKS,
    total: MOCK_DELETED_TASKS.length
  };
};
