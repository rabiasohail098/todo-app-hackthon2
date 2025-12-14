"use client";

import { useState, useEffect } from "react";
import { Task, TaskUpdate } from "@/types";
import { Check, X, Edit3, Trash2, Save } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: number, isCompleted: boolean) => void;
  onUpdate: (taskId: number, updates: TaskUpdate) => void;
  onDelete: (taskId: number) => void;
  className?: string;
}

/**
 * Individual task item component.
 *
 * Displays a task with toggle, edit, and delete functionality.
 */
export default function TaskItem({
  task,
  onToggle,
  onUpdate,
  onDelete,
  className = ""
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<TaskUpdate>({
    title: task.title,
    description: task.description || "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const { language } = useApp();
  const t = useTranslation();

  // Task animation effect
  useEffect(() => {
    const element = document.querySelector(`[data-task-id="${task.id}"]`);
    if (element) {
      element.classList.add('task-item-enter');
    }
  }, [task.id]);

  /**
   * Handle toggle completion.
   */
  const handleToggle = async () => {
    setIsLoading(true);
    try {
      await onToggle(task.id, !task.is_completed);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle save edit.
   */
  const handleSaveEdit = async () => {
    if (!editData.title?.trim()) {
      return;
    }

    setIsLoading(true);
    try {
      await onUpdate(task.id, editData);
      setIsEditing(false);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle cancel edit.
   */
  const handleCancelEdit = () => {
    setEditData({
      title: task.title,
      description: task.description || "",
    });
    setIsEditing(false);
  };

  /**
   * Handle delete task.
   */
  const handleDelete = async () => {
    if (!confirm(t.confirmDelete)) {
      return;
    }

    setIsLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsLoading(false);
    }
  };

  // Format creation date based on language
  const createdDate = new Date(task.created_at).toLocaleDateString(
    language === 'ur' ? 'ur-PK' : 'en-US'
  );

  // Edit mode
  if (isEditing) {
    return (
      <div
        data-task-id={task.id}
        className={`p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700 animate-pulse ${className}`}
      >
        <div className="space-y-3">
          <input
            type="text"
            value={editData.title}
            onChange={(e) =>
              setEditData({ ...editData, title: e.target.value })
            }
            className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:text-zinc-100"
            placeholder={language === 'ur' ? "کام کا عنوان" : "Task title"}
            maxLength={200}
            disabled={isLoading}
          />
          <textarea
            value={editData.description || ""}
            onChange={(e) =>
              setEditData({ ...editData, description: e.target.value })
            }
            className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded focus:ring-2 focus:ring-blue-500 dark:bg-zinc-700 dark:text-zinc-100"
            placeholder={language === 'ur' ? "کام کی تفصیل (اختیاری)" : "Task description (optional)"}
            rows={2}
            disabled={isLoading}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSaveEdit}
              disabled={isLoading || !editData.title?.trim()}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors disabled:bg-zinc-400 disabled:cursor-not-allowed"
            >
              <Save size={16} />
              {t.save}
            </button>
            <button
              onClick={handleCancelEdit}
              disabled={isLoading}
              className="flex items-center gap-1 px-3 py-1.5 bg-zinc-500 hover:bg-zinc-600 text-white text-sm rounded transition-colors"
            >
              <X size={16} />
              {t.cancel}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Display mode
  return (
    <div
      data-task-id={task.id}
      className={`p-5 glass rounded-2xl transition-all duration-500 transform hover:scale-105 ${
        task.is_completed
          ? "border-2 border-green-400/30 shadow-lg shadow-green-500/20"
          : "border border-purple-300/20 hover:shadow-xl hover:shadow-purple-500/30"
      } ${className}`}
      style={{
        boxShadow: task.is_completed
          ? '0 8px 32px rgba(34, 197, 94, 0.2)'
          : '0 8px 32px rgba(147, 51, 234, 0.15)'
      }}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className={`flex-shrink-0 w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
            task.is_completed
              ? "bg-green-500 border-green-500"
              : "border-zinc-300 dark:border-zinc-600 hover:border-green-400"
          } disabled:opacity-50`}
          aria-label={
            task.is_completed ? t.markIncomplete : t.markComplete
          }
        >
          {task.is_completed && <Check size={16} className="text-white" />}
        </button>

        {/* Task Content */}
        <div className="flex-grow min-w-0">
          <h3
            className={`font-medium transition-all duration-300 ${
              task.is_completed
                ? "line-through text-zinc-500 dark:text-zinc-500"
                : "text-zinc-900 dark:text-zinc-100"
            }`}
            style={{ animation: 'textFadeUp 0.4s ease-out' }}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.is_completed
                  ? "line-through text-zinc-400 dark:text-zinc-600"
                  : "text-zinc-600 dark:text-zinc-400"
              }`}
            >
              {task.description}
            </p>
          )}
          <p className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
            {t.created} {createdDate}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
            className="p-2 text-zinc-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
            aria-label={t.editTask}
          >
            <Edit3 size={16} />
          </button>
          <button
            onClick={handleDelete}
            disabled={isLoading}
            className="p-2 text-zinc-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            aria-label={t.deleteTask}
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
