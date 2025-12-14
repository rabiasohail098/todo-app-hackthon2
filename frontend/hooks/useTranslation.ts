import { useApp } from '@/context/AppContext';
import { translations } from '@/lib/translations';

export function useTranslation() {
  const { language } = useApp();
  return translations[language];
}
