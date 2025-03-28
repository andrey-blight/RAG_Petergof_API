import React, {useEffect, useState} from "react";
import {Form, Button, Spinner, Alert, Container} from "react-bootstrap";
import axios from "axios";
import Nav from "react-bootstrap/Nav";
import {isAdmin} from "../api/IsAdmin";
import {useNavigate} from "react-router-dom";

const OcrUpload = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchAllow = async () => {
            const is_admin = await isAdmin(navigate)
            if (!is_admin) {
                navigate("/chat")
            }
        };
        fetchAllow();
    }, [navigate]);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            setError("Please select a file.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("/api/ocr", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setResult(response.data.text);
        } catch (err) {
            setError("Failed to process file. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="mt-4">

            <Nav
                activeKey="/file"
                variant="tabs"
            >
                <Nav.Item>
                    <Nav.Link href="/chat">Чат</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/file">Добавить файл</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/index">Создать индекс</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/login">Выйти из аккаунта</Nav.Link>
                </Nav.Item>
            </Nav>

            <h2>Загрузить файл</h2>
            <Form onSubmit={handleSubmit}>
                <Form.Group controlId="formFile" className="mb-3">
                    <Form.Label>Выберите файл</Form.Label>
                    <Form.Control type="file" onChange={handleFileChange}/>
                </Form.Group>
                <Button type="submit" variant="primary" disabled={loading}>
                    {loading ? <Spinner animation="border" size="sm"/> : "Отправить"}
                </Button>
            </Form>
            {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            {result && <Alert variant="success" className="mt-3">{result}</Alert>}
        </Container>
    );
};

export default OcrUpload;