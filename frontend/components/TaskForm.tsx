"use client";

import { useState, useEffect } from "react";
import { Task, TaskCreate, FormError } from "@/types";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";
import CategoryBadge from "./CategoryBadge";
import PriorityIndicator, { Priority } from "./PriorityIndicator";
import TagInput from "./TagInput";
import RecurrenceSelector from "./RecurrenceSelector";

type RecurrencePattern = "daily" | "weekly" | "monthly" | null;

interface Category {
  id: number;
  name: string;
  color: string;
  icon?: string;
}

interface Tag {
  id?: number;
  name: string;
}

interface TaskFormProps {
  onTaskAdded: (task: Task) => void;
}

/**
 * Task creation form component.
 *
 * Allows users to create new tasks with title and optional description.
 */
export default function TaskForm({ onTaskAdded }: TaskFormProps) {
  const [formData, setFormData] = useState<TaskCreate>({
    title: "",
    description: "",
  });
  const [errors, setErrors] = useState<FormError[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isFetchingCategories, setIsFetchingCategories] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(
    null,
  );
  const [selectedPriority, setSelectedPriority] = useState<Priority>("medium");
  const [selectedDueDate, setSelectedDueDate] = useState<string>("");
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [selectedRecurrence, setSelectedRecurrence] =
    useState<RecurrencePattern>(null);
  const { language } = useApp();
  const t = useTranslation();

  // Fetch categories on mount only
  // Empty dependency array [] ensures this runs only once on component mount (FR-008)
  // Adding fetchCategories to dependencies would cause infinite loop since it's recreated on every render
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setIsFetchingCategories(true);
    setFetchError(null);

    try {
      const response = await fetch("/api/categories");

      if (!response.ok) {
        // Map HTTP errors to user-friendly messages
        if (response.status === 503) {
          throw new Error("The service is temporarily unavailable. Please try again in a few minutes.");
        } else if (response.status === 401) {
          throw new Error("Please sign in to continue.");
        } else if (response.status === 404) {
          throw new Error("Categories not found.");
        } else {
          throw new Error("Unable to load categories. Please try again later.");
        }
      }

      const data = await response.json();
      setCategories(data);
      setFetchError(null);
    } catch (error) {
      console.error("Failed to fetch categories:", error);

      // User-friendly error messages
      if (error instanceof Error) {
        if (error.message.includes('fetch failed') || error.message.includes('Failed to fetch') || error.message.includes('Network request failed')) {
          setFetchError("Unable to connect to server. Please check your connection.");
        } else {
          setFetchError(error.message);
        }
      } else {
        setFetchError("An unexpected error occurred. Please try again.");
      }

      // Empty array fallback (FR-004)
      setCategories([]);
    } finally {
      setIsFetchingCategories(false);
    }
  };

  /**
   * Validate form data.
   */
  const validateForm = (): boolean => {
    const newErrors: FormError[] = [];

    // Title validation
    if (!formData.title.trim()) {
      newErrors.push({ field: "title", message: t.titleRequired });
    } else if (formData.title.length > 200) {
      newErrors.push({
        field: "title",
        message: t.titleLimit,
      });
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    // Validate
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call the API to create the task
      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description || undefined,
          category_id: selectedCategoryId || undefined,
          priority: selectedPriority,
          due_date: selectedDueDate || undefined,
          tags: selectedTags.map((tag) => tag.name),
          recurrence_pattern: selectedRecurrence || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create task");
      }

      const newTask: Task = await response.json();
      onTaskAdded(newTask);

      // Clear form
      setFormData({ title: "", description: "" });
      setSelectedCategoryId(null);
      setSelectedPriority("medium");
      setSelectedDueDate("");
      setSelectedTags([]);
      setSelectedRecurrence(null);
    } catch (error: any) {
      setErrors([
        {
          field: "general",
          message: error.message || t.failedCreate,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const getFieldError = (field: string) =>
    errors.find((err) => err.field === field)?.message;

  return (
    <div className="glass-strong rounded-2xl p-6 card-3d">
      <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent mb-4 text-fade-up">
        {t.addNewTask}
      </h2>

      {getFieldError("general") && (
        <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg fade-in">
          {getFieldError("general")}
        </div>
      )}

      {/* Category fetch error state with retry button */}
      {fetchError && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-300 mb-2">{fetchError}</p>
          <button
            type="button"
            onClick={fetchCategories}
            disabled={isFetchingCategories}
            className="px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isFetchingCategories ? (language === "ur" ? "دوبارہ کوشش..." : "Retrying...") : (language === "ur" ? "دوبارہ کوشش کریں" : "Retry")}
          </button>
        </div>
      )}

      {/* Loading state for categories */}
      {isFetchingCategories && !fetchError && (
        <div className="mb-4 text-sm text-purple-600 dark:text-purple-400">
          {language === "ur" ? "کیٹیگریز لوڈ ہو رہی ہیں..." : "Loading categories..."}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Input */}
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1"
          >
            {t.title} <span className="text-red-500">({t.required})</span>
          </label>
          <input
            id="title"
            type="text"
            value={formData.title}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all ${
              getFieldError("title")
                ? "border-red-500"
                : "border-zinc-300 dark:border-zinc-700"
            }`}
            placeholder={
              language === "ur" ? "دودھ، انڈے، روٹی" : "Buy groceries"
            }
            disabled={isLoading}
            maxLength={200}
          />
          {getFieldError("title") && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              {getFieldError("title")}
            </p>
          )}
        </div>

        {/* Description Input */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1"
          >
            {t.description}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>
          <textarea
            id="description"
            value={formData.description || ""}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all"
            placeholder={
              language === "ur" ? "دودھ، انڈے، روٹی" : "Milk, eggs, bread..."
            }
            rows={3}
            disabled={isLoading}
          />
        </div>

        {/* Category Selector */}
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            {language === "ur" ? "کیٹیگری" : "Category"}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>

          {/* Dropdown Select with Create New button */}
          <div className="flex gap-2">
            <select
              id="category"
              value={selectedCategoryId ?? ""}
              onChange={(e) => {
                const value = e.target.value;
                setSelectedCategoryId(value ? Number(value) : null);
              }}
              className="flex-1 px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all"
              disabled={isLoading}
            >
              <option value="">
                {language === "ur" ? "کیٹیگری منتخب کریں" : "Select Category"}
              </option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.icon ? `${category.icon} ` : ""}{category.name}
                </option>
              ))}
            </select>
            <a
              href="/categories"
              className="px-3 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors text-sm font-medium whitespace-nowrap flex items-center gap-1"
            >
              ➕ {language === "ur" ? "نئی" : "New"}
            </a>
          </div>

          {/* Selected category badge preview */}
          {selectedCategoryId && categories.find(c => c.id === selectedCategoryId) && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-zinc-500 dark:text-zinc-400">
                {language === "ur" ? "منتخب:" : "Selected:"}
              </span>
              <CategoryBadge
                category={categories.find(c => c.id === selectedCategoryId)!}
                size="sm"
              />
              <button
                type="button"
                onClick={() => setSelectedCategoryId(null)}
                className="text-xs text-red-500 hover:text-red-600 dark:text-red-400"
              >
                {language === "ur" ? "ہٹائیں" : "Remove"}
              </button>
            </div>
          )}
        </div>

        {/* Priority Selector */}
        <div>
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            {language === "ur" ? "ترجیح" : "Priority"}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {(["critical", "high", "medium", "low"] as Priority[]).map(
              (priority) => (
                <button
                  key={priority}
                  type="button"
                  onClick={() => setSelectedPriority(priority)}
                  className={`transition-all ${
                    selectedPriority === priority
                      ? "ring-2 ring-purple-500 ring-offset-2 dark:ring-offset-zinc-800"
                      : "opacity-70 hover:opacity-100"
                  }`}
                  disabled={isLoading}
                >
                  <PriorityIndicator priority={priority} size="sm" />
                </button>
              ),
            )}
          </div>
        </div>

        {/* Due Date Picker */}
        <div>
          <label
            htmlFor="due-date"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            {language === "ur" ? "آخری تاریخ" : "Due Date"}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>
          <div className="flex gap-2">
            <input
              id="due-date"
              type="date"
              value={selectedDueDate}
              onChange={(e) => setSelectedDueDate(e.target.value)}
              className="flex-1 px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all"
              disabled={isLoading}
            />
            {selectedDueDate && (
              <button
                type="button"
                onClick={() => setSelectedDueDate("")}
                className="px-3 py-2 text-sm text-zinc-600 dark:text-zinc-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                disabled={isLoading}
              >
                {language === "ur" ? "صاف کریں" : "Clear"}
              </button>
            )}
          </div>
          {/* Quick date buttons */}
          <div className="flex flex-wrap gap-2 mt-2">
            <button
              type="button"
              onClick={() => {
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                setSelectedDueDate(tomorrow.toISOString().split("T")[0]);
              }}
              className="px-3 py-1 text-xs bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-200 dark:hover:bg-zinc-600 transition-colors"
              disabled={isLoading}
            >
              {language === "ur" ? "کل" : "Tomorrow"}
            </button>
            <button
              type="button"
              onClick={() => {
                const nextWeek = new Date();
                nextWeek.setDate(nextWeek.getDate() + 7);
                setSelectedDueDate(nextWeek.toISOString().split("T")[0]);
              }}
              className="px-3 py-1 text-xs bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg hover:bg-zinc-200 dark:hover:bg-zinc-600 transition-colors"
              disabled={isLoading}
            >
              {language === "ur" ? "اگلا ہفتہ" : "Next Week"}
            </button>
          </div>
        </div>

        {/* Recurrence Selector */}
        <div>
          <label
            htmlFor="recurrence"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            {language === "ur" ? "بار بار" : "Recurrence"}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>
          <RecurrenceSelector
            value={selectedRecurrence}
            onChange={setSelectedRecurrence}
            className="w-full"
          />
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            {language === "ur"
              ? "بار بار ہونے والے کاموں کے لیے ایک پیٹرن منتخب کریں"
              : "Select a pattern for recurring tasks"}
          </p>
        </div>

        {/* Tags Input */}
        <div>
          <label
            htmlFor="tags"
            className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2"
          >
            {language === "ur" ? "ٹیگز" : "Tags"}{" "}
            <span className="text-zinc-400">({t.optional})</span>
          </label>
          <TagInput
            value={selectedTags}
            onChange={setSelectedTags}
            placeholder={language === "ur" ? "#urgent #work" : "#urgent #work"}
            className="w-full"
          />
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            {language === "ur"
              ? "ٹیگ شامل کرنے کے لیے ٹائپ کریں اور Enter دبائیں یا تجویز کردہ میں سے منتخب کریں"
              : "Type to add tags and press Enter or select from suggestions"}
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
        >
          <span className="relative z-10">
            {isLoading ? t.adding : t.addTask}
          </span>
          <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
        </button>
      </form>
    </div>
  );
}
