import urllib.parse

from src.inbounds.schemas import InboundSecurity


def generate_vless_config(
    address: str,
    port: str,
    uuid: str,
    host: str,
    sni: str,
    fp: str,
    path: str,
    security: str,
    sid: str,
    spx: str,
    pbk: str,
    remark: str,
    network_type: str = "ws",
):
    alpn = "h2,http/1.1,h3"

    prefix_txt = "%s@%s:%s" % (uuid, address, port)
    prefix = "vless://" + prefix_txt
    postfix_list = [
        "path=%s" % urllib.parse.quote(path.encode("utf8")),
        "security=%s" % security,
        "encryption=%s" % "none",
        "host=%s" % host,
        "fp=%s" % fp,
        "type=%s" % network_type,
        "sni=%s" % sni,
    ]

    if security == InboundSecurity.reality.value:
        postfix_list.extend(
            [
                "sid=%s" % sid,
                "pbk=%s" % pbk,
                "spx=%s" % urllib.parse.quote(spx.encode("utf8")),
            ]
        )
    # postfix_list.append('alpn=%s' % urllib.parse.quote(alpn.encode('utf8')))
    link = (
        prefix
        + "?"
        + "&".join(postfix_list)
        + "#"
        + urllib.parse.quote(remark.encode("utf8"))
    )
    return link
