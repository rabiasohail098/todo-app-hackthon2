import React from "react";

/**
 * Highlight matching search terms in text
 *
 * @param text - The text to search within
 * @param query - The search query to highlight
 * @returns React element with highlighted matches
 */
export function highlightText(text: string, query: string): React.ReactNode {
  if (!query || !text) {
    return text;
  }

  // Escape special regex characters in the query
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // Split by the search query (case insensitive)
  const regex = new RegExp(`(${escapedQuery})`, "gi");
  const parts = text.split(regex);

  return (
    <>
      {parts.map((part, index) => {
        // Check if this part matches the query (case insensitive)
        const isMatch = part.toLowerCase() === query.toLowerCase();

        return isMatch ? (
          <mark
            key={index}
            className="bg-yellow-200 dark:bg-yellow-800 text-zinc-900 dark:text-zinc-100 font-semibold px-0.5 rounded"
          >
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        );
      })}
    </>
  );
}
