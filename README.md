# WTI Oil Alert (Hyperliquid → Telegram)

Jedna wiadomość TG **tylko** gdy cena WTI (`xyz:CL`) zmieni się o **≥ $1** vs ostatni alert.
W tej samej wiadomości: cena + przepłynięcia cieśniny Ormuz.

## Logika
1. GitHub Actions poll co **15 min**
2. Porównanie z `last_price` w `state.json`
3. Jeśli `|Δ| < $1` → cisza (tylko update `last_check_ts`)
4. Jeśli `|Δ| ≥ $1` → fetch Hormuz + **1 wiadomość** (cena + crossings), nowy anchor = bieżąca cena

## Setup
```bash
# sekrety
gh secret set TG_TOKEN -b "..."
gh secret set TG_CHAT_ID -b "..."

# test
TG_TOKEN=... TG_CHAT_ID=... python alert.py
gh workflow run alert.yml
```

## Pliki
- `alert.py` — cena + Hormuz + TG
- `state.json` — anchor ceny i crossings
- `hormuz.py` — stary osobny skrypt (nieużywany w workflow)
