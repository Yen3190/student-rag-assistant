import { Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

function Sidebar() {
  const user = JSON.parse(localStorage.getItem("user"));
  const userEmail = user?.email?.toLowerCase().trim();
  const admins = ["dangngochongyen40@gmail.com", "thunguyen465933@gmail.com"];
  const isAdmin = admins.includes(userEmail);
  
  const location = useLocation();
  const [sidebarHeight, setSidebarHeight] = useState("100vh");

  useEffect(() => {
    if (location.pathname === "/history" || location.pathname === "/users") {
      setSidebarHeight("auto");
    } else {
      setSidebarHeight("100vh");
    }
  }, [location]);

  const logout = () => {
    localStorage.removeItem("user");
    window.location.href = "/"; 
  };

  const linkStyle = { 
    color: "white", 
    textDecoration: "none",
    display: "block",
    padding: "10px 0",
    fontSize: "16px"
  };

  return (
    <div style={{
      width: "230px",
      background: "linear-gradient(180deg,#F7CAC9,#92A8D1)",
      height: sidebarHeight,
      color: "white",
      padding: "25px",
      boxShadow: "2px 0 10px rgba(0,0,0,0.1)"
    }}>
      <h2 style={{ marginBottom: "30px" }}>Student AI</h2>
      
      <p><Link style={linkStyle} to="/">Chat với AI</Link></p>

      <h4 style={{ marginTop: "30px", marginBottom: "10px", opacity: 0.8, fontSize: "13px", textTransform: "uppercase" }}>
        Hệ thống quản lý
      </h4>

      {isAdmin && (
        <>
          <p><Link style={linkStyle} to="/users">Quản lý người dùng</Link></p>
          <p><Link style={linkStyle} to="/documents">Quản lý tài liệu</Link></p>
        </>
      )}

      <p><Link style={linkStyle} to="/history">Lịch sử trò chuyện</Link></p>

      <button onClick={logout} style={{
          marginTop: "40px", padding: "12px", border: "none", borderRadius: "8px",
          background: "white", color: "#777", fontWeight: "bold", cursor: "pointer", width: "100%"
      }}>Đăng xuất</button>
    </div>
  );
}

export default Sidebar;