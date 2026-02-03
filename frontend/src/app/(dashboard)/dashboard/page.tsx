// Dashboard page with task list and notifications.

"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/lib/auth-provider";
import { TaskList } from "@/components/TaskList";
import { CreateTaskForm } from "@/components/CreateTaskForm";
import { EditTaskForm } from "@/components/EditTaskForm";
import { Button } from "@/components/Button";
import { ChatBot } from "@/components/ChatBot";
import { useNotifications, useToastNotifications } from "@/lib/notifications";
import type { Task } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, logout, isLoading: authLoading } = useAuth();

  // Callback to refresh tasks when chatbot makes changes
  const handleTasksUpdated = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["tasks"] });
    queryClient.invalidateQueries({ queryKey: ["deletedTasks"] });
  }, [queryClient]);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [authLoading, user, router]);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);

  // Notifications hooks
  const {
    permission: notificationPermission,
    supported: notificationsSupported,
    requestPermission,
    startPeriodicCheck,
    stopPeriodicCheck,
  } = useNotifications({
    onPermissionGranted: () => {
      console.log("Notification permission granted");
    },
    onPermissionDenied: () => {
      console.log("Notification permission denied");
    },
  });

  const { toasts, removeToast, showTaskAlerts } = useToastNotifications();

  // Request notification permission on mount
  useEffect(() => {
    if (notificationsSupported && notificationPermission === "default") {
      requestPermission();
    }
  }, [notificationsSupported, notificationPermission, requestPermission]);

  // Update tasks when TaskList data changes
  // This is handled by the TaskList component internally

  // Start/stop periodic notification checks
  useEffect(() => {
    if (tasks.length > 0) {
      startPeriodicCheck(tasks);
    }

    return () => {
      stopPeriodicCheck();
    };
  }, [tasks, startPeriodicCheck, stopPeriodicCheck]);

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Toast notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`
              px-4 py-3 rounded-lg shadow-lg max-w-sm animate-slide-in
              ${
                toast.type === "error"
                  ? "bg-red-100 text-red-800 border border-red-200"
                  : toast.type === "warning"
                  ? "bg-yellow-100 text-yellow-800 border border-yellow-200"
                  : toast.type === "success"
                  ? "bg-green-100 text-green-800 border border-green-200"
                  : "bg-blue-100 text-blue-800 border border-blue-200"
              }
            `}
          >
            <div className="flex items-center justify-between gap-4">
              <span className="text-sm font-medium">{toast.message}</span>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Header */}
      <header className="bg-indigo-600 shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <h1 className="text-xl font-bold text-white">Todo</h1>
          </div>
          <div className="flex items-center gap-4">
            {/* Notification status indicator - only show when enabled */}
            {notificationPermission === "granted" && (
              <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                🔔 Notifications On
              </span>
            )}
            {/* User email with icon */}
            <div className="flex items-center gap-2 text-white">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span className="text-sm font-medium">{user?.email}</span>
            </div>
            <Button variant="outline" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Edit task form */}
        {editingTask && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-lg font-semibold mb-4">Edit Task</h2>
            <EditTaskForm
              task={editingTask}
              onSuccess={() => setEditingTask(null)}
              onCancel={() => setEditingTask(null)}
            />
          </div>
        )}

        {/* Actions */}
        <div className="mb-8">
          {showCreateForm ? (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Create New Task</h2>
              <CreateTaskForm
                onSuccess={() => setShowCreateForm(false)}
              />
              <Button
                variant="secondary"
                onClick={() => setShowCreateForm(false)}
                className="mt-4"
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button onClick={() => setShowCreateForm(true)}>
              + Add New Task
            </Button>
          )}
        </div>

        {/* Task list */}
        <TaskList onEditTask={setEditingTask} />
      </main>

      {/* ChatBot */}
      {user && (
        <ChatBot userId={user.id} onTasksUpdated={handleTasksUpdated} />
      )}

      {/* CSS for toast animations */}
      <style jsx global>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
