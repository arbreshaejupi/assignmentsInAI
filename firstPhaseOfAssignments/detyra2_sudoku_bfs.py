"""
Detyra 2 - Sudoku Solver
Kerkim i painformuar: Breadth First Search (BFS) me Backtracking.

Modelimi (shkurt):
  - Variablat: 81 qeliza X(r,k), r,k in {0..8}
  - Domeni:    {1..9} per qelizat bosh; qelizat e dhena kane domen me nje vlere
  - Kufizimet: AllDifferent ne cdo rresht, kolone dhe kuti 3x3
  - Objective: f(S) = (qeliza bosh) + (cifte konfliktesh) -> kerkojme f(S) = 0

Si e kombinojme BFS me backtracking:
  BFS e eksploron pemen nivel pas niveli (radhe FIFO). Kur nje gjendje e pjesshme
  shkel nje kufizim ose ndonje qelize i mbetet domeni bosh, dega "kthehet mbrapa":
  nuk shtohet ne radhe dhe asnje pasardhes i saj nuk gjenerohet me (krasitje).
"""

import sys
import time
from collections import deque

NIVELET = {
    "easy":   "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
    "medium": "000260701680070090190004500820100040004602900050003028009300074040050036703018000",
    "hard":   "800000000003600000070090200050007000000045700000100030001000068008500010090000400",
}

# Per cdo qelize i llogarisim nje here "fqinjet" (qelizat ne te njejtin rresht/kolone/kuti)
FQINJET = []
for i in range(81):
    r, k = divmod(i, 9)
    kr, kk = 3 * (r // 3), 3 * (k // 3)
    s = set()
    for t in range(9):
        s.add(r * 9 + t)
        s.add(t * 9 + k)
    for a in range(kr, kr + 3):
        for b in range(kk, kk + 3):
            s.add(a * 9 + b)
    s.discard(i)
    FQINJET.append(tuple(s))

TE_GJITHA = frozenset(range(1, 10))


def lexo(varg):
    varg = varg.replace(".", "0").strip()
    if len(varg) != 81 or not varg.isdigit():
        raise ValueError("Sudoku duhet te kete saktesisht 81 shifra (0 ose . per bosh).")
    return [int(c) for c in varg]


def domenet_fillestare(tabela):
    """Domeni i cdo qelize bosh = {1..9} minus vlerat e fqinjeve."""
    dom = {}
    for i, v in enumerate(tabela):
        if v == 0:
            dom[i] = set(TE_GJITHA) - {tabela[j] for j in FQINJET[i]}
    return dom


def cakto(tabela, dom, i, v, propagim=True):
    """Kthen (tabela_e_re, domeni_i_ri) pasi X[i] = v, ose None nese dega deshton.
    Me propagim=True perdoret forward checking + 'naked singles' (qelizat me nje
    vlere te vetme mbushen menjehere)."""
    t = tabela[:]
    d = {q: set(s) for q, s in dom.items()}
    stack = [(i, v)]
    while stack:
        q, val = stack.pop()
        if t[q] != 0:
            if t[q] != val:
                return None
            continue
        t[q] = val
        d.pop(q, None)
        for f in FQINJET[q]:
            if f in d and val in d[f]:
                d[f].discard(val)
                if not d[f]:
                    return None                 # domen bosh -> backtrack
                if propagim and len(d[f]) == 1:
                    stack.append((f, next(iter(d[f]))))
    return t, d


def bfs_sudoku(tabela, propagim=True):
    statistika = {"zgjeruar": 0, "gjeneruar": 1, "krasitur": 0, "max_radha": 1, "thellesia": 0}
    dom = domenet_fillestare(tabela)
    for q, s in dom.items():
        if not s:
            return None, statistika

    radha = deque([(tabela, dom, 0)])
    while radha:
        statistika["max_radha"] = max(statistika["max_radha"], len(radha))
        gjendja, d, niveli = radha.popleft()          # FIFO -> BFS
        statistika["zgjeruar"] += 1

        if not d:                                      # s'ka me qeliza bosh -> qellimi
            statistika["thellesia"] = niveli
            return gjendja, statistika

        # Zgjedhim qelizen me domenin me te vogel (MRV) qe pema te jete sa me e ngushte
        i = min(d, key=lambda q: len(d[q]))
        for v in sorted(d[i]):
            femija = cakto(gjendja, d, i, v, propagim)
            if femija is None:
                statistika["krasitur"] += 1            # dege e pavlefshme -> backtrack
                continue
            statistika["gjeneruar"] += 1
            radha.append((femija[0], femija[1], niveli + 1))
    return None, statistika


def objective(tabela):
    """f(S) = numri i qelizave bosh + numri i cifteve te fqinjeve me vlere te njejte."""
    bosh = tabela.count(0)
    konflikte = 0
    for i in range(81):
        if tabela[i]:
            for j in FQINJET[i]:
                if j > i and tabela[j] == tabela[i]:
                    konflikte += 1
    return bosh + konflikte


def landscape(tabela):
    bosh = tabela.count(0)
    dom = domenet_fillestare(tabela)
    pas_reduktimit = 1
    for s in dom.values():
        pas_reduktimit *= len(s)
    return bosh, 9 ** bosh, pas_reduktimit


def shtyp(tabela):
    for r in range(9):
        if r % 3 == 0 and r:
            print("------+-------+------")
        rreshti = ""
        for k in range(9):
            if k % 3 == 0 and k:
                rreshti += "| "
            v = tabela[r * 9 + k]
            rreshti += (str(v) if v else ".") + " "
        print(rreshti.rstrip())


def zgjidh_nje(emri, varg, propagim=True):
    tabela = lexo(varg)
    bosh, total, reduktuar = landscape(tabela)
    print(f"=============== {emri.upper()} ===============")
    shtyp(tabela)
    print(f"\nQeliza bosh: {bosh}")
    print(f"Landscape (pa kufizime):    9^{bosh} = {total:.3e}")
    print(f"Landscape (pas domeneve):   {reduktuar:.3e}")
    print(f"Objective ne fillim f(S0) = {objective(tabela)}")

    t0 = time.time()
    zgjidhja, st = bfs_sudoku(tabela, propagim)
    dt = time.time() - t0

    if zgjidhja is None:
        print("\nNuk ka zgjidhje.\n")
        return
    print(f"\nZgjidhja (f(S) = {objective(zgjidhja)}):")
    shtyp(zgjidhja)
    print(f"\nNyje te zgjeruara: {st['zgjeruar']}, te gjeneruara: {st['gjeneruar']}, "
          f"dege te krasitura (backtrack): {st['krasitur']}")
    print(f"Madhesia maksimale e radhes (frontier): {st['max_radha']}, "
          f"thellesia e zgjidhjes: {st['thellesia']}, koha: {dt:.3f}s\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    propagim = "--pa-propagim" not in args
    args = [a for a in args if a != "--pa-propagim"]

    if not args:
        for emri, varg in NIVELET.items():
            zgjidh_nje(emri, varg, propagim)
    elif args[0].lower() in NIVELET:
        zgjidh_nje(args[0], NIVELET[args[0].lower()], propagim)
    else:
        zgjidh_nje("sudoku e dhene", args[0], propagim)
