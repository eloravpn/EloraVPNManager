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
    remark: str,
    sid: str,
    spx: str,
    pbk: str,
    flow: str,
    network_type: str = "ws",
):
    alpn = "h2,http/1.1,h3"

    prefix_txt = "%s@%s:%s" % (uuid, address, port)
    prefix = "vless://" + prefix_txt
    postfix_list = [
        "path=%s" % urllib.parse.quote(path.encode("utf8")),
        "security=%s" % security,
        "encryption=%s" % "none",
        "fp=%s" % fp,
        "type=%s" % network_type,
    ]

    if sni:
        postfix_list.append("sni=%s" % sni)

    if host:
        postfix_list.append("host=%s" % host)

    if flow:
        postfix_list.append("flow=%s" % flow)

    if security == InboundSecurity.reality.value:
        if sid:
            postfix_list.append("sid=%s" % sid)
        if pbk:
            postfix_list.append("pbk=%s" % pbk)
        if spx:
            postfix_list.append("spx=%s" % urllib.parse.quote(spx.encode("utf8")))
    # postfix_list.append('alpn=%s' % urllib.parse.quote(alpn.encode('utf8')))
    link = (
        prefix
        + "?"
        + "&".join(postfix_list)
        + "#"
        + urllib.parse.quote(remark.encode("utf8"))
    )
    return link
