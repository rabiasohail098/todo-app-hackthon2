"use client";

import { useState, useEffect, useRef } from "react";
import { MessageSquare, Send, Loader2, Plus, History, Bot, Sparkles, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import ThemeToggle from "@/components/ThemeToggle";
import LanguageDropdown from "@/components/LanguageDropdown";
import ConfirmDialog from "@/components/ConfirmDialog";
import { signOut } from "@/lib/auth-client";
import { authFetch } from "@/lib/api";
import { LogOut } from "lucide-react";
import { useTranslation } from "@/hooks/useTranslation";
import { useApp } from "@/context/AppContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  preview?: string;
}

export default function ChatPage() {
  const router = useRouter();
  const t = useTranslation();
  const { language } = useApp();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [conversationToDelete, setConversationToDelete] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      console.log("Loading conversations...");
      const response = await authFetch("/api/chat/conversations");
      console.log("Response status:", response.status);
      if (response.ok) {
        const data = await response.json();
        console.log("Conversations data:", data);
        console.log("Conversations array:", data.conversations);
        setConversations(data.conversations || []);
      } else if (response.status === 401) {
        // Unauthorized - redirect to sign-in
        console.log("Unauthorized access, redirecting to sign-in");
        router.push("/auth/sign-in");
      } else {
        console.error("Failed to load conversations:", response.status);
        // Show error message to user
        const errorData = await response.json().catch(() => ({}));
        console.error("Error details:", errorData);
      }
    } catch (error) {
      console.error("Network error loading conversations:", error);
    }
  };

  const loadConversation = async (convId: string) => {
    try {
      console.log("Loading conversation:", convId);
      const response = await authFetch(`/api/chat/conversations/${convId}/messages`);
      console.log("Load conversation response:", response.status);
      if (response.ok) {
        const data = await response.json();
        console.log("Conversation messages:", data);
        setMessages(data.messages || []);
        setConversationId(convId);
        setShowHistory(false);
      } else {
        console.error("Failed to load conversation:", response.status);
      }
    } catch (error) {
      console.error("Error loading conversation:", error);
    }
  };

  const deleteConversation = async (convId: string) => {
    try {
      console.log("Deleting conversation:", convId);
      const response = await authFetch(`/api/chat/conversations/${convId}`, {
        method: "DELETE",
      });

      if (response.ok || response.status === 204) {
        console.log("Conversation deleted successfully");
        // If deleted conversation was active, clear messages
        if (conversationId === convId) {
          setMessages([]);
          setConversationId(null);
        }
        // Refresh conversations list
        await loadConversations();
      } else {
        console.error("Failed to delete conversation:", response.status);
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
    }
  };

  const startNewChat = async () => {
    console.log('New Chat button clicked!');
    try {
      setMessages([]);
      setConversationId(null);
      setShowHistory(false);
      setInputMessage('');
      // Refresh conversations list
      await loadConversations();
    } catch (error) {
      console.error('Error starting new chat:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    // Add user message to UI immediately (optimistic update)
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await authFetch("/api/chat/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId,
          language: language,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Unauthorized - redirect to sign-in
          console.log("Unauthorized access, redirecting to sign-in");
          router.push("/auth/sign-in");
          return;
        } else if (response.status === 500) {
          // Server error - likely backend issue
          throw new Error("Server is temporarily unavailable. Please try again later.");
        } else {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
      }

      const data = await response.json();

      // Update conversation ID if it's a new conversation
      if (data.conversation_id && !conversationId) {
        console.log("New conversation created:", data.conversation_id);
        setConversationId(data.conversation_id);
        await loadConversations(); // Refresh conversation list
      }

      // Add assistant message to UI
      const assistantMsg: Message = {
        id: data.message_id,
        role: "assistant",
        content: data.response,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Determine error type and provide appropriate message
      let errorMessage = t.sorryError;
      if (error instanceof Error) {
        if (error.message.includes("fetch") || error.message.includes("network")) {
          errorMessage = "Unable to connect to the server. Please check your internet connection.";
        } else if (error.message.includes("500") || error.message.includes("502") || error.message.includes("503")) {
          errorMessage = "The server is temporarily unavailable. Please try again later.";
        } else if (error.message.includes("401")) {
          errorMessage = "Authentication expired. Please sign in again.";
          // Redirect to sign-in after a delay
          setTimeout(() => {
            router.push("/auth/sign-in");
          }, 2000);
        } else {
          errorMessage = error.message || t.sorryError;
        }
      }

      // Add error message
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: errorMessage,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSignOut = async () => {
    await signOut();
    router.push("/");
  };

  return (
    <div className="h-screen relative overflow-hidden" dir={language === 'ur' ? 'rtl' : 'ltr'}>
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-20 left-10 w-20 h-20 bg-purple-500/20 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-pink-500/20 rounded-full blur-xl animate-pulse delay-75"></div>
        <div className="absolute bottom-40 left-1/4 w-24 h-24 bg-blue-500/20 rounded-full blur-xl animate-pulse delay-150"></div>
        <div className="absolute bottom-20 right-1/3 w-28 h-28 bg-cyan-500/20 rounded-full blur-xl animate-pulse"></div>
      </div>

      {/* Header */}
      <div className="relative z-20 glass-strong border-b border-purple-200/30 dark:border-purple-700/30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/30">
              <Bot className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
                {t.aiTaskAssistant}
              </h1>
              <p className="text-sm text-purple-600 dark:text-purple-300">
                {t.manageTasksNaturally}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push("/dashboard")}
              className="px-4 py-2 rounded-xl glass hover:glass-strong transition-all text-purple-700 dark:text-purple-300 font-medium"
            >
              {t.dashboard}
            </button>
            <div className="glass-strong rounded-xl p-2">
              <ThemeToggle />
            </div>
            <LanguageDropdown />
            <button
              onClick={handleSignOut}
              className="glass-strong p-2 rounded-xl hover:bg-red-500/20 transition-all"
              title="Sign Out"
            >
              <LogOut size={20} className="text-red-500" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-4 relative z-10 overflow-auto" style={{ maxHeight: 'calc(100vh - 88px)' }}>
        <div className="grid grid-cols-12 gap-4 relative z-10">
          {/* Sidebar - Chat History */}
          <div className={`col-span-12 md:col-span-3 glass-strong rounded-3xl p-4 border-2 border-purple-200/40 dark:border-purple-700/40 overflow-y-auto transition-all relative z-10 ${showHistory ? '' : 'hidden md:block'}`} style={{ touchAction: 'auto', maxHeight: 'calc(100vh - 120px)', minHeight: '400px' }}>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent flex items-center gap-2">
                <History size={18} />
                {t.chatHistory}
              </h2>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowHistory(false);
                }}
                className="md:hidden glass p-2 rounded-lg cursor-pointer relative z-20"
                type="button"
              >
                ✕
              </button>
            </div>

            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                startNewChat();
              }}
              className="w-full mb-4 px-4 py-3 bg-gradient-to-br from-green-500 via-emerald-500 to-teal-500 hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 text-white font-bold rounded-xl shadow-xl shadow-green-500/40 hover:shadow-2xl hover:shadow-green-600/60 transition-all transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2 relative z-20 cursor-pointer border-2 border-white/20"
              type="button"
            >
              <Plus size={20} className="font-bold" strokeWidth={3} />
              <span className="text-base">{t.newChat}</span>
            </button>

            <div className="space-y-1.5">
              {conversations.length === 0 ? (
                <div className="text-center py-6 text-purple-500 dark:text-purple-400 text-xs">
                  {language === 'ur' ? 'ابھی تک کوئی گفتگو نہیں' : 'No conversations yet'}
                  <br />
                  <span className="text-[10px]">{language === 'ur' ? 'نئی چیٹ شروع کریں' : 'Start a new chat'}</span>
                </div>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={`w-full rounded-lg transition-all relative z-10 group ${
                      conversationId === conv.id
                        ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-2 border-purple-400/50"
                        : "glass hover:glass-strong"
                    }`}
                  >
                    <div className="flex items-start gap-2 px-3 py-2">
                      <MessageSquare size={14} className="mt-0.5 text-purple-500 flex-shrink-0" />
                      <div
                        className="flex-1 min-w-0 cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          loadConversation(conv.id);
                        }}
                      >
                        <p className="text-xs font-medium text-purple-900 dark:text-purple-100 truncate">
                          {t.chat} {new Date(conv.created_at).toLocaleDateString()}
                        </p>
                        <p className="text-[10px] text-purple-600 dark:text-purple-400">
                          {new Date(conv.updated_at).toLocaleTimeString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setConversationToDelete(conv.id);
                          setDeleteDialogOpen(true);
                        }}
                        type="button"
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-500/20 rounded flex-shrink-0"
                        title={language === 'ur' ? 'حذف کریں' : 'Delete'}
                      >
                        <Trash2 size={12} className="text-red-500" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="col-span-12 md:col-span-9 flex flex-col relative z-10" style={{ minHeight: '400px' }}>
            {/* Robot Visual */}
            <div className="glass-strong rounded-3xl border-2 border-purple-200/40 dark:border-purple-700/40 flex flex-col overflow-hidden relative z-10">
              {/* Chat Messages */}
              <div className="overflow-y-auto p-4 space-y-4" style={{ maxHeight: 'calc(100vh - 280px)', minHeight: '300px' }}>
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center text-center space-y-3 py-3">
                    {/* Simple Friendly Robot Character */}
                    <div className="relative scale-75" style={{ animation: 'float 3s ease-in-out infinite' }}>
                      {/* Antenna with light */}
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 flex flex-col items-center">
                        <div className="w-1 h-6 bg-purple-400 rounded-full"></div>
                        <div className="w-4 h-4 bg-pink-400 rounded-full animate-pulse shadow-lg shadow-pink-400"></div>
                      </div>

                      {/* Robot Head */}
                      <div className="w-24 h-24 mx-auto bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-2xl relative mb-2 border-4 border-white/20">
                        {/* Face Screen */}
                        <div className="absolute inset-3 bg-cyan-400/30 backdrop-blur-sm rounded-xl border-2 border-cyan-300/50">
                          {/* Big Friendly Eyes */}
                          <div className="absolute top-4 left-1/2 -translate-x-1/2 flex gap-3">
                            <div className="relative">
                              <div className="w-6 h-6 bg-white rounded-full"></div>
                              <div className="absolute top-1 left-1 w-4 h-4 bg-purple-600 rounded-full" style={{ animation: 'blink 4s ease-in-out infinite' }}></div>
                            </div>
                            <div className="relative">
                              <div className="w-6 h-6 bg-white rounded-full"></div>
                              <div className="absolute top-1 left-1 w-4 h-4 bg-purple-600 rounded-full" style={{ animation: 'blink 4s ease-in-out infinite' }}></div>
                            </div>
                          </div>

                          {/* Happy Smile */}
                          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-10 h-5 border-b-4 border-pink-400 rounded-full"></div>
                        </div>

                        {/* Ear Lights */}
                        <div className="absolute top-8 -left-2 w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400"></div>
                        <div className="absolute top-8 -right-2 w-3 h-3 bg-blue-400 rounded-full animate-pulse shadow-lg shadow-blue-400" style={{ animationDelay: '0.5s' }}></div>
                      </div>

                      {/* Robot Body */}
                      <div className="relative">
                        {/* Waving Left Arm */}
                        <div className="absolute -left-10 top-2" style={{ animation: 'wave 2s ease-in-out infinite', transformOrigin: 'top center' }}>
                          <div className="w-4 h-14 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full shadow-lg"></div>
                          <div className="w-5 h-5 bg-pink-500 rounded-full mt-1 shadow-lg"></div>
                        </div>

                        {/* Static Right Arm */}
                        <div className="absolute -right-10 top-2">
                          <div className="w-4 h-14 bg-gradient-to-b from-purple-500 to-pink-500 rounded-full shadow-lg"></div>
                          <div className="w-5 h-5 bg-pink-500 rounded-full mt-1 shadow-lg"></div>
                        </div>

                        {/* Torso */}
                        <div className="w-28 h-32 mx-auto bg-gradient-to-br from-purple-500 via-pink-500 to-purple-600 rounded-2xl shadow-2xl relative border-4 border-white/20">
                          {/* Chest Panel */}
                          <div className="absolute inset-4 bg-white/10 backdrop-blur-sm rounded-xl border-2 border-white/20">
                            {/* Glowing Heart/Core */}
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full shadow-2xl shadow-cyan-400/80" style={{ animation: 'heartbeat 2s ease-in-out infinite' }}>
                              <Bot className="w-5 h-5 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                            </div>
                          </div>

                          {/* Status Lights */}
                          <div className="absolute top-2 left-1/2 -translate-x-1/2 flex gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400"></div>
                            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse shadow-lg shadow-yellow-400" style={{ animationDelay: '0.3s' }}></div>
                            <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse shadow-lg shadow-pink-400" style={{ animationDelay: '0.6s' }}></div>
                          </div>
                        </div>

                        {/* Legs */}
                        <div className="flex gap-4 justify-center mt-2">
                          <div className="w-5 h-16 bg-gradient-to-b from-purple-600 to-pink-600 rounded-full shadow-lg"></div>
                          <div className="w-5 h-16 bg-gradient-to-b from-purple-600 to-pink-600 rounded-full shadow-lg"></div>
                        </div>

                        {/* Feet */}
                        <div className="flex gap-4 justify-center">
                          <div className="w-7 h-4 bg-pink-600 rounded-full shadow-xl"></div>
                          <div className="w-7 h-4 bg-pink-600 rounded-full shadow-xl"></div>
                        </div>
                      </div>

                      {/* Floating Sparkles */}
                      <Sparkles className="absolute -top-4 -right-8 w-6 h-6 text-pink-400 animate-bounce" />
                      <Sparkles className="absolute top-16 -left-8 w-5 h-5 text-purple-400 animate-bounce" style={{ animationDelay: '0.5s' }} />
                      <Sparkles className="absolute -bottom-4 right-0 w-4 h-4 text-cyan-400 animate-bounce" style={{ animationDelay: '1s' }} />
                    </div>

                    <div className="max-w-2xl">
                      <h3 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent mb-1">
                        {t.hiImYourAI}
                      </h3>
                      <p className="text-xs text-purple-700 dark:text-purple-300 mb-2">
                        {t.canHelpManage}
                      </p>
                      <div className="grid grid-cols-2 gap-1.5 text-xs text-purple-700 dark:text-purple-300">
                        <div className="glass px-2 py-1.5 rounded-lg hover:glass-strong transition-all">
                          <span className="text-base mr-1">➕</span>
                          <span className="font-medium text-[11px]">{t.addTaskExample}</span>
                        </div>
                        <div className="glass px-2 py-1.5 rounded-lg hover:glass-strong transition-all">
                          <span className="text-base mr-1">📋</span>
                          <span className="font-medium text-[11px]">{t.showAllTasksExample}</span>
                        </div>
                        <div className="glass px-2 py-1.5 rounded-lg hover:glass-strong transition-all">
                          <span className="text-base mr-1">✅</span>
                          <span className="font-medium text-[11px]">{t.markCompleteExample}</span>
                        </div>
                        <div className="glass px-2 py-1.5 rounded-lg hover:glass-strong transition-all">
                          <span className="text-base mr-1">🔍</span>
                          <span className="font-medium text-[11px]">{t.showCompletedExample}</span>
                        </div>
                      </div>

                      <div className="mt-2 grid grid-cols-1 gap-1.5 text-xs text-purple-700 dark:text-purple-300">
                        <div className="glass px-2 py-1.5 rounded-lg hover:glass-strong transition-all">
                          <span className="text-base mr-1">✍️</span>
                          <span className="font-medium text-[11px]">{language === 'ur' ? 'Auto description لکھیں' : 'Auto-generate description'}</span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setShowHistory(!showHistory);
                      }}
                      className="md:hidden glass px-6 py-3 rounded-xl flex items-center gap-2 hover:glass-strong transition-all cursor-pointer relative z-20"
                      type="button"
                    >
                      <History size={18} />
                      {t.viewHistory}
                    </button>

                    {/* Arrow pointing down to input */}
                    <div className="mt-4 flex flex-col items-center animate-bounce">
                      <p className="text-purple-600 dark:text-purple-400 font-bold text-sm mb-1">
                        {language === 'ur' ? '👇 نیچے ٹائپ کریں' : '👇 Type Below'}
                      </p>
                      <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </div>
                  </div>
                ) : (
                  <>
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        <div
                          className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-lg ${
                            message.role === "user"
                              ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white"
                              : "glass-strong border-2 border-purple-200/40 dark:border-purple-700/40 text-purple-900 dark:text-purple-100"
                          }`}
                        >
                          {message.role === "assistant" && (
                            <div className="flex items-center gap-2 mb-2">
                              <Bot size={16} className="text-purple-500" />
                              <span className="text-xs font-semibold text-purple-600 dark:text-purple-400">{t.aiAssistant}</span>
                            </div>
                          )}
                          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="glass-strong border-2 border-purple-200/40 dark:border-purple-700/40 rounded-2xl px-5 py-3">
                          <Loader2 className="w-5 h-5 animate-spin text-purple-600 dark:text-purple-300" />
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t-4 border-purple-400/50 dark:border-purple-600/50 p-3 bg-gradient-to-b from-purple-50/80 to-white/80 dark:from-purple-900/30 dark:to-purple-950/30 backdrop-blur-md relative z-20 shadow-lg">
                {/* Example Prompts */}
                <div className="mb-2 flex flex-wrap gap-1.5 justify-center relative z-20">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setInputMessage(language === 'ur' ? 'گروسری خریدنے کا کام شامل کریں' : 'Add a task to buy groceries');
                    }}
                    className="text-xs px-3 py-1.5 glass hover:glass-strong rounded-lg text-purple-700 dark:text-purple-300 transition-all hover:scale-105 cursor-pointer"
                    disabled={isLoading}
                    type="button"
                  >
                    ➕ {language === 'ur' ? 'کام شامل کریں' : 'Add task'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setInputMessage(language === 'ur' ? 'میرے تمام کام دکھائیں' : 'Show me all my tasks');
                    }}
                    className="text-xs px-3 py-1.5 glass hover:glass-strong rounded-lg text-purple-700 dark:text-purple-300 transition-all hover:scale-105 cursor-pointer"
                    disabled={isLoading}
                    type="button"
                  >
                    📋 {language === 'ur' ? 'تمام کام' : 'All tasks'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setInputMessage(language === 'ur' ? 'مکمل شدہ کام دکھائیں' : 'Show completed tasks');
                    }}
                    className="text-xs px-3 py-1.5 glass hover:glass-strong rounded-lg text-purple-700 dark:text-purple-300 transition-all hover:scale-105 cursor-pointer"
                    disabled={isLoading}
                    type="button"
                  >
                    ✅ {language === 'ur' ? 'مکمل شدہ' : 'Completed'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setInputMessage(language === 'ur' ? 'نامکمل کام دکھائیں' : 'Show incomplete tasks');
                    }}
                    className="text-xs px-3 py-1.5 glass hover:glass-strong rounded-lg text-purple-700 dark:text-purple-300 transition-all hover:scale-105 cursor-pointer"
                    disabled={isLoading}
                    type="button"
                  >
                    ⏳ {language === 'ur' ? 'نامکمل' : 'Incomplete'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      setInputMessage(language === 'ur' ? 'description خود لکھو' : 'Generate description for task: Buy groceries');
                    }}
                    className="text-xs px-3 py-1.5 glass hover:glass-strong rounded-lg text-purple-700 dark:text-purple-300 transition-all hover:scale-105 cursor-pointer"
                    disabled={isLoading}
                    type="button"
                  >
                    ✍️ {language === 'ur' ? 'Auto description' : 'Auto description'}
                  </button>
                </div>

                {/* Input Field Label */}
                <div className="mb-1.5 flex items-center gap-2">
                  <MessageSquare size={16} className="text-purple-600 dark:text-purple-400" />
                  <label className="text-xs font-bold text-purple-700 dark:text-purple-300">
                    {language === 'ur' ? 'یہاں اپنا پیغام ٹائپ کریں:' : 'Type your message here:'}
                  </label>
                </div>

                {/* Input Field */}
                <div className="flex gap-2 relative z-20">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={t.typeYourMessage}
                    className="flex-1 px-4 py-3 bg-white dark:bg-purple-950/50 border-3 border-purple-400/60 dark:border-purple-500/60 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-500/50 focus:border-purple-500 text-purple-900 dark:text-purple-100 placeholder-purple-500/70 dark:placeholder-purple-400/70 text-sm font-medium shadow-lg shadow-purple-200/50 dark:shadow-purple-900/50"
                    disabled={isLoading}
                    autoFocus
                  />
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      sendMessage();
                    }}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-gradient-to-br from-purple-600 via-pink-600 to-purple-700 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:via-pink-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 shadow-xl shadow-purple-500/40 hover:shadow-2xl hover:shadow-purple-600/60 transform hover:scale-105 disabled:hover:scale-100 cursor-pointer font-bold"
                    type="button"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span className="text-sm">{t.send}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={() => {
          if (conversationToDelete) {
            deleteConversation(conversationToDelete);
            setConversationToDelete(null);
          }
        }}
        title={language === 'ur' ? 'گفتگو حذف کریں؟' : 'Delete Conversation?'}
        message={language === 'ur'
          ? 'کیا آپ واقعی اس گفتگو کو حذف کرنا چاہتے ہیں؟ یہ عمل واپس نہیں ہو سکتا۔'
          : 'Are you sure you want to delete this conversation? This action cannot be undone.'}
        confirmText={language === 'ur' ? 'حذف کریں' : 'Delete'}
        cancelText={language === 'ur' ? 'منسوخ کریں' : 'Cancel'}
        isDangerous={true}
      />
    </div>
  );
}
