"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { LogOut, Settings, MessageSquare, BarChart3, FolderOpen, ArrowLeft } from "lucide-react";
import { signOut } from "@/lib/auth-client";
import { useApp } from "@/context/AppContext";
import { useTranslation } from "@/hooks/useTranslation";
import ThemeToggle from "@/components/ThemeToggle";
import LanguageToggle from "@/components/LanguageToggle";
import BackgroundToggle from "@/components/BackgroundToggle";
import CategoryBadge from "@/components/CategoryBadge";

interface Category {
  id: number;
  name: string;
  color: string;
  icon?: string;
}

export default function CategoriesPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const settingsRef = useRef<HTMLDivElement>(null);
  const { backgroundMode, language } = useApp();
  const t = useTranslation();

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    color: "#8B5CF6",
    icon: "📁",
  });

  // Update body class based on background mode
  useEffect(() => {
    document.body.classList.remove('with-background', 'with-background-image');
    if (backgroundMode === 'gradient') {
      document.body.classList.add('with-background');
    } else if (backgroundMode === 'image') {
      document.body.classList.add('with-background-image');
    }
  }, [backgroundMode]);

  // Close settings when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(event.target as Node)) {
        setShowSettings(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch categories
  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/categories");
      if (!response.ok) throw new Error("Failed to fetch categories");
      const data = await response.json();
      setCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const url = editingCategory
        ? `/api/categories/${editingCategory.id}`
        : "/api/categories";
      const method = editingCategory ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to save category");

      setFormData({ name: "", color: "#8B5CF6", icon: "📁" });
      setShowForm(false);
      setEditingCategory(null);
      fetchCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  // Handle delete
  const handleDelete = async (id: number) => {
    if (!confirm(language === "ur"
      ? "کیا آپ اس کیٹیگری کو حذف کرنا چاہتے ہیں؟"
      : "Delete this category? Tasks will remain but be uncategorized."
    )) return;

    try {
      const response = await fetch(`/api/categories/${id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Failed to delete category");
      fetchCategories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    }
  };

  // Handle edit
  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      color: category.color,
      icon: category.icon || "📁",
    });
    setShowForm(true);
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await signOut();
      router.push("/");
    } catch (error: any) {
      setError(error.message || "Failed to log out");
    }
  };

  // Common emoji options
  const emojiOptions = [
    "📁", "💼", "🏠", "🛒", "❤️", "💪", "📚", "🎯",
    "⭐", "🔥", "💡", "✅", "🎨", "🎵", "🍕", "✈️",
  ];

  return (
    <div className="min-h-screen transition-colors duration-300">
      <div className="max-w-5xl mx-auto p-6 space-y-8 fade-in">
        {/* Header */}
        <header className="flex flex-col sm:flex-row justify-between items-center py-8 gap-6 glass-strong rounded-3xl px-8">
          <div className="text-center sm:text-left">
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center gap-2 text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 mb-3 transition-colors"
            >
              <ArrowLeft size={20} />
              <span>{language === "ur" ? "ڈیش بورڈ پر واپس" : "Back to Dashboard"}</span>
            </button>
            <h1 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent heading-animate flex items-center gap-3">
              <FolderOpen className="text-purple-600 dark:text-purple-400" size={40} />
              {language === "ur" ? "کیٹیگریز" : "Categories"}
            </h1>
            <p className="mt-3 text-lg font-medium bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent">
              {language === "ur" ? "اپنے کاموں کو کیٹیگریز میں ترتیب دیں" : "Organize your tasks with custom categories"}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Statistics button */}
            <button
              onClick={() => router.push("/dashboard/statistics")}
              className="flex items-center gap-2 px-4 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="Statistics"
            >
              <BarChart3 size={20} className="text-blue-600 dark:text-blue-400 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-blue-600 to-green-600 dark:from-blue-400 dark:to-green-400 bg-clip-text text-transparent">
                {t.statistics || "Statistics"}
              </span>
            </button>

            {/* AI Chat button */}
            <button
              onClick={() => router.push("/chat")}
              className="flex items-center gap-2 px-4 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="AI Chat"
            >
              <MessageSquare size={20} className="text-purple-600 dark:text-purple-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">AI Chat</span>
            </button>

            {/* Settings dropdown */}
            <div className="relative" ref={settingsRef}>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-3 rounded-xl glass hover:glass-strong transition-all transform hover:scale-110 hover:rotate-90 duration-300 group"
                aria-label="Settings"
              >
                <Settings size={22} className="text-purple-600 dark:text-purple-400 group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors" />
              </button>

              {showSettings && (
                <div className="absolute right-0 mt-3 w-64 glass-strong rounded-2xl p-4 z-10 fade-in border border-purple-300/20">
                  <div className="space-y-3">
                    <ThemeToggle />
                    <LanguageToggle />
                    <BackgroundToggle />
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-5 py-3 glass hover:glass-strong rounded-xl transition-all transform hover:scale-105 group"
              aria-label="Log out"
            >
              <LogOut size={20} className="text-red-500 dark:text-red-400 group-hover:rotate-12 transition-transform" />
              <span className="hidden sm:inline font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">{t.logOut}</span>
            </button>
          </div>
        </header>

        {/* Error Display */}
        {error && (
          <div className="p-4 glass-strong border border-red-400/50 text-red-700 dark:text-red-300 rounded-2xl fade-in">
            {error}
            <button onClick={() => setError(null)} className="ml-4 underline text-sm">
              {language === "ur" ? "بند کریں" : "Dismiss"}
            </button>
          </div>
        )}

        {/* New Category Button */}
        <div className="flex justify-end">
          <button
            onClick={() => {
              setShowForm(!showForm);
              setEditingCategory(null);
              setFormData({ name: "", color: "#8B5CF6", icon: "📁" });
            }}
            className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition-all transform hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50"
          >
            {showForm
              ? (language === "ur" ? "منسوخ کریں" : "Cancel")
              : (language === "ur" ? "+ نئی کیٹیگری" : "+ New Category")}
          </button>
        </div>

        {/* Category form */}
        {showForm && (
          <div className="glass-strong rounded-2xl p-6 card-3d">
            <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent mb-4">
              {editingCategory
                ? (language === "ur" ? "کیٹیگری میں ترمیم" : "Edit Category")
                : (language === "ur" ? "نئی کیٹیگری بنائیں" : "Create New Category")}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                  {language === "ur" ? "کیٹیگری کا نام" : "Category Name"}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder={language === "ur" ? "مثلاً: کام، ذاتی، خریداری" : "e.g., Work, Personal, Shopping"}
                  className="w-full px-4 py-3 border border-zinc-300 dark:border-zinc-600 rounded-xl focus:ring-2 focus:ring-purple-500 dark:bg-zinc-800 dark:text-white transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                  {language === "ur" ? "رنگ" : "Color"}
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="h-12 w-24 rounded-lg cursor-pointer border-2 border-zinc-300 dark:border-zinc-600"
                  />
                  <div className="flex gap-2">
                    {["#8B5CF6", "#EC4899", "#3B82F6", "#10B981", "#F59E0B", "#EF4444"].map((color) => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setFormData({ ...formData, color })}
                        className={`w-8 h-8 rounded-full transition-all ${formData.color === color ? "ring-2 ring-offset-2 ring-purple-500 dark:ring-offset-zinc-800" : ""}`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                  {language === "ur" ? "آئیکن (ایموجی)" : "Icon (Emoji)"}
                </label>
                <div className="grid grid-cols-8 gap-2 mb-3">
                  {emojiOptions.map((emoji) => (
                    <button
                      key={emoji}
                      type="button"
                      onClick={() => setFormData({ ...formData, icon: emoji })}
                      className={`p-2 text-2xl rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-all ${
                        formData.icon === emoji ? "bg-purple-200 dark:bg-purple-900/50 ring-2 ring-purple-500" : ""
                      }`}
                    >
                      {emoji}
                    </button>
                  ))}
                </div>
              </div>

              {/* Preview */}
              {formData.name && (
                <div className="p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-xl">
                  <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                    {language === "ur" ? "پیش نظارہ:" : "Preview:"}
                  </p>
                  <CategoryBadge
                    category={{ id: 0, name: formData.name, color: formData.color, icon: formData.icon }}
                    size="lg"
                  />
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white py-3 rounded-xl font-semibold transition-all transform hover:scale-105"
                >
                  {editingCategory
                    ? (language === "ur" ? "اپڈیٹ کریں" : "Update Category")
                    : (language === "ur" ? "بنائیں" : "Create Category")}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setEditingCategory(null);
                    setFormData({ name: "", color: "#8B5CF6", icon: "📁" });
                  }}
                  className="px-6 py-3 glass hover:glass-strong rounded-xl transition-all text-zinc-700 dark:text-zinc-300"
                >
                  {language === "ur" ? "منسوخ" : "Cancel"}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Categories list */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-zinc-600 dark:text-zinc-400">
              {language === "ur" ? "لوڈ ہو رہا ہے..." : "Loading categories..."}
            </p>
          </div>
        ) : categories.length === 0 ? (
          <div className="text-center py-16 glass-strong rounded-2xl">
            <FolderOpen size={64} className="mx-auto text-purple-400 mb-4" />
            <p className="text-xl text-zinc-600 dark:text-zinc-400">
              {language === "ur"
                ? "ابھی تک کوئی کیٹیگری نہیں۔ شروع کرنے کے لیے ایک بنائیں!"
                : "No categories yet. Create one to get started!"}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {categories.map((category) => (
              <div
                key={category.id}
                className="glass-strong rounded-2xl p-5 hover:shadow-xl transition-all transform hover:scale-[1.02] card-3d"
              >
                <div className="flex items-center justify-between">
                  <CategoryBadge category={category} size="lg" />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(category)}
                      className="px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-100 dark:text-blue-400 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                    >
                      {language === "ur" ? "ترمیم" : "Edit"}
                    </button>
                    <button
                      onClick={() => handleDelete(category.id)}
                      className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-100 dark:text-red-400 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                    >
                      {language === "ur" ? "حذف" : "Delete"}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
