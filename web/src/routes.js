// import
import Dashboard from "views/Dashboard/Dashboard";


import {
  HomeIcon,
  StatsIcon,
  CreditIcon,
  PersonIcon,
  DocumentIcon,
  RocketIcon,
  SupportIcon,
} from "components/Icons/Icons";
import {createBrowserRouter} from "react-router-dom";
import Tables from "./views/Dashboard/Tables";
import Login from "./views/Dashboard/Login";
import Inbounds from "./views/Dashboard/Inbounds";
// import Admin from "./layouts/Admin";
// import React from "react";

// var dashRoutes = [
//   {
//     path: "/dashboard",
//     name: "Dashboard",
//     rtlName: "لوحة القيادة",
//     icon: <HomeIcon color="inherit" />,
//     component: Dashboard,
//     layout: "/admin",
//   }
// ];

const dashRoutes =[
   {
    path: "/dashboard",
    name: "Dashboard",
    rtlName: "لوحة القيادة",
    icon: <HomeIcon color="inherit" />,
    component: Dashboard,
    layout: "/admin",
  },{
    path: "/hosts",
    name: "Hosts",
    rtlName: "Hosts",
    icon: <StatsIcon color="inherit" />,
    component: Tables,
    layout: "/admin",
  },{
    path: "/inbounds",
    name: "Inbounds",
    rtlName: "Inbounds",
    icon: <StatsIcon color="inherit" />,
    component: Inbounds,
    layout: "/admin",
  },{
    path: "/login",
    name: "Logout",
    rtlName: "Logout",
    icon: <StatsIcon color="inherit" />,
    component: Login,
    layout: "",
  },
];
export default dashRoutes;
