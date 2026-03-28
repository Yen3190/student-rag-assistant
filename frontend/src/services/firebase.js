import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCaU2yeTUSqj77IZZ3GBKt7NRgxmAmE3GE",
  authDomain: "student-rag-assistant.firebaseapp.com",
  projectId: "student-rag-assistant",
  storageBucket: "student-rag-assistant.firebasestorage.app",
  messagingSenderId: "370210311003",
  appId: "1:370210311003:web:bdd02c18d7b3700d9be87e",
  measurementId: "G-47KY2G77NG"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

export const provider = new GoogleAuthProvider();