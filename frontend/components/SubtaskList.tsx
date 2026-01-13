"use client";

import React, { useState } from "react";
import { Check, X, Trash2, Plus } from "lucide-react";
import { useApp } from "@/context/AppContext";

interface Subtask {
  id: number;
  title: string;
  is_completed: boolean;
  order: number;
  parent_task_id: number;
}

interface SubtaskListProps {
  taskId: number;
  subtasks: Subtask[];
  onSubtaskToggle: (subtaskId: number, isCompleted: boolean) => void;
  onSubtaskDelete: (subtaskId: number) => void;
  onSubtaskAdd: (title: string) => void;
  className?: string;
}

const SubtaskList: React.FC<SubtaskListProps> = ({
  taskId,
  subtasks,
  onSubtaskToggle,
  onSubtaskDelete,
  onSubtaskAdd,
  className = "",
}) => {
  const [newSubtaskTitle, setNewSubtaskTitle] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const { language } = useApp();

  const handleAddSubtask = () => {
    if (!newSubtaskTitle.trim()) return;

    onSubtaskAdd(newSubtaskTitle.trim());
    setNewSubtaskTitle("");
    setIsAdding(false);
  };

  // Calculate progress
  const total = subtasks.length;
  const completed = subtasks.filter((s) => s.is_completed).length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Header with progress */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
          {language === "ur" ? "ذیلی کام" : "Subtasks"} {total > 0 && `(${completed}/${total})`}
        </h4>
        {total > 0 && (
          <span className="text-xs text-zinc-500 dark:text-zinc-400">
            {percentage}% {language === "ur" ? "مکمل" : "complete"}
          </span>
        )}
      </div>

      {/* Progress Bar */}
      {total > 0 && (
        <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}

      {/* Subtask List */}
      <div className="space-y-2">
        {subtasks.map((subtask) => (
          <div
            key={subtask.id}
            className="flex items-center gap-2 p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            {/* Checkbox */}
            <button
              onClick={() => onSubtaskToggle(subtask.id, !subtask.is_completed)}
              className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                subtask.is_completed
                  ? "bg-green-500 border-green-500"
                  : "border-zinc-300 dark:border-zinc-600 hover:border-green-400"
              }`}
              aria-label={
                subtask.is_completed
                  ? language === "ur"
                    ? "نامکمل نشان زد"
                    : "Mark incomplete"
                  : language === "ur"
                  ? "مکمل نشان زد"
                  : "Mark complete"
              }
            >
              {subtask.is_completed && <Check size={14} className="text-white" />}
            </button>

            {/* Title */}
            <span
              className={`flex-grow text-sm ${
                subtask.is_completed
                  ? "line-through text-zinc-500 dark:text-zinc-500"
                  : "text-zinc-900 dark:text-zinc-100"
              }`}
            >
              {subtask.title}
            </span>

            {/* Delete Button */}
            <button
              onClick={() => onSubtaskDelete(subtask.id)}
              className="flex-shrink-0 p-1 text-zinc-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              aria-label={language === "ur" ? "حذف کریں" : "Delete subtask"}
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      {/* Add Subtask Form */}
      {isAdding ? (
        <div className="flex gap-2">
          <input
            type="text"
            value={newSubtaskTitle}
            onChange={(e) => setNewSubtaskTitle(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleAddSubtask()}
            placeholder={
              language === "ur" ? "ذیلی کام کا عنوان..." : "Subtask title..."
            }
            className="flex-1 px-3 py-2 text-sm border border-zinc-300 dark:border-zinc-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-zinc-800 dark:text-zinc-100"
            autoFocus
          />
          <button
            onClick={handleAddSubtask}
            className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors"
            disabled={!newSubtaskTitle.trim()}
          >
            <Check size={16} />
          </button>
          <button
            onClick={() => {
              setIsAdding(false);
              setNewSubtaskTitle("");
            }}
            className="px-3 py-2 bg-zinc-500 hover:bg-zinc-600 text-white text-sm rounded-lg transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <button
          onClick={() => setIsAdding(true)}
          className="flex items-center gap-2 px-3 py-2 text-sm text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg transition-colors w-full"
        >
          <Plus size={16} />
          {language === "ur" ? "ذیلی کام شامل کریں" : "Add subtask"}
        </button>
      )}

      {/* Empty State */}
      {total === 0 && !isAdding && (
        <p className="text-xs text-zinc-500 dark:text-zinc-400 text-center py-2">
          {language === "ur"
            ? "ابھی تک کوئی ذیلی کام نہیں"
            : "No subtasks yet"}
        </p>
      )}
    </div>
  );
};

export default SubtaskList;
