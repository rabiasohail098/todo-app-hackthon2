'use client';

/**
 * Character Counter Component (Phase 3 - Phase 11)
 *
 * Shows character count for chat input with visual warning
 */

interface CharacterCounterProps {
  count: number;
  max: number;
  language?: 'en' | 'ur';
}

export default function CharacterCounter({ count, max, language = 'en' }: CharacterCounterProps) {
  const percentage = (count / max) * 100;
  const isWarning = percentage > 80;
  const isError = percentage > 95;

  // Color based on usage
  const getColor = () => {
    if (isError) return 'text-red-600 dark:text-red-400';
    if (isWarning) return 'text-orange-600 dark:text-orange-400';
    return 'text-purple-600 dark:text-purple-400';
  };

  // Show count only when approaching limit
  if (percentage < 50) return null;

  const label = language === 'ur'
    ? `${max.toLocaleString()} / ${count.toLocaleString()}`
    : `${count.toLocaleString()} / ${max.toLocaleString()}`;

  return (
    <div className="flex items-center gap-2">
      {/* Progress Bar */}
      <div className="flex-1 h-1 bg-purple-200/30 dark:bg-purple-800/30 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            isError
              ? 'bg-red-500'
              : isWarning
              ? 'bg-orange-500'
              : 'bg-purple-500'
          }`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      {/* Count */}
      <span className={`text-xs font-medium transition-colors ${getColor()}`}>
        {label}
      </span>

      {/* Warning Icon */}
      {isError && (
        <span className="text-red-600 dark:text-red-400 animate-pulse" title="Character limit exceeded">
          ⚠️
        </span>
      )}
    </div>
  );
}
