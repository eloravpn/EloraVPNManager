import { redirect } from "react-router-dom";

import { toast } from "../../index";
import { InboundConfigAPI } from "api/InboundConfigAPI";

export async function action({ params }) {
  await InboundConfigAPI.delete(params.inboundConfigId).then((res) => {
    toast({
      title: "Inbound config deleted.",
      status: "success",
      duration: 9000,
      isClosable: true,
    });
  });
  return redirect("/admin/inbound-configs");
}
