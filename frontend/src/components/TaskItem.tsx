
// Task item component with full visual indicators and actions.

"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { Task, TaskPriority } from "@/types";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-provider";
import { Button } from "./Button";

interface TaskItemProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onRestore?: (task: Task) => void;
}

export function TaskItem({ task, onEdit, onRestore }: TaskItemProps) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showDeleteReason, setShowDeleteReason] = useState(false);
  const [deleteReason, setDeleteReason] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [toggleError, setToggleError] = useState("");
  const [optimisticCompleted, setOptimisticCompleted] = useState<boolean | null>(null);

  const toggleMutation = useMutation({
    mutationFn: () => {
      if (!user) throw new Error("Not authenticated");
      return api.toggleComplete(user.id, task.id);
    },
    onSuccess: () => {
      setOptimisticCompleted(null);
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setToggleError("");
    },
    onError: (err: Error) => {
      setOptimisticCompleted(null);
      setToggleError(err.message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (reason: string) => {
      if (!user) throw new Error("Not authenticated");
      return api.deleteTask(user.id, task.id, reason);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["deletedTasks"] });
      setShowDeleteReason(false);
      setDeleteReason("");
      setDeleteError("");
    },
    onError: (err: Error) => {
      setDeleteError(err.message);
    },
  });

  const restoreMutation = useMutation({
    mutationFn: () => {
      if (!user) throw new Error("Not authenticated");
      return api.restoreTask(user.id, task.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["deletedTasks"] });
      onRestore?.(task);
    },
  });

  const handleToggle = () => {
    setOptimisticCompleted(!task.completed);
    toggleMutation.mutate();
  };

  const handleDelete = () => {
    setShowDeleteReason(true);
  };

  const confirmDelete = async () => {
    if (!deleteReason.trim()) {
      setDeleteError("Please provide a deletion reason");
      return;
    }
    deleteMutation.mutate(deleteReason);
  };

  const getPriorityColor = (priority: TaskPriority) => {
    const p = priority.toLowerCase();
    switch (p) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const isDeleted = task.deleted_at !== null;

  return (
    <div
      className={`
        flex flex-col gap-2 p-4 bg-white rounded-lg shadow border-l-4
        ${
          isDeleted
            ? "border-gray-400 opacity-60"
            : task.is_overdue
            ? "border-red-500"
            : task.is_due_today
            ? "border-yellow-500"
            : "border-blue-500"
        }
        ${(optimisticCompleted !== null ? optimisticCompleted : task.completed) ? "opacity-60" : ""}
      `}
    >
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={optimisticCompleted !== null ? optimisticCompleted : task.completed}
          onChange={handleToggle}
          disabled={toggleMutation.isPending || isDeleted}
          className="w-5 h-5 mt-1 text-blue-600 rounded focus:ring-blue-500 cursor-pointer"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3
              className={`
                text-lg font-medium truncate
                ${(optimisticCompleted !== null ? optimisticCompleted : task.completed) ? "line-through text-gray-500" : "text-gray-900"}
              `}
            >
              {task.title}
            </h3>

            {/* Priority badge */}
            <span
              className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getPriorityColor(
                task.priority
              )}`}
            >
              {task.priority.toLowerCase()}
            </span>

            {/* Overdue indicator */}
            {task.is_overdue && !task.completed && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 text-red-800 border border-red-200">
                ⚠ Overdue
              </span>
            )}

            {/* Due today indicator */}
            {task.is_due_today && !task.completed && !task.is_overdue && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 border border-yellow-200">
                Due today
              </span>
            )}

            {/* Recurring indicator */}
            {task.is_recurring && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-purple-100 text-purple-800 border border-purple-200">
                🔄 Recurring
              </span>
            )}
          </div>

          {task.description && (
            <p className="text-sm text-gray-500 mt-1 truncate">{task.description}</p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Due date */}
          {task.due_date && (
            <p className="text-sm text-gray-500 mt-1">
              📅 Due: {formatDueDate(task.due_date)}
            </p>
          )}

          {/* Deleted info */}
          {isDeleted && task.deletion_reason && (
            <p className="text-sm text-gray-500 mt-1 italic">
              Deleted: {task.deletion_reason}
            </p>
          )}

          {/* Toggle error */}
          {toggleError && (
            <p className="text-red-500 text-sm mt-1">Error: {toggleError}</p>
          )}
        </div>

        {/* Actions */}
        {!isDeleted && (
          <div className="flex items-center gap-2">
            {onEdit && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onEdit(task)}
              >
                Edit
              </Button>
            )}
            <Button
              variant="danger"
              size="sm"
              onClick={handleDelete}
              isLoading={deleteMutation.isPending}
            >
              Delete
            </Button>
          </div>
        )}

        {/* Restore action for deleted tasks */}
        {isDeleted && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => restoreMutation.mutate()}
            isLoading={restoreMutation.isPending}
          >
            Restore
          </Button>
        )}
      </div>

      {/* Delete confirmation with reason */}
      {showDeleteReason && !isDeleted && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Reason for deletion (required):
          </label>
          <textarea
            value={deleteReason}
            onChange={(e) => setDeleteReason(e.target.value)}
            placeholder="Enter reason for deleting this task..."
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          {deleteError && (
            <p className="text-red-500 text-sm mt-1">{deleteError}</p>
          )}
          <div className="flex gap-2 mt-2">
            <Button
              size="sm"
              onClick={confirmDelete}
              isLoading={deleteMutation.isPending}
            >
              Confirm Delete
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setShowDeleteReason(false);
                setDeleteReason("");
                setDeleteError("");
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
