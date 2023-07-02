import { useLoaderData, Link, Outlet } from "react-router-dom";
import {api} from "api/axios";
import {HostAPI} from "api/HostAPI";
import Hosts from "views/Dashboard/Hosts";
import {InboundAPI} from "../../api/InboundAPI";
import Inbounds from "../../views/Dashboard/Inbounds";
// import { getNotes } from "../notes";

export async function loader() {
  return await InboundAPI.getAll()
}


export default function Root() {
  const inbounds = useLoaderData();

  return (
    <Inbounds data={inbounds}/>
  );
}

