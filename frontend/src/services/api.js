import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  withCredentials: false,
});

// --- CHAT & FILE ---
export const askQuestion = (question, email) => API.post("/chat", { question, email });

export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file); 
  return API.post("/upload", form);
};

export const getFiles = () => API.get("/pdfs");

export const deleteFile = (name) => API.delete(`/file/${encodeURIComponent(name)}`);

export const rebuildAI = () => API.post("/rebuild");

export const getHistory = (email) => API.get(`/history?email=${encodeURIComponent(email)}`);

export const deleteHistoryChat = (id) => API.delete(`/history/${id}`);

export const getAllUsers = () => API.get("/admin/users");

export const deleteUser = (email) => API.delete(`/admin/user/${encodeURIComponent(email)}`);

export const updateProfile = (data) => API.post("/user/update_profile", data);

