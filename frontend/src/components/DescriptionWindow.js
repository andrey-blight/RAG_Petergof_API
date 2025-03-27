import React from "react";
import {Button, Card} from "react-bootstrap";
import {X} from "react-bootstrap-icons";

const DescriptionWindow = ({onClose}) => {
    localStorage.setItem('show_about', "false");

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
                    <p> Привет! Я приложение-помощник для изучения исторической литературы Петергофа. В чате ты можешь
                        выбирать индекс модели (которые заранее создал сотрудник музея) и задавать мне разные вопросы.
                        Я в свою очередь постараюсь ответить на твой вопрос и указать название документа и страницу
                        с информацией.
                    </p>

                    <p> Если вы сотрудник, то вам доступна функциональность создания индекса. На странички загрузки pdf
                        вы можете загрузить ваш документ, и я начну его анализировать (это может занять довольно
                        продолжительное время, около минуты на 10 страниц). На странице создания индекса вы можете
                        выбрать из уже загруженных документов те документы, на которых вы хотите осуществлять поиск.
                        После нажатия на кнопку создать индекс создастся и появится в чате в списке доступных
                        индексов
                    </p>
                </Card.Body>
            </Card>
        </div>
    );
};

export default DescriptionWindow;