import { Fragment, useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { useTranslation } from 'react-i18next';
import { useAiStore } from '../../../store/ai';

interface AiSettingsDrawerProps {
  open: boolean;
  onClose: () => void;
}

const AiSettingsDrawer = ({ open, onClose }: AiSettingsDrawerProps) => {
  const { t, i18n } = useTranslation();
  const settings = useAiStore((state) => state.settings);
  const updateSettings = useAiStore((state) => state.updateSettings);
  const [localTemperature, setLocalTemperature] = useState(settings.temperature);

  const handleLanguageChange = (lang: 'ar' | 'en') => {
    updateSettings({ language: lang });
    i18n.changeLanguage(lang);
  };

  const handleTemperatureChange = (value: number) => {
    setLocalTemperature(value);
    updateSettings({ temperature: value });
  };

  return (
    <Transition show={open} as={Fragment}>
      <Dialog onClose={onClose} className="relative z-50">
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden">
            <div className="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
              <Transition.Child
                as={Fragment}
                enter="transform transition ease-in-out duration-200"
                enterFrom="translate-x-full"
                enterTo="translate-x-0"
                leave="transform transition ease-in duration-200"
                leaveFrom="translate-x-0"
                leaveTo="translate-x-full"
              >
                <Dialog.Panel className="pointer-events-auto w-screen max-w-md bg-white dark:bg-slate-900 shadow-xl p-6 flex flex-col">
                  <Dialog.Title className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                    {t('ai.settings.title', 'إعدادات المساعد')}
                  </Dialog.Title>

                  <div className="space-y-6">
                    <section>
                      <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-3">
                        {t('ai.settings.language', 'لغة المساعد')}
                      </h4>
                      <div className="flex gap-2">
                        {(['ar', 'en'] as const).map((lang) => (
                          <button
                            key={lang}
                            type="button"
                            onClick={() => handleLanguageChange(lang)}
                            className={`px-3 py-2 text-sm rounded-full border ${
                              settings.language === lang
                                ? 'bg-primary-600 text-white border-primary-600'
                                : 'border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-200'
                            }`}
                          >
                            {lang === 'ar' ? 'العربية' : 'English'}
                          </button>
                        ))}
                      </div>
                    </section>

                    <section>
                      <label className="flex items-center justify-between text-sm font-semibold text-slate-700 dark:text-slate-200 mb-2">
                        <span>{t('ai.settings.model', 'النموذج')}</span>
                        <code className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs">{settings.model}</code>
                      </label>
                      <input
                        type="text"
                        className="w-full rounded border border-slate-300 dark:border-slate-700 bg-transparent px-3 py-2 text-sm"
                        value={settings.model}
                        onChange={(event) => updateSettings({ model: event.target.value })}
                      />
                    </section>

                    <section>
                      <label className="flex items-center justify-between text-sm font-semibold text-slate-700 dark:text-slate-200 mb-2">
                        <span>{t('ai.settings.temperature', 'درجة الإبداع')}</span>
                        <span className="text-xs text-slate-500">{localTemperature.toFixed(1)}</span>
                      </label>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.1}
                        value={localTemperature}
                        onChange={(event) => handleTemperatureChange(Number(event.target.value))}
                        className="w-full"
                      />
                    </section>

                    <section className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                          {t('ai.settings.tts', 'تشغيل القراءة الصوتية')}
                        </h4>
                        <p className="text-xs text-slate-500 mt-1">
                          {t('ai.settings.tts_hint', 'قريباً: استمع لردود المساعد عند توفر الاتصال.')} 
                        </p>
                      </div>
                      <input
                        type="checkbox"
                        checked={settings.enableTts}
                        onChange={(event) => updateSettings({ enableTts: event.target.checked })}
                        className="h-4 w-4"
                      />
                    </section>
                  </div>

                  <div className="mt-8 flex justify-end gap-2">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 rounded-full border border-slate-300 text-sm"
                    >
                      {t('common.close', 'إغلاق')}
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default AiSettingsDrawer;
