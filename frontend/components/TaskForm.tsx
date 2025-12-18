"use client";

import { useState } from "react";
import { Task, TaskCreate, FormError } from "@/types";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";

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
  const { language } = useApp();
  const t = useTranslation();

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
            placeholder={language === 'ur' ? "دودھ، انڈے، روٹی" : "Buy groceries"}
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
            {t.description} <span className="text-zinc-400">({t.optional})</span>
          </label>
          <textarea
            id="description"
            value={formData.description || ""}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all"
            placeholder={language === 'ur' ? "دودھ، انڈے، روٹی" : "Milk, eggs, bread..."}
            rows={3}
            disabled={isLoading}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
        >
          <span className="relative z-10">{isLoading ? t.adding : t.addTask}</span>
          <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
        </button>
      </form>
    </div>
  );
}
