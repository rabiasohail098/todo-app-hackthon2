"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { FileText, Eye, Edit3 } from "lucide-react";

interface NotesEditorProps {
  taskId: number;
  initialNotes?: string;
  onSave: (notes: string) => Promise<void>;
}

export default function NotesEditor({ taskId, initialNotes = "", onSave }: NotesEditorProps) {
  const [notes, setNotes] = useState(initialNotes);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(notes);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to save notes:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isEditing && !notes) {
    return (
      <button
        onClick={() => setIsEditing(true)}
        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
      >
        <FileText className="w-4 h-4" />
        Add notes
      </button>
    );
  }

  if (!isEditing) {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Notes
          </h4>
          <button
            onClick={() => setIsEditing(true)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Edit
          </button>
        </div>
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{notes}</ReactMarkdown>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Notes
        </h4>
        <div className="flex gap-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 flex items-center gap-1"
          >
            {showPreview ? (
              <>
                <Edit3 className="w-3 h-3" />
                Edit
              </>
            ) : (
              <>
                <Eye className="w-3 h-3" />
                Preview
              </>
            )}
          </button>
        </div>
      </div>

      {showPreview ? (
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{notes || "*No content*"}</ReactMarkdown>
        </div>
      ) : (
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add notes in markdown format...&#10;&#10;**Example:**&#10;- Bullet points&#10;- **Bold text**&#10;- *Italic text*"
          className="w-full h-32 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-y"
        />
      )}

      <div className="flex gap-2">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? "Saving..." : "Save"}
        </button>
        <button
          onClick={() => {
            setNotes(initialNotes);
            setIsEditing(false);
            setShowPreview(false);
          }}
          disabled={isSaving}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
