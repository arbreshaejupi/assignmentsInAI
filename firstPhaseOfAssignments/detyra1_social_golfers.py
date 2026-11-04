"""
Detyra 1 - Social Golfers Problem
Kerkim i painformuar: Depth First Search (DFS) me Backtracking.

Modelimi (shkurt):
  - Variablat: X[j][g][k] = lojtari ne javen j, grupin g, vendin k
  - Domeni:    {0, 1, ..., n-1}, ku n = g * p
  - Kufizimet: (1) cdo lojtar paraqitet saktesisht nje here ne jave
               (2) dy lojtare takohen ne te njejtin grup se shumti nje here
  - Objective: f(S) = numri i ciftit (a,b) qe takohen me shume se 1 here -> kerkojme f(S) = 0
"""

import random
import sys
import time
from math import factorial

sys.setrecursionlimit(10000)


class LimitArritur(Exception):
    """Hidhet kur nje kalim i DFS e kalon numrin e lejuar te nyjeve (per restart)."""


class SocialGolfers:
    def __init__(self, nr_grupeve, madhesia_grupit, nr_javeve):
        self.G = nr_grupeve
        self.P = madhesia_grupit
        self.W = nr_javeve
        self.N = nr_grupeve * madhesia_grupit

        # takuar[a] = bitmask i lojtareve qe 'a' i ka takuar tashme ne ndonje grup
        self.takuar = [0] * self.N
        # orari[j][g] = lista e lojtareve ne grupin g te javes j
        self.orari = [[[] for _ in range(self.G)] for _ in range(self.W)]
        # perdorur[j] = bitmask i lojtareve qe jane vendosur tashme ne javen j
        self.perdorur = [0] * self.W

        self.nyje_te_vizituara = 0
        self.backtracks = 0


    def _mund_te_hyje(self, lojtari, grupi):
        """Lojtari mund te hyje ne grup vetem nese nuk e ka takuar asnje anetar."""
        for tjeter in grupi:
            if self.takuar[lojtari] >> tjeter & 1:
                return False
        return True

    def _vendos(self, j, g, lojtari):
        grupi = self.orari[j][g]
        for tjeter in grupi:
            self.takuar[lojtari] |= 1 << tjeter
            self.takuar[tjeter] |= 1 << lojtari
        grupi.append(lojtari)
        self.perdorur[j] |= 1 << lojtari

    def _hiq(self, j, g):
        grupi = self.orari[j][g]
        lojtari = grupi.pop()
        for tjeter in grupi:
            self.takuar[lojtari] &= ~(1 << tjeter)
            self.takuar[tjeter] &= ~(1 << lojtari)
        self.perdorur[j] &= ~(1 << lojtari)

    def _me_i_vogli_i_lire(self, j):
        maska = self.perdorur[j]
        for x in range(self.N):
            if not maska >> x & 1:
                return x
        return -1

    def _forward_check(self, j):
        """Pas mbylljes se nje grupi: cdo lojtar i pavendosur ne javen j duhet te kete
        te pakten P-1 lojtare te tjere te pavendosur qe nuk i ka takuar. Ndryshe dega
        eshte e vdekur dhe bejme backtrack menjehere (prerje e hershme)."""
        te_lire = ~self.perdorur[j] & ((1 << self.N) - 1)
        x = te_lire
        while x:
            b = x & -x
            lojtari = b.bit_length() - 1
            te_mundshem = te_lire & ~self.takuar[lojtari] & ~b
            if bin(te_mundshem).count("1") < self.P - 1:
                return False
            x ^= b
        return True

    # ---------------- DFS + Backtracking ----------------
    def zgjidh(self, limit_nyjesh=None, rng=None):
        """Nje kalim i DFS. Nese limit_nyjesh != None dhe tejkalohet -> hedh LimitArritur."""
        self.limit = limit_nyjesh
        self.rng = rng
        # Thyerje simetrie: java e pare fiksohet (0,1,2,3 | 4,5,6,7 | ...)
        for g in range(self.G):
            for k in range(self.P):
                self._vendos(0, g, g * self.P + k)
        return self._dfs(1, 0, 0)

    def _kandidatet(self, j, g, k):
        grupi = self.orari[j][g]
        if k == 0:
            # Simetri: grupet renditen sipas lojtarit te pare -> i pari eshte gjithmone
            # lojtari me i vogel qe s'eshte vendosur ende ne kete jave.
            return [self._me_i_vogli_i_lire(j)]

        te_lire = ~self.perdorur[j] & ((1 << self.N) - 1)
        lejuar = te_lire
        for t in grupi:
            lejuar &= ~self.takuar[t]          # vetem ata qe s'i kane takuar anetaret
        lejuar &= ~((1 << (grupi[0] + 1)) - 1)  # me te medhenj se i pari i grupit

        kand = [x for x in range(self.N) if lejuar >> x & 1]
        if self.rng:
            self.rng.shuffle(kand)              # ndryshon vetem barazimet ne renditje
        # Renditja e vlerave: se pari lojtari me "pak opsione" (me pak partnere te lire),
        # qe te mos mbetet i bllokuar ne fund te javes.
        kand.sort(key=lambda x: bin(te_lire & ~self.takuar[x]).count("1"))
        return kand

    def _dfs(self, j, g, k):
        """Mbush slotin (java j, grupi g, pozita k). Rendi i variablave eshte fiks."""
        self.nyje_te_vizituara += 1
        if self.limit is not None and self.nyje_te_vizituara > self.limit:
            raise LimitArritur()

        if j == self.W:                      # te gjitha javet u mbushen -> qellimi
            return True
        if g == self.G:                      # java j perfundoi, kalo ne javen tjeter
            return self._dfs(j + 1, 0, 0)
        if k == self.P:                      # grupi perfundoi, kalo ne grupin tjeter
            if not self._forward_check(j):
                return False
            return self._dfs(j, g + 1, 0)

        for x in self._kandidatet(j, g, k):
            self._vendos(j, g, x)
            if self._dfs(j, g, k + 1):
                return True
            self._hiq(j, g)                  # backtrack
            self.backtracks += 1

        return False

    # ---------------- objective function ----------------
    def objective(self):
        """f(S) = sa cifte takohen me shume se nje here. Zgjidhje valide <=> f(S) = 0."""
        numero = {}
        for java in self.orari:
            for grupi in java:
                for a in range(len(grupi)):
                    for b in range(a + 1, len(grupi)):
                        cift = (min(grupi[a], grupi[b]), max(grupi[a], grupi[b]))
                        numero[cift] = numero.get(cift, 0) + 1
        return sum(c - 1 for c in numero.values() if c > 1)

    def shtyp(self):
        koka = "Java    | " + " | ".join(f"Grupi {g + 1:<6}" for g in range(self.G))
        print(koka)
        print("-" * len(koka))
        for j, java in enumerate(self.orari):
            rreshti = " | ".join(f"{','.join(map(str, sorted(gr))):<12}" for gr in java)
            print(f"Java {j + 1:<3}| {rreshti}")


def landscape(G, P, W):
    """Numri i ndarjeve te n lojtareve ne G grupe me P (pa renditje) per nje jave,
    dhe hapesira totale per W java."""
    N = G * P
    nje_jave = factorial(N) // (factorial(P) ** G * factorial(G))
    pa_simetri = factorial(N) ** W          # nese cdo slot trajtohet si variabel e renditur
    return nje_jave, nje_jave ** W, pa_simetri


def ekzekuto(G, P, W, koha_max=60.0, limit_nyjesh=50_000, seed=7):
    """DFS me backtracking. Kalimi i pare eshte DFS klasik deterministik; nese ai
    harxhon me shume se 'limit_nyjesh' nyje pa sukses, e rifillojme DFS-ne me nje
    renditje tjeter te barazimeve (restart) dhe me limit pak me te madh. Cdo kalim eshte prape DFS i plote me
    backtracking - restartet vetem e shmangin ngecjen ne nje dege te keqe ne fillim."""
    rng = random.Random(seed)
    t0 = time.time()
    nyje = backtracks = 0
    restarte = 0
    while True:
        s = SocialGolfers(G, P, W)
        try:
            ok = s.zgjidh(limit_nyjesh, rng if restarte else None)
            nyje += s.nyje_te_vizituara
            backtracks += s.backtracks
            break
        except LimitArritur:
            nyje += s.nyje_te_vizituara
            backtracks += s.backtracks
            restarte += 1
            # limiti rritet pak nga pak: ne fund DFS behet e plote, pra nese zgjidhja
            # nuk ekziston, kerkimi e verteton kete (kompletesia ruhet)
            limit_nyjesh = int(limit_nyjesh * 1.1)
            if time.time() - t0 > koha_max:
                ok = None                    # nuk dime - koha mbaroi
                break
    s.nyje_te_vizituara, s.backtracks, s.restarte = nyje, backtracks, restarte
    return s, ok, time.time() - t0


if __name__ == "__main__":
    args = list(map(int, sys.argv[1:]))
    G, P = (args[0], args[1]) if len(args) >= 2 else (8, 4)
    N = G * P
    # kufiri teorik: cdo lojtar takon P-1 te tjere ne jave, gjithsej N-1 te tjere
    kufiri = (N - 1) // (P - 1)

    print(f"Social Golfers: {N} lojtare, {G} grupe me nga {P}")
    print(f"Kufiri i siperm teorik i javeve: floor(({N}-1)/({P}-1)) = {kufiri}")
    a, b, c = landscape(G, P, 1)
    print(f"Landscape per 1 jave: {a:,} menyra te ndryshme te ndarjes ne grupe")
    print()

    if len(args) >= 3:
        javet = [args[2]]
    else:
        javet = range(1, kufiri + 1)

    zgjidhja_me_e_mire = None
    for W in javet:
        s, ok, dt = ekzekuto(G, P, W)
        status = {True: "U GJET", False: "NUK EKZISTON", None: "KOHA MBAROI"}[ok]
        print(f"w = {W:2d}: {status:12s} | nyje = {s.nyje_te_vizituara:>10,} | "
              f"backtracks = {s.backtracks:>10,} | restarte = {s.restarte:>4} | koha = {dt:.2f}s")
        if ok:
            zgjidhja_me_e_mire = s
        else:
            break

    if zgjidhja_me_e_mire:
        print(f"\nOrari me i gjate i gjetur: {zgjidhja_me_e_mire.W} java "
              f"(objective f(S) = {zgjidhja_me_e_mire.objective()})\n")
        zgjidhja_me_e_mire.shtyp()
