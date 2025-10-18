import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';

interface Resident {
  id: number;
  unit_no: string;
  start_date: string;
  end_date?: string;
  user: {
    id: number;
    name: string;
    phone?: string;
    email?: string;
  };
}

const ResidentsPage = () => {
  const [residents, setResidents] = useState<Resident[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: '', phone: '', email: '', unit_no: '', start_date: '' });
  const [assignUnit, setAssignUnit] = useState('');
  const [selectedResident, setSelectedResident] = useState<number | null>(null);

  const loadResidents = async () => {
    setLoading(true);
    try {
      const response = await api.get<Resident[]>('/residents');
      setResidents(response);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResidents();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.name || !form.unit_no || !form.start_date) return;
    await api.post('/residents', form);
    setForm({ name: '', phone: '', email: '', unit_no: '', start_date: '' });
    loadResidents();
  };

  const handleAssign = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedResident || !assignUnit) return;
    await api.post(`/residents/${selectedResident}/assign-unit`, null, { params: { unit_no: assignUnit } });
    setAssignUnit('');
    setSelectedResident(null);
    loadResidents();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">إضافة مقيم جديد</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-5">
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="اسم المقيم"
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
            value={form.unit_no}
            onChange={(event) => setForm((prev) => ({ ...prev, unit_no: event.target.value }))}
            placeholder="رقم الوحدة"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            type="date"
            value={form.start_date}
            onChange={(event) => setForm((prev) => ({ ...prev, start_date: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <button
            type="submit"
            className="md:col-span-5 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white hover:bg-primary-700"
          >
            حفظ المقيم
          </button>
        </form>
      </section>

      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800">سجل المقيمين</h2>
          {loading ? <span className="text-xs text-slate-400">جارٍ التحميل...</span> : null}
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-right text-slate-500 border-b">
                <th className="py-2">الاسم</th>
                <th className="py-2">الوحدة</th>
                <th className="py-2">الجوال</th>
                <th className="py-2">البريد</th>
                <th className="py-2">تاريخ البدء</th>
                <th className="py-2">إعادة التعيين</th>
              </tr>
            </thead>
            <tbody>
              {residents.map((resident) => (
                <tr key={resident.id} className="border-b last:border-none">
                  <td className="py-3 font-medium text-slate-700">{resident.user.name}</td>
                  <td className="py-3">{resident.unit_no}</td>
                  <td className="py-3">{resident.user.phone ?? '-'}</td>
                  <td className="py-3">{resident.user.email ?? '-'}</td>
                  <td className="py-3">{resident.start_date}</td>
                  <td className="py-3">
                    <button
                      onClick={() => setSelectedResident(resident.id)}
                      className="text-xs text-primary-600 hover:underline"
                    >
                      اختيار
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {selectedResident ? (
          <form onSubmit={handleAssign} className="mt-4 flex gap-3">
            <input
              value={assignUnit}
              onChange={(event) => setAssignUnit(event.target.value)}
              placeholder="الوحدة الجديدة"
              className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
            />
            <button type="submit" className="rounded-xl bg-primary-600 px-4 py-2 text-sm text-white">
              حفظ
            </button>
          </form>
        ) : null}
      </section>
    </div>
  );
};

export default ResidentsPage;
