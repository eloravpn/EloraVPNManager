import { useLoaderData } from "react-router-dom";
import Users from "views/Dashboard/Users";
import { UserAPI } from "../../api/UserAPI";
// import { getNotes } from "../notes";

export async function loader() {
  const users = await UserAPI.getAll();
  return users;
}

export default function Root() {
  const users = useLoaderData();

  return <Users data={users} />;
}
