import { useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import {
  HomeIcon,
  UsersIcon,
  ClipboardDocumentListIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  BellIcon,
  Cog6ToothIcon,
  BuildingOffice2Icon
} from '@heroicons/react/24/outline';
import DashboardPage from './pages/DashboardPage';
import ResidentsPage from './pages/ResidentsPage';
import SupervisorsPage from './pages/SupervisorsPage';
import SubscriptionsPage from './pages/SubscriptionsPage';
import InvoicesPage from './pages/InvoicesPage';
import AssetsPage from './pages/AssetsPage';
import MaintenancePage from './pages/MaintenancePage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';
import ChatDock from './features/ai/components/ChatDock';

const navItems = [
  { to: '/', label: 'اللوحة الرئيسية', icon: HomeIcon },
  { to: '/residents', label: 'المقيمون', icon: UsersIcon },
  { to: '/supervisors', label: 'المشرفون', icon: BuildingOffice2Icon },
  { to: '/subscriptions', label: 'الاشتراكات', icon: ClipboardDocumentListIcon },
  { to: '/invoices', label: 'الفواتير', icon: CurrencyDollarIcon },
  { to: '/assets', label: 'الأصول', icon: WrenchScrewdriverIcon },
  { to: '/maintenance', label: 'الصيانة', icon: WrenchScrewdriverIcon },
  { to: '/notifications', label: 'التنبيهات', icon: BellIcon },
  { to: '/settings', label: 'الإعدادات', icon: Cog6ToothIcon }
];

const App = () => {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="flex">
        <aside className="hidden md:flex md:w-64 flex-col bg-white border-l border-slate-200 min-h-screen">
          <div className="px-6 py-5 border-b border-slate-200">
            <h1 className="text-lg font-semibold text-primary-600">مقر برو</h1>
            <p className="text-xs text-slate-500 mt-1">إدارة العقارات والذكاء الاصطناعي في لوحة واحدة</p>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border border-primary-200'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="flex-1">
          <header className="flex items-center justify-between bg-white border-b border-slate-200 px-6 py-4">
            <div>
              <h2 className="text-xl font-semibold text-slate-800">مرحبًا بك في مركز التحكم</h2>
              <p className="text-sm text-slate-500">تابع المقيمين والفواتير والصيانة والتنبيهات بضغطة زر</p>
            </div>
            <button
              onClick={() => setChatOpen(true)}
              className="rounded-full border border-primary-200 px-4 py-2 text-sm text-primary-600 hover:bg-primary-50"
            >
              فتح المساعد الذكي
            </button>
          </header>

          <div className="p-6 space-y-6">
            <Routes>
              <Route path="/" element={<DashboardPage onOpenAssistant={() => setChatOpen(true)} />} />
              <Route path="/residents" element={<ResidentsPage />} />
              <Route path="/supervisors" element={<SupervisorsPage />} />
              <Route path="/subscriptions" element={<SubscriptionsPage />} />
              <Route path="/invoices" element={<InvoicesPage />} />
              <Route path="/assets" element={<AssetsPage />} />
              <Route path="/maintenance" element={<MaintenancePage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>

      <ChatDock open={chatOpen} onOpenChange={setChatOpen} />
    </div>
  );
};

export default App;
