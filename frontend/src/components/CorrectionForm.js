import React, {useState} from "react";
import {Button, Form, Row, Col, Card} from "react-bootstrap";
import {X} from "react-bootstrap-icons";
import {sendStatistic} from "../api/SendStatistic";
import {useNavigate} from "react-router-dom";  // Импорт иконки крестика

const CorrectionForm = ({messageForCorrection, setMessageForCorrection, question, onClose}) => {
    const [correctedAnswer, setCorrectedAnswer] = useState("");
    const navigate = useNavigate();

    const handleCorrectionSubmit = async (e) => {
        e.preventDefault();

        await sendStatistic(question, messageForCorrection, false, correctedAnswer, navigate)

        setMessageForCorrection("");
        setCorrectedAnswer("");
        onClose();
    };

    return (
        <div
            className="d-flex justify-content-center align-items-center position-fixed top-50 start-50 translate-middle"
            style={{width: '80%'}} // Увеличиваем ширину контейнера
        >
            <Card className="p-4" style={{width: "100%", maxWidth: "800px"}}>
                <Card.Body>
                    <Button
                        variant="link"
                        onClick={onClose}
                        style={{
                            position: "absolute",
                            top: "10px",
                            right: "10px",
                            fontSize: "1.5rem",
                            color: "black",
                        }}
                    >
                        <X/>
                    </Button>

                    <Form onSubmit={handleCorrectionSubmit}>
                        <Row className="mb-3">
                            <Col>
                                <h4>Текст ответа:</h4>
                                <div className="d-flex justify-content-between align-items-center">
                                    <span>{messageForCorrection}</span>
                                </div>
                            </Col>
                        </Row>

                        <Row className="mb-3">
                            <Col>
                                <Form.Label>Правильный ответ</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={5}
                                    value={correctedAnswer}
                                    onChange={(e) => setCorrectedAnswer(e.target.value)}
                                    placeholder="Введите правильный ответ"
                                />
                            </Col>
                        </Row>

                        <Row>
                            <Col xs="auto">
                                <Button type="submit" variant="primary">
                                    Отправить
                                </Button>
                            </Col>
                        </Row>
                    </Form>
                </Card.Body>
            </Card>
        </div>
    );
};

export default CorrectionForm;