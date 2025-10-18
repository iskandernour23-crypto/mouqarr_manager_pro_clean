import { FormEvent, ReactNode, useState } from 'react';
import { useAuthStore } from '../store/auth';

interface AuthGateProps {
  children: ReactNode;
}

const AuthGate = ({ children }: AuthGateProps) => {
  const { token, login } = useAuthStore();
  const [identifier, setIdentifier] = useState('admin@example.com');
  const [error, setError] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await login(identifier);
      setError(undefined);
    } catch (err) {
      setError('تعذر تسجيل الدخول، تحقق من البيانات.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-2xl bg-white border border-slate-200 px-6 py-8 space-y-4 shadow-lg">
          <h1 className="text-lg font-semibold text-slate-800 text-center">الدخول إلى مقر برو</h1>
          <p className="text-xs text-slate-500 text-center">أدخل البريد أو رقم الجوال المسجل للمسؤول.</p>
          <input
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            className="w-full rounded-xl border border-slate-200 px-4 py-2 text-sm"
            placeholder="admin@example.com"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-primary-600 px-4 py-2 text-sm text-white disabled:opacity-40"
          >
            {loading ? 'جارٍ الدخول...' : 'تسجيل الدخول'}
          </button>
          {error ? <p className="text-xs text-rose-500 text-center">{error}</p> : null}
          <p className="text-[10px] text-slate-400 text-center">المستخدم الافتراضي: admin@example.com</p>
        </form>
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthGate;
