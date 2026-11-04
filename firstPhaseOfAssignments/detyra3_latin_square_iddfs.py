"""
Detyra 3 - Latin Square
Kerkim i painformuar: Iterative Deepening Depth First Search (IDDFS) + Backtracking.

Modelimi (shkurt):
  - Variablat: L[r][k], r,k in {0..n-1}   (n^2 variabla)
  - Domeni:    {1..n}
  - Kufizimet: AllDifferent ne cdo rresht dhe ne cdo kolone
  - Objective: f(S) = sum_rreshta (n - |vlera unike|) + sum_kolona (n - |vlera unike|)
               -> kerkojme nje matrice te plote me f(S) = 0
  - Gjendja = matrica e mbushur pjeserisht; thellesia d = sa qeliza jane mbushur.
    Qellimi gjendet ne thellesine d = n^2.

IDDFS: ekzekutojme DFS me kufi thellesie L = 0, 1, 2, ... deri sa te gjendet qellimi.
Backtracking: cdo vlere qe perseritet ne rresht/kolone refuzohet menjehere dhe
kthehemi mbrapa te qeliza paraprake.

"""

import sys
import time
from math import factorial


class LatinSquareIDDFS:
    def __init__(self, n):
        self.n = n
        self.L = [[0] * n for _ in range(n)]
        # maska bitesh: ne_rresht[r] ka bitin v te ndezur nese v eshte perdorur ne rreshtin r
        self.ne_rresht = [0] * n
        self.ne_kolone = [0] * n
        self.nyje_gjithsej = 0
        self.iteracione = []           # (kufiri, nyje te vizituara ne ate iteracion)

    def _lejohet(self, r, k, v):
        bit = 1 << v
        return not (self.ne_rresht[r] & bit) and not (self.ne_kolone[k] & bit)

    def _vendos(self, r, k, v):
        self.L[r][k] = v
        self.ne_rresht[r] |= 1 << v
        self.ne_kolone[k] |= 1 << v

    def _hiq(self, r, k, v):
        self.L[r][k] = 0
        self.ne_rresht[r] &= ~(1 << v)
        self.ne_kolone[k] &= ~(1 << v)

    def _ka_vend_bosh_te_vdekur(self, r, k):
        """Forward checking: pas vendosjes ne (r,k), cdo qelize bosh ne te njejtin
        rresht ose kolone duhet te kete te pakten nje vlere te mundshme."""
        plot = (1 << (self.n + 1)) - 2                 # bitet 1..n
        for kk in range(k + 1, self.n):
            if not (plot & ~(self.ne_rresht[r] | self.ne_kolone[kk])):
                return True
        for rr in range(r + 1, self.n):
            if not (plot & ~(self.ne_rresht[rr] | self.ne_kolone[k])):
                return True
        return False

    def _dls(self, thellesia, kufiri):
        """Depth Limited Search. Kthen 'GJETUR', 'PRERE' (u arrit kufiri) ose 'DESHTIM'.
        thellesia = sa qeliza te lira jane mbushur deri tani."""
        self.nyje_gjithsej += 1
        self._nyje_iter += 1

        if thellesia == len(self.qelizat):
            return "GJETUR"
        if thellesia == kufiri:
            return "PRERE"

        r, k = self.qelizat[thellesia]        # qelizat mbushen rresht pas rreshti
        u_pre = False
        for v in self._renditja_e_vlerave(r, k):
            if not self._lejohet(r, k, v):
                continue                      # krasitje: shkel AllDifferent
            self._vendos(r, k, v)
            if not self._ka_vend_bosh_te_vdekur(r, k):
                rez = self._dls(thellesia + 1, kufiri)
                if rez == "GJETUR":
                    return rez
                if rez == "PRERE":
                    u_pre = True
            self._hiq(r, k, v)                # backtrack
        return "PRERE" if u_pre else "DESHTIM"

    def _renditja_e_vlerave(self, r, k):
        # Fillojme nga vlera ((k - r) mod n) + 1 dhe vazhdojme ciklikisht. Kjo eshte
        # vetem renditje e vlerave (jo heuristike e informuar): te gjitha n vlerat
        # provohen perseri, por dega e pare zakonisht eshte e vlefshme.
        n = self.n
        fillim = (k - r) % n
        return [((fillim + i) % n) + 1 for i in range(n)]

    def zgjidh(self):
        # Thyerje simetrie: cdo katror latin mund te shnderrohet (duke riemertuar vlerat
        # dhe duke nderruar rreshtat) ne nje katror me rreshtin e pare 1, 2, ..., n dhe
        # kolonen e pare 1, n, n-1, ..., 2. Keto qeliza fiksohen; kerkojme vetem te tjerat.
        n = self.n
        self.qelizat = [(r, k) for r in range(1, n) for k in range(1, n)]
        for kufiri in range(0, len(self.qelizat) + 1):
            self._nyje_iter = 0
            # pastrojme matricen para cdo iteracioni (IDDFS rifillon nga rrenja)
            self._gjendja_fillestare()
            rez = self._dls(0, kufiri)
            self.iteracione.append((kufiri, self._nyje_iter, rez))
            if rez == "GJETUR":
                return True
            if rez == "DESHTIM":
                return False
        return False

    def _gjendja_fillestare(self):
        n = self.n
        self.L = [[0] * n for _ in range(n)]
        self.ne_rresht = [0] * n
        self.ne_kolone = [0] * n
        for k in range(n):
            self._vendos(0, k, k + 1)
        for r in range(1, n):
            self._vendos(r, 0, n - r + 1)

    def objective(self):
        n = self.n
        f = 0
        for r in range(n):
            f += n - len(set(x for x in self.L[r] if x))
        for k in range(n):
            f += n - len(set(self.L[r][k] for r in range(n) if self.L[r][k]))
        return f

    def shtyp(self):
        w = len(str(self.n))
        for rreshti in self.L:
            print(" ".join(str(x).rjust(w) for x in rreshti))


def landscape(n):
    pa_kufizime = n ** (n * n)                      # cdo qelize merr cfaredo vlere
    vetem_rreshta = factorial(n) ** n               # cdo rresht eshte permutacion
    return pa_kufizime, vetem_rreshta


if __name__ == "__main__":
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = int(input("Jepni n: "))
    if n < 1:
        print("n duhet te jete >= 1")
        sys.exit(1)

    a, b = landscape(n)
    print(f"Latin Square {n}x{n}")
    print(f"Landscape pa kufizime: {n}^{n * n} = {a:.3e}")
    print(f"Landscape kur cdo rresht eshte permutacion: ({n}!)^{n} = {b:.3e}\n")

    if n >= 7:
        print("Kujdes: IDDFS i rieksploron te gjitha nivelet me te cekta ne cdo iteracion;")
        print("per n >= 7 numri i gjendjeve te pjesshme rritet shume dhe kerkimi zgjat.\n")

    s = LatinSquareIDDFS(n)
    t0 = time.time()
    ok = s.zgjidh()
    dt = time.time() - t0

    print("Iteracionet e IDDFS (kufiri -> nyje te vizituara):")
    for kufiri, nyje, rez in s.iteracione:
        print(f"  L = {kufiri:3d}: {nyje:6d} nyje  [{rez}]")

    if ok:
        print(f"\nDalja (f(S) = {s.objective()}):")
        s.shtyp()
    else:
        print("\nNuk u gjet zgjidhje.")
    print(f"\nNyje gjithsej: {s.nyje_gjithsej}, koha: {dt:.4f}s")
