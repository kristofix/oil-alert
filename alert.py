import os
import json
import time
import pathlib
import requests

STATE_FILE = pathlib.Path(__file__).parent / "state.json"
THRESHOLD_PCT = 0.7
SYMBOL = "xyz:CL"
DEX = "xyz"
API = "https://api.hyperliquid.xyz/info"


def get_price() -> float:
    r = requests.post(API, json={"type": "metaAndAssetCtxs", "dex": DEX}, timeout=10)
    r.raise_for_status()
    meta, ctxs = r.json()
    for i, u in enumerate(meta["universe"]):
        if u["name"] == SYMBOL:
            return float(ctxs[i]["markPx"])
    raise RuntimeError(f"{SYMBOL} not in universe")


def send_tg(msg: str) -> None:
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
        timeout=10,
    )
    r.raise_for_status()


def load_state(default: dict) -> dict:
    """Tolerate a missing/corrupt state file (e.g. git merge-conflict markers) — treat as fresh."""
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError) as e:
        print(f"WARN: state nieczytelny ({e}) — reset baseline")
        return default


def main() -> None:
    price = get_price()
    state = load_state({"last_price": price})
    anchor = float(state.get("last_price", price))
    pct = (price - anchor) / anchor * 100.0

    if abs(pct) >= THRESHOLD_PCT:
        direction = "WZROST" if pct > 0 else "SPADEK"
        msg = (
            f"*WTI {direction}* `${price:.2f}` "
            f"({pct:+.2f}% vs anchor `${anchor:.2f}`)\n"
            f"Hyperliquid `xyz:CL`"
        )
        send_tg(msg)
        state["last_price"] = price
        state["last_alert_ts"] = int(time.time())
        print(f"ALERT sent: {pct:+.2f}% {anchor:.2f} -> {price:.2f}")
    else:
        print(f"OK: {pct:+.2f}% (anchor {anchor:.2f}, now {price:.2f}, below {THRESHOLD_PCT}%)")

    STATE_FILE.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
