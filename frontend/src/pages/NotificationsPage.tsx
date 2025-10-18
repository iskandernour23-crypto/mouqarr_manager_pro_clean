import { useEffect, useState } from 'react';
import api from '../api/client';

interface NotificationItem {
  id: number;
  title: string;
  body: string;
  channel: string;
  sent_at: string;
  read: boolean;
}

const NotificationsPage = () => {
  const [items, setItems] = useState<NotificationItem[]>([]);

  const loadNotifications = async () => {
    const response = await api.get<NotificationItem[]>('/notifications');
    setItems(response);
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const markAsRead = async (id: number) => {
    await api.post(`/notifications/${id}/read`);
    loadNotifications();
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800">مركز التنبيهات</h2>
        <button onClick={loadNotifications} className="text-xs text-slate-500 underline">
          تحديث
        </button>
      </div>
      <div className="space-y-3">
        {items.map((notification) => (
          <div key={notification.id} className="rounded-2xl border border-slate-200 px-5 py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-800">{notification.title}</p>
                <p className="text-xs text-slate-500 mt-1">{notification.body}</p>
              </div>
              <div className="text-xs text-slate-400 text-left">
                <p>{notification.sent_at}</p>
                <p>القناة: {notification.channel}</p>
              </div>
            </div>
            {!notification.read ? (
              <button
                onClick={() => markAsRead(notification.id)}
                className="mt-3 rounded-xl bg-primary-50 px-3 py-1 text-xs text-primary-700"
              >
                تعليم كمقروء
              </button>
            ) : (
              <span className="mt-3 inline-block rounded-full bg-emerald-100 px-3 py-1 text-xs text-emerald-700">
                تمت قراءته
              </span>
            )}
          </div>
        ))}
        {items.length === 0 ? <p className="text-sm text-slate-500">لا توجد تنبيهات حالية.</p> : null}
      </div>
    </div>
  );
};

export default NotificationsPage;
