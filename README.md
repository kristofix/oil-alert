# WTI Oil Alert (Hyperliquid → Telegram)

Jedna wiadomość TG **tylko** gdy cena WTI (`xyz:CL`) zmieni się o **≥ $1** vs ostatni alert.
W tej samej wiadomości: cena + przepłynięcia cieśniny Ormuz.

**Działa 24/7 przy wyłączonym PC** — wszystko na GitHub Actions.

## Jak działa poll co 15 min

Sam `schedule: */15` w GHA **nie jest** wiarygodny (opóźnienia 1–3 h).

Dlatego workflow:

1. Startuje z crona co **~4 h** (albo ręcznie).
2. Trzyma runner do **~6 h**.
3. W pętli co **15 min** odpala `alert.py` + zapis `state.json`.

Dzięki temu między startami joba cena jest sprawdzana równo co kwadrans — **bez Twojego komputera** i bez cron-job.org.

| | |
|---|---|
| Gdzie leci | GitHub-hosted runner (public repo = free) |
| Twój PC | niepotrzebny |
| Częstotliwość | co 15 min w trakcie działającego joba |
| Alert TG | tylko gdy `\|Δ\| ≥ $1` od ostatniego alertu |

## Logika alertu
1. Cena z Hyperliquid (`xyz:CL`)
2. Porównanie z `last_price` w `state.json`
3. `|Δ| < $1` → cisza
4. `|Δ| ≥ $1` → Hormuz + 1 wiadomość TG, nowy anchor

## Setup (raz)
```bash
gh secret set TG_TOKEN -b "..."
gh secret set TG_CHAT_ID -b "..."

# start pętli 15 min (once=false)
gh workflow run alert.yml -f once=false

# jeden test / sample
gh workflow run alert.yml -f once=true
gh workflow run alert.yml -f sample=true
```

## Pliki
- `alert.py` — cena + Hormuz + TG
- `state.json` — anchor (commitowany przez Actions)
- `scripts/push_state.sh` — bezpieczny push stanu
- `.github/workflows/alert.yml` — pętla polla 15 min / ~6 h
- `hormuz.py` — stary skrypt (nieużywany w workflow)
