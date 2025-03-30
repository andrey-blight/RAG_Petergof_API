import React, {useEffect, useState} from "react";
import {Button, Form, ListGroup, Container, Spinner} from "react-bootstrap";
import {getFiles} from "../api/GetFiles";
import {useNavigate} from "react-router-dom";
import Nav from "react-bootstrap/Nav";
import {isAdmin} from "../api/IsAdmin";
import {uploadIndexApi} from "../api/UploadIndex";
import {checkIndexRunning} from "../api/CheckIndexRunning";

const CreateIndex = () => {
    const [files, setFiles] = useState([]);
    const [processing, setProcessing] = useState(false);
    const [input, setInput] = useState("");
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
            await checkIndexRunning(navigate);
            setProcessing(localStorage.getItem("index_loading") === "true");
        };
        fetchFiles();
    }, [navigate]);

    const toggleFile = (id) => {
        setFiles(files.map(file => file.id === id ? {...file, checked: !file.checked} : file));
    };

    const uploadIndexButton = async () => {
        const selectedFiles = files.filter(file => file.checked);
        if (selectedFiles.length === 0) {
            alert("Выберите хотя бы один файл для загрузки индекса");
            return;
        }
        const listFiles = selectedFiles.map(file => file.name);
        localStorage.setItem('index_loading', "true");
        setProcessing(true);
        await uploadIndexApi(listFiles, input, navigate);
        localStorage.setItem('index_loading', "false");
        setProcessing(false);
    };

    return (
        <Container className="mt-4">
            <Nav
                activeKey="/create_index"
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

            <Form.Control
                className="mt-4"
                as="textarea"
                placeholder="Введите название индекса"
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />

            <Button onClick={uploadIndexButton} disabled={processing} className="mt-4">
                {processing && <Spinner animation="border" size="sm" className="me-2"/>}
                Загрузить индекс
            </Button>

        </Container>
    );
};

export default CreateIndex;