# WTI Oil Alert (Hyperliquid → Telegram)

Jedna wiadomość TG **tylko** gdy cena WTI (`xyz:CL`) zmieni się o **≥ $1** vs ostatni alert.
W tej samej wiadomości: cena + przepłynięcia cieśniny Ormuz.

**24/7 bez Twojego PC** — GitHub Actions + samopodtrzymujący się łańcuch.

## Niezawodność (warstwy)

| Warstwa | Mechanizm |
|--------|-----------|
| 1. Pętla | Job ~6 h, poll **co 15 min** |
| 2. Self-chain | Koniec pętli → od razu nowy job (`POLL_PAT`) |
| 3. Schedule | Bootstrap **2× / h** (backup gdy chain padnie) |
| 4. Watchdog | Co ~30 min: jeśli cisza ≥25 min → restart + notka TG |
| 5. Fail → TG | Padnięcie joba → wiadomość z linkiem do runu |
| 6. Odporność polla | Błąd jednego checka nie zabija pętli (do 5 z rzędu) |

Sam cron GHA (`schedule`) jest **zawodny** — dlatego pętla + chain + watchdog, nie sam `*/15`.

### Sekrety
```bash
gh secret set TG_TOKEN -b "..."
gh secret set TG_CHAT_ID -b "..."
# token z scope workflow / Actions:Write — do self-chain i watchdog
gh secret set POLL_PAT -b "ghp_..."   # lub token z: gh auth token
```

Jeśli `gh auth login` odświeży token OAuth, zaktualizuj `POLL_PAT`:
```bash
gh auth token | gh secret set POLL_PAT -R kristofix/oil-alert
```

Lepiej: **fine-grained PAT** tylko na `oil-alert` (Contents: Read, Actions: Write, Metadata: Read).

## Logika alertu
1. Cena Hyperliquid `xyz:CL`
2. vs `last_price` w `state.json`
3. `|Δ| < $1` → cisza  
4. `|Δ| ≥ $1` → Hormuz + 1× TG, nowy anchor

## Komendy
```bash
# start / restart pętli 15 min
gh workflow run alert.yml -f once=false

# jeden check / sample
gh workflow run alert.yml -f once=true
gh workflow run alert.yml -f sample=true

# ręczny watchdog
gh workflow run watchdog.yml
```

## Pliki
- `alert.py` — cena + Hormuz + TG  
- `state.json` — anchor (commit przez Actions)  
- `scripts/push_state.sh` — bezpieczny push stanu  
- `.github/workflows/alert.yml` — pętla + chain + fail-TG  
- `.github/workflows/watchdog.yml` — pilnuje luk  
- `hormuz.py` — legacy (nieużywany w workflow)
