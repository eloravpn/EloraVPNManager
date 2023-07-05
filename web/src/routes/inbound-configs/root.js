import { useLoaderData } from "react-router-dom";
import { InboundConfigs } from "views/Dashboard/InboundConfigs";
import { InboundConfigAPI } from "api/InboundConfigAPI";
// import { getNotes } from "../notes";

export async function loader() {
  return await InboundConfigAPI.getAll();
}

export default function Root() {
  const inboundConfigs = useLoaderData();

  return <InboundConfigs data={inboundConfigs} />;
}
