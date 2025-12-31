"use client";

import { useState, useRef, useEffect } from "react";
import { Languages, Check } from "lucide-react";
import { useApp } from "@/context/AppContext";
import type { Language } from "@/lib/translations";

interface LanguageOption {
  code: Language;
  name: string;
  nativeName: string;
  flag: string;
}

const languages: LanguageOption[] = [
  { code: "en", name: "English", nativeName: "English", flag: "🇬🇧" },
  { code: "ur", name: "Urdu", nativeName: "اردو", flag: "🇵🇰" },
];

export default function LanguageDropdown() {
  const { language, setLanguage } = useApp();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLanguage = languages.find((lang) => lang.code === language);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLanguageChange = (langCode: Language) => {
    setLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Dropdown Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 glass-strong rounded-xl hover:bg-purple-500/10 transition-all"
        title="Change Language"
      >
        <Languages size={20} className="text-purple-600 dark:text-purple-400" />
        <span className="text-2xl">{currentLanguage?.flag}</span>
        <span className="hidden sm:inline text-sm font-medium text-purple-700 dark:text-purple-300">
          {currentLanguage?.nativeName}
        </span>
        <svg
          className={`w-4 h-4 text-purple-600 dark:text-purple-400 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 glass-strong border-2 border-purple-200/40 dark:border-purple-700/40 rounded-2xl shadow-2xl shadow-purple-500/20 overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="p-2">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  language === lang.code
                    ? "bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-2 border-purple-400/50"
                    : "hover:bg-purple-500/10"
                }`}
              >
                <span className="text-2xl">{lang.flag}</span>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-purple-900 dark:text-purple-100">
                    {lang.nativeName}
                  </div>
                  <div className="text-xs text-purple-600 dark:text-purple-400">
                    {lang.name}
                  </div>
                </div>
                {language === lang.code && (
                  <Check size={20} className="text-purple-600 dark:text-purple-400" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
