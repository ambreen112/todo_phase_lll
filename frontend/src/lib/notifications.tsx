// Browser notifications hook for task reminders.

"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import type { Task } from "@/types";

interface UseNotificationsOptions {
  onPermissionGranted?: () => void;
  onPermissionDenied?: () => void;
  checkIntervalMs?: number;
}

interface NotificationState {
  permission: NotificationPermission;
  supported: boolean;
  requested: boolean;
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { onPermissionGranted, onPermissionDenied, checkIntervalMs = 60000 } = options;
  const [state, setState] = useState<NotificationState>({
    permission: "default",
    supported: false,
    requested: false,
  });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastNotifiedRef = useRef<Set<string>>(new Set());

  // Check if notifications are supported and get current permission
  useEffect(() => {
    const supported = "Notification" in window;
    const permission = supported ? Notification.permission : "denied";
    setState({ permission, supported, requested: false });
  }, []);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    if (!("Notification" in window)) {
      return "denied";
    }

    try {
      const permission = await Notification.requestPermission();
      setState((prev) => ({ ...prev, permission, requested: true }));

      if (permission === "granted") {
        onPermissionGranted?.();
      } else {
        onPermissionDenied?.();
      }

      return permission;
    } catch (error) {
      console.error("Failed to request notification permission:", error);
      return "denied";
    }
  }, [onPermissionGranted, onPermissionDenied]);

  // Show a notification
  const showNotification = useCallback(
    (title: string, options?: NotificationOptions) => {
      if (state.permission !== "granted") {
        return null;
      }

      try {
        const notification = new Notification(title, {
          icon: "/favicon.ico",
          badge: "/favicon.ico",
          ...options,
        });

        // Auto-close after 5 seconds
        setTimeout(() => notification.close(), 5000);

        return notification;
      } catch (error) {
        console.error("Failed to show notification:", error);
        return null;
      }
    },
    [state.permission]
  );

  // Check tasks and send notifications for due/overdue tasks
  const notifyDueTasks = useCallback(
    (tasks: Task[]) => {
      if (state.permission !== "granted") return;

      const now = new Date();
      const dueTasks = tasks.filter(
        (task) =>
          !task.completed &&
          !task.deleted_at &&
          task.due_date &&
          (task.is_overdue || task.is_due_today) &&
          !lastNotifiedRef.current.has(task.id)
      );

      if (dueTasks.length === 0) return;

      // Build notification message
      const overdueCount = dueTasks.filter((t) => t.is_overdue).length;
      const dueTodayCount = dueTasks.filter((t) => t.is_due_today).length;

      let title = "";
      let body = "";
      let tag = "";

      if (overdueCount > 0 && dueTodayCount > 0) {
        title = "Tasks Alert";
        body = `${overdueCount} overdue, ${dueTodayCount} due today`;
      } else if (overdueCount > 0) {
        title = "Overdue Tasks";
        body = overdueCount === 1
          ? `1 task is overdue: ${dueTasks[0].title}`
          : `${overdueCount} tasks are overdue`;
      } else if (dueTodayCount > 0) {
        title = "Tasks Due Today";
        body = dueTodayCount === 1
          ? `1 task due today: ${dueTasks[0].title}`
          : `${dueTodayCount} tasks due today`;
      }

      if (title) {
        tag = `tasks-${now.toISOString().split("T")[0]}`;

        // Check if we've already notified for this tag/time
        if (!lastNotifiedRef.current.has(tag)) {
          showNotification(title, {
            body,
            tag,
            requireInteraction: overdueCount > 0,
          });

          // Mark as notified (will be cleared on next day)
          lastNotifiedRef.current.add(tag);
        }
      }
    },
    [state.permission, showNotification]
  );

  // Clear old notification tracking (call this daily)
  const clearOldNotifications = useCallback(() => {
    const today = new Date().toISOString().split("T")[0];
    const keysToRemove: string[] = [];

    lastNotifiedRef.current.forEach((key) => {
      if (key.includes(today)) {
        keysToRemove.push(key);
      }
    });

    keysToRemove.forEach((key) => lastNotifiedRef.current.delete(key));
  }, []);

  // Set up periodic checking
  const startPeriodicCheck = useCallback(
    (tasks: Task[]) => {
      // Clear old notifications first
      clearOldNotifications();

      // Initial check
      notifyDueTasks(tasks);

      // Set up interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }

      intervalRef.current = setInterval(() => {
        notifyDueTasks(tasks);
      }, checkIntervalMs);
    },
    [checkIntervalMs, notifyDueTasks, clearOldNotifications]
  );

  // Stop periodic checking
  const stopPeriodicCheck = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPeriodicCheck();
    };
  }, [stopPeriodicCheck]);

  return {
    ...state,
    requestPermission,
    showNotification,
    notifyDueTasks,
    startPeriodicCheck,
    stopPeriodicCheck,
    clearOldNotifications,
  };
}

// Hook for in-app toast notifications (for when browser notifications aren't available)
export function useToastNotifications() {
  const [toasts, setToasts] = useState<
    Array<{ id: string; message: string; type: "info" | "warning" | "success" | "error" }>
  >([]);
  const timeoutRef = useRef<Record<string, NodeJS.Timeout>>({});

  const addToast = useCallback(
    (
      message: string,
      type: "info" | "warning" | "success" | "error" = "info",
      durationMs = 5000
    ) => {
      const id = Math.random().toString(36).substring(2, 9);

      setToasts((prev) => [...prev, { id, message, type }]);

      // Auto-remove toast
      if (timeoutRef.current[id]) {
        clearTimeout(timeoutRef.current[id]);
      }

      timeoutRef.current[id] = setTimeout(() => {
        removeToast(id);
      }, durationMs);

      return id;
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
    if (timeoutRef.current[id]) {
      clearTimeout(timeoutRef.current[id]);
      delete timeoutRef.current[id];
    }
  }, []);

  const showTaskAlerts = useCallback(
    (overdueCount: number, dueTodayCount: number) => {
      if (overdueCount > 0) {
        addToast(
          `${overdueCount} overdue task${overdueCount !== 1 ? "s" : ""}`,
          "error",
          8000
        );
      }
      if (dueTodayCount > 0) {
        addToast(
          `${dueTodayCount} due today`,
          "warning",
          8000
        );
      }
    },
    [addToast]
  );

  return {
    toasts,
    addToast,
    removeToast,
    showTaskAlerts,
  };
}
