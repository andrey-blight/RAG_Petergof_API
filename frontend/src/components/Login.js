import React, {useState} from 'react';
import {setUser} from "../api/Authorization";
import {useNavigate} from "react-router-dom";
import {Button, Form, Container, Alert, Nav} from 'react-bootstrap';
import {LinkContainer} from "react-router-bootstrap";

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setEmail('');
            setPassword('');
            setError(null);
            await setUser(email, password);

            navigate("/chat");
        } catch (error) {
            if (error.response.status === 401) {
                if (error.response.data.detail === "Incorrect email") {
                    setError('Неверная почта. Попробуйте снова.');
                } else {
                    setError('Неверный пароль. Попробуйте снова.');
                }

            } else {
                setError('Ошибка, мы уже работаем над ней, попробуйте позже');
            }
        }
    };

    return (
        <Container className="d-flex justify-content-center align-items-center" style={{height: '100vh'}}>
            <div className="w-50">
                <h2 className="mb-4">Авторизация</h2>

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
                    <div className="d-flex justify-content-between">
                        <Button variant="primary" type="submit">
                            Войти
                        </Button>

                        <LinkContainer to="/register">
                            <Nav.Link className="ms-3">Нет аккаунта? Зарегистрируйтесь!</Nav.Link>
                        </LinkContainer>
                    </div>
                </Form>
            </div>
        </Container>
    );
};

export default LoginForm;