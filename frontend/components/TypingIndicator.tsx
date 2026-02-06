'use client';

/**
 * Typing Indicator Component (Phase 3 - Phase 11)
 *
 * Shows animated "AI is typing..." indicator during message processing
 */

interface TypingIndicatorProps {
  language?: 'en' | 'ur';
}

export default function TypingIndicator({ language = 'en' }: TypingIndicatorProps) {
  const text = language === 'ur' ? 'AI لکھ رہا ہے' : 'AI is typing';

  return (
    <div className="flex items-start gap-3 px-4 py-3 animate-in fade-in duration-300">
      {/* AI Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0 shadow-lg">
        <span className="text-white text-sm font-bold">AI</span>
      </div>

      {/* Typing Bubble */}
      <div className="glass rounded-2xl px-4 py-3 max-w-[200px]">
        <div className="flex items-center gap-2">
          <span className="text-sm text-purple-700 dark:text-purple-300">
            {text}
          </span>

          {/* Animated Dots */}
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
