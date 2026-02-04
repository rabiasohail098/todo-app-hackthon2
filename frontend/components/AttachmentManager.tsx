"use client";

import { useState, useEffect, useRef } from "react";
import { Paperclip, Upload, X, FileText, Image as ImageIcon, Download, Trash2, Loader } from "lucide-react";
import { authFetch } from "@/lib/api";

interface Attachment {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  cloudinary_url: string;
  created_at: string;
}

interface AttachmentManagerProps {
  taskId: number;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/gif",
  "image/webp",
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "text/plain",
  "text/csv",
  "application/zip",
  "application/x-zip-compressed",
];

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function getFileIcon(fileType: string) {
  if (fileType.startsWith("image/")) {
    return <ImageIcon className="w-4 h-4" />;
  }
  return <FileText className="w-4 h-4" />;
}

export default function AttachmentManager({ taskId }: AttachmentManagerProps) {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchAttachments();
  }, [taskId]);

  const fetchAttachments = async () => {
    setIsLoading(true);
    try {
      const response = await authFetch(`/api/tasks/${taskId}/attachments`);
      if (response.ok) {
        const data = await response.json();
        setAttachments(data);
      }
    } catch (error) {
      console.error("Failed to fetch attachments:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return `File size (${formatFileSize(file.size)}) exceeds maximum 10MB`;
    }
    if (!ALLOWED_TYPES.includes(file.type)) {
      return `File type "${file.type}" is not allowed`;
    }
    return null;
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await authFetch(`/api/tasks/${taskId}/attachments`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to upload file");
      }

      const newAttachment = await response.json();
      setAttachments([newAttachment, ...attachments]);

      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error: any) {
      setError(error.message || "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (attachmentId: number) => {
    if (!confirm("Are you sure you want to delete this attachment?")) return;

    try {
      const response = await authFetch(`/api/tasks/${taskId}/attachments/${attachmentId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete attachment");
      }

      setAttachments(attachments.filter((a) => a.id !== attachmentId));
    } catch (error: any) {
      setError(error.message || "Failed to delete attachment");
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <Paperclip className="w-4 h-4" />
          Attachments {attachments.length > 0 && `(${attachments.length})`}
        </h4>
        <label
          htmlFor={`file-upload-${taskId}`}
          className={`flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm cursor-pointer ${
            isUploading ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          {isUploading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload
            </>
          )}
        </label>
        <input
          ref={fileInputRef}
          id={`file-upload-${taskId}`}
          type="file"
          onChange={handleFileSelect}
          disabled={isUploading}
          className="hidden"
          accept={ALLOWED_TYPES.join(",")}
        />
      </div>

      {error && (
        <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-4">
          <Loader className="w-5 h-5 animate-spin text-gray-400" />
        </div>
      ) : attachments.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
          No attachments yet. Upload files up to 10MB.
        </p>
      ) : (
        <div className="space-y-2">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="text-gray-600 dark:text-gray-400">
                  {getFileIcon(attachment.file_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {attachment.original_filename}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(attachment.file_size)} •{" "}
                    {new Date(attachment.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <a
                  href={attachment.cloudinary_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                  title="Download"
                >
                  <Download className="w-4 h-4" />
                </a>
                <button
                  onClick={() => handleDelete(attachment.id)}
                  className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-500 dark:text-gray-400">
        Allowed: Images, PDFs, Documents, Spreadsheets, Text files, ZIP (max 10MB)
      </p>
    </div>
  );
}
