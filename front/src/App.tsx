import { Routes, Route, Navigate } from 'react-router-dom';
import type { ReactNode } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Home from './pages/Home';
import Books from './pages/Books';
import BookDetail from './pages/BookDetail';
import Library from './pages/Library';
import Shelves from './pages/Shelves';
import ShelfDetail from './pages/ShelfDetail';
import Clubs from './pages/Clubs';
import ClubDetail from './pages/ClubDetail';
import ClubForum from './pages/ClubForum';
import Profile from './pages/Profile';

function Guard({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
      />

      <Route
        path="/"
        element={
          <Guard>
            <Layout>
              <Home />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/books"
        element={
          <Guard>
            <Layout>
              <Books />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/books/:id"
        element={
          <Guard>
            <Layout>
              <BookDetail />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/library"
        element={
          <Guard>
            <Layout>
              <Library />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/shelves"
        element={
          <Guard>
            <Layout>
              <Shelves />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/shelves/:id"
        element={
          <Guard>
            <Layout>
              <ShelfDetail />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/clubs"
        element={
          <Guard>
            <Layout>
              <Clubs />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/clubs/:id"
        element={
          <Guard>
            <Layout>
              <ClubDetail />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/clubs/:id/forum"
        element={
          <Guard>
            <Layout>
              <ClubForum />
            </Layout>
          </Guard>
        }
      />

      <Route
        path="/profile"
        element={
          <Guard>
            <Layout>
              <Profile />
            </Layout>
          </Guard>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
