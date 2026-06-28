"""
make_dark_charts.py — re-renderiza los gráficos del backend en tema OSCURO NEÓN
(fondo transparente) para combinar con el deck Tower Defense.

Corre con el venv del backend:  python make_dark_charts.py
Salida: assets/dark/*.png
"""
from __future__ import annotations
import os, sys, json, math

BACK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "repositorios",
                                    "Tower-Defense-Estocastico-back"))
sys.path.insert(0, BACK)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import Scenario
from simulation import correr
from analytical import mmc, mmck

COLD = "#3FA7FF"; HOT = "#FF5A36"; GOLD = "#FFC34D"; GREEN = "#38D39F"
PURPLE = "#A78BFA"; TEXT = "#E8EEF7"; MUT = "#8A97AE"; GRID = "#2A3550"

plt.rcParams.update({
    "figure.facecolor": "none", "axes.facecolor": "none", "savefig.facecolor": "none",
    "text.color": TEXT, "axes.labelcolor": TEXT, "xtick.color": MUT, "ytick.color": MUT,
    "axes.edgecolor": GRID, "grid.color": GRID, "font.size": 13,
    "axes.titlecolor": TEXT, "font.family": "DejaVu Sans",
})
OUT = os.path.join(os.path.dirname(__file__), "assets", "dark")
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    for ax in fig.axes:
        ax.grid(alpha=.25)
        for s in ax.spines.values():
            s.set_alpha(.4)
    fig.tight_layout()
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=130, transparent=True); plt.close(fig)
    print("[ok]", name)


def main():
    d = json.load(open(os.path.join(BACK, "output.json"), encoding="utf-8"))
    s = d["series"]; st = d["stats"]; p = d["params"]

    # 1. temperatura
    fig, ax = plt.subplots(figsize=(9, 4.2))
    cols = [COLD, PURPLE, HOT]
    for i, temps in enumerate(s["tower_temp"]):
        ax.plot(s["time"], temps, lw=1.1, color=cols[i % 3], label=f"Torre {i}")
    ax.axhline(p["T_max"], ls="--", color=HOT, alpha=.7, label="T_max")
    ax.axhline(p["T_resume"], ls=":", color=GOLD, alpha=.7, label="T_resume")
    ax.set(xlabel="tiempo [s]", ylabel="temperatura [°]")
    ax.legend(loc="upper right", fontsize=9, labelcolor=TEXT, framealpha=0)
    save(fig, "temperatura.png")

    # 2. cola/sistema
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(s["time"], s["in_system"], lw=1.0, color=HOT, label="En el sistema (L)")
    ax.plot(s["time"], s["queue_len"], lw=1.0, color=COLD, label="En cola (Lq)")
    ax.set(xlabel="tiempo [s]", ylabel="n.º de enemigos")
    ax.legend(loc="upper right", fontsize=9, labelcolor=TEXT, framealpha=0)
    save(fig, "series_colas.png")

    # 3. rendimiento marginal (sweep)
    sweep = [r for r in d["sweep"] if r["stable"]]
    cs = [r["c"] for r in sweep]; lq = [r["Lq"] for r in sweep]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.3))
    a1.plot(cs, lq, "o-", color=COLD, lw=2, ms=8)
    a1.set(xlabel="n.º de torres (c)", ylabel="Lq [enemigos]", title="Longitud de cola vs. capacidad")
    dc = cs[1:]; dlq = [lq[i] - lq[i + 1] for i in range(len(lq) - 1)]
    a2.bar([str(c) for c in dc], dlq, color=GOLD)
    a2.set(xlabel="torre agregada", ylabel="ΔLq (reducción)", title="Rendimiento marginal decreciente")
    save(fig, "rendimiento_marginal.png")

    # 4. costo optimo
    C_T, C_F = 1.0, 25.0
    allr = d["sweep"]
    cc = [r["c"] for r in allr]
    ct = [r["c"] * C_T for r in allr]
    cf = [C_F * p["lambda"] * r["leak_rate_sim"] for r in allr]
    tot = [a + b for a, b in zip(ct, cf)]
    copt = cc[min(range(len(tot)), key=lambda i: tot[i])]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(cc, ct, "o--", color=GREEN, label="Costo torres")
    ax.plot(cc, cf, "s--", color=HOT, label="Costo fugas")
    ax.plot(cc, tot, "D-", color=GOLD, lw=2.5, label="Costo TOTAL")
    ax.axvline(copt, ls=":", color=COLD, alpha=.8, label=f"c* = {copt}")
    ax.set(xlabel="n.º de torres (c)", ylabel="costo / unidad de tiempo")
    ax.legend(labelcolor=TEXT, framealpha=0, fontsize=10)
    save(fig, "costo_optimo.png")

    # 5. utilizacion
    util = st["tower_utilization"]; over = st["overheat_events"]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bars = ax.bar(range(len(util)), util, color=COLD)
    ax.axhline(d["analytical"]["rho"], ls="--", color=GOLD, label=f"ρ teórica={d['analytical']['rho']:.2f}")
    for i, b in enumerate(bars):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + .01, f"{over[i]} sobrecal.",
                ha="center", color=MUT, fontsize=9)
    ax.set(xlabel="torre", ylabel="utilización", ylim=(0, 1)); ax.set_xticks(range(len(util)))
    ax.legend(labelcolor=TEXT, framealpha=0)
    save(fig, "utilizacion.png")

    # --- experimentos (corren sims) ---
    base = Scenario()
    # 6. IC fuga vs c
    seeds = list(range(1000, 1012))
    cs2, mean, lo = [], [], []
    for c in range(1, 7):
        leaks = []
        for sd in seeds:
            sc = Scenario(**{**base.__dict__, "c": c, "seed": sd}); sc.layout = base.layout
            r = correr(sc); leaks.append(r.leaked / r.spawned * 100 if r.spawned else 0)
        m = sum(leaks) / len(leaks)
        sd_ = (sum((x - m) ** 2 for x in leaks) / (len(leaks) - 1)) ** .5
        cs2.append(c); mean.append(m); lo.append(1.96 * sd_ / len(leaks) ** .5)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.errorbar(cs2, mean, yerr=lo, fmt="o-", color=HOT, capsize=5, lw=2, ms=8,
                ecolor=GOLD, label="fuga (media ± IC95%)")
    ax.set(xlabel="n.º de torres (c)", ylabel="tasa de fuga [%]")
    ax.legend(labelcolor=TEXT, framealpha=0)
    save(fig, "ci_fuga.png")

    # 7. no estacionario
    per = 150.0; sched = []; t = 0.0; hi = False
    while t < base.sim_time:
        sched.append((t, 0.75 if hi else 0.15)); hi = not hi; t += per
    res = {}
    for c in (2, 4):
        sc = Scenario(**{**base.__dict__, "c": c, "lam_schedule": sched, "seed": 42}); sc.layout = base.layout
        res[c] = correr(sc)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    ts, lam = [], []
    for i, (t0, v) in enumerate(sched):
        t1 = sched[i + 1][0] if i + 1 < len(sched) else base.sim_time
        ts += [t0, t1]; lam += [v, v]
    a1.plot(ts, lam, color=GOLD, lw=2); a1.set(ylabel="λ(t)", title="Oleadas: λ(t) y cola resultante")
    for c, col in ((2, HOT), (4, COLD)):
        r = res[c]
        a2.plot([x["t"] for x in r.samples], [x["queue_len"] for x in r.samples], lw=0.9,
                color=col, label=f"c={c} (fuga {r.leaked/r.spawned*100:.0f}%)")
    a2.set(xlabel="tiempo [s]", ylabel="cola"); a2.legend(labelcolor=TEXT, framealpha=0)
    save(fig, "no_estacionario.png")

    # 8. prioridad
    tipos = [(0.5, 2.0, "debil"), (0.5, 2.0 / 3.0, "fuerte")]
    def run(pri):
        wf = wd = nf = nd = 0.0
        for sd in range(3000, 3012):
            sc = Scenario(**{**base.__dict__, "enemy_types": tipos, "priority": pri, "seed": sd}); sc.layout = base.layout
            r = correr(sc)
            wf += r.wait_by_type.get("fuerte", 0); nf += r.n_by_type.get("fuerte", 0)
            wd += r.wait_by_type.get("debil", 0); nd += r.n_by_type.get("debil", 0)
        return wf / max(1, nf), wd / max(1, nd)
    f_f, f_d = run(False); p_f, p_d = run(True)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = range(3); clases = ["fuerte", "débil", "ponderada"]
    W = 3.0
    fifo = [f_f, f_d, (W * f_f + f_d) / (W + 1)]
    prio = [p_f, p_d, (W * p_f + p_d) / (W + 1)]
    ax.bar([i - .2 for i in x], fifo, .4, color=MUT, label="FIFO")
    ax.bar([i + .2 for i in x], prio, .4, color=PURPLE, label="Prioridad (fuerte primero)")
    ax.set_xticks(list(x)); ax.set_xticklabels(clases); ax.set(ylabel="Wq [s]")
    ax.legend(labelcolor=TEXT, framealpha=0)
    save(fig, "prioridad.png")

    print("\nDark charts en", OUT)


if __name__ == "__main__":
    main()
