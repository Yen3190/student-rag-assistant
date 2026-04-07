import { useEffect, useState } from "react";
import { getHistory, deleteHistoryChat } from "../services/api";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const userLocal = JSON.parse(localStorage.getItem("user") || "{}");
  const userEmail = userLocal?.email || "thunguyen465933@gmail.com";

  const load = async () => {
    if (!userEmail) {
      setHistory([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const res = await getHistory(userEmail);
      
      if (res && res.data && Array.isArray(res.data)) {
        setHistory(res.data);
      } else {
        setHistory([]);
      }
    } catch (err) {
      console.error("Lỗi khi tải lịch sử:", err);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const deleteOne = async (id) => {
    if (!window.confirm("Bạn có chắc chắn muốn xóa dòng lịch sử này?")) return;
    try {
      const res = await deleteHistoryChat(id);
      if (res.status === 200 || res.data?.message === "Deleted") {
        setHistory(prev => prev.filter(item => item.id !== id));
      }
    } catch (err) { 
      console.error("Lỗi khi xóa:", err);
      alert("Không thể xóa lúc này, vui lòng thử lại!"); 
    }
  };

  return (
    <div style={{ 
      padding: "20px",
      width: "100%", 
      boxSizing: "border-box", 
      minHeight: "100vh",
      backgroundColor: "#f0f2f5",
      display: "flex",
      justifyContent: "center"
    }}>
      
      <div className="card" style={{ 
        background: "#fff", 
        padding: "30px", 
        borderRadius: "15px", 
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        width: "100%",
        maxWidth: "1200px",
        boxSizing: "border-box",
        borderTop: "6px solid #92A8D1"
      }}>
        
        <h2 style={{ 
          margin: 0, 
          borderBottom: "2px solid #f0f0f0", 
          paddingBottom: "15px",
          color: "#92A8D1", 
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap"
        }}>
          <span>Lịch sử trò chuyện</span>
          <span style={{ fontSize: "14px", color: "#A2B5BB", fontWeight: "normal" }}>
            {userEmail}
          </span>
        </h2>

        {loading ? (
          <p style={{ textAlign: "center", marginTop: "40px", color: "#888" }}>Đang tải...</p>
        ) : history.length === 0 ? (
          <p style={{ textAlign: "center", marginTop: "40px", color: "#888" }}>Chưa có lịch sử trò chuyện nào!</p>
        ) : (
          <div className="history-container" style={{ marginTop: "10px" }}>
            {history.map((h) => (
              <div key={h.id} style={{ 
                marginTop: "20px", 
                borderBottom: "1px solid #f9f9f9", 
                position: 'relative',
                backgroundColor: "#fcfcfc",
                padding: "15px",
                borderRadius: "8px",
                marginBottom: "10px",
                transition: "0.3s"
              }}>
                <button 
                  onClick={() => deleteOne(h.id)} 
                  style={{ 
                    position: 'absolute', 
                    right: "10px", 
                    top: "10px", 
                    color: '#ff7875', 
                    cursor: 'pointer', 
                    background: 'none', 
                    border: 'none', 
                    fontSize: '20px'
                  }}
                  title="Xóa tin nhắn"
                >
                  ✖
                </button>
                <p style={{ margin: "0 0 10px 0", lineHeight: "1.6", paddingRight: "30px" }}>
                  <b style={{ color: "#92A8D1" }}>Câu hỏi:</b> {h.question}
                </p>
                <p style={{ margin: 0, color: "#555", lineHeight: "1.6" }}>
                  <b style={{ color: "#88B04B" }}>AI trả lời:</b> {h.answer}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default History;