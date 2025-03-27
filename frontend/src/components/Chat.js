import React, {useEffect, useState} from "react";
import {Button, Form, Container, Row, Col, Card, DropdownButton, ButtonGroup} from "react-bootstrap";
import Dropdown from 'react-bootstrap/Dropdown';
import {askQuestion} from "../api/SendQuestion";
import {useNavigate} from "react-router-dom";
import CorrectionForm from "../components/CorrectionForm";
import {sendStatistic} from "../api/SendStatistic";
import DescriptionWindow from "./DescriptionWindow";
import {getIndexes} from "../api/GetIndexes";
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';

const ChatComponent = () => {
    const navigate = useNavigate();
    const [indexes, setIndexes] = useState([]);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [selectIndex, setSelectIndex] = useState(indexes[0]);
    const [messageForCorrection, setMessageForCorrection] = useState("");
    const [questionForCorrection, setQuestionForCorrection] = useState("");
    const [showCorrectionForm, setShowCorrectionForm] = useState(false);
    const [showDescriptionWindow, setShowDescriptionWindow] = useState(JSON.parse(localStorage.getItem("show_about") || "true"));

    useEffect(() => {
        const fetchIndexes = async () => {
            const data = await getIndexes(navigate);
            setIndexes(data || []);
            setSelectIndex(data[0] || "");
        };
        fetchIndexes();
    }, [navigate]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessage = {id: messages.length + 1, text: input, sender: "user"};
        setMessages([...messages, newMessage]);
        setInput("");

        const botResponse = {
            id: messages.length + 2,
            text: await askQuestion(selectIndex, input.trim(), navigate),
            sender: "bot",
            liked: null
        };
        setMessages((prev) => [...prev, botResponse]);
    };

    const handleLike = async (id, is_like) => {
        setMessages((messages) =>
            messages.map((msg) =>
                msg.id === id ? {...msg, liked: is_like} : msg
            )
        );
        const message = messages.find(item => item.id === id);
        const question = messages.find(item => item.id === message.id - 1).text;


        if (!is_like) {
            setMessageForCorrection(message.text);
            setQuestionForCorrection(question);
            setShowCorrectionForm(true);
        } else {
            await sendStatistic(question, message.text, true, null, navigate);
        }
    };

    const handleCorrectionClose = () => {
        setShowCorrectionForm(false);
        setMessageForCorrection("");
        setQuestionForCorrection("");
    };

    const handleDescriptionClose = () => {
        setShowDescriptionWindow(false);
    };

    return (
        <Container className="d-flex flex-column vh-100 border shadow-lg">
            <Tabs
                defaultActiveKey="profile"
                id="uncontrolled-tab-example"
                className="mb-3"
                activeKey={"Chat"}
            >
                <Tab eventKey="Chat" title="Чат">
                    Tab content for Home
                </Tab>
                <Tab eventKey="files" title="Добавить файл">
                    Tab content for Profile
                </Tab>
                <Tab eventKey="index" title="Создать индекс">
                    Tab content for Contact
                </Tab>
            </Tabs>

            <div className="flex-grow-1 p-3 overflow-auto">
                {messages.map((msg) => (
                    <Card
                        key={msg.id}
                        className={`mb-2 ${msg.sender === "user" ? "text-white bg-primary ms-auto" : "bg-light"}`}
                        style={{maxWidth: "75%"}}
                    >
                        <Card.Body>
                            <div className="d-flex justify-content-between align-items-center">
                                <span>{msg.text}</span>
                                {msg.sender === "bot" && (
                                    <ButtonGroup size="sm">
                                        <Button
                                            variant={msg.liked ? "success" : "outline-success"}
                                            onClick={() => handleLike(msg.id, true)}
                                        >
                                            👍
                                        </Button>
                                        <Button
                                            variant={msg.liked !== null && !msg.liked ? "danger" : "outline-danger"}
                                            onClick={() => handleLike(msg.id, false)}
                                        >
                                            👎
                                        </Button>
                                    </ButtonGroup>
                                )}
                            </div>
                        </Card.Body>
                    </Card>
                ))}
            </div>

            {showCorrectionForm && (
                <CorrectionForm
                    messageForCorrection={messageForCorrection}
                    setMessageForCorrection={setMessageForCorrection}
                    question={questionForCorrection}
                    onClose={handleCorrectionClose}
                />
            )}

            {showDescriptionWindow && (
                <DescriptionWindow
                    onClose={handleDescriptionClose}
                />
            )}

            <Row className="border-top p-3">
                <Col>
                    <Form.Control
                        as="textarea"
                        placeholder="Введите вопрос..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={async (e) => {
                            if (e.key === "Enter") {
                                if (e.shiftKey) {
                                    e.preventDefault();
                                    setInput((prev) => prev + "\n");
                                } else {
                                    e.preventDefault();
                                    await sendMessage();
                                }
                            }
                        }}
                    />
                </Col>
                <Col xs="auto">
                    <Button onClick={sendMessage}>Отправить</Button>
                </Col>
                <Col xs="auto">
                    <DropdownButton id="dropdown-basic-button" title={selectIndex || "индекс"} drop="up">
                        {indexes.map((index) => (
                            <Dropdown.Item key={index}
                                           onClick={() => setSelectIndex(index)}>{index}
                            </Dropdown.Item>
                        ))}
                    </DropdownButton>
                </Col>
                <Col xs="auto">
                    <Button
                        variant="light"
                        onClick={() => setShowDescriptionWindow(true)}
                    >
                        ?
                    </Button>
                </Col>
            </Row>
        </Container>
    );
};

export default ChatComponent;