"use client";

import React from "react";

interface CategoryBadgeProps {
  category?: {
    id: number;
    name: string;
    color: string;
    icon?: string;
  } | null;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const CategoryBadge: React.FC<CategoryBadgeProps> = ({
  category,
  size = "md",
  className = "",
}) => {
  if (!category) {
    return null;
  }

  // Size-specific classes
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-1",
    lg: "text-base px-3 py-1.5",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium
        ${sizeClasses[size]}
        ${className}
      `}
      style={{
        backgroundColor: `${category.color}20`, // 20% opacity
        color: category.color,
        borderColor: `${category.color}40`, // 40% opacity
        borderWidth: "1px",
        borderStyle: "solid",
      }}
    >
      {category.icon && <span className="text-base">{category.icon}</span>}
      <span>{category.name}</span>
    </span>
  );
};

export default CategoryBadge;
