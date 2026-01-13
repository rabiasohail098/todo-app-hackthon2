'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark';
type Language = 'en' | 'ur';
type BackgroundMode = 'none' | 'gradient' | 'image';

interface AppContextType {
  theme: Theme;
  toggleTheme: () => void;
  language: Language;
  toggleLanguage: () => void;
  setLanguage: (lang: Language) => void;
  backgroundEnabled: boolean;
  toggleBackground: () => void;
  backgroundMode: BackgroundMode;
  setBackgroundMode: (mode: BackgroundMode) => void;
  isInitialized: boolean;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

// Helper to safely get localStorage values (handles SSR)
function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return 'light';
  const saved = localStorage.getItem('theme') as Theme | null;
  if (saved) return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getInitialLanguage(): Language {
  if (typeof window === 'undefined') return 'en';
  return (localStorage.getItem('language') as Language) || 'en';
}

function getInitialBackgroundEnabled(): boolean {
  if (typeof window === 'undefined') return true;
  const saved = localStorage.getItem('backgroundEnabled');
  return saved === null ? true : saved === 'true';
}

function getInitialBackgroundMode(): BackgroundMode {
  if (typeof window === 'undefined') return 'gradient';
  return (localStorage.getItem('backgroundMode') as BackgroundMode) || 'gradient';
}

export function AppWrapper({ children }: { children: ReactNode }) {
  // Initialize state with localStorage values to prevent cascading re-renders
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [language, setLanguage] = useState<Language>(getInitialLanguage);
  const [backgroundEnabled, setBackgroundEnabled] = useState<boolean>(getInitialBackgroundEnabled);
  const [backgroundMode, setBackgroundModeState] = useState<BackgroundMode>(getInitialBackgroundMode);
  const [isInitialized, setIsInitialized] = useState(false);

  // Single useEffect to apply theme class and mark as initialized
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    setIsInitialized(true);
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
    localStorage.setItem('theme', newTheme);
  };

  const toggleLanguage = () => {
    const newLanguage = language === 'en' ? 'ur' : 'en';
    setLanguage(newLanguage);
    localStorage.setItem('language', newLanguage);
  };

  const changeLanguage = (lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  const toggleBackground = () => {
    const newBackgroundEnabled = !backgroundEnabled;
    setBackgroundEnabled(newBackgroundEnabled);
    localStorage.setItem('backgroundEnabled', String(newBackgroundEnabled));
  };

  const setBackgroundMode = (mode: BackgroundMode) => {
    setBackgroundModeState(mode);
    localStorage.setItem('backgroundMode', mode);
  };

  return (
    <AppContext.Provider value={{
      theme,
      toggleTheme,
      language,
      toggleLanguage,
      setLanguage: changeLanguage,
      backgroundEnabled,
      toggleBackground,
      backgroundMode,
      setBackgroundMode,
      isInitialized
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppWrapper');
  }
  return context;
}