# 聚合订阅合并器：从环境变量 SUB_URL_1..3 拉取 Clash 格式订阅，合并 proxies，
# 节点名加来源前缀 [1]/[2]/[3] 防撞名，输出 out/all.yaml：
# 一个名为「聚合」的 select 总组包含全部节点，规则 MATCH 直达总组。
# 某条订阅拉取/解析失败只跳过并打警告，三条全失败才报错退出（不覆盖旧文件）。
import os, sys, base64
import requests
import yaml

UA = {"User-Agent": "ClashMeta/1.18"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "all.yaml")


def fetch_proxies(idx, url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        text = r.text
    except Exception as e:
        print(f"[{idx}] 拉取失败：{e}")
        return []
    try:
        data = yaml.safe_load(text)
    except Exception:
        data = None
    if not isinstance(data, dict) or not data.get("proxies"):
        # 有的面板对非 Clash UA 返回 base64 通用订阅；这里再按 base64 解一次试试
        try:
            decoded = base64.b64decode(text.strip()).decode("utf-8", "ignore")
            data = yaml.safe_load(decoded)
        except Exception:
            data = None
    if not isinstance(data, dict) or not data.get("proxies"):
        print(f"[{idx}] 解析失败：不是含 proxies 的 Clash 配置（前 80 字：{text[:80]!r}）")
        return []
    proxies = data["proxies"]
    print(f"[{idx}] OK：{len(proxies)} 个节点")
    return proxies


def main():
    all_proxies, seen = [], set()
    for idx in (1, 2, 3):
        url = (os.environ.get(f"SUB_URL_{idx}") or "").strip()
        if not url:
            print(f"[{idx}] 未设置 SUB_URL_{idx}，跳过")
            continue
        for p in fetch_proxies(idx, url):
            if not isinstance(p, dict) or not p.get("name"):
                continue
            # 商店占位节点过滤：有些订阅商店对不匹配的拉取方式只返回提示语假节点
            # （server 127.0.0.1、名字是「订阅链接不兼容/联系客服」之类的整句提示），不能混进聚合
            _nm = str(p.get("name"))
            if str(p.get("server")) in ("127.0.0.1", "localhost") or any(
                    k in _nm for k in ("订阅链接", "不兼容", "客服", "请复制", "导入客户端")):
                print(f"[{idx}] 跳过占位节点：{_nm}")
                continue
            p = dict(p)
            p["name"] = f"[{idx}] {p['name']}"
            key = (p["name"], str(p.get("server")), str(p.get("port")), str(p.get("type")))
            if key in seen:
                continue
            seen.add(key)
            all_proxies.append(p)
    if not all_proxies:
        print("三条订阅都没拿到节点，保留旧文件，退出。")
        sys.exit(1)
    names = [p["name"] for p in all_proxies]
    config = {
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "proxies": all_proxies,
        "proxy-groups": [
            {"name": "聚合", "type": "select", "proxies": ["DIRECT"] + names},
        ],
        "rules": ["MATCH,聚合"],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
    print(f"已写入 {OUT}：共 {len(all_proxies)} 个节点")


if __name__ == "__main__":
    main()
