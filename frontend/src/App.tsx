import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import Dashboard from './components/Dashboard/Dashboard';
import { Toaster } from 'react-hot-toast';
import './App.css';

const AuthenticatedApp: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <AuthWrapper />;
  }

  return <Dashboard />;
};

const AuthWrapper: React.FC = () => {
  const { login, register } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (username: string, password: string) => {
    setLoading(true);
    try {
      await login(username, password);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (
    email: string,
    username: string,
    password: string,
    fullName?: string
  ) => {
    setLoading(true);
    try {
      await register(email, username, password, fullName);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {isLoginMode ? (
        <LoginForm
          onLogin={handleLogin}
          onSwitchToRegister={() => setIsLoginMode(false)}
          loading={loading}
        />
      ) : (
        <RegisterForm
          onRegister={handleRegister}
          onSwitchToLogin={() => setIsLoginMode(true)}
          loading={loading}
        />
      )}
    </>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="App">
        <AuthenticatedApp />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </AuthProvider>
  );
};

export default App;