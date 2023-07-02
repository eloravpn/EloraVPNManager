import { useLoaderData, Link, Outlet } from "react-router-dom";
import {api} from "api/axios";
import {HostAPI} from "api/HostAPI";
import Hosts from "views/Dashboard/Hosts";
// import { getNotes } from "../notes";

export async function loader() {
  const hosts = await HostAPI.getAll()
  return hosts;
}


export default function Root() {
  const hosts = useLoaderData();

  return (
    <Hosts hosts={hosts}/>
  );
}

