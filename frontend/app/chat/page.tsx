"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState, FormEvent, useCallback } from "react";
import { Send, ArrowLeft, Bot, User, Loader2, MessageSquare, Plus, Menu, X, Trash2 } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
}

export default function ChatPage() {
  const router = useRouter();
  const { backgroundMode } = useApp();
  const t = useTranslation();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("Thinking...");
  const abortControllerRef = useRef<AbortController | null>(null);

  // Conversation state
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);

  // Load conversations on mount
  const loadConversations = useCallback(async () => {
    try {
      const res = await fetch("/api/conversations");
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, []);

  // Load messages for a conversation
  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const res = await fetch(`/api/conversations/${conversationId}/messages`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data);
      }
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  }, []);

  // Update body class based on background mode
  useEffect(() => {
    document.body.classList.remove("with-background", "with-background-image");
    if (backgroundMode === "gradient") {
      document.body.classList.add("with-background");
    } else if (backgroundMode === "image") {
      document.body.classList.add("with-background-image");
    }
  }, [backgroundMode]);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Start a new chat conversation
  const handleNewChat = async () => {
    try {
      const res = await fetch("/api/conversations", { method: "POST" });
      if (res.ok) {
        const newConv = await res.json();
        setConversations(prev => [newConv, ...prev]);
        setCurrentConversationId(newConv.id);
        setMessages([]);
        setInputValue("");
        setError(null);
        setShowSidebar(false);
      }
    } catch (err) {
      // Fallback to local-only new chat
      setCurrentConversationId(null);
      setMessages([]);
      setInputValue("");
      setError(null);
    }
  };

  // Switch to a conversation
  const handleSelectConversation = async (convId: string) => {
    setCurrentConversationId(convId);
    await loadMessages(convId);
    setError(null);
    setShowSidebar(false);
  };

  // Delete a conversation
  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/conversations/${convId}`, { method: "DELETE" });
      if (res.ok || res.status === 204) {
        setConversations(prev => prev.filter(c => c.id !== convId));
        if (currentConversationId === convId) {
          setCurrentConversationId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    setError(null);
    setLoadingMessage("Thinking...");

    // Create abort controller for timeout
    abortControllerRef.current = new AbortController();
    const timeoutId = setTimeout(() => {
      setLoadingMessage("Taking longer than usual...");
    }, 5000);

    const hardTimeoutId = setTimeout(() => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        setError("Request timed out. Please try again.");
        setIsLoading(false);
      }
    }, 30000);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
        signal: abortControllerRef.current.signal,
      });

      clearTimeout(timeoutId);
      clearTimeout(hardTimeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error:", response.status, errorText);
        throw new Error(`API Error: ${response.status} - ${errorText || "Failed to get response"}`);
      }

      // Get response text
      const assistantContent = await response.text();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: assistantContent,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      clearTimeout(timeoutId);
      clearTimeout(hardTimeoutId);
      if (err.name === "AbortError") {
        setError("Request was cancelled or timed out.");
      } else {
        setError(err.message || "Something went wrong");
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-300">
      <div className="max-w-4xl mx-auto w-full p-4 sm:p-6 flex flex-col h-screen">
        {/* Header */}
        <header className="flex items-center justify-between py-4 px-6 glass-strong rounded-2xl mb-4 fade-in">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/dashboard")}
              className="p-2 rounded-xl glass hover:glass-strong transition-all transform hover:scale-105"
              aria-label="Back to Dashboard"
            >
              <ArrowLeft
                size={20}
                className="text-purple-600 dark:text-purple-400"
              />
            </button>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent">
                AI Assistant
              </h1>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Manage tasks with natural language
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleNewChat}
              className="flex items-center gap-2 px-4 py-2 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="New Chat"
              disabled={isLoading}
            >
              <Plus
                size={20}
                className="text-purple-600 dark:text-purple-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors"
              />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
                New Chat
              </span>
            </button>
            <Bot
              size={24}
              className="text-purple-600 dark:text-purple-400 animate-pulse"
            />
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 px-2 py-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 fade-in">
              <div className="p-6 rounded-full glass-strong">
                <MessageSquare
                  size={48}
                  className="text-purple-600 dark:text-purple-400"
                />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-zinc-800 dark:text-zinc-200">
                  Start a conversation
                </h2>
                <p className="text-zinc-600 dark:text-zinc-400 mt-2 max-w-md">
                  Try saying things like:
                </p>
                <div className="flex flex-wrap gap-2 mt-4 justify-center">
                  {[
                    "Add a task to buy groceries",
                    "Show me my tasks",
                    "Mark task 1 as complete",
                    "Delete task 2",
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setInputValue(suggestion)}
                      className="px-4 py-2 text-sm glass hover:glass-strong rounded-full transition-all transform hover:scale-105 text-purple-700 dark:text-purple-300"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.role === "user" ? "flex-row-reverse" : ""
                } fade-in`}
              >
                <div
                  className={`p-2 rounded-full ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-purple-500 to-pink-500"
                      : "glass-strong"
                  }`}
                >
                  {message.role === "user" ? (
                    <User size={20} className="text-white" />
                  ) : (
                    <Bot
                      size={20}
                      className="text-purple-600 dark:text-purple-400"
                    />
                  )}
                </div>
                <div
                  className={`max-w-[80%] p-4 rounded-2xl ${
                    message.role === "user"
                      ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white"
                      : "glass-strong text-zinc-800 dark:text-zinc-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))
          )}

          {/* Loading indicator */}
          {isLoading && messages[messages.length - 1]?.role === "user" && (
            <div className="flex items-start gap-3 fade-in">
              <div className="p-2 rounded-full glass-strong">
                <Bot
                  size={20}
                  className="text-purple-600 dark:text-purple-400"
                />
              </div>
              <div className="glass-strong p-4 rounded-2xl">
                <div className="flex items-center gap-2">
                  <Loader2
                    size={16}
                    className="animate-spin text-purple-600 dark:text-purple-400"
                  />
                  <span className={`${loadingMessage.includes("longer") ? "text-amber-600 dark:text-amber-400" : "text-zinc-600 dark:text-zinc-400"}`}>
                    {loadingMessage}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Error display */}
          {error && (
            <div className="p-4 bg-red-100 dark:bg-red-900/50 border border-red-400 text-red-700 dark:text-red-300 rounded-xl fade-in">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form
          onSubmit={onSubmit}
          className="flex gap-3 p-4 glass-strong rounded-2xl mt-4"
        >
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message... (e.g., 'Add a task to call mom')"
            className="flex-1 px-4 py-3 rounded-xl glass focus:outline-none focus:ring-2 focus:ring-purple-500 dark:focus:ring-purple-400 text-zinc-800 dark:text-zinc-200 placeholder-zinc-500 dark:placeholder-zinc-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
