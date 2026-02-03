// Task list component with filtering, search, and sorting.

"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-provider";
import { TaskItem } from "./TaskItem";
import { Input } from "./Input";
import type { Task, TaskPriority, TaskFilters } from "@/types";

interface TaskListProps {
  onEditTask?: (task: Task) => void;
}

export function TaskList({ onEditTask }: TaskListProps) {
  const { user, isLoading: authLoading } = useAuth();

  // Filter state
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "completed">(
    "all"
  );
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | "">("");
  const [dueStatusFilter, setDueStatusFilter] = useState<
    "all" | "overdue" | "due_today" | "future"
  >("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState<"created_at" | "due_date" | "priority" | "title">(
    "created_at"
  );
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  // Debounce search input to prevent excessive API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Build filters object
  const filters: TaskFilters = {
    completed: statusFilter === "all" ? undefined : statusFilter === "completed",
    priority: priorityFilter || undefined,
    due_status: dueStatusFilter === "all" ? undefined : dueStatusFilter,
    search: debouncedSearch.trim() || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["tasks", user?.id, filters],
    queryFn: async () => {
      if (!user) throw new Error("Not authenticated");
      return api.getTasks(user.id, filters);
    },
    enabled: !!user && !authLoading,
    placeholderData: (previousData) => previousData,
  });

  const { data: deletedData, refetch: refetchDeleted } = useQuery({
    queryKey: ["deletedTasks", user?.id],
    queryFn: async () => {
      if (!user) throw new Error("Not authenticated");
      return api.getDeletedTasks(user.id);
    },
    enabled: !!user && !authLoading,
  });

  const [showDeleted, setShowDeleted] = useState(false);

  const handleRestore = (task: Task) => {
    refetch();
    refetchDeleted();
  };

  // Show loading state on initial load only
  const isInitialLoad = isLoading && !data;

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Error loading tasks</p>
      </div>
    );
  }

  const tasks = (showDeleted ? deletedData?.tasks : data?.tasks) || [];

  return (
    <div>
      {/* Initial loading state */}
      {isInitialLoad && (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading tasks...</p>
        </div>
      )}

      {/* Statistics banner */}
      {!showDeleted && data && (data.overdue_count > 0 || data.due_today_count > 0) && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          {data.overdue_count > 0 && (
            <p className="text-red-700 text-sm">
              ⚠️ {data.overdue_count} overdue task
              {data.overdue_count !== 1 ? "s" : ""}
            </p>
          )}
          {data.due_today_count > 0 && (
            <p className="text-yellow-700 text-sm">
              📅 {data.due_today_count} due today
            </p>
          )}
        </div>
      )}

      {/* Search and Filters */}
      <div className="mb-4 space-y-3">
        {/* Search */}
        <Input
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        {/* Filter controls */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) =>
              setStatusFilter(e.target.value as "all" | "active" | "completed")
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>

          {/* Priority filter */}
          <select
            value={priorityFilter}
            onChange={(e) =>
              setPriorityFilter(e.target.value as TaskPriority | "")
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Due status filter */}
          <select
            value={dueStatusFilter}
            onChange={(e) =>
              setDueStatusFilter(
                e.target.value as "all" | "overdue" | "due_today" | "future"
              )
            }
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="all">All Due Dates</option>
            <option value="overdue">Overdue</option>
            <option value="due_today">Due Today</option>
            <option value="future">Future</option>
          </select>

          {/* Sort */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [by, order] = e.target.value.split("-");
              setSortBy(by as "created_at" | "due_date" | "priority" | "title");
              setSortOrder(order as "asc" | "desc");
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="created_at-desc">Newest First</option>
            <option value="created_at-asc">Oldest First</option>
            <option value="due_date-asc">Due Date (Soonest)</option>
            <option value="due_date-desc">Due Date (Latest)</option>
            <option value="priority-desc">Priority (High→Low)</option>
            <option value="priority-asc">Priority (Low→High)</option>
            <option value="title-asc">Title (A→Z)</option>
            <option value="title-desc">Title (Z→A)</option>
          </select>
        </div>

        {/* Toggle deleted tasks view */}
        <button
          onClick={() => setShowDeleted(!showDeleted)}
          className="text-sm text-gray-600 hover:text-gray-900 underline"
        >
          {showDeleted
            ? `Hide deleted tasks (${deletedData?.total || 0})`
            : `Show deleted tasks (${deletedData?.total || 0})`}
        </button>
      </div>

      {/* Task count */}
      {!showDeleted && data && (
        <p className="text-sm text-gray-500 mb-2">
          Showing {data.tasks.length} of {data.total} tasks
        </p>
      )}

      {/* Task list */}
      {tasks.length > 0 ? (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onEdit={onEditTask}
              onRestore={handleRestore}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500 mb-2">
            {showDeleted
              ? "No deleted tasks"
              : "No tasks found"}
          </p>
          <p className="text-sm text-gray-400">
            {showDeleted
              ? "Deleted tasks will appear here"
              : "Create your first task to get started!"}
          </p>
        </div>
      )}
    </div>
  );
}
