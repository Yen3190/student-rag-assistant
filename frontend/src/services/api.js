import axios from "axios";

// 1. Cấu hình BASE_URL
const BASE_URL = "https://thu-student-rag.azurewebsites.net";

const API = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ================= 2. API CHAT & HISTORY =================

export const askQuestion = (question, email) => {
  return API.post("/chat", { question, email });
};

// Lấy lịch sử chat 
export const getHistory = (email) => {
  return API.get("/history", { 
    params: { email: email } 
  });
};

// Xóa một tin nhắn trong lịch sử
export const deleteHistoryChat = (id) => {
  return API.delete(`/history/${id}`);
};

// ================= 3. QUẢN LÝ TÀI LIỆU (PDF) =================

// Lấy danh sách file PDF
export const getFiles = () => {
  return API.get("/pdfs");
};

// Upload file PDF (Dùng FormData)
export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return API.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// Xóa file PDF
export const deleteFile = (name) => {
  return API.delete(`/file/${encodeURIComponent(name)}`);
};

// Yêu cầu AI học lại dữ liệu mới
export const rebuildAI = () => {
  return API.post("/rebuild");
};

// ================= 4. QUẢN LÝ NGƯỜI DÙNG (ADMIN) =================

export const updateProfile = (data) => {
  return API.post("/user/update_profile", data);
};

export const getAllUsers = () => {
  return API.get("/admin/users");
};

export const deleteUser = (email) => {
  return API.delete(`/admin/user/${encodeURIComponent(email)}`);
};

export default API;