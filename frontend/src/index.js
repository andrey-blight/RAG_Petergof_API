import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css';
import {createRoot} from "react-dom/client";

const domNode = document.getElementById('root');
const root = createRoot(domNode);
root.render(<App/>);
