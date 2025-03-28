import React, {useState} from "react";
import {Button, Form, ListGroup, Container, Row, Col, Spinner} from "react-bootstrap";

const CreateIndex = () => {
    const [files, setFiles] = useState([
        {id: 1, name: "file1.txt", checked: false},
        {id: 2, name: "file2.pdf", checked: false},
        {id: 3, name: "file3.docx", checked: false}
    ]);
    const [processing, setProcessing] = useState(true);

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