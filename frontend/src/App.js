import {BrowserRouter as Router, Routes, Route, Navigate} from "react-router-dom";
import LoginForm from "./components/Login";
import RegisterForm from "./components/Register";
import ChatComponent from "./components/Chat";
import CreateIndex from "./components/CreateIndex";
import OcrUpload from "./components/OcrUpload";

function App() {
    const isAuthenticated = localStorage.getItem("access_token") && localStorage.getItem("refresh_token");

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginForm/>}/>
                <Route path="register" element={<RegisterForm/>}/>
                <Route path="/chat" element={<ChatComponent/>}/>
                <Route path="/create" element={<CreateIndex/>}/>
                <Route path="/file" element={<OcrUpload/>}/>
                <Route path="*" element={<Navigate to={isAuthenticated ? "/chat" : "/login"}/>}/>
            </Routes>
        </Router>
    );
}

export default App
