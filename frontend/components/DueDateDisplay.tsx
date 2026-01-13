"use client";

import React from "react";

interface DueDateDisplayProps {
  dueDate: string | null;
  isCompleted?: boolean;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

const DueDateDisplay: React.FC<DueDateDisplayProps> = ({
  dueDate,
  isCompleted = false,
  size = "md",
  showLabel = true,
  className = "",
}) => {
  if (!dueDate) {
    return null;
  }

  const date = new Date(dueDate);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const nextWeek = new Date(today);
  nextWeek.setDate(nextWeek.getDate() + 7);

  // Calculate if overdue
  const isOverdue = date < now && !isCompleted;
  const isToday = date >= today && date < tomorrow;
  const isTomorrow = date >= tomorrow && date < new Date(tomorrow.getTime() + 24 * 60 * 60 * 1000);
  const isThisWeek = date >= today && date < nextWeek;

  // Determine color scheme
  let colorScheme = {
    bg: "bg-gray-100 dark:bg-gray-700",
    text: "text-gray-700 dark:text-gray-300",
    border: "border-gray-300 dark:border-gray-600",
    icon: "📅",
  };

  if (isOverdue) {
    colorScheme = {
      bg: "bg-red-100 dark:bg-red-900/30",
      text: "text-red-700 dark:text-red-300",
      border: "border-red-300 dark:border-red-700",
      icon: "⚠️",
    };
  } else if (isToday) {
    colorScheme = {
      bg: "bg-orange-100 dark:bg-orange-900/30",
      text: "text-orange-700 dark:text-orange-300",
      border: "border-orange-300 dark:border-orange-700",
      icon: "📅",
    };
  } else if (isTomorrow) {
    colorScheme = {
      bg: "bg-yellow-100 dark:bg-yellow-900/30",
      text: "text-yellow-700 dark:text-yellow-300",
      border: "border-yellow-300 dark:border-yellow-700",
      icon: "📅",
    };
  } else if (isThisWeek) {
    colorScheme = {
      bg: "bg-blue-100 dark:bg-blue-900/30",
      text: "text-blue-700 dark:text-blue-300",
      border: "border-blue-300 dark:border-blue-700",
      icon: "📅",
    };
  }

  // Format date string
  let dateText = "";
  if (isOverdue) {
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    dateText = diffDays === 1 ? "Overdue by 1 day" : `Overdue by ${diffDays} days`;
  } else if (isToday) {
    dateText = "Due today";
  } else if (isTomorrow) {
    dateText = "Due tomorrow";
  } else {
    // Format as readable date
    const options: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
    const year = date.getFullYear();
    if (year !== now.getFullYear()) {
      options.year = "numeric";
    }
    dateText = `Due ${date.toLocaleDateString("en-US", options)}`;
  }

  // Size-specific classes
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
    lg: "text-base px-3 py-1.5",
  };

  if (!showLabel) {
    // Icon-only mode
    return (
      <span className={`text-base ${colorScheme.text} ${className}`} title={dateText}>
        {colorScheme.icon}
      </span>
    );
  }

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${sizeClasses[size]}
        ${colorScheme.bg}
        ${colorScheme.text}
        ${colorScheme.border}
        ${className}
      `}
    >
      <span>{colorScheme.icon}</span>
      <span>{dateText}</span>
    </span>
  );
};

export default DueDateDisplay;
