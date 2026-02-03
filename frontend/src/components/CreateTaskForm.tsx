// Create task form component with full metadata fields.

"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-provider";
import { Input } from "./Input";
import { Button } from "./Button";
import type { TaskPriority, TaskRecurrence } from "@/types";

interface CreateTaskFormProps {
  onSuccess?: () => void;
}

export function CreateTaskForm({ onSuccess }: CreateTaskFormProps) {
  const { user, isLoading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [tags, setTags] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [recurrence, setRecurrence] = useState<TaskRecurrence>("none");
  const [error, setError] = useState("");

  const createMutation = useMutation({
    mutationFn: async (task: {
      title: string;
      description?: string;
      priority: TaskPriority;
      tags?: string[];
      due_date?: string;
      recurrence: TaskRecurrence;
    }) => {
      if (!user) throw new Error("Not authenticated");
      return api.createTask(user.id, task);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks", user?.id] });
      resetForm();
      onSuccess?.();
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setPriority("medium");
    setTags("");
    setDueDate("");
    setDueTime("");
    setRecurrence("none");
    setError("");
  };

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

    createMutation.mutate({
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

      <Button
        type="submit"
        isLoading={createMutation.isPending}
        disabled={authLoading}
      >
        Create Task
      </Button>
    </form>
  );
}
