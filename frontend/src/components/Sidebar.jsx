import { Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

function Sidebar({ isOpen, onClose, onToggle }) {
  const user = JSON.parse(localStorage.getItem("user"));
  const userEmail = user?.email?.toLowerCase().trim();
  const admins = ["dangngochongyen40@gmail.com", "thunguyen465933@gmail.com"];
  const isAdmin = admins.includes(userEmail);
  
  const location = useLocation();

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

  useEffect(() => {
    if (window.innerWidth <= 768) {
      onClose();
    }
  }, [location]);

  return (
    <>
      <style>{`
        /* Nút menu - chỉ hiện trên mobile */
        .menu-btn {
          position: fixed;
          top: 15px;
          left: 15px;
          background: linear-gradient(135deg, #F7CAC9, #92A8D1);
          border: none;
          color: white;
          font-size: 24px;
          cursor: pointer;
          padding: 10px 15px;
          border-radius: 8px;
          z-index: 1000;
          box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        /* Overlay tối đằng sau */
        .sidebar-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.5);
          z-index: 1001;
        }

        /* Sidebar drawer */
        .sidebar-drawer {
          position: fixed;
          top: 0;
          left: -300px;
          width: 260px;
          height: 100%;
          background: linear-gradient(180deg, #F7CAC9, #92A8D1);
          color: white;
          padding: 25px;
          box-shadow: 2px 0 10px rgba(0,0,0,0.1);
          transition: left 0.3s ease;
          z-index: 1002;
          overflow-y: auto;
        }

        /* Khi mở */
        .sidebar-drawer.open {
          left: 0;
        }

        /* Nút đóng */
        .close-btn {
          position: absolute;
          top: 15px;
          right: 20px;
          background: none;
          border: none;
          color: white;
          font-size: 28px;
          cursor: pointer;
          padding: 0;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .close-btn:hover {
          opacity: 0.8;
        }

        /* DESKTOP: sidebar luôn hiện cố định bên trái */
        @media (min-width: 769px) {
          .menu-btn {
            display: none !important;
          }
          .sidebar-overlay {
            display: none !important;
          }
          .sidebar-drawer {
            left: 0 !important;
            position: fixed;
          }
          .close-btn {
            display: none !important;
          }
        }

        /* MOBILE: sidebar ẩn hoàn toàn, chỉ hiện khi có class open */
        @media (max-width: 768px) {
          .menu-btn {
            display: block !important;
          }
          .sidebar-drawer {
            left: -300px !important;
          }
          .sidebar-drawer.open {
            left: 0 !important;
          }
        }

        
      `}</style>

      <button className="menu-btn" onClick={onToggle}>
        ☰
      </button>

      {isOpen && window.innerWidth <= 768 && (
        <div className="sidebar-overlay" onClick={onClose}></div>
      )}

      <div className={`sidebar-drawer ${isOpen ? "open" : ""}`}>
        <button className="close-btn" onClick={onClose}>×</button>
        
        <h2 style={{ marginBottom: "30px", marginTop: "0" }}>Student AI</h2>
        
        <p><Link style={linkStyle} to="/" onClick={onClose}>Chat với AI</Link></p>

        <h4 style={{ marginTop: "30px", marginBottom: "10px", opacity: 0.8, fontSize: "13px", textTransform: "uppercase" }}>
          Hệ thống quản lý
        </h4>

        {isAdmin && (
          <>
            <p><Link style={linkStyle} to="/users" onClick={onClose}>Quản lý người dùng</Link></p>
            <p><Link style={linkStyle} to="/documents" onClick={onClose}>Quản lý tài liệu</Link></p>
          </>
        )}

        <p><Link style={linkStyle} to="/history" onClick={onClose}>Lịch sử trò chuyện</Link></p>

        <button onClick={logout} style={{
            marginTop: "40px", padding: "12px", border: "none", borderRadius: "8px",
            background: "white", color: "#777", fontWeight: "bold", cursor: "pointer", width: "100%"
        }}>Đăng xuất</button>
      </div>
    </>
  );
}

export default Sidebar;