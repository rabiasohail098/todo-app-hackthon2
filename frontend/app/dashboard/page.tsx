"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Task, TaskUpdate } from "@/types";
import TaskForm from "@/components/TaskForm";
import TaskList from "@/components/TaskList";
import { apiClient } from "@/lib/api";
import { signOut } from "@/lib/auth-client";
import { LogOut, Settings } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";
import ThemeToggle from "@/components/ThemeToggle";
import LanguageToggle from "@/components/LanguageToggle";
import BackgroundToggle from "@/components/BackgroundToggle";
import ViewToggleButton from "@/components/ViewToggleButton";

/**
 * Dashboard page - main task management interface.
 *
 * Displays task creation form and task list.
 * Protected route - requires authentication.
 */
export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);
  const [currentView, setCurrentView] = useState<'list' | 'grid' | 'calendar' | 'timeline'>('list');
  const { backgroundMode } = useApp();
  const t = useTranslation();

  // Update body class based on background mode
  useEffect(() => {
    // Remove all background classes first
    document.body.classList.remove('with-background', 'with-background-image');

    // Add appropriate class based on mode
    if (backgroundMode === 'gradient') {
      document.body.classList.add('with-background');
    } else if (backgroundMode === 'image') {
      document.body.classList.add('with-background-image');
    }
  }, [backgroundMode]);

  // Close settings when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setShowSettings(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  /**
   * Fetch tasks on component mount.
   */
  useEffect(() => {
    fetchTasks();
  }, []);

  /**
   * Fetch all tasks for the current user.
   */
  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual API call when backend is ready
      // const fetchedTasks = await apiClient.get<Task[]>("/api/tasks");

      // Mock data for now
      await new Promise((resolve) => setTimeout(resolve, 500));
      const mockTasks: Task[] = [
        {
          id: 1,
          user_id: "mock-user-id",
          title: "Complete project documentation",
          description: "Write README and API docs",
          is_completed: false,
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
        {
          id: 2,
          user_id: "mock-user-id",
          title: "Review pull requests",
          description: null,
          is_completed: true,
          created_at: new Date(Date.now() - 172800000).toISOString(),
        },
      ];

      setTasks(mockTasks);
    } catch (err: any) {
      setError(err.message || "Failed to fetch tasks");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle task added.
   */
  const handleTaskAdded = (newTask: Task) => {
    setTasks((prev) => [newTask, ...prev]);
  };

  /**
   * Handle task toggle.
   */
  const handleTaskToggle = async (taskId: number, isCompleted: boolean) => {
    try {
      // TODO: Replace with actual API call
      // await apiClient.patch(`/api/tasks/${taskId}`, { is_completed: isCompleted });

      // Optimistic UI update
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId ? { ...task, is_completed: isCompleted } : task
        )
      );
    } catch (err: any) {
      setError(err.message || "Failed to toggle task");
      // Revert optimistic update
      fetchTasks();
    }
  };

  /**
   * Handle task update.
   */
  const handleTaskUpdate = async (taskId: number, updates: TaskUpdate) => {
    try {
      // TODO: Replace with actual API call
      // await apiClient.patch(`/api/tasks/${taskId}`, updates);

      // Optimistic UI update
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId ? { ...task, ...updates } : task
        )
      );
    } catch (err: any) {
      setError(err.message || "Failed to update task");
      // Revert optimistic update
      fetchTasks();
    }
  };

  /**
   * Handle task delete.
   */
  const handleTaskDelete = async (taskId: number) => {
    try {
      // TODO: Replace with actual API call
      // await apiClient.delete(`/api/tasks/${taskId}`);

      // Optimistic UI update
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err: any) {
      setError(err.message || "Failed to delete task");
      // Revert optimistic update
      fetchTasks();
    }
  };

  /**
   * Handle user logout.
   */
  const handleLogout = async () => {
    try {
      // Call Better Auth sign-out
      await signOut();

      // Redirect to landing page
      router.push("/");
    } catch (error: any) {
      setError(error.message || "Failed to log out");
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-300">
      <div className="max-w-5xl mx-auto p-6 space-y-8 fade-in">
        {/* Header */}
        <header className="flex flex-col sm:flex-row justify-between items-center py-8 gap-6 glass-strong rounded-3xl px-8">
          <div className="text-center sm:text-left">
            <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent heading-animate" style={{textShadow: '0 0 40px rgba(167, 139, 250, 0.3)'}}>
              {t.myTasks}
            </h1>
            <p className="mt-3 text-lg font-medium bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent text-fade-up text-fade-up-delay-1">
              {t.manageTasksEfficiently}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Settings dropdown */}
            <div className="relative" ref={settingsRef}>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-3 rounded-xl glass hover:glass-strong transition-all transform hover:scale-110 hover:rotate-90 duration-300 group"
                aria-label="Settings"
              >
                <Settings size={22} className="text-purple-600 dark:text-purple-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors" />
              </button>

              {showSettings && (
                <div className="absolute right-0 mt-3 w-64 glass-strong rounded-2xl p-4 z-10 fade-in border border-purple-300/20">
                  <div className="space-y-3">
                    <ThemeToggle />
                    <LanguageToggle />
                    <BackgroundToggle />
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-5 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="Log out"
            >
              <LogOut size={20} className="text-red-500 dark:text-red-400 group-hover:rotate-12 transition-transform" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">{t.logOut}</span>
            </button>
          </div>
        </header>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg fade-in">
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 underline text-sm"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Task Form */}
        <TaskForm onTaskAdded={handleTaskAdded} />

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12 fade-in">
            <p className="text-zinc-500 dark:text-zinc-400">{t.loadingTasks}</p>
          </div>
        )}

        {/* View Toggle and Task List */}
        {!isLoading && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 text-fade-up">
                {t.yourTasks}
              </h2>
              <ViewToggleButton
                currentView={currentView}
                onChangeView={setCurrentView}
              />
            </div>

            <TaskList
              tasks={tasks}
              onToggle={handleTaskToggle}
              onUpdate={handleTaskUpdate}
              onDelete={handleTaskDelete}
              className="fade-in"
              viewMode={currentView === 'grid' ? 'grid' : 'list'}
            />
          </div>
        )}
      </div>
    </div>
  );
}
