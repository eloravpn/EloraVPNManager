// import
import Dashboard from "views/Dashboard/Dashboard";

import { HomeIcon, StatsIcon } from "components/Icons/Icons";
import Tables from "./views/Dashboard/Tables";
import Login from "./views/Dashboard/Login";
import Inbounds from "./views/Dashboard/Inbounds";
import { InboundConfigs } from "views/Dashboard/InboundConfigs";
import Users from "views/Dashboard/Users";
import { PersonIcon } from "components/Icons/Icons";
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

const dashRoutes = [
  {
    path: "/dashboard",
    name: "Dashboard",
    rtlName: "لوحة القيادة",
    icon: <HomeIcon color="inherit" />,
    component: Dashboard,
    layout: "/admin",
  },
  {
    path: "/users",
    name: "Users",
    rtlName: "Users",
    icon: <PersonIcon color="inherit" />,
    component: Users,
    layout: "/admin",
  },
  {
    path: "/hosts",
    name: "Hosts",
    rtlName: "Hosts",
    icon: <StatsIcon color="inherit" />,
    component: Tables,
    layout: "/admin",
  },
  {
    path: "/inbounds",
    name: "Inbounds",
    rtlName: "Inbounds",
    icon: <StatsIcon color="inherit" />,
    component: Inbounds,
    layout: "/admin",
  },
  {
    path: "/inbound-configs",
    name: "Inbound Configs",
    rtlName: "InboundConfigs",
    icon: <StatsIcon color="inherit" />,
    component: InboundConfigs,
    layout: "/admin",
  },
  {
    path: "/login",
    name: "Logout",
    rtlName: "Logout",
    icon: <StatsIcon color="inherit" />,
    component: Login,
    layout: "",
  },
];
export default dashRoutes;
