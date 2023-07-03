import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';

import {Alert, AlertIcon, ChakraProvider} from '@chakra-ui/react'
import {
    createBrowserRouter,
    HashRouter,
    Navigate,
    Route,
    RouterProvider,
    Routes,
    useRouteError
} from "react-router-dom";
import Admin from "./layouts/Admin";
import Tables from "./views/Dashboard/Tables";
import HostsRoot, {loader as hostsRootLoader} from "./routes/hosts/root";
import InboundsRoot, {loader as inboundsRootLoader} from "./routes/inbounds/root"

// import Host, {action as newHostAction, loader as hostLoader} from "./routes/hosts/host";
import {action as destroyHostAction} from "./routes/hosts/destroy";
import {action as destroyInboundAction} from "./routes/inbounds/destroy";
import Dashboard from "./views/Dashboard/Dashboard";

import {createStandaloneToast} from '@chakra-ui/react'
import Login from "./views/Dashboard/Login";

export const {toast} = createStandaloneToast()
// Enable RTl support
// document.documentElement.dir = 'rtl';


let router = createBrowserRouter([
    {
        path: "/login",
        element: <Login/>
    },
    {
        path: "/admin",
        element: <Admin/>,
        // errorElement: <Login/>,
        children: [
            {
                path: "hosts",
                element: <HostsRoot/>,
                loader: hostsRootLoader,

                children: [


                    {
                        path: "host/:hostId/destroy",
                        // element: <Host/>,
                        // loader: hostLoader,
                        action: destroyHostAction,
                        // errorElement: <h2>Host not found</h2>,
                    },
                ],
            },
            {
                path: "inbounds",
                element: <InboundsRoot/>,
                loader: inboundsRootLoader,

                children: [


                    {
                        path: "inbound/:inboundId/destroy",
                        action: destroyInboundAction,
                    },
                ],
            }
        ]
    }

]);


function ErrorBoundary() {
    let error = useRouteError();
    console.log(error);

    return (<Alert status='error'>
        <AlertIcon/>
        There was an error processing your request
    </Alert>);

}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <RouterProvider router={router}/>
    </React.StrictMode>
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
