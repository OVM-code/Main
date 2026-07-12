import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './index.css'
import { getToken } from './api'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import PeopleSearch from './pages/PeopleSearch'
import SearchView from './pages/SearchView'

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />
  return <>{children}</>
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="/searches/:id"
          element={
            <RequireAuth>
              <SearchView />
            </RequireAuth>
          }
        />
        <Route
          path="/personen"
          element={
            <RequireAuth>
              <PeopleSearch />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
