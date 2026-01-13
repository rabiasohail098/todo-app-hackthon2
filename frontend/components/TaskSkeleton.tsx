"use client";

/**
 * Task skeleton loading component.
 *
 * Displays a placeholder animation while tasks are loading.
 */
export default function TaskSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="p-5 glass rounded-2xl border border-purple-300/20 animate-pulse"
        >
          <div className="flex items-start gap-3">
            {/* Checkbox skeleton */}
            <div className="flex-shrink-0 w-6 h-6 rounded border-2 border-zinc-300 dark:border-zinc-600 bg-zinc-200 dark:bg-zinc-700" />

            {/* Content skeleton */}
            <div className="flex-grow min-w-0 space-y-2">
              {/* Title skeleton */}
              <div className="h-5 bg-zinc-200 dark:bg-zinc-700 rounded w-3/4" />

              {/* Description skeleton */}
              <div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-1/2" />

              {/* Tags skeleton */}
              <div className="flex gap-2 mt-2">
                <div className="h-6 w-16 bg-purple-100 dark:bg-purple-900/30 rounded-md" />
                <div className="h-6 w-20 bg-purple-100 dark:bg-purple-900/30 rounded-md" />
              </div>

              {/* Date skeleton */}
              <div className="h-3 bg-zinc-200 dark:bg-zinc-700 rounded w-32 mt-2" />
            </div>

            {/* Actions skeleton */}
            <div className="flex gap-2 flex-shrink-0">
              <div className="w-8 h-8 bg-zinc-200 dark:bg-zinc-700 rounded" />
              <div className="w-8 h-8 bg-zinc-200 dark:bg-zinc-700 rounded" />
              <div className="w-8 h-8 bg-zinc-200 dark:bg-zinc-700 rounded" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
