import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';

interface Asset {
  id: number;
  name: string;
  category: string;
  serial_no: string;
  warranty_until?: string;
  status: string;
}

const AssetsPage = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [form, setForm] = useState({ name: '', category: '', serial_no: '', warranty_until: '', status: 'active' });

  const loadAssets = async () => {
    const response = await api.get<Asset[]>('/assets');
    setAssets(response);
  };

  useEffect(() => {
    loadAssets();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!form.name || !form.category || !form.serial_no) return;
    await api.post('/assets', {
      name: form.name,
      category: form.category,
      serial_no: form.serial_no,
      warranty_until: form.warranty_until || null,
      status: form.status
    });
    setForm({ name: '', category: '', serial_no: '', warranty_until: '', status: 'active' });
    loadAssets();
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">تسجيل أصل</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-3 md:grid-cols-5">
          <input
            value={form.name}
            onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
            placeholder="اسم الأصل"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.category}
            onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))}
            placeholder="التصنيف"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            value={form.serial_no}
            onChange={(event) => setForm((prev) => ({ ...prev, serial_no: event.target.value }))}
            placeholder="الرقم التسلسلي"
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <input
            type="date"
            value={form.warranty_until}
            onChange={(event) => setForm((prev) => ({ ...prev, warranty_until: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          />
          <select
            value={form.status}
            onChange={(event) => setForm((prev) => ({ ...prev, status: event.target.value }))}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="active">نشط</option>
            <option value="maintenance">تحت الصيانة</option>
            <option value="retired">موقوف</option>
          </select>
          <button
            type="submit"
            className="md:col-span-5 inline-flex justify-center rounded-xl bg-primary-600 px-4 py-2 text-sm text-white"
          >
            حفظ الأصل
          </button>
        </form>
      </section>

      <section className="rounded-2xl bg-white border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800">قائمة الأصول</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {assets.map((asset) => (
            <div key={asset.id} className="rounded-2xl border border-slate-200 px-5 py-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{asset.name}</p>
                  <p className="text-xs text-slate-500">{asset.category}</p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs ${
                    asset.status === 'active'
                      ? 'bg-emerald-100 text-emerald-700'
                      : asset.status === 'maintenance'
                      ? 'bg-amber-100 text-amber-600'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {asset.status}
                </span>
              </div>
              <div className="mt-3 text-xs text-slate-500 space-y-1">
                <p>الرقم التسلسلي: {asset.serial_no}</p>
                <p>الضمان حتى: {asset.warranty_until ?? 'غير محدد'}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default AssetsPage;
