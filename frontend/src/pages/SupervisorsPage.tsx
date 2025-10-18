import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';

interface Supervisor {
  id: number;
  department?: string;
  user: {
    id: number;
    name: string;
    email?: string;
    phone?: string;
  };
}

const SupervisorsPage = () => {
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [form, setForm] = useState({ name: '', phone: '', email: '', department: '' });

  const loadSupervisors = async () => {
    const response = await api.get<Supervisor[]>('/supervisors');
    setSupervisors(response);
  };

  useEffect(() => {
    loadSupervisors();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.name) return;
    await api.post('/supervisors', form);
    setForm({ name: '', phone: '', email: '', department: '' });
    loadSupervisors();
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 space-y-6">
      <section>
        <h2 className="text-lg font-semibold text-slate-800">إضافة مشرف</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-4">
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="اسم المشرف"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.phone}
            onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))}
            placeholder="رقم الجوال"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.email}
            onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
            placeholder="البريد الإلكتروني"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.department}
            onChange={(event) => setForm((prev) => ({ ...prev, department: event.target.value }))}
            placeholder="القسم"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <button
            type="submit"
            className="md:col-span-4 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white"
          >
            حفظ المشرف
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-slate-800">قائمة المشرفين</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {supervisors.map((supervisor) => (
            <div key={supervisor.id} className="rounded-2xl border border-slate-200 px-5 py-4">
              <div className="flex justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{supervisor.user.name}</p>
                  <p className="text-xs text-slate-500">{supervisor.department ?? 'غير محدد'}</p>
                </div>
                <span className="text-xs text-slate-400">#{supervisor.id}</span>
              </div>
              <div className="mt-3 text-xs text-slate-500 space-y-1">
                <p>الجوال: {supervisor.user.phone ?? '-'}</p>
                <p>البريد: {supervisor.user.email ?? '-'}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default SupervisorsPage;
