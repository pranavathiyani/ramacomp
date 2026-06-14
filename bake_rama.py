#!/usr/bin/env python3
"""
bake_rama.py - Bake the MolProbity / Top8000 Ramachandran reference
distributions into rama-data.js for RamaComp.

Data source : github.com/rlabduke/reference_data
              Top8000/Top8000_ramachandran_pct_contour_grids/  (licensed CC-BY-4.0)
Reference    : Williams et al. (2018) "MolProbity: More and better reference
               data for improved all-atom structure validation."
               Protein Science 27:293-315.  (Top8000 dataset, Richardson Lab, Duke.)

Usage (needs internet; run it once, e.g. in WSL):
    python3 bake_rama.py
Then put the generated rama-data.js next to index.html and commit both.

Notes
-----
* Six MolProbity categories: general, glycine, Ile/Val, pre-Pro, trans-Pro, cis-Pro.
* Contour cutoffs follow the MolProbity convention: favoured = 98% contour,
  allowed = 99.95% contour, computed as cumulative population of the reference grid.
* The Top8000 contour grids are licensed CC-BY-4.0 (confirmed with the Richardson
  Lab, Dec 2025). Keep the attribution and the Williams et al. 2018 citation.
"""

import urllib.request, base64, struct, sys, json

BASE = "https://raw.githubusercontent.com/rlabduke/reference_data/master/Top8000/Top8000_ramachandran_pct_contour_grids/"
FILES = {
    "general":  "rama8000-general-noGPIVpreP.data",
    "glycine":  "rama8000-gly-sym.data",
    "ileval":   "rama8000-ileval-nopreP.data",
    "prepro":   "rama8000-prepro-noGP.data",
    "transpro": "rama8000-transpro.data",
    "cispro":   "rama8000-cispro.data",
}

FAV_FRAC   = 0.98     # favoured = 98% contour
ALLOW_FRAC = 0.9995   # allowed  = 99.95% contour


def parse(text):
    """Parse a rama8000 .data file into (n, dense n*n grid in row-major psi*n+phi)."""
    n = None
    pts = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            low = line.lstrip("# ").lower()
            if low.startswith("x1:"):
                parts = line.split(":", 1)[1].split()
                n = int(parts[2])           # number_of_bins
            continue
        p = line.split()
        if len(p) < 3:
            continue
        x1, x2, v = float(p[0]), float(p[1]), float(p[-1])
        pts[(x1, x2)] = v
    if n is None:
        n = len({k[0] for k in pts}) or 180
    step = 360.0 / n
    grid = [0.0] * (n * n)
    for (x1, x2), v in pts.items():
        i = int(round((x1 - step / 2.0) / step)) % n   # phi bin
        j = int(round((x2 - step / 2.0) / step)) % n   # psi bin
        grid[j * n + i] = v
    return n, grid


def quantize(grid):
    mx = max(grid) or 1.0
    q = bytearray()
    recon = []
    for v in grid:
        u = int(round(v / mx * 65535))
        u = 0 if u < 0 else (65535 if u > 65535 else u)
        q += struct.pack("<H", u)
        recon.append(u / 65535.0 * mx)
    return mx, bytes(q), recon


def cutoffs(grid):
    """Density level enclosing FAV_FRAC / ALLOW_FRAC of the population."""
    total = sum(grid)
    if total <= 0:
        return 0.0, 0.0
    s = sorted(grid, reverse=True)
    cum = 0.0
    fav = allow = 0.0
    fav_set = False
    for v in s:
        cum += v
        if not fav_set and cum / total >= FAV_FRAC:
            fav = v; fav_set = True
        if cum / total >= ALLOW_FRAC:
            allow = v
            break
    return fav, allow


def main():
    classes = {}
    for cls, fname in FILES.items():
        url = BASE + fname
        sys.stderr.write("fetching %s ...\n" % fname)
        try:
            raw = urllib.request.urlopen(url, timeout=120).read()
            text = raw.decode("utf-8", "replace")
        except Exception as e:
            sys.stderr.write("  ERROR: %s\n  tried: %s\n"
                             "  If the path moved, check github.com/rlabduke/reference_data.\n" % (e, url))
            sys.exit(1)
        n, grid = parse(text)
        mx, qbytes, recon = quantize(grid)         # cutoffs on the *reconstructed* grid
        fav, allow = cutoffs(recon)                # so they match what the browser sees
        classes[cls] = {
            "n": n,
            "max": mx,
            "fav": fav,
            "allow": allow,
            "b64": base64.b64encode(qbytes).decode("ascii"),
        }
        sys.stderr.write("  n=%d  fav=%.4g  allow=%.4g  cells=%d\n" % (n, fav, allow, n * n))

    payload = {
        "source": "Top8000 / MolProbity (Richardson Lab, Duke). Williams et al. 2018 Protein Science 27:293-315.",
        "favFrac": FAV_FRAC,
        "allowFrac": ALLOW_FRAC,
        "classes": classes,
    }
    js = "window.RAMA_DATA=" + json.dumps(payload, separators=(",", ":")) + ";\n"
    with open("rama-data.js", "w") as fh:
        fh.write(js)
    sys.stderr.write("wrote rama-data.js (%.0f KB)\n" % (len(js) / 1024.0))


if __name__ == "__main__":
    main()
