import React, {useEffect, useState} from "react";
import {Form, Container, Button} from "react-bootstrap";
import {useNavigate} from "react-router-dom";
import Nav from "react-bootstrap/Nav";
import {isAdmin} from "../api/IsAdmin";
import {getSettings} from "../api/GetSettings";
import {sendSettings} from "../api/SendSettings";

const Settings = () => {
    const [settings, setSettings] = useState({
        prompt: "",
        temperature: 0,
        count_vector: 0,
        count_fulltext: 0
    });
    const navigate = useNavigate();
    const [showTabs, setShowTabs] = useState(false);

    useEffect(() => {
        const fetchSettings = async () => {
            const data = await getSettings(navigate);
            if (data) {
                setSettings({
                    prompt: data.prompt,
                    temperature: data.temperature,
                    count_vector: data.count_vector,
                    count_fulltext: data.count_fulltext
                });
            }
        };
        fetchSettings();
        isAdmin(navigate).then(setShowTabs);
    }, [navigate]);

    const updateSetting = (key, value) => {
        setSettings(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const handleSave = async () => {
        await sendSettings(settings, navigate);
    };

    return (
        <Container className="mt-4">
            <Nav
                activeKey="/settings"
                variant="tabs"
            >
                <Nav.Item>
                    <Nav.Link href="/chat">Чат</Nav.Link>

                </Nav.Item>

                <Nav.Item>
                    <Nav.Link href="/settings">Настройки</Nav.Link>
                </Nav.Item>


                {showTabs && (
                    <>
                        <Nav.Item>
                            <Nav.Link href="/file">Добавить файл</Nav.Link>
                        </Nav.Item>
                        <Nav.Item>
                            <Nav.Link href="/create_index">Создать индекс</Nav.Link>
                        </Nav.Item>
                    </>
                )}

                <Nav.Item>
                    <Nav.Link href="/login">Выйти из аккаунта</Nav.Link>
                </Nav.Item>
            </Nav>


            <Form.Group controlId="promptInput" className="mt-4">
                <Form.Label>Значение промта</Form.Label>
                <Form.Control
                    className="mt-1"
                    as="textarea"
                    placeholder="Введите промт"
                    value={settings.prompt}
                    onChange={(e) => updateSetting('prompt', e.target.value)}
                />
            </Form.Group>

            <Form.Group controlId="temperatureInput" className="mt-4">
                <Form.Label>Температура: {settings.temperature}</Form.Label>
                <Form.Range
                    className="mt-1"
                    min={0}
                    max={1}
                    step={0.01}
                    value={settings.temperature}
                    onChange={(e) => updateSetting('temperature', e.target.value)}
                />
            </Form.Group>

            <Form.Group controlId="vectorInput" className="mt-4">
                <Form.Label>Кол-во элементов векторным поиском: {settings.count_vector}</Form.Label>
                <Form.Range
                    className="mt-1"
                    min={1}
                    max={30}
                    step={1}
                    value={settings.count_vector}
                    onChange={(e) => updateSetting('count_vector', e.target.value)}
                />
            </Form.Group>

            <Form.Group controlId="vectorInput" className="mt-4">
                <Form.Label>Кол-во элементов полнотекстовым поиском: {settings.count_fulltext}</Form.Label>
                <Form.Range
                    className="mt-1"
                    min={1}
                    max={30}
                    step={1}
                    value={settings.count_fulltext}
                    onChange={(e) => updateSetting('count_fulltext', e.target.value)}
                />
            </Form.Group>

            <div className="d-flex justify-content-between mt-4">
                <Button
                    variant="outline-secondary"
                    onClick={() =>
                        setSettings({
                            prompt: "Вы ассистируете научного руководителя музейного комплекса Петергоф. Ниже вам дан контекст, откуда брать информацию. Разрешено брать сразу несколько текстов. Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным. Вместе с ответом также напишите название файла и страницу, откуда была взята информация.. Ответь на вопрос: ",
                            temperature: 0.2,
                            count_vector: 15,
                            count_fulltext: 5,
                        })
                    }
                    className="me-2"
                >
                    Сбросить
                </Button>

                <Button
                    variant="primary"
                    onClick={handleSave}
                    className="ms-2"
                >
                    Сохранить
                </Button>
            </div>

        </Container>
    );
};

export default Settings;