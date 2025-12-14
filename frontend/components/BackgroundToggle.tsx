import { Image as ImageIcon, Palette, X } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { useTranslation } from '@/hooks/useTranslation';

export default function BackgroundToggle() {
  const { backgroundMode, setBackgroundMode } = useApp();
  const t = useTranslation();

  const modes = [
    { value: 'none' as const, icon: X, label: t.none },
    { value: 'gradient' as const, icon: Palette, label: t.gradient },
    { value: 'image' as const, icon: ImageIcon, label: t.image },
  ];

  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs text-zinc-600 dark:text-zinc-400 mb-1">
        {t.background}
      </span>
      <div className="flex gap-1">
        {modes.map(({ value, icon: Icon, label }) => (
          <button
            key={value}
            onClick={() => setBackgroundMode(value)}
            className={`p-2 rounded-lg flex items-center gap-1 transition-all duration-300 ${
              backgroundMode === value
                ? 'bg-blue-500 text-white scale-105 shadow-lg'
                : 'bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300 dark:hover:bg-zinc-600'
            }`}
            aria-label={`${label} background`}
            title={label}
          >
            <Icon size={16} />
          </button>
        ))}
      </div>
    </div>
  );
}