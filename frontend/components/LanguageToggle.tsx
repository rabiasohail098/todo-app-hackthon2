import { Globe } from 'lucide-react';
import { useApp } from '@/context/AppContext';

export default function LanguageToggle() {
  const { language, toggleLanguage } = useApp();

  return (
    <button
      onClick={toggleLanguage}
      className="p-2 rounded-lg bg-zinc-200 dark:bg-zinc-700 hover:bg-zinc-300 dark:hover:bg-zinc-600 transition-colors flex items-center gap-2"
      aria-label={language === 'en' ? 'Switch to Urdu' : 'Switch to English'}
    >
      <Globe size={20} className="text-zinc-700 dark:text-zinc-300" />
      <span className="text-sm font-medium">
        {language === 'en' ? 'UR' : 'EN'}
      </span>
    </button>
  );
}