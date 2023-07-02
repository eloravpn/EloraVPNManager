import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
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
import ErrorPage from "./error-page";
import Tables from "./views/Dashboard/Tables";
import HostsRoot, {loader as hostsRootLoader} from "./routes/hosts/root";
import InboundsRoot, {loader as inboundsRootLoader} from "./routes/inbounds/root"

// import Host, {action as newHostAction, loader as hostLoader} from "./routes/hosts/host";
import {action as destroyAction} from "./routes/hosts/destroy";
import Dashboard from "./views/Dashboard/Dashboard";

import {createStandaloneToast} from '@chakra-ui/react'
import Login from "./views/Dashboard/Login";

export const {toast} = createStandaloneToast()
// Enable RTl support
// document.documentElement.dir = 'rtl';


// const router = createBrowserRouter([
//     {
//         path: "/",
//         element: <h2> Landing Page </h2>,
//         errorElement: <ErrorPage/>,
//     },
//     {
//         path: "/admin",
//         element: <Admin/>,
//         children: [
//             {
//                 path: "dashboard",
//                 element: <Dashboard/>
//             },
//             {
//                 path: "hosts",
//                 element: <Tables/>
//             }
//         ]
//     },
// ]);


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
                        action: destroyAction,
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
                        path: "host/:hostId/destroy",
                        // element: <Host/>,
                        // loader: hostLoader,
                        action: destroyAction,
                        // errorElement: <h2>Host not found</h2>,
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
    // <React.StrictMode>
    //   <App />
    // </React.StrictM

    <React.StrictMode>
        <RouterProvider router={router}/>
        {/* <HashRouter>*/}
        {/*    <Routes>*/}
        {/*        <Route path={`/admin`} element={Admin} />*/}
        {/*        /!*<Navigate  from={`/`} to="/admin/dashboard" />*!/*/}
        {/*    </Routes>*/}
        {/*</HashRouter>*/}
    </React.StrictMode>




    // <ChakraProvider>
    //     <App />
    // </ChakraProvider>
);

// root.render(
//        <HashRouter>
//         <Routes>
//             <Route path={`/admin`} component={Admin} />
//             {/*<Navigate  from={`/`} to="/admin/dashboard" />*/}
//         </Routes>
//     </HashRouter>
// );

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
