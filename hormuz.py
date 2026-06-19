import os
import json
import time
import pathlib
import requests

STATE_FILE = pathlib.Path(__file__).parent / "hormuz_state.json"
API = "https://hormuz.data-tracking.net/api/summary"
POLL_INTERVAL_SEC = 1140  # brama czasowa: ~19 min -> realny cadence ~20 min na lancuchu co 2 min


def get_summary() -> dict:
    r = requests.get(API, timeout=15, headers={"User-Agent": "oil-alert-hormuz/1.0"})
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
    """Tolerate a missing/corrupt state file (e.g. git merge-conflict markers) — treat as fresh."""
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError) as e:
        print(f"WARN: state nieczytelny ({e}) — reset baseline")
        return {}


def main() -> None:
    now = int(time.time())
    state = load_state()

    elapsed = now - int(state.get("last_poll_ts", 0))
    if state and elapsed < POLL_INTERVAL_SEC:
        print(f"SKIP: {elapsed // 60} min od ostatniego polla (<20)")
        return

    try:
        data = get_summary()
        crossings = int(data["total_crossings"])
        inb = data.get("inbound", "?")
        outb = data.get("outbound", "?")
        ins = data.get("in_strait", "?")
        prev = state.get("last_crossings")
        print(f"poll: crossings={crossings} prev={prev} (in {inb}/out {outb}, strait {ins})")
        state["last_crossings"] = crossings

        if prev is None:
            print(f"INIT baseline={crossings} (cicho — bez wiadomości startowej)")
        elif crossings != int(prev):
            d = crossings - int(prev)
            send_tg(
                f"🚢 *Hormuz — przekroczenia 24h*\n"
                f"`{prev}` → `{crossings}`  (Δ {d:+d})\n"
                f"inbound {inb} / outbound {outb} · w cieśninie {ins}"
            )
            print(f"CHANGE {prev}->{crossings} ({d:+d})")
        else:
            print(f"OK bez zmian ({crossings})")
    except Exception as e:
        print(f"WARN: poll nieudany: {e}")
    finally:
        state["last_poll_ts"] = now
        STATE_FILE.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
