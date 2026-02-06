"use client";

import React, { useState, useEffect } from "react";
import { useApp } from "@/context/AppContext";

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder,
  className = "",
}) => {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [debouncedQuery, setDebouncedQuery] = useState<string>("");
  const { language } = useApp();

  // Debounce search query to avoid excessive API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Call onSearch when debounced query changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    onSearch(debouncedQuery);
  }, [debouncedQuery]); // onSearch excluded to prevent infinite loop

  const handleClear = () => {
    setSearchQuery("");
  };

  const defaultPlaceholder =
    language === "ur"
      ? "ٹاسک تلاش کریں..."
      : "Search tasks...";

  return (
    <div className={`relative ${className}`}>
      {/* Search Icon */}
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400 dark:text-zinc-500">
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Search Input */}
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder={placeholder || defaultPlaceholder}
        className={`
          w-full pl-10 pr-10 py-3
          bg-white dark:bg-zinc-800
          border border-zinc-300 dark:border-zinc-700
          rounded-xl
          text-zinc-900 dark:text-zinc-100
          placeholder-zinc-400 dark:placeholder-zinc-500
          focus:outline-none
          focus:ring-2
          focus:ring-purple-500
          focus:border-transparent
          transition-all
        `}
      />

      {/* Clear Button */}
      {searchQuery && (
        <button
          onClick={handleClear}
          className="
            absolute right-3 top-1/2 transform -translate-y-1/2
            text-zinc-400 dark:text-zinc-500
            hover:text-zinc-600 dark:hover:text-zinc-300
            transition-colors
          "
          aria-label="Clear search"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  );
};

export default SearchBar;
