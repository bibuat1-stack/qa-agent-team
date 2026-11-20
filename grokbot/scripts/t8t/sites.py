"""三站生产前台入口。只放已复核的生产地址，不放测试或灰度地址。"""

SITES = {
    "yy567": {
        "name": "YY567",
        "entry": "https://www.u51xcbknsspro.com/#/",
        "default_phone": "9959950001",
    },
    "muskan": {
        "name": "MuskanClub",
        "entry": "https://www.nfdyhip.com/",
        "default_phone": "9959950001",
    },
    "paglu": {
        "name": "PagluGame",
        "entry": "https://www.syrooyofyoslzevq.com/#/",
        "default_phone": "9959950001",
    },
}

ALLOWED_PHONES = ("9959950001", "9959950002", "9959950003")


def get_site(key: str) -> dict:
    try:
        site = SITES[key]
    except KeyError as exc:
        known = ", ".join(SITES)
        raise SystemExit(f"未知站点 {key}。只能是 {known}。") from exc
    return {"key": key, **site}
