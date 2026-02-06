"use client";

import React from "react";

export type Priority = "critical" | "high" | "medium" | "low";

interface PriorityIndicatorProps {
  priority: Priority;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

const PriorityIndicator: React.FC<PriorityIndicatorProps> = ({
  priority,
  size = "md",
  showLabel = true,
  className = "",
}) => {
  // Priority configurations
  const priorityConfig = {
    critical: {
      label: "Critical",
      color: "bg-red-500",
      textColor: "text-red-700 dark:text-red-300",
      bgColor: "bg-red-100 dark:bg-red-900/30",
      borderColor: "border-red-300 dark:border-red-700",
      icon: "🔴",
    },
    high: {
      label: "High",
      color: "bg-orange-500",
      textColor: "text-orange-700 dark:text-orange-300",
      bgColor: "bg-orange-100 dark:bg-orange-900/30",
      borderColor: "border-orange-300 dark:border-orange-700",
      icon: "🟠",
    },
    medium: {
      label: "Medium",
      color: "bg-yellow-500",
      textColor: "text-yellow-700 dark:text-yellow-300",
      bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
      borderColor: "border-yellow-300 dark:border-yellow-700",
      icon: "🟡",
    },
    low: {
      label: "Low",
      color: "bg-green-500",
      textColor: "text-green-700 dark:text-green-300",
      bgColor: "bg-green-100 dark:bg-green-900/30",
      borderColor: "border-green-300 dark:border-green-700",
      icon: "🟢",
    },
  };

  const config = priorityConfig[priority];

  // Size-specific classes
  const sizeClasses = {
    sm: {
      container: "text-xs px-2 py-0.5",
      dot: "w-2 h-2",
      icon: "text-sm",
    },
    md: {
      container: "text-sm px-2.5 py-1",
      dot: "w-2.5 h-2.5",
      icon: "text-base",
    },
    lg: {
      container: "text-base px-3 py-1.5",
      dot: "w-3 h-3",
      icon: "text-lg",
    },
  };

  const sizeClass = sizeClasses[size];

  if (!showLabel) {
    // Icon-only mode
    return (
      <span className={`${sizeClass.icon} ${className}`} title={config.label}>
        {config.icon}
      </span>
    );
  }

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${sizeClass.container}
        ${config.bgColor}
        ${config.textColor}
        ${config.borderColor}
        ${className}
      `}
    >
      <span className={sizeClass.icon}>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
};

export default PriorityIndicator;
