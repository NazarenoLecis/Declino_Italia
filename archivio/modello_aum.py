"""
Previdenza complementare – scenario a regime con obbligo + opt-out

Il modello calcola:
AuM_T = stock_iniziale * (1+r)^T
        + FV(versamenti annui crescenti su platea aderente)

Tutti i parametri modificabili sono all'inizio.
"""

import math

# ======================================================
# ====== PARAMETRI MODIFICABILI ========================
# ======================================================

stock_iniziale = 250e9          # AuM iniziale (euro)

dipendenti_totali = 18.976e6    # lavoratori dipendenti
opt_out = 0.10                  # quota che rinuncia (=> adesione 90%)

crescita_salariale = 0.02       # crescita annua dei versamenti
rendimenti = [0.02, 0.04]       # rendimenti annui
orizzonti = [5, 10]             # anni

# Versamenti medi annui per aderente (euro/anno)
versamento_senza_tfr = 1900     # volontari + datore
versamento_tfr = 1700           # quota TFR

# Scenari
scenari_con_tfr = [False, True]

# ======================================================
# ====== FUNZIONI ======================================
# ======================================================

def aderenti_totali(dipendenti: float, opt_out: float) -> float:
    if not (0.0 <= opt_out <= 1.0):
        raise ValueError("opt_out deve essere tra 0 e 1.")
    return dipendenti * (1.0 - opt_out)

def fv_rendita_crescente(c0: float, g: float, r: float, n: int) -> float:
    if n <= 0:
        return 0.0
    if abs(r - g) < 1e-12:
        return c0 * n * (1.0 + r) ** (n - 1)
    return c0 * (((1.0 + r) ** n - (1.0 + g) ** n) / (r - g))

def aum_totale(stock0: float, flusso0: float, g: float, r: float, n: int) -> float:
    return stock0 * (1.0 + r) ** n + fv_rendita_crescente(flusso0, g, r, n)

def flusso_annuo_iniziale(aderenti: float, con_tfr: bool,
                          v_senza_tfr: float, v_tfr: float) -> float:
    v = v_senza_tfr + (v_tfr if con_tfr else 0.0)
    return aderenti * v

# ======================================================
# ====== ESECUZIONE ====================================
# ======================================================

n_aderenti = aderenti_totali(dipendenti_totali, opt_out)
print(f"Aderenti a regime: {n_aderenti/1e6:.2f} mln\n")

for con_tfr in scenari_con_tfr:
    nome = "CON TFR" if con_tfr else "SENZA TFR"
    flusso0 = flusso_annuo_iniziale(
        aderenti=n_aderenti,
        con_tfr=con_tfr,
        v_senza_tfr=versamento_senza_tfr,
        v_tfr=versamento_tfr
    )

    print(f"Scenario: {nome}")
    print(f"  Versamento medio per aderente: "
          f"{(versamento_senza_tfr + (versamento_tfr if con_tfr else 0)):.0f} €/anno")
    print(f"  Flusso annuo iniziale totale: {flusso0/1e9:.1f} mld €")

    for r in rendimenti:
        for n in orizzonti:
            aum = aum_totale(stock_iniziale, flusso0, crescita_salariale, r, n)
            print(f"    r={int(r*100)}% | {n} anni -> AuM: {aum/1e9:.0f} mld €")
    print()
