"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Task, TaskUpdate } from "@/types";
import TaskForm from "@/components/TaskForm";
import TaskList from "@/components/TaskList";
import SearchBar from "@/components/SearchBar";
import TaskFilters, { FilterState } from "@/components/TaskFilters";
import TaskSkeleton from "@/components/TaskSkeleton";
import { apiClient, authFetch } from "@/lib/api";
import { signOut } from "@/lib/auth-client";
import { LogOut, Settings, MessageSquare, BarChart3 } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
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
  const [isAuthChecked, setIsAuthChecked] = useState(false);

  // Client-side auth check for HuggingFace (cookies may not work)
  useEffect(() => {
    const checkAuth = () => {
      // Check localStorage for session (HuggingFace fallback)
      const storedSession = localStorage.getItem("better-auth-session");
      if (storedSession) {
        try {
          const session = JSON.parse(storedSession);
          // Check if session is less than 24 hours old
          if (session.timestamp && Date.now() - session.timestamp < 24 * 60 * 60 * 1000) {
            setIsAuthChecked(true);
            return;
          }
        } catch (e) {
          console.error("Failed to parse session:", e);
        }
      }

      // Check for cookie as well
      const hasCookie = document.cookie.includes("better-auth");
      if (hasCookie) {
        setIsAuthChecked(true);
        return;
      }

      // No valid session found, redirect to sign-in
      console.log("No valid session found, redirecting to sign-in");
      router.push("/auth/sign-in");
    };

    checkAuth();
  }, [router]);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);
  const [currentView, setCurrentView] = useState<'list' | 'grid' | 'calendar' | 'timeline'>('list');
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [filters, setFilters] = useState<FilterState>({
    status: "all",
    categoryId: null,
    priority: "all",
    dueDateFilter: "all",
    tagIds: [],
  });
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
   * Fetch all tasks for the current user with optional search and filters.
   * Wrapped in useCallback to prevent infinite loops
   */
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = new URLSearchParams();

      // Add search
      if (searchQuery) {
        params.append("search", searchQuery);
      }

      // Add filters
      if (filters.status !== "all") {
        params.append("is_completed", filters.status === "completed" ? "true" : "false");
      }
      if (filters.categoryId !== null) {
        params.append("category_id", filters.categoryId.toString());
      }
      if (filters.priority !== "all") {
        params.append("priority", filters.priority);
      }
      if (filters.dueDateFilter !== "all") {
        params.append("due_date_filter", filters.dueDateFilter);
      }
      if (filters.tagIds.length > 0) {
        filters.tagIds.forEach((tagId) => {
          params.append("tag_ids", tagId.toString());
        });
      }

      // Fetch from our Next.js API route
      const url = `/api/tasks${params.toString() ? `?${params.toString()}` : ""}`;
      const response = await authFetch(url);

      if (!response.ok) {
        // Handle different error statuses appropriately
        if (response.status === 401) {
          // Unauthorized - redirect to sign-in
          console.log("Unauthorized access, redirecting to sign-in");
          router.push("/auth/sign-in");
          return;
        } else if (response.status === 403) {
          // Forbidden - likely a session issue
          setError("Access forbidden. Please sign in again.");
          router.push("/auth/sign-in");
          return;
        } else if (response.status >= 500) {
          // Server error - likely database or backend issue
          throw new Error("Server error occurred. The backend may be experiencing issues.");
        } else {
          // Other client errors
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `Failed to fetch tasks (${response.status})`);
        }
      }

      const fetchedTasks: Task[] = await response.json();
      setTasks(fetchedTasks);
    } catch (err: any) {
      console.error("Error fetching tasks:", err);
      if (err.message.includes("Failed to fetch")) {
        setError("Unable to connect to the server. Please check your internet connection and try again.");
      } else if (err.message.includes("Server error")) {
        setError("Server is temporarily unavailable. Please try again later.");
      } else {
        setError(err.message || "An unexpected error occurred while fetching tasks.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, filters, router]); // Dependencies: only re-create when search or filters change

  /**
   * Fetch tasks on component mount and when search query or filters change.
   */
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  /**
   * Handle search query change.
   * Wrapped in useCallback to prevent infinite loops
   */
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  /**
   * Handle filter change.
   */
  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
  }, []);

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
    // Optimistic UI update
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, is_completed: isCompleted } : task
      )
    );

    try {
      const response = await authFetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_completed: isCompleted }),
      });

      if (!response.ok) {
        throw new Error("Failed to toggle task");
      }
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
    // Optimistic UI update
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, ...updates } : task
      )
    );

    try {
      const response = await authFetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error("Failed to update task");
      }
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
    // Optimistic UI update
    setTasks((prev) => prev.filter((task) => task.id !== taskId));

    try {
      const response = await authFetch(`/api/tasks/${taskId}`, {
        method: "DELETE",
      });

      if (!response.ok && response.status !== 204) {
        throw new Error("Failed to delete task");
      }
    } catch (err: any) {
      setError(err.message || "Failed to delete task");
      // Revert optimistic update
      fetchTasks();
    }
  };

  /**
   * Handle tag click - filter tasks by tag.
   */
  const handleTagClick = (tagId: number, tagName: string) => {
    // Toggle tag in filters
    const newTagIds = filters.tagIds.includes(tagId)
      ? filters.tagIds.filter((id) => id !== tagId)
      : [...filters.tagIds, tagId];

    setFilters({ ...filters, tagIds: newTagIds });
  };

  /**
   * Handle keyboard shortcuts.
   */
  useKeyboardShortcuts({
    onNewTask: () => {
      // Focus on task title input
      const titleInput = document.querySelector<HTMLInputElement>('input[id="title"]');
      if (titleInput) {
        titleInput.focus();
        titleInput.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    },
    onSearch: () => {
      // Focus on search input
      const searchInput = document.querySelector<HTMLInputElement>('input[type="search"]');
      if (searchInput) {
        searchInput.focus();
        searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    },
    onEscape: () => {
      // Close settings dropdown
      setShowSettings(false);
      // Blur active element
      if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur();
      }
    },
  });

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

  // Show loading while checking auth
  if (!isAuthChecked) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-purple-600 dark:text-purple-400 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

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
            {/* Statistics button */}
            <button
              onClick={() => router.push("/dashboard/statistics")}
              className="flex items-center gap-2 px-4 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="Statistics"
            >
              <BarChart3 size={20} className="text-blue-600 dark:text-blue-400 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-blue-600 to-green-600 dark:from-blue-400 dark:to-green-400 bg-clip-text text-transparent">
                {t.statistics || "Statistics"}
              </span>
            </button>

            {/* AI Chat button */}
            <button
              onClick={() => router.push("/chat")}
              className="flex items-center gap-2 px-4 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="AI Chat"
            >
              <MessageSquare size={20} className="text-purple-600 dark:text-purple-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">AI Chat</span>
            </button>

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
            <div className="flex gap-4 mt-2">
              <button
                onClick={() => {
                  setError(null);
                  fetchTasks(); // Retry fetching tasks
                }}
                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm"
              >
                Retry
              </button>
              <button
                onClick={() => setError(null)}
                className="underline text-sm"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Task Form - always rendered to prevent remounting */}
        <TaskForm onTaskAdded={handleTaskAdded} />

        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} />

        {/* Search Results Count */}
        {searchQuery && !isLoading && (
          <div className="text-sm text-zinc-600 dark:text-zinc-400 fade-in">
            {tasks.length > 0
              ? `Found ${tasks.length} task(s) matching "${searchQuery}"`
              : `No tasks found matching "${searchQuery}"`}
          </div>
        )}

        {/* Filters and Task List */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar - always rendered to prevent remounting */}
          <div className="lg:col-span-1">
            <TaskFilters
              onFilterChange={handleFilterChange}
              className="sticky top-6"
            />
          </div>

          {/* Main Task List */}
          <div className="lg:col-span-3 space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 text-fade-up">
                {t.yourTasks}
              </h2>
              <ViewToggleButton
                currentView={currentView}
                onChangeView={setCurrentView}
              />
            </div>

            {/* Show skeleton while loading tasks, then show task list */}
            {isLoading ? (
              <TaskSkeleton count={5} />
            ) : (
              <TaskList
                tasks={tasks}
                onToggle={handleTaskToggle}
                onUpdate={handleTaskUpdate}
                onDelete={handleTaskDelete}
                onTagClick={handleTagClick}
                className="fade-in"
                viewMode={currentView === 'grid' ? 'grid' : 'list'}
                searchQuery={searchQuery}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
