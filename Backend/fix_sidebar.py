
import os

file_path = r"..\..\Frontend\src\components\Sidebar.js"

content = r"""import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  FileText, 
  Shield, 
  AlertTriangle, 
  Users, 
  Settings,
  LogOut,
  CheckCircle
} from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    // Force logout process
    console.log("Logout clicked");
    logout();
    // Force hard navigation to clear any stuck state
    window.location.href = '/login';
  };

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/frameworks', icon: Shield, label: 'Frameworks' },
    { path: '/evidence', icon: FileText, label: 'Evidence' },
    { path: '/risk', icon: AlertTriangle, label: 'Risk Register' },
    { path: '/access-reviews', icon: Users, label: 'Access Reviews' },
    { path: '/policies', icon: CheckCircle, label: 'Policies' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-64 bg-gray-900 text-white h-screen flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold">AssuRisk</h1>
        <p className="text-sm text-gray-400">Compliance Platform</p>
      </div>

      <nav className="flex-1 p-4 overflow-y-auto">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 rounded-lg w-full text-gray-300 hover:bg-red-600 hover:text-white transition-colors cursor-pointer"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
"""

try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Updated {os.path.abspath(file_path)}")
except Exception as e:
    print(f"ERROR: Failed to update file. {e}")
