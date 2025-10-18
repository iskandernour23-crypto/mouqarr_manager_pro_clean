import { useEffect, useState } from 'react';
import api from '../api/client';

interface DashboardProps {
  onOpenAssistant: () => void;
}

interface StatCard {
  title: string;
  value: string | number;
  subtitle?: string;
}

const DashboardPage = ({ onOpenAssistant }: DashboardProps) => {
  const [stats, setStats] = useState<StatCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [residents, invoices, maintenance] = await Promise.all([
          api.get<unknown[]>('/residents'),
          api.get<unknown[]>('/invoices?status=overdue'),
          api.get<unknown[]>('/maintenance')
        ]);
        setStats([
          { title: 'عدد المقيمين', value: residents.length },
          { title: 'فواتير متأخرة', value: invoices.length, subtitle: 'يجب المتابعة اليوم' },
          { title: 'تذاكر الصيانة المفتوحة', value: (maintenance as any[]).filter((item) => item.status === 'open').length }
        ]);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-3">
        {loading
          ? Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="h-28 rounded-2xl bg-white border border-slate-200 animate-pulse" />
            ))
          : stats.map((item) => (
              <div key={item.title} className="rounded-2xl bg-white border border-slate-200 px-6 py-5 shadow-sm">
                <h3 className="text-sm text-slate-500">{item.title}</h3>
                <p className="text-2xl font-bold text-slate-900 mt-2">{item.value}</p>
                {item.subtitle ? <p className="text-xs text-amber-600 mt-1">{item.subtitle}</p> : null}
              </div>
            ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-white border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800">المهام السريعة</h3>
          <p className="text-sm text-slate-500 mt-2">استخدم المساعد الذكي لتنفيذ المهام اليومية</p>
          <div className="mt-4 space-y-3">
            {[
              'من المتأخرون هذا الأسبوع؟',
              'أنشئ تذكرة صيانة لتسريب الماء في شقة 4B',
              'هل هناك فواتير كهرباء أو ماء مستحقة اليوم؟'
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={onOpenAssistant}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-right hover:border-primary-300 hover:bg-primary-50"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800">الإجراءات القادمة</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-600">
            <li>مراجعة الفواتير المتأخرة والتواصل مع المقيمين.</li>
            <li>متابعة تذاكر الصيانة ذات الأولوية العالية.</li>
            <li>التأكد من تفعيل التنبيهات البريدية والبرقية.</li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
