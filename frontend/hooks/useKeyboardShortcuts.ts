import { useEffect } from "react";

/**
 * Custom hook for keyboard shortcuts.
 *
 * Handles common keyboard shortcuts like Ctrl+N, Ctrl+F, etc.
 */
export function useKeyboardShortcuts(shortcuts: {
  onNewTask?: () => void;
  onSearch?: () => void;
  onEscape?: () => void;
}) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for Ctrl (Windows/Linux) or Cmd (Mac)
      const isCtrlOrCmd = event.ctrlKey || event.metaKey;

      // Ctrl+N or Cmd+N: New task (focus on title input)
      if (isCtrlOrCmd && event.key === "n") {
        event.preventDefault();
        if (shortcuts.onNewTask) shortcuts.onNewTask();
      }

      // Ctrl+F or Cmd+F: Search (focus on search input)
      if (isCtrlOrCmd && event.key === "f") {
        event.preventDefault();
        if (shortcuts.onSearch) shortcuts.onSearch();
      }

      // Escape: Clear focus or close modals
      if (event.key === "Escape") {
        if (shortcuts.onEscape) shortcuts.onEscape();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [shortcuts]);
}
