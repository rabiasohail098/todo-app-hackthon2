"use client";

import React, { useState, useEffect, useRef } from "react";
import { X, Hash } from "lucide-react";
import { useApp } from "@/context/AppContext";

interface Tag {
  id?: number;
  name: string;
}

interface TagInputProps {
  value: Tag[];
  onChange: (tags: Tag[]) => void;
  placeholder?: string;
  className?: string;
}

/**
 * Tag input component with autocomplete.
 *
 * Allows users to add, remove, and select tags with suggestions.
 */
export default function TagInput({
  value,
  onChange,
  placeholder,
  className = "",
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState<Tag[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { language } = useApp();

  // Fetch all tags on mount
  // Empty dependency array [] ensures this runs only once on component mount (FR-006)
  // Adding fetchAllTags to dependencies would cause infinite loop since it's recreated on every render
  useEffect(() => {
    fetchAllTags();
  }, []);

  // Filter suggestions based on input
  useEffect(() => {
    if (inputValue.trim()) {
      const filtered = allTags.filter(
        (tag) =>
          tag.name.toLowerCase().includes(inputValue.toLowerCase()) &&
          !value.some((v) => v.name.toLowerCase() === tag.name.toLowerCase())
      );
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [inputValue, allTags, value]);

  const fetchAllTags = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/tags");

      if (!response.ok) {
        // Map HTTP errors to user-friendly messages
        if (response.status === 503) {
          throw new Error("The service is temporarily unavailable. Please try again in a few minutes.");
        } else if (response.status === 401) {
          throw new Error("Please sign in to continue.");
        } else if (response.status === 404) {
          throw new Error("Tags not found.");
        } else {
          throw new Error("Unable to load tags. Please try again later.");
        }
      }

      const tags = await response.json();
      setAllTags(tags);
      setError(null);
    } catch (error) {
      console.error("Error fetching tags:", error);

      // User-friendly error messages (FR-020: Failed requests MUST show specific, actionable error messages)
      if (error instanceof Error) {
        if (error.message.includes('fetch failed') || error.message.includes('Failed to fetch') || error.message.includes('Network request failed')) {
          setError("Unable to connect to server. Please check your connection.");
        } else {
          setError(error.message);
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }

      // Empty array fallback (FR-004: Components MUST set empty arrays as fallback when fetches fail)
      setAllTags([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(inputValue.trim());
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      // Remove last tag when backspace is pressed on empty input
      onChange(value.slice(0, -1));
    }
  };

  const addTag = (tagName: string) => {
    if (!tagName) return;

    // Remove # prefix if present
    const cleanName = tagName.replace(/^#/, "").toLowerCase();

    // Check if tag already exists in value
    if (value.some((t) => t.name.toLowerCase() === cleanName)) {
      setInputValue("");
      return;
    }

    // Add tag
    onChange([...value, { name: cleanName }]);
    setInputValue("");
    setShowSuggestions(false);
  };

  const removeTag = (tagToRemove: Tag) => {
    onChange(value.filter((t) => t.name !== tagToRemove.name));
  };

  const selectSuggestion = (tag: Tag) => {
    addTag(tag.name);
    inputRef.current?.focus();
  };

  return (
    <div className={`relative ${className}`}>
      {/* Tags display and input */}
      <div className="flex flex-wrap items-center gap-2 p-3 border border-zinc-300 dark:border-zinc-600 rounded-lg focus-within:ring-2 focus-within:ring-purple-500 dark:bg-zinc-800">
        {/* Existing tags as chips */}
        {value.map((tag, index) => (
          <div
            key={index}
            className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-md text-sm"
          >
            <Hash size={12} />
            <span>{tag.name}</span>
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="ml-1 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200 transition-colors"
              aria-label={`Remove ${tag.name}`}
            >
              <X size={14} />
            </button>
          </div>
        ))}

        {/* Input field */}
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleInputKeyDown}
          placeholder={
            value.length === 0
              ? placeholder ||
                (language === "ur"
                  ? "ٹیگز شامل کریں..."
                  : "Add tags...")
              : ""
          }
          className="flex-1 min-w-[120px] outline-none bg-transparent text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 dark:placeholder-zinc-500"
        />
      </div>

      {/* Suggestions dropdown */}
      {showSuggestions && (
        <div className="absolute z-10 w-full mt-1 glass-strong rounded-lg max-h-48 overflow-y-auto border border-purple-300/20">
          {suggestions.map((tag) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => selectSuggestion(tag)}
              className="w-full px-3 py-2 text-left text-sm hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors flex items-center gap-2"
            >
              <Hash size={14} className="text-purple-600 dark:text-purple-400" />
              <span className="text-zinc-900 dark:text-zinc-100">
                {tag.name}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* Helper text */}
      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
        {language === "ur"
          ? "Enter یا کوما دبائیں ٹیگ شامل کرنے کے لیے"
          : "Press Enter or comma to add tag"}
      </p>

      {/* Error state with retry button (FR-010: Error states MUST include a "Retry" button) */}
      {error && (
        <div className="mt-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-700 dark:text-red-300 mb-2">{error}</p>
          <button
            type="button"
            onClick={fetchAllTags}
            disabled={isLoading}
            className="px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (language === "ur" ? "دوبارہ کوشش..." : "Retrying...") : (language === "ur" ? "دوبارہ کوشش کریں" : "Retry")}
          </button>
        </div>
      )}

      {/* Loading state indicator */}
      {isLoading && !error && (
        <div className="mt-2 text-sm text-purple-600 dark:text-purple-400">
          {language === "ur" ? "ٹیگز لوڈ ہو رہے ہیں..." : "Loading tags..."}
        </div>
      )}
    </div>
  );
}
