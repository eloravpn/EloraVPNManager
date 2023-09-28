import urllib.parse


def generate_vless_config(
    address: str,
    port: str,
    uuid: str,
    host: str,
    path: str,
    remark: str,
    network_type: str = "ws",
):
    alpn = "h2,http/1.1,h3"

    prefix_txt = "%s@%s:%s" % (uuid, address, port)
    prefix = "vless://" + prefix_txt
    postfix_list = [
        "path=%s" % urllib.parse.quote(path.encode("utf8")),
        "security=%s" % "tls",
        "encryption=%s" % "none",
        "host=%s" % host,
        "fp=%s" % "chrome",
        "type=%s" % network_type,
        "sni=%s" % host,
    ]
    # postfix_list.append('alpn=%s' % urllib.parse.quote(alpn.encode('utf8')))
    link = (
        prefix
        + "?"
        + "&".join(postfix_list)
        + "#"
        + urllib.parse.quote(remark.encode("utf8"))
    )
    return link
