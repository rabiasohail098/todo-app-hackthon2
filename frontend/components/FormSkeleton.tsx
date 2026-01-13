"use client";

/**
 * Form skeleton loading component.
 *
 * Displays a placeholder animation while form is loading.
 */
export default function FormSkeleton() {
  return (
    <div className="glass-strong rounded-2xl p-6 card-3d animate-pulse">
      {/* Title skeleton */}
      <div className="h-6 bg-zinc-200 dark:bg-zinc-700 rounded w-1/3 mb-4" />

      <div className="space-y-4">
        {/* Input field skeleton */}
        <div>
          <div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-20 mb-2" />
          <div className="h-10 bg-zinc-200 dark:bg-zinc-700 rounded w-full" />
        </div>

        {/* Textarea skeleton */}
        <div>
          <div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-24 mb-2" />
          <div className="h-20 bg-zinc-200 dark:bg-zinc-700 rounded w-full" />
        </div>

        {/* Category selector skeleton */}
        <div>
          <div className="h-4 bg-zinc-200 dark:bg-zinc-700 rounded w-20 mb-2" />
          <div className="flex gap-2">
            <div className="h-8 w-16 bg-zinc-200 dark:bg-zinc-700 rounded-lg" />
            <div className="h-8 w-20 bg-zinc-200 dark:bg-zinc-700 rounded-lg" />
            <div className="h-8 w-16 bg-zinc-200 dark:bg-zinc-700 rounded-lg" />
          </div>
        </div>

        {/* Submit button skeleton */}
        <div className="h-12 bg-gradient-to-r from-purple-400 to-pink-400 dark:from-purple-600 dark:to-pink-600 rounded-xl w-full" />
      </div>
    </div>
  );
}
