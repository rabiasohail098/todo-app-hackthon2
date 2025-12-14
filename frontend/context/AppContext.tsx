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
  backgroundEnabled: boolean;
  toggleBackground: () => void;
  backgroundMode: BackgroundMode;
  setBackgroundMode: (mode: BackgroundMode) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppWrapper({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [language, setLanguage] = useState<Language>('en');
  const [backgroundEnabled, setBackgroundEnabled] = useState<boolean>(true);
  const [backgroundMode, setBackgroundModeState] = useState<BackgroundMode>('gradient');

  useEffect(() => {
    // Check for saved theme in localStorage or default to system preference
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const initialTheme = savedTheme || systemTheme;
    
    setTheme(initialTheme);
    document.documentElement.classList.toggle('dark', initialTheme === 'dark');
  }, []);

  useEffect(() => {
    // Check for saved language in localStorage
    const savedLanguage = localStorage.getItem('language') as Language | null;
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  useEffect(() => {
    // Check for saved background preference
    const savedBackground = localStorage.getItem('backgroundEnabled');
    if (savedBackground !== null) {
      setBackgroundEnabled(savedBackground === 'true');
    }

    // Check for saved background mode
    const savedMode = localStorage.getItem('backgroundMode') as BackgroundMode | null;
    if (savedMode) {
      setBackgroundModeState(savedMode);
    }
  }, []);

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
      backgroundEnabled,
      toggleBackground,
      backgroundMode,
      setBackgroundMode
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