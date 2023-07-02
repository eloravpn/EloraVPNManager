import logo from './logo.svg';
import './App.css';
import {Tabs, TabList, TabPanels, Tab, TabPanel} from '@chakra-ui/react'
import { ofetch } from 'ofetch'
import {useEffect, useState} from "react";
import Admin from "./layouts/Admin";


// const fetchData = async () => {
//     return  ofetch('http://127.0.0.1:8000/api/hosts');
// }


// fetchData().then((res) => {
    // console.table(res.hosts)
    // console.table(res.total)
// });

function App() {
    // const [hosts, initHosts] = useState([]);
    // useEffect(() => {
    //     fetchData()
    //         .then((res) => {
    //             initHosts(res.hosts)
    //         })
    //         .catch((e) => {
    //             console.log(e.message)
    //         })
    // }, []);
    // return (
    //     <Admin/>
    // );

}

export default App;
