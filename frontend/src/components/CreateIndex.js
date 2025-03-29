import React, {useEffect, useState} from "react";
import {Button, Form, ListGroup, Container, Spinner} from "react-bootstrap";
import {getFiles} from "../api/GetFiles";
import {useNavigate} from "react-router-dom";
import Nav from "react-bootstrap/Nav";
import {isAdmin} from "../api/IsAdmin";

const CreateIndex = () => {
    const [files, setFiles] = useState([]);
    const [processing, setProcessing] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchFiles = async () => {
            const is_admin = await isAdmin(navigate);
            if (!is_admin) {
                navigate("/chat")
            }
            const files = (await getFiles(navigate)).map((name, index) => ({
                id: index + 1,
                name: name,
                checked: false
            }));
            setFiles(files || []);
        };
        fetchFiles();
    }, [navigate]);

    const toggleFile = (id) => {
        setFiles(files.map(file => file.id === id ? {...file, checked: !file.checked} : file));
    };

    const uploadIndex = () => {
        const selectedFiles = files.filter(file => file.checked);
        if (selectedFiles.length === 0) {
            alert("Выберите хотя бы один файл для загрузки индекса");
            return;
        }
        console.log("Загружаем индекс для файлов:", selectedFiles);
        alert(`Индекс загружен для: ${selectedFiles.map(f => f.name).join(", ")}`);
    };

    return (
        <Container className="mt-4">
            <Nav
                activeKey="/index"
                variant="tabs"
            >
                <Nav.Item>
                    <Nav.Link href="/chat">Чат</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/file">Добавить файл</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/create_index">Создать индекс</Nav.Link>
                </Nav.Item>
                <Nav.Item>
                    <Nav.Link href="/login">Выйти из аккаунта</Nav.Link>
                </Nav.Item>
            </Nav>

            <h3>Выберите файлы для загрузки индекса</h3>
            <ListGroup>
                {files.map(file => (
                    <ListGroup.Item key={file.id}>
                        <Form.Check
                            type="checkbox"
                            label={file.name}
                            checked={file.checked}
                            onChange={() => toggleFile(file.id)}
                        />
                    </ListGroup.Item>
                ))}
            </ListGroup>

            <Button onClick={uploadIndex} disabled={processing} className="mt-4">
                {processing && <Spinner animation="border" size="sm" className="me-2"/>}
                Загрузить индекс
            </Button>

        </Container>
    );
};

export default CreateIndex;