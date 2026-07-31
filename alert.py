import os
import sys
import json
import time
import pathlib
import requests

STATE_FILE = pathlib.Path(__file__).parent / "state.json"
SYMBOL = "xyz:CL"
DEX = "xyz"
HL_API = "https://api.hyperliquid.xyz/info"
HORMUZ_API = "https://hormuz.data-tracking.net/api/summary"
THRESHOLD_USD = 1.0


def get_price() -> float:
    r = requests.post(HL_API, json={"type": "metaAndAssetCtxs", "dex": DEX}, timeout=10)
    r.raise_for_status()
    meta, ctxs = r.json()
    for i, u in enumerate(meta["universe"]):
        if u["name"] == SYMBOL:
            return float(ctxs[i]["markPx"])
    raise RuntimeError(f"{SYMBOL} not in universe")


def get_hormuz() -> dict:
    r = requests.get(HORMUZ_API, timeout=15, headers={"User-Agent": "oil-alert/2.0"})
    r.raise_for_status()
    return r.json()


def send_tg(msg: str) -> None:
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
        timeout=10,
    )
    r.raise_for_status()


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError) as e:
        print(f"WARN: state nieczytelny ({e}) — reset baseline")
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def format_msg(price: float, anchor: float, hormuz: dict, prev_crossings) -> str:
    delta = price - anchor
    pct = delta / anchor * 100.0 if anchor else 0.0
    arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")

    crossings = int(hormuz["total_crossings"])
    if prev_crossings is None:
        cross_line = f"🚢 24h: `{crossings}`"
    else:
        d = crossings - int(prev_crossings)
        cross_line = f"🚢 24h: `{prev_crossings}` → `{crossings}` (Δ {d:+d})"

    return (
        f"*WTI* `${price:.2f}` {arrow} Δ `${delta:+.2f}` (`{pct:+.2f}%`) vs `${anchor:.2f}`\n"
        f"{cross_line}"
    )


def main() -> None:
    sample = os.environ.get("SAMPLE", "").lower() in ("1", "true", "yes") or "--sample" in sys.argv
    price = get_price()
    state = load_state()
    now = int(time.time())

    if sample:
        anchor = float(state.get("last_price", price))
        try:
            hormuz = get_hormuz()
        except Exception as e:
            print(f"WARN: hormuz fail: {e}")
            hormuz = {"total_crossings": state.get("last_crossings", 0)}
        msg = format_msg(price, anchor, hormuz, state.get("last_crossings"))
        send_tg(msg)
        print("SAMPLE sent (state bez zmian)")
        return

    if "last_price" not in state:
        state["last_price"] = price
        state["last_check_ts"] = now
        save_state(state)
        print(f"INIT baseline=${price:.2f} (cicho)")
        return

    anchor = float(state["last_price"])
    delta = price - anchor
    print(f"check: ${price:.2f} vs anchor ${anchor:.2f} (Δ {delta:+.2f})")

    if abs(delta) < THRESHOLD_USD:
        print(f"SKIP: |Δ|={abs(delta):.2f} < {THRESHOLD_USD}")
        return

    try:
        hormuz = get_hormuz()
    except Exception as e:
        print(f"WARN: hormuz fail: {e}")
        hormuz = {"total_crossings": state.get("last_crossings", "?"), "inbound": "?", "outbound": "?", "in_strait": "?"}

    prev_x = state.get("last_crossings")
    msg = format_msg(price, anchor, hormuz, prev_x)
    send_tg(msg)

    try:
        state["last_crossings"] = int(hormuz["total_crossings"])
    except (TypeError, ValueError, KeyError):
        pass
    state["last_price"] = price
    state["last_alert_ts"] = now
    state["last_check_ts"] = now
    save_state(state)
    print(f"SENT: {anchor:.2f} -> {price:.2f} (Δ {delta:+.2f})")


if __name__ == "__main__":
    main()
