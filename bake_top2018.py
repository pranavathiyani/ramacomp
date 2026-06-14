#!/usr/bin/env python3
"""
bake_top2018.py - Build Ramachandran contour grids from the Top2018 main-chain
per-residue dataset and bake them into rama-top2018.js for RamaComp.

Data source : pydangle top2018 MC (Prisant, 2026), CC-BY-4.0
              https://doi.org/10.5281/zenodo.19040026
              file: top2018mc_measures.jsonl.gz  (~74 MB, ~3M residues)
References   : Williams et al. (2021) Protein Science 30:170-184 (Top2018);
              Williams et al. (2018) Protein Science 27:293-315 (MolProbity);
              Read et al. (2011) Structure 19:1395-1412 (rama categories).

Each JSONL record carries phi, psi (degrees, may be null) and a six-class
Ramachandran label (rama_category / rama6): General, Gly, IleVal, TransPro,
CisPro, PrePro. We group by that label, build a phi/psi histogram per class,
smooth it on the torus, and derive the 98% / 99.95% population contours -
the same convention RamaComp uses for the Top8000 grids.

Requires: numpy   (pip install numpy)
Usage (needs internet; large download):  python3 bake_top2018.py
Then place rama-top2018.js next to index.html and commit it.

The smoothing bandwidth (SIGMA_DEG) is the one methodological choice here. The
default is a sane value for ~3M residues; for contours that match the Richardson
Lab's published methodology precisely, ask them for their KDE parameters.
"""

import urllib.request, gzip, json, base64, struct, sys
import numpy as np

URL = "https://zenodo.org/records/19040026/files/top2018mc_measures.jsonl.gz?download=1"

# pydangle/Read-2011 six-class labels -> RamaComp internal keys
CATMAP = {
    "general": "general", "gly": "glycine", "ileval": "ileval",
    "prepro": "prepro", "transpro": "transpro", "cispro": "cispro",
}
CLASSES = ["general", "glycine", "ileval", "prepro", "transpro", "cispro"]

RES_DEG    = 2.0      # grid spacing (deg); n = 360/RES_DEG bins per axis
SIGMA_DEG  = 3.0      # Gaussian smoothing bandwidth (deg) on the torus
FAV_FRAC   = 0.98     # favoured = 98% contour
ALLOW_FRAC = 0.9995   # allowed  = 99.95% contour

N = int(round(360.0 / RES_DEG))


def category_of(rec):
    for k in ("rama_category", "rama6", "rama", "ramaCategory"):
        if k in rec and rec[k] is not None:
            return CATMAP.get(str(rec[k]).strip().lower())
    return None


def gaussian_wrap(grid, sigma_bins):
    if sigma_bins <= 0:
        return grid
    rad = max(1, int(round(3 * sigma_bins)))
    xs = np.arange(-rad, rad + 1)
    k = np.exp(-0.5 * (xs / sigma_bins) ** 2)
    k /= k.sum()
    out = np.zeros_like(grid)
    for off, w in zip(xs, k):
        out += w * np.roll(grid, int(off), axis=0)
    tmp, out = out, np.zeros_like(grid)
    for off, w in zip(xs, k):
        out += w * np.roll(tmp, int(off), axis=1)
    return out


def cutoffs(grid):
    flat = np.sort(grid.ravel())[::-1]
    total = flat.sum()
    if total <= 0:
        return 0.0, 0.0
    cum = np.cumsum(flat) / total
    fav = float(flat[np.searchsorted(cum, FAV_FRAC)])
    ai = np.searchsorted(cum, ALLOW_FRAC)
    allow = float(flat[min(ai, len(flat) - 1)])
    return fav, allow


def main():
    counts = {c: np.zeros((N, N), dtype=np.float64) for c in CLASSES}
    n_read = n_used = 0
    step = 360.0 / N
    printed_keys = False

    sys.stderr.write("downloading + streaming %s\n" % URL)
    try:
        resp = urllib.request.urlopen(URL, timeout=300)
        gz = gzip.open(resp)
    except Exception as e:
        sys.stderr.write("  ERROR opening dataset: %s\n  Check the DOI/file at "
                         "https://doi.org/10.5281/zenodo.19040026\n" % e)
        sys.exit(1)

    for raw in gz:
        n_read += 1
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        if not printed_keys:
            sys.stderr.write("  first-record keys: %s\n" % ", ".join(rec.keys()))
            printed_keys = True
        phi, psi = rec.get("phi"), rec.get("psi")
        if phi is None or psi is None:
            continue
        cls = category_of(rec)
        if cls is None:
            continue
        i = int(((phi % 360.0) + 360.0) % 360.0 / step) % N   # phi bin
        j = int(((psi % 360.0) + 360.0) % 360.0 / step) % N   # psi bin
        counts[cls][j, i] += 1.0
        n_used += 1
        if n_read % 500000 == 0:
            sys.stderr.write("  ...%d records\n" % n_read)

    if n_used == 0:
        sys.stderr.write("  ERROR: no usable records. The phi/psi or category field "
                         "names may differ - see 'first-record keys' above and tell "
                         "me what they are.\n")
        sys.exit(1)
    sys.stderr.write("  read %d records, used %d\n" % (n_read, n_used))

    sigma_bins = SIGMA_DEG / step
    out = {}
    for cls in CLASSES:
        g = gaussian_wrap(counts[cls], sigma_bins)
        mx = float(g.max()) or 1.0
        q = (np.clip(np.round(g / mx * 65535.0), 0, 65535)).astype("<u2")
        recon = q.astype(np.float64) / 65535.0 * mx
        fav, allow = cutoffs(recon)
        out[cls] = {
            "n": N, "max": mx, "fav": fav, "allow": allow,
            "b64": base64.b64encode(q.tobytes()).decode("ascii"),
        }
        sys.stderr.write("  %-8s n=%d fav=%.4g allow=%.4g count=%d\n"
                         % (cls, N, fav, allow, int(counts[cls].sum())))

    payload = {
        "source": "Top2018 MC (Prisant 2026, pydangle), CC-BY-4.0. "
                  "Williams et al. 2021 Protein Science 30:170-184.",
        "res": RES_DEG, "sigmaDeg": SIGMA_DEG,
        "favFrac": FAV_FRAC, "allowFrac": ALLOW_FRAC,
        "classes": out,
    }
    js = "window.RAMA_TOP2018=" + json.dumps(payload, separators=(",", ":")) + ";\n"
    with open("rama-top2018.js", "w") as fh:
        fh.write(js)
    sys.stderr.write("wrote rama-top2018.js (%.0f KB)\n" % (len(js) / 1024.0))


if __name__ == "__main__":
    main()
