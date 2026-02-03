// Edit task form component with full metadata fields.

"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-provider";
import { Input } from "./Input";
import { Button } from "./Button";
import type { Task, TaskPriority, TaskRecurrence } from "@/types";

interface EditTaskFormProps {
  task: Task;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function EditTaskForm({ task, onSuccess, onCancel }: EditTaskFormProps) {
  const { user, isLoading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  // Form state - initialize from task
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || "");
  const [priority, setPriority] = useState<TaskPriority>(task.priority as TaskPriority);
  const [tags, setTags] = useState(task.tags?.join(", ") || "");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [recurrence, setRecurrence] = useState<TaskRecurrence>(task.recurrence as TaskRecurrence);
  const [error, setError] = useState("");

  // Parse due_date on mount - convert to local timezone for display
  useEffect(() => {
    if (task.due_date) {
      const date = new Date(task.due_date);
      // Use local date/time methods instead of toISOString() which returns UTC
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      setDueDate(`${year}-${month}-${day}`);
      setDueTime(`${hours}:${minutes}`);
    }
  }, [task.due_date]);

  const updateMutation = useMutation({
    mutationFn: async (updates: {
      title: string;
      description?: string;
      priority: TaskPriority;
      tags?: string[];
      due_date?: string;
      recurrence: TaskRecurrence;
    }) => {
      if (!user) throw new Error("Not authenticated");
      return api.updateTask(user.id, task.id, updates);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", user?.id] });
      onSuccess?.();
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    // Parse tags from comma-separated string
    const tagsArray = tags
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    // Build due_date from date and time inputs
    // Use Date constructor with individual components to ensure local timezone interpretation
    let dueDateTime: string | undefined;
    if (dueDate) {
      const [year, month, day] = dueDate.split('-').map(Number);
      if (dueTime) {
        const [hours, minutes] = dueTime.split(':').map(Number);
        // Create date using local timezone (month is 0-indexed)
        const localDate = new Date(year, month - 1, day, hours, minutes, 0);
        dueDateTime = localDate.toISOString();
      } else {
        const localDate = new Date(year, month - 1, day, 0, 0, 0);
        dueDateTime = localDate.toISOString();
      }
    }

    updateMutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      tags: tagsArray.length > 0 ? tagsArray : undefined,
      due_date: dueDateTime,
      recurrence,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter task title"
        error={error}
        required
      />

      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description (optional)
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Priority */}
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Priority
        </label>
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as TaskPriority)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>
      </div>

      {/* Tags */}
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tags (comma-separated, optional)
        </label>
        <Input
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="work, urgent, meeting"
        />
      </div>

      {/* Due Date and Time */}
      <div className="grid grid-cols-2 gap-4">
        <div className="w-full">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Due Date (optional)
          </label>
          <Input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>
        <div className="w-full">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Due Time (optional)
          </label>
          <Input
            type="time"
            value={dueTime}
            onChange={(e) => setDueTime(e.target.value)}
          />
        </div>
      </div>

      {/* Recurrence */}
      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Recurrence
        </label>
        <select
          value={recurrence}
          onChange={(e) => setRecurrence(e.target.value as TaskRecurrence)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="none">none</option>
          <option value="daily">daily</option>
          <option value="weekly">weekly</option>
          <option value="monthly">monthly</option>
        </select>
      </div>

      <div className="flex gap-2">
        <Button
          type="submit"
          isLoading={updateMutation.isPending}
          disabled={authLoading}
        >
          Update Task
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
