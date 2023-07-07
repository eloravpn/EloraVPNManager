import { redirect } from "react-router-dom";
import { HostAPI } from "../../api/HostAPI";

import { toast } from "../../index";
import { UserAPI } from "../../api/UserAPI";

export async function action({ params }) {
  await UserAPI.deleteUser(params.userId).then((res) => {
    toast({
      title: "User deleted.",
      status: "success",
      duration: 9000,
      isClosable: true,
    });
  });
  return redirect("/admin/users");
}
