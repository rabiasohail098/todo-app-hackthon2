"use client";

import React, { useState, useEffect, useRef } from "react";
import CategoryBadge from "./CategoryBadge";
import PriorityIndicator, { Priority } from "./PriorityIndicator";

interface Category {
  id: number;
  name: string;
  color: string;
  icon?: string;
}

interface Tag {
  id: number;
  name: string;
}

interface TaskFiltersProps {
  onFilterChange: (filters: FilterState) => void;
  className?: string;
}

export interface FilterState {
  status: "all" | "completed" | "incomplete";
  categoryId: number | null;
  priority: Priority | "all";
  dueDateFilter:
    | "all"
    | "today"
    | "this_week"
    | "overdue"
    | "has_due_date"
    | "no_due_date";
  tagIds: number[];
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  onFilterChange,
  className = "",
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    status: "all",
    categoryId: null,
    priority: "all",
    dueDateFilter: "all",
    tagIds: [],
  });

  // Ref to track if it's the initial mount to prevent double firing
  const isMounted = useRef(false);

  // Fetch categories and tags on mount only
  // Empty dependency array [] ensures this runs only once on component mount (FR-007)
  // Adding fetchData to dependencies would cause infinite loop since it's recreated on every render
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch both categories and tags in parallel
      const [categoriesRes, tagsRes] = await Promise.all([
        fetch("/api/categories"),
        fetch("/api/tags")
      ]);

      // Handle categories response
      if (!categoriesRes.ok) {
        if (categoriesRes.status === 503) {
          throw new Error("The service is temporarily unavailable. Please try again in a few minutes.");
        } else if (categoriesRes.status === 401) {
          throw new Error("Please sign in to continue.");
        } else {
          throw new Error("Unable to load filters. Please try again later.");
        }
      }

      // Handle tags response
      if (!tagsRes.ok) {
        if (tagsRes.status === 503) {
          throw new Error("The service is temporarily unavailable. Please try again in a few minutes.");
        } else if (tagsRes.status === 401) {
          throw new Error("Please sign in to continue.");
        } else {
          throw new Error("Unable to load filters. Please try again later.");
        }
      }

      const categoriesData = await categoriesRes.json();
      const tagsData = await tagsRes.json();

      setCategories(categoriesData);
      setTags(tagsData);
      setError(null);
    } catch (error) {
      console.error("Failed to fetch filters:", error);

      // User-friendly error messages
      if (error instanceof Error) {
        if (error.message.includes('fetch failed') || error.message.includes('Failed to fetch') || error.message.includes('Network request failed')) {
          setError("Unable to connect to server. Please check your connection.");
        } else {
          setError(error.message);
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }

      // Empty array fallbacks (FR-004)
      setCategories([]);
      setTags([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Notify parent when filters change
  // FIX: Removed 'onFilterChange' from dependency array to prevent infinite loop
  // FIX: Skip the very first run to avoid initial double-fetch that causes infinite reload
  useEffect(() => {
    // Skip initial mount - only call onFilterChange when user actually changes filters
    if (!isMounted.current) {
      isMounted.current = true;
      return;
    }
    onFilterChange(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const handleStatusChange = (status: "all" | "completed" | "incomplete") => {
    setFilters({ ...filters, status });
  };

  const handleCategoryChange = (categoryId: number | null) => {
    setFilters({ ...filters, categoryId });
  };

  const handlePriorityChange = (priority: Priority | "all") => {
    setFilters({ ...filters, priority });
  };

  const handleDueDateFilterChange = (
    dueDateFilter:
      | "all"
      | "today"
      | "this_week"
      | "overdue"
      | "has_due_date"
      | "no_due_date",
  ) => {
    setFilters({ ...filters, dueDateFilter });
  };

  const handleTagToggle = (tagId: number) => {
    const newTagIds = filters.tagIds.includes(tagId)
      ? filters.tagIds.filter((id) => id !== tagId)
      : [...filters.tagIds, tagId];
    setFilters({ ...filters, tagIds: newTagIds });
  };

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${className}`}
    >
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        Filters
      </h3>

      {/* Error state with retry button */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-300 mb-2">{error}</p>
          <button
            type="button"
            onClick={fetchData}
            disabled={isLoading}
            className="px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Retrying..." : "Retry"}
          </button>
        </div>
      )}

      {/* Loading state indicator */}
      {isLoading && !error && (
        <div className="mb-4 text-sm text-purple-600 dark:text-purple-400">
          Loading filters...
        </div>
      )}

      {/* Status Filter */}
      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Status
        </label>
        <div className="flex gap-2">
          <button
            onClick={() => handleStatusChange("all")}
            className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.status === "all"
                ? "bg-purple-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            All
          </button>
          <button
            onClick={() => handleStatusChange("incomplete")}
            className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.status === "incomplete"
                ? "bg-purple-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            Active
          </button>
          <button
            onClick={() => handleStatusChange("completed")}
            className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.status === "completed"
                ? "bg-purple-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
            }`}
          >
            Done
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Category
        </label>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {/* All categories option */}
          <button
            onClick={() => handleCategoryChange(null)}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.categoryId === null
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            All Categories
          </button>

          {/* Individual category options */}
          {categories.length === 0 ? (
            <p className="text-xs text-gray-500 dark:text-gray-400 px-3 py-2">
              No categories yet
            </p>
          ) : (
            categories.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryChange(category.id)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  filters.categoryId === category.id
                    ? "bg-purple-100 dark:bg-purple-900/30"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <CategoryBadge category={category} size="sm" />
              </button>
            ))
          )}
        </div>

        {categories.length > 0 && (
          <a
            href="/categories"
            className="block mt-3 text-xs text-purple-600 dark:text-purple-400 hover:underline"
          >
            Manage Categories →
          </a>
        )}
      </div>

      {/* Priority Filter */}
      <div className="mt-4">
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Priority
        </label>
        <div className="space-y-2">
          {/* All priorities option */}
          <button
            onClick={() => handlePriorityChange("all")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.priority === "all"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            All Priorities
          </button>

          {/* Individual priority options */}
          {(["critical", "high", "medium", "low"] as Priority[]).map(
            (priority) => (
              <button
                key={priority}
                onClick={() => handlePriorityChange(priority)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  filters.priority === priority
                    ? "bg-purple-100 dark:bg-purple-900/30"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                }`}
              >
                <PriorityIndicator priority={priority} size="sm" />
              </button>
            ),
          )}
        </div>
      </div>

      {/* Due Date Filter */}
      <div className="mt-4">
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Due Date
        </label>
        <div className="space-y-2">
          {/* All dates option */}
          <button
            onClick={() => handleDueDateFilterChange("all")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "all"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            All Dates
          </button>

          {/* Individual date filter options */}
          <button
            onClick={() => handleDueDateFilterChange("today")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "today"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            📅 Due Today
          </button>

          <button
            onClick={() => handleDueDateFilterChange("this_week")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "this_week"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            📅 Due This Week
          </button>

          <button
            onClick={() => handleDueDateFilterChange("overdue")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "overdue"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            ⚠️ Overdue
          </button>

          <button
            onClick={() => handleDueDateFilterChange("has_due_date")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "has_due_date"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            📅 Has Due Date
          </button>

          <button
            onClick={() => handleDueDateFilterChange("no_due_date")}
            className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
              filters.dueDateFilter === "no_due_date"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
            }`}
          >
            ⭕ No Due Date
          </button>
        </div>
      </div>

      {/* Tags Filter */}
      <div className="mt-4">
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
          Tags
        </label>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {tags.length === 0 ? (
            <p className="text-xs text-gray-500 dark:text-gray-400 px-3 py-2">
              No tags yet
            </p>
          ) : (
            tags.map((tag) => (
              <button
                key={tag.id}
                onClick={() => handleTagToggle(tag.id)}
                className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 ${
                  filters.tagIds.includes(tag.id)
                    ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                }`}
              >
                <span className="text-purple-600 dark:text-purple-400">#</span>
                {tag.name}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Clear Filters */}
      {(filters.status !== "all" ||
        filters.categoryId !== null ||
        filters.priority !== "all" ||
        filters.dueDateFilter !== "all" ||
        filters.tagIds.length > 0) && (
        <button
          onClick={() =>
            setFilters({
              status: "all",
              categoryId: null,
              priority: "all",
              dueDateFilter: "all",
              tagIds: [],
            })
          }
          className="w-full mt-4 px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
};

export default TaskFilters;
