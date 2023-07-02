import {redirect} from "react-router-dom";
import {HostAPI} from "../../api/HostAPI";

import {toast} from "../../index";

export async function action({params}) {
    await HostAPI.deleteHost(params.hostId).then(res => {
            toast({
                title: 'Host deleted.',
                status: 'success',
                duration: 9000,
                isClosable: true,
            })
        }
    );
    return redirect("/admin/hosts");
}