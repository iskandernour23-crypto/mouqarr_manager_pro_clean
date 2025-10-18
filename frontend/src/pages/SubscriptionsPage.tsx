import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';

interface Subscription {
  id: number;
  resident_id: number;
  type: string;
  plan?: string;
  cycle: string;
  unit_price: number;
  next_due: string;
  active: boolean;
}

interface ResidentOption {
  id: number;
  label: string;
}

const SubscriptionsPage = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [residents, setResidents] = useState<ResidentOption[]>([]);
  const [form, setForm] = useState({ resident_id: '', type: 'electricity', plan: '', cycle: 'monthly', unit_price: '', next_due: '' });

  const loadData = async () => {
    const [subs, res] = await Promise.all([
      api.get<Subscription[]>('/subscriptions'),
      api.get<any[]>('/residents')
    ]);
    setSubscriptions(subs);
    setResidents(res.map((item: any) => ({ id: item.id, label: `${item.user.name} - ${item.unit_no}` })));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.resident_id || !form.next_due || !form.unit_price) return;
    await api.post('/subscriptions', {
      resident_id: Number(form.resident_id),
      type: form.type,
      plan: form.plan,
      cycle: form.cycle,
      unit_price: Number(form.unit_price),
      next_due: form.next_due,
      active: true
    });
    setForm({ resident_id: '', type: 'electricity', plan: '', cycle: 'monthly', unit_price: '', next_due: '' });
    loadData();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">اشتراك جديد</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-6">
          <select
            value={form.resident_id}
            onChange={(event) => setForm((prev) => ({ ...prev, resident_id: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="">اختر المقيم</option>
            {residents.map((resident) => (
              <option key={resident.id} value={resident.id}>
                {resident.label}
              </option>
            ))}
          </select>
          <select
            value={form.type}
            onChange={(event) => setForm((prev) => ({ ...prev, type: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="electricity">كهرباء</option>
            <option value="water">ماء</option>
            <option value="internet">إنترنت</option>
          </select>
          <input
            value={form.plan}
            onChange={(event) => setForm((prev) => ({ ...prev, plan: event.target.value }))}
            placeholder="الخطة"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <select
            value={form.cycle}
            onChange={(event) => setForm((prev) => ({ ...prev, cycle: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="monthly">شهري</option>
            <option value="weekly">أسبوعي</option>
            <option value="quarterly">ربع سنوي</option>
            <option value="yearly">سنوي</option>
          </select>
          <input
            type="number"
            value={form.unit_price}
            onChange={(event) => setForm((prev) => ({ ...prev, unit_price: event.target.value }))}
            placeholder="السعر"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            type="date"
            value={form.next_due}
            onChange={(event) => setForm((prev) => ({ ...prev, next_due: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <button
            type="submit"
            className="md:col-span-6 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white"
          >
            حفظ الاشتراك
          </button>
        </form>
      </section>

      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">الاشتراكات النشطة</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-right text-slate-500 border-b">
                <th className="py-2">المقيم</th>
                <th className="py-2">النوع</th>
                <th className="py-2">الخطة</th>
                <th className="py-2">الدورة</th>
                <th className="py-2">السعر</th>
                <th className="py-2">الاستحقاق القادم</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((subscription) => (
                <tr key={subscription.id} className="border-b last:border-none">
                  <td className="py-3">#{subscription.resident_id}</td>
                  <td className="py-3">{subscription.type}</td>
                  <td className="py-3">{subscription.plan ?? '-'}</td>
                  <td className="py-3">{subscription.cycle}</td>
                  <td className="py-3">{subscription.unit_price} ر.س</td>
                  <td className="py-3">{subscription.next_due}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default SubscriptionsPage;
