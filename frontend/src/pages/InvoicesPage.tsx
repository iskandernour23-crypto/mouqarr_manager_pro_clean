import { useEffect, useState } from 'react';
import api from '../api/client';

interface Invoice {
  id: number;
  resident_id: number;
  subscription_id?: number;
  amount: number;
  status: string;
  due_date: string;
  reference: string;
  paid_at?: string;
}

const statuses = [
  { value: 'due', label: 'مستحقة' },
  { value: 'paid', label: 'مدفوعة' },
  { value: 'overdue', label: 'متأخرة' }
];

const InvoicesPage = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const loadInvoices = async (status?: string) => {
    setLoading(true);
    try {
      const query = status ? `?status=${status}` : '';
      const response = await api.get<Invoice[]>(`/invoices${query}`);
      setInvoices(response);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  const handlePay = async (invoiceId: number) => {
    await api.post(`/invoices/${invoiceId}/pay-mock`);
    loadInvoices(statusFilter || undefined);
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <h2 className="text-lg font-semibold text-slate-800">الفواتير</h2>
        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value);
              loadInvoices(event.target.value || undefined);
            }}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            <option value="">جميع الحالات</option>
            {statuses.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => loadInvoices(statusFilter || undefined)}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm"
          >
            تحديث
          </button>
        </div>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-right text-slate-500 border-b">
              <th className="py-2">المرجع</th>
              <th className="py-2">المقيم</th>
              <th className="py-2">المبلغ</th>
              <th className="py-2">الحالة</th>
              <th className="py-2">الاستحقاق</th>
              <th className="py-2">دفع</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-400">
                  جارٍ تحميل الفواتير...
                </td>
              </tr>
            ) : (
              invoices.map((invoice) => (
                <tr key={invoice.id} className="border-b last:border-none">
                  <td className="py-3 font-semibold text-slate-700">{invoice.reference}</td>
                  <td className="py-3">#{invoice.resident_id}</td>
                  <td className="py-3">{invoice.amount} ر.س</td>
                  <td className="py-3">
                    <span
                      className={`rounded-full px-3 py-1 text-xs ${
                        invoice.status === 'paid'
                          ? 'bg-emerald-100 text-emerald-700'
                          : invoice.status === 'overdue'
                          ? 'bg-rose-100 text-rose-600'
                          : 'bg-amber-100 text-amber-600'
                      }`}
                    >
                      {invoice.status}
                    </span>
                  </td>
                  <td className="py-3">{invoice.due_date}</td>
                  <td className="py-3">
                    <button
                      disabled={invoice.status === 'paid'}
                      onClick={() => handlePay(invoice.id)}
                      className="rounded-xl bg-primary-600 px-3 py-1 text-xs text-white disabled:opacity-40"
                    >
                      سداد وهمي
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InvoicesPage;
