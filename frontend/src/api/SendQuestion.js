import axios from 'axios';
import {refreshToken} from "./GetToken";

export const askQuestion = async (user_question, navigate) => {
    const askUrl = process.env.REACT_APP_API_URL + "/answer";

    const accessToken = localStorage.getItem("access_token");
    try {
        const response = await axios.post(askUrl, {
            'question': user_question
        }, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.answer;
    } catch (error) {
        if (error.response.status === 401) {
            if (await refreshToken(navigate)) {
                return await askQuestion(user_question, navigate);
            } else {
                navigate("/login");
            }
        } else {
            console.error('API Error:', error.response?.data || error.message);
        }
    }
};