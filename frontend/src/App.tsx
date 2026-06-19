import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/auth";
import Login from "@/pages/Login";
import Layout from "@/components/Layout";
import Resumes from "@/pages/Resumes";
import Parse from "@/pages/Parse";
import Recommend from "@/pages/Recommend";
import Positions from "@/pages/Positions";
import Users from "@/pages/Users";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/resumes" replace />} />
        <Route path="parse" element={<Parse />} />
        <Route path="recommend" element={<Recommend />} />
        <Route path="resumes" element={<Resumes />} />
        <Route path="positions" element={<Positions />} />
        <Route path="users" element={<Users />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}