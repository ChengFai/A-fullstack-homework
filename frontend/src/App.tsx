import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAppSelector } from './store/hooks';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import './index.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated } = useAppSelector(state => state.auth);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 侧边栏 */}
      {isAuthenticated && (
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      )}

      {/* 主内容区域 */}
      <div className={`transition-all duration-300 ${isAuthenticated ? 'lg:ml-64' : ''}`}>
        {/* 顶部导航栏 */}
        <TopBar onMenuToggle={toggleSidebar} />

        {/* 页面内容 */}
        <main className="p-4 lg:p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
