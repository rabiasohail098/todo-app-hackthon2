"use client";

import { useState } from "react";
import { ChevronDown, Repeat } from "lucide-react";
import { useApp } from "@/context/AppContext";

type RecurrencePattern = "daily" | "weekly" | "monthly" | null;

interface RecurrenceSelectorProps {
  value: RecurrencePattern;
  onChange: (pattern: RecurrencePattern) => void;
  className?: string;
}

/**
 * Recurrence pattern selector component.
 *
 * Allows users to select recurring task patterns (Daily, Weekly, Monthly).
 */
export default function RecurrenceSelector({
  value,
  onChange,
  className = "",
}: RecurrenceSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { language } = useApp();

  const patterns: { value: RecurrencePattern; label: string; labelUr: string }[] = [
    { value: null, label: "No Recurrence", labelUr: "بار بار نہیں" },
    { value: "daily", label: "Daily", labelUr: "روزانہ" },
    { value: "weekly", label: "Weekly", labelUr: "ہفتہ وار" },
    { value: "monthly", label: "Monthly", labelUr: "ماہانہ" },
  ];

  const selectedPattern = patterns.find((p) => p.value === value);
  const displayLabel = language === "ur" ? selectedPattern?.labelUr : selectedPattern?.label;

  return (
    <div className={`relative ${className}`}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-zinc-800 dark:text-zinc-100 transition-all hover:border-purple-400"
      >
        <div className="flex items-center gap-2">
          <Repeat size={16} className="text-purple-600 dark:text-purple-400" />
          <span className="text-sm">{displayLabel}</span>
        </div>
        <ChevronDown
          size={16}
          className={`text-zinc-500 transition-transform ${isOpen ? "rotate-180" : ""}`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop to close dropdown */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Options List */}
          <div className="absolute z-20 w-full mt-1 glass-strong rounded-lg border border-purple-300/20 overflow-hidden shadow-xl">
            {patterns.map((pattern) => (
              <button
                key={pattern.value || "none"}
                type="button"
                onClick={() => {
                  onChange(pattern.value);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2.5 text-sm transition-colors ${
                  value === pattern.value
                    ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium"
                    : "text-zinc-700 dark:text-zinc-300 hover:bg-purple-50 dark:hover:bg-purple-900/10"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Repeat
                    size={14}
                    className={
                      value === pattern.value
                        ? "text-purple-600 dark:text-purple-400"
                        : "text-zinc-400"
                    }
                  />
                  <span>
                    {language === "ur" ? pattern.labelUr : pattern.label}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
