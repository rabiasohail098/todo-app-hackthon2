"use client";

import { useState, useEffect } from "react";
import { Clock, Loader } from "lucide-react";

interface Activity {
  id: number;
  action: string;
  field: string | null;
  old_value: string | null;
  new_value: string | null;
  description: string | null;
  created_at: string;
}

interface ActivityLogProps {
  taskId: number;
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function getActionColor(action: string): string {
  switch (action.toLowerCase()) {
    case "created":
      return "text-green-600 dark:text-green-400";
    case "completed":
      return "text-blue-600 dark:text-blue-400";
    case "deleted":
      return "text-red-600 dark:text-red-400";
    case "updated":
      return "text-yellow-600 dark:text-yellow-400";
    default:
      return "text-gray-600 dark:text-gray-400";
  }
}

function formatActivity(activity: Activity): string {
  if (activity.description) {
    return activity.description;
  }

  if (activity.field && activity.old_value && activity.new_value) {
    return `Changed ${activity.field} from "${activity.old_value}" to "${activity.new_value}"`;
  }

  if (activity.field && activity.new_value) {
    return `Set ${activity.field} to "${activity.new_value}"`;
  }

  return `${activity.action} task`;
}

export default function ActivityLog({ taskId }: ActivityLogProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchActivities();
  }, [taskId]);

  const fetchActivities = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/tasks/${taskId}/activity`);

      if (!response.ok) {
        throw new Error("Failed to load activity history");
      }

      const data = await response.json();
      setActivities(data);
    } catch (error: any) {
      setError(error.message || "Failed to load activity history");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-8">
        No activity history yet
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <Clock className="w-4 h-4" />
        Activity History
      </h4>

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-2 top-0 bottom-0 w-px bg-gray-200 dark:bg-gray-700" />

        {/* Activities */}
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="relative flex gap-4 pl-8">
              {/* Timeline dot */}
              <div
                className={`absolute left-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-900 ${
                  activity.action === "created"
                    ? "bg-green-500"
                    : activity.action === "completed"
                    ? "bg-blue-500"
                    : activity.action === "deleted"
                    ? "bg-red-500"
                    : "bg-gray-400"
                }`}
              />

              {/* Activity content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-gray-100">
                  <span className={`font-medium ${getActionColor(activity.action)}`}>
                    {activity.action}
                  </span>{" "}
                  {formatActivity(activity)}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {formatTimestamp(activity.created_at)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
