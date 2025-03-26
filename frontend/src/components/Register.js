import React, {useState} from 'react';
import {registerUser} from "../api/Authorization";
import {useNavigate} from "react-router-dom";
import {Button, Form, Container, Alert, Nav} from 'react-bootstrap';
import {LinkContainer} from "react-router-bootstrap";

const RegisterForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [repeatPassword, setRepeatPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (password === "" || password !== repeatPassword) {
                setError("Пароли не совпадают");
                return;
            }
            await registerUser(email, password);

            setEmail('');
            setPassword('');
            setRepeatPassword('');
            setError(null);
            navigate("/chat");
        } catch (error) {
            console.log(error.response.status)
            console.log(error.response.data.detail)
            if (error.response.status === 400 && error.response.data.detail === "User already registered") {
                setError('Пользователь с такой почтой уже зарегистрирован');
            } else {
                setError('Ошибка, мы уже работаем над ней, попробуйте позже');
            }
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center" style={{height: '100vh'}}>
            <div className="w-50">
                <h2 className="mb-4">Регистрация</h2>

                {error && <Alert variant="danger">{error}</Alert>}

                <Form onSubmit={handleSubmit}>
                    <Form.Group controlId="formEmail" className="mb-3">
                        <Form.Label>Email</Form.Label>
                        <Form.Control
                            type="email"
                            placeholder="Введите email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formPassword" className="mb-3">
                        <Form.Label>Пароль</Form.Label>
                        <Form.Control
                            type="password"
                            placeholder="Введите пароль"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group controlId="formPasswordRepeat" className="mb-3">
                        <Form.Label>Повторите пароль</Form.Label>
                        <Form.Control
                            type="password"
                            placeholder="Введите пароль повторно"
                            value={repeatPassword}
                            onChange={(e) => setRepeatPassword(e.target.value)}
                        />
                    </Form.Group>

                    <div className="d-flex justify-content-between">
                        <Button variant="primary" type="submit">
                            Зарегистрироваться
                        </Button>

                        <LinkContainer to="/login">
                            <Nav.Link className="ms-3">Есть аккаунт? Войдите!</Nav.Link>
                        </LinkContainer>
                    </div>
                </Form>
            </div>
        </Container>
    );
};

export default RegisterForm;