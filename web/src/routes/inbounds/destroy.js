import {redirect} from "react-router-dom";

import {toast} from "../../index";
import {InboundAPI} from "../../api/InboundAPI";

export async function action({params}) {
    await InboundAPI.delete(params.inboundId).then(res => {
            toast({
                title: 'Inbound deleted.',
                status: 'success',
                duration: 9000,
                isClosable: true,
            })
        }
    );
    return redirect("/admin/inbounds");
}
