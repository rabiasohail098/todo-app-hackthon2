'use client';

/**
 * Chat Loading Skeleton Component (Phase 3 - Phase 11)
 *
 * Shows skeleton UI while chat history is loading
 */

export default function ChatLoadingSkeleton() {
  return (
    <div className="flex flex-col gap-4 p-4 animate-pulse">
      {/* User Message Skeleton */}
      <div className="flex justify-end">
        <div className="glass rounded-2xl px-4 py-3 max-w-[70%]">
          <div className="h-4 bg-purple-300/30 dark:bg-purple-700/30 rounded w-48" />
        </div>
      </div>

      {/* AI Message Skeleton */}
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-purple-300/30 dark:bg-purple-700/30" />
        <div className="glass rounded-2xl px-4 py-3 max-w-[70%] space-y-2">
          <div className="h-4 bg-purple-300/30 dark:bg-purple-700/30 rounded w-64" />
          <div className="h-4 bg-purple-300/30 dark:bg-purple-700/30 rounded w-48" />
        </div>
      </div>

      {/* User Message Skeleton */}
      <div className="flex justify-end">
        <div className="glass rounded-2xl px-4 py-3 max-w-[70%]">
          <div className="h-4 bg-purple-300/30 dark:bg-purple-700/30 rounded w-32" />
        </div>
      </div>

      {/* AI Message Skeleton */}
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-purple-300/30 dark:bg-purple-700/30" />
        <div className="glass rounded-2xl px-4 py-3 max-w-[70%] space-y-2">
          <div className="h-4 bg-purple-300/30 dark:bg-purple-700/30 rounded w-56" />
        </div>
      </div>
    </div>
  );
}

/**
 * Conversation List Loading Skeleton
 */
export function ConversationLoadingSkeleton() {
  return (
    <div className="space-y-2 p-3 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="glass rounded-xl px-3 py-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-300/30 dark:bg-purple-700/30" />
            <div className="flex-1 space-y-2">
              <div className="h-3 bg-purple-300/30 dark:bg-purple-700/30 rounded w-32" />
              <div className="h-2 bg-purple-300/30 dark:bg-purple-700/30 rounded w-20" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
