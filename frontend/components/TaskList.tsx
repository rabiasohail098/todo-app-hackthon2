"use client";

import { Task, TaskUpdate } from "@/types";
import TaskItem from "./TaskItem";
import { useTranslation } from "@/hooks/useTranslation";

type ViewMode = 'list' | 'grid';

interface TaskListProps {
  tasks: Task[];
  onToggle: (taskId: number, isCompleted: boolean) => void;
  onUpdate: (taskId: number, updates: TaskUpdate) => void;
  onDelete: (taskId: number) => void;
  onTagClick?: (tagId: number, tagName: string) => void;
  className?: string;
  viewMode?: ViewMode;
  searchQuery?: string;
}

/**
 * Task list component.
 *
 * Displays a list of tasks with filtering and grouping by status.
 */
export default function TaskList({
  tasks,
  onToggle,
  onUpdate,
  onDelete,
  onTagClick,
  className = "",
  viewMode = 'list',
  searchQuery = ""
}: TaskListProps) {
  const t = useTranslation();

  // Separate tasks by completion status
  const activeTasks = tasks.filter((task) => !task.is_completed);
  const completedTasks = tasks.filter((task) => task.is_completed);

  if (tasks.length === 0) {
    return (
      <div className="text-center py-16 fade-in">
        <p className="text-zinc-500 dark:text-zinc-400 text-lg">
          {t.noActiveTasks}
        </p>
      </div>
    );
  }

  // Grid view layout
  if (viewMode === 'grid') {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
        {[...activeTasks, ...completedTasks].map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={onToggle}
            onUpdate={onUpdate}
            onDelete={onDelete}
            onTagClick={onTagClick}
            searchQuery={searchQuery}
          />
        ))}
      </div>
    );
  }

  // Default list view
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Active Tasks */}
      {activeTasks.length > 0 && (
        <div className="animate-fadeIn">
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4 slide-in">
            {t.activeTasks} ({activeTasks.length})
          </h2>
          <div className="space-y-3">
            {activeTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={onToggle}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onTagClick={onTagClick}
                searchQuery={searchQuery}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="animate-fadeIn">
          <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4 slide-in">
            {t.completedTasks} ({completedTasks.length})
          </h2>
          <div className="space-y-3">
            {completedTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggle={onToggle}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onTagClick={onTagClick}
                searchQuery={searchQuery}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
