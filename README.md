# WTI Oil Alert (Hyperliquid → Telegram)

Powiadomienia o ruchu ceny WTI (`xyz:CL`) na Hyperliquid 24/7. Cron co 15 min, alert gdy `|Δ| ≥ 1%` vs poprzedni check.

## Setup (jednorazowy)

### 1. Bot Telegram
```
@BotFather → /newbot → skopiuj TOKEN
napisz cokolwiek do swojego bota
otwórz: https://api.telegram.org/bot<TOKEN>/getUpdates
skopiuj "chat":{"id": LICZBA} → CHAT_ID
```

### 2. Push do GitHub
```bash
cd /home/l/Dokumenty/cursor/oil_alert
git init && git add . && git commit -m "init"
gh repo create oil-alert --private --source=. --push
```

### 3. Sekrety w GitHub
```bash
gh secret set TG_TOKEN -b "1234567:ABC..."
gh secret set TG_CHAT_ID -b "123456789"
```

### 4. Test ręczny
```bash
gh workflow run alert.yml
gh run watch
```

## Konfiguracja
- `THRESHOLD_PCT` w `alert.py` — próg w % (default 1.0)
- Cron `*/15 * * * *` w `.github/workflows/alert.yml` — interwał

## Test lokalny
```bash
TG_TOKEN=... TG_CHAT_ID=... python alert.py
```

## Limity
- GitHub Actions: 2000 min/mc free (private), unlimited (public). Job ~30s × 96/dzień ≈ 48 min/dzień ≈ **24h/mc**. Spokojnie.
- Cron GitHub miewa opóźnienia 1-15 min — alert "co 15 min" w praktyce ~15-20 min.

## Zmiana symbolu
Inne perpy z dexa "xyz" (HIP-3): `xyz:BRENTOIL`, `xyz:NATGAS`, `xyz:COPPER`, `xyz:DXY`, `xyz:EUR`, `xyz:CORN`, etc. Edytuj `SYMBOL` w `alert.py`.
