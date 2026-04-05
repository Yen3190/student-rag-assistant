import { useEffect, useState } from "react";
import { uploadFile, getFiles, deleteFile, rebuildAI } from "../services/api";

function Documents() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const user = JSON.parse(localStorage.getItem("user"));
  const admins = ["dangngochongyen40@gmail.com", "thunguyen465933@gmail.com"];
  const isAdmin = admins.includes(user?.email);

  const loadFiles = async () => {
    try {
      const res = await getFiles();
      const data = res?.data;
      setFiles(Array.isArray(data?.pdf_files) ? data.pdf_files : []);
    } catch (err) {
      console.error("Không thể tải danh sách file", err);
      setFiles([]);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleSave = async () => {
    if (!selectedFile) {
      alert("Chưa chọn file!");
      return;
    }

    try {
      setIsUploading(true); 
      
      await uploadFile(selectedFile);
      

      await rebuildAI();

      alert("Tài liệu đã được lưu");
      setSelectedFile(null);
      await loadFiles();
    } catch (err) {
      console.error(err);
      alert("Lỗi xử lý tài liệu!");
    } finally {
      setIsUploading(false);
    }
  };

  const remove = async (filename) => {
    if (!window.confirm(`Chắc chắn xóa file "${filename}" chứ?`)) return;

    try {
      await deleteFile(filename);
      await rebuildAI(); 
      await loadFiles();
    } catch (err) {
      console.error(err);
      alert("Xóa thất bại rồi!");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <div className="card">
        <h2>Documents</h2>

        {isAdmin && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px",
              marginBottom: "20px",
              background: "var(--serenity-soft)",
              padding: "15px",
              borderRadius: "12px",
            }}
          >
            <label style={{ fontWeight: "600" }}>Thêm tài liệu mới cho AI:</label>

            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              style={{ padding: "5px" }}
            />

            <button
              className="btn"
              onClick={handleSave}
              disabled={isUploading}
              style={{ width: "fit-content" }}
            >
              {isUploading ? " Đang xử lý..." : " Lưu tài liệu"}
            </button>
            
            {isUploading && (
              <small style={{ color: "#666", fontStyle: "italic" }}>
                Vui lòng đợi một chút để AI phân tích nội dung file ...
              </small>
            )}
          </div>
        )}

        <hr style={{ border: "1px solid #eee", margin: "20px 0" }} />

        <h3>Danh sách đã tải lên:</h3>

        <ul style={{ padding: 0, listStyle: "none" }}>
          {files.length > 0 ? (
            files.map((f) => (
              <li
                key={f}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "10px",
                  borderBottom: "1px solid #eee",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span style={{ wordBreak: "break-word" }}>📄 {f}</span>

                {isAdmin && (
                  <button
                    className="btn"
                    style={{
                      background: "#ff6b6b",
                      padding: "5px 10px",
                      fontSize: "12px",
                      whiteSpace: "nowrap",
                    }}
                    onClick={() => remove(f)}
                  >
                    Xóa
                  </button>
                )}
              </li>
            ))
          ) : (
            <p style={{ color: "#999" }}>Chưa có tài liệu nào trong kho.</p>
          )}
        </ul>
      </div>
    </div>
  );
}

export default Documents;