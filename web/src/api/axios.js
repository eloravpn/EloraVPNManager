import axios from "axios"
import {getAuthToken} from "./AuthStorage";

// axios.defaults.headers.common['Authorization'] = `bearer `+ getAuthToken()


// export const api = () => {
//     console.log('API Call ..');
//
//     const defaultOptions = {
//         baseURL: "http://localhost:8000/api",
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     };
//
//     // Create instance
//     const instance = axios.create(defaultOptions);
//
//     // Set the AUTH token for any request
//     instance.interceptors.request.use(function (config) {
//         const token = localStorage.getItem('token');
//         console.log("Tokes::: " + token);
//         config.headers.Authorization = token ? `Bearer ${token}` : '';
//         return config;
//     });
//
//     return instance;
// };


export const api =  axios.create({
  // withCredentials: true,
  baseURL: "http://localhost:8000/api",
  // headers:  {'Authorization': `bearer `+ getAuthToken()}
})

export const api_base = axios.create({
    baseURL: "http://localhost:8000/api"
})

api.interceptors.request.use(function (config) {
    const token = getAuthToken();
    console.log('Token::::' + token);
    config.headers.Authorization = `Bearer ` + token;

    return config;
})
