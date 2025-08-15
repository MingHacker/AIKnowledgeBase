import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  DocumentTextIcon, 
  ChatBubbleLeftRightIcon, 
  CogIcon, 
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline';

interface HeaderProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

const Header: React.FC<HeaderProps> = ({ currentPage, onPageChange }) => {
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Documents', id: 'documents', icon: DocumentTextIcon },
    { name: 'Chat', id: 'chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Settings', id: 'settings', icon: CogIcon },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900">
                🤖 AI Knowledge Base
              </h1>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => onPageChange(item.id)}
                  className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                    currentPage === item.id
                      ? 'text-primary-600 bg-primary-50'
                      : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-2" />
                  {item.name}
                </button>
              );
            })}
          </nav>

          {/* User menu */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              Welcome, {user?.full_name || user?.username}
            </span>
            <button
              onClick={logout}
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-red-600 hover:bg-red-50 transition-colors duration-200"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;