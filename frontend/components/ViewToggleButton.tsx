import { List, Grid3X3, Calendar, Clock } from 'lucide-react';
import { useApp } from '@/context/AppContext';

type ViewMode = 'list' | 'grid' | 'calendar' | 'timeline';

interface ViewToggleButtonProps {
  currentView: ViewMode;
  onChangeView: (view: ViewMode) => void;
}

export default function ViewToggleButton({ currentView, onChangeView }: ViewToggleButtonProps) {
  const { language } = useApp();
  
  // Translations
  const translations = {
    en: {
      listView: "List View",
      gridView: "Grid View",
      calendarView: "Calendar View",
      timelineView: "Timeline View",
    },
    ur: {
      listView: "فہرست نظارہ",
      gridView: "گرڈ نظارہ",
      calendarView: "کیلینڈر نظارہ",
      timelineView: "ٹائم لائن نظارہ",
    }
  };

  const t = translations[language];

  const views: { id: ViewMode; icon: any; label: string }[] = [
    { id: 'list', icon: List, label: t.listView },
    { id: 'grid', icon: Grid3X3, label: t.gridView },
    // { id: 'calendar', icon: Calendar, label: t.calendarView },
    // { id: 'timeline', icon: Clock, label: t.timelineView },
  ];

  return (
    <div className="flex border border-zinc-300 dark:border-zinc-700 rounded-lg bg-zinc-100 dark:bg-zinc-800">
      {views.map((view) => {
        const Icon = view.icon;
        return (
          <button
            key={view.id}
            onClick={() => onChangeView(view.id)}
            className={`p-2 rounded-md transition-colors flex items-center gap-2 min-w-[100px] ${
              currentView === view.id
                ? 'bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 shadow'
                : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-200 dark:hover:bg-zinc-700'
            }`}
            aria-label={view.label}
            title={view.label}
          >
            <Icon size={16} />
            <span className="hidden sm:inline text-xs">{view.id}</span>
          </button>
        );
      })}
    </div>
  );
}