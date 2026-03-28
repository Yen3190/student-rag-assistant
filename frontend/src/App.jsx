import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Chat from "./pages/Chat";
import Documents from "./pages/Documents";
import History from "./pages/History";
import Login from "./pages/Login";
import UserManagement from "./pages/UserManagement";
import { updateProfile } from "./services/api"; // Import hàm cập nhật profile

function App() {
  const userString = localStorage.getItem("user");
  const user = userString ? JSON.parse(userString) : null;

  // Tự động cập nhật thông tin người dùng lên Backend mỗi khi vào App
  useEffect(() => {
    if (user && user.email) {
      const profileData = {
        email: user.email,
        fullname: user.displayName || user.fullname || "Sinh viên VLU",
        major: "Information Technology",
        university: "Van Lang University"
      };
      
      updateProfile(profileData)
        .then(() => console.log("Đã cập nhật danh sách người dùng!"))
        .catch((err) => console.error("Lỗi cập nhật profile:", err));
    }
  }, [userString]); // Chạy lại nếu thông tin user thay đổi

  if (!user) return <Login />;

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>
        <Sidebar />
        <div style={{ flex: 1, backgroundColor: "#f9f9f9" }}>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/history" element={<History />} />
            <Route path="/users" element={<UserManagement />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;