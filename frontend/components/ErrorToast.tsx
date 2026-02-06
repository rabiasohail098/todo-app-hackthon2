'use client';

/**
 * Error Toast Component (Phase 3 - Phase 11)
 *
 * Shows error messages in a non-intrusive toast notification
 */

import { useEffect, useState } from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ErrorToastProps {
  message: string;
  onClose: () => void;
  duration?: number; // Auto-close duration in ms (0 = no auto-close)
  type?: 'error' | 'warning' | 'info';
}

export default function ErrorToast({
  message,
  onClose,
  duration = 5000,
  type = 'error',
}: ErrorToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Wait for fade-out animation
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  if (!isVisible) return null;

  const colors = {
    error: {
      bg: 'from-red-500 to-pink-600',
      border: 'border-red-300 dark:border-red-700',
      text: 'text-red-900 dark:text-red-100',
    },
    warning: {
      bg: 'from-orange-500 to-yellow-600',
      border: 'border-orange-300 dark:border-orange-700',
      text: 'text-orange-900 dark:text-orange-100',
    },
    info: {
      bg: 'from-blue-500 to-purple-600',
      border: 'border-blue-300 dark:border-blue-700',
      text: 'text-blue-900 dark:text-blue-100',
    },
  };

  const style = colors[type];

  return (
    <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-top-2 duration-300">
      <div className={`glass-strong border-2 ${style.border} rounded-2xl px-4 py-3 max-w-md shadow-2xl`}>
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br ${style.bg} shadow-lg flex-shrink-0`}>
            <AlertCircle className="text-white" size={20} />
          </div>

          {/* Message */}
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-medium ${style.text}`}>
              {message}
            </p>
          </div>

          {/* Close Button */}
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(onClose, 300);
            }}
            className="p-1 rounded-lg glass hover:glass-strong transition-all flex-shrink-0"
            aria-label="Close"
          >
            <X size={16} className="text-purple-600 dark:text-purple-400" />
          </button>
        </div>

        {/* Progress Bar (if auto-closing) */}
        {duration > 0 && (
          <div className="mt-2 h-1 bg-purple-200/30 dark:bg-purple-800/30 rounded-full overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${style.bg} animate-shrink`}
              style={{ animationDuration: `${duration}ms` }}
            />
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }
        .animate-shrink {
          animation: shrink linear forwards;
        }
      `}</style>
    </div>
  );
}

/**
 * Toast Manager Hook (optional - for managing multiple toasts)
 */
export function useToast() {
  const [toasts, setToasts] = useState<Array<{
    id: string;
    message: string;
    type: 'error' | 'warning' | 'info';
  }>>([]);

  const showToast = (message: string, type: 'error' | 'warning' | 'info' = 'error') => {
    const id = `toast-${Date.now()}`;
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const hideToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return {
    toasts,
    showToast,
    hideToast,
    showError: (message: string) => showToast(message, 'error'),
    showWarning: (message: string) => showToast(message, 'warning'),
    showInfo: (message: string) => showToast(message, 'info'),
  };
}
