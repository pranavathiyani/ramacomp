# RamaComp

Compare backbone **φ/ψ (Ramachandran) plots** across two or more protein structures, side by side, in the browser. Drop in PDB or mmCIF files, read the maps together, and export publication-ready figures. Nothing is uploaded — all parsing and geometry runs locally on your machine.

**▶ Live: [pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/)** — no install, nothing to set up.

*Co-developed by Pranavathiyani Gnanasekar & Claude.*

---

## Why

Most Ramachandran tools (MolProbity, RAMPAGE, RamPlot, the viewers in PyMOL/ChimeraX/VMD) are built around a single structure at a time. When you want to put a predicted model next to its experimental counterpart, or compare two refinements, or look at a handful of homologues together, you end up generating plots one by one and lining them up by hand. RamaComp does that comparison in one view, and exports the whole panel as a single figure.

## Features

- **Two ways in.** Drop/open local `.pdb` / `.mmcif` files, or **fetch by ID** — a PDB code pulls from RCSB, a UniProt/AlphaFold accession pulls the model from the AlphaFold DB.
- **Multiple structures at once.** Each gets its own plot; choose how many sit side by side (1–5, or auto, and it never crowds them below readable width on small screens).
- **PDB and mmCIF.** Author numbering preferred, with fallback to label fields. First model only; highest-occupancy altloc kept.
- **Reference contours** for the six MolProbity residue categories (general, glycine, Ile/Val, pre-Pro, trans-Pro, cis-Pro), each residue scored against its own category. With the Top8000 reference data baked in (see [Reference data](#reference-data)), the contours and favoured/allowed/outlier calls are the actual MolProbity reference distributions (favoured = 98% contour, allowed = 99.95% contour). Without the data file, RamaComp falls back to a built-in analytical approximation (four categories, indicative percentages only).
- **Colour points** by residue type, by chain, or by **B-factor / pLDDT** (a low→high ramp over the B-factor column — temperature factor for crystal structures, confidence for AlphaFold models).
- **Interactive.** Hover for chain, residue, φ, ψ, class, region, and B-factor/pLDDT. Per-structure favoured/allowed/outlier counts and a clickable outlier list.
- **Export** a single plot or a combined side-by-side comparison as **PNG, JPEG, SVG, or PDF**, or the underlying angles as **CSV**. SVG keeps axes, points, and labels as true vectors (the contour field rides along as a raster layer).

## How to use

1. Open **[pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/)** (or `index.html` locally).
2. In the **Workspace** tab, add structures: drag/open files, or type IDs into **Fetch by ID** (e.g. `1UBQ, 4HHB` or `P69905, AF-P69905`, comma-separated).
3. Set **Columns**, pick the **reference contour** set, and choose how points are coloured (residue type / chain / B-factor·pLDDT).
4. Hover points to inspect; open the outlier list under a plot to jump to outliers.
5. Export one plot from the download icon on its card, or tick **compare** on several (or none = all) and use **Export comparison**. Pick PNG/JPEG/SVG/PDF for a figure, or CSV for the data.

The **About / Help** tab documents the method and limitations in full.

### Fetching structures

IDs are routed automatically: a 4-character code (`1UBQ`) is treated as a PDB entry and pulled from `files.rcsb.org`; a UniProt or AlphaFold accession (`P69905`, `AF-P69905`) goes to the AlphaFold DB. AlphaFold filenames are version-stamped (currently `…model_v6`), so RamaComp asks the AlphaFold **prediction API** (`/api/prediction/{accession}`) for the current file URL rather than hard-coding a version. Everything is fetched directly from those public servers to your browser; nothing passes through any RamaComp backend (there isn't one).

## How it works

For each residue with an intact peptide bond on both sides:

```
φ = dihedral( C(i−1), N(i),  Cα(i), C(i)   )
ψ = dihedral( N(i),   Cα(i), C(i),  N(i+1) )
```

Dihedrals use the Praxeolitic formula (IUPAC sign convention). A residue is only plotted when the C(i−1)–N(i) and C(i)–N(i+1) peptide bonds are both shorter than 2.0 Å, so terminal residues and chain breaks are skipped rather than producing spurious angles.

Residues are sorted into the six MolProbity categories — **cis-Pro, trans-Pro, Gly, pre-Pro, Ile/Val, general** (in that precedence). cis vs trans proline is decided by the peptide ω angle (the Cα–C–N–Cα dihedral; |ω| < 30° is cis). Each residue is scored against its own category's reference distribution as favoured, allowed, or outlier.

### About the contours and percentages

When the Top8000 reference data file (`rama-data.js`) is present, the contours and the favoured/allowed/outlier calls are the actual MolProbity reference distributions (Top8000, Richardson Lab, Duke), with favoured = the 98% contour and allowed = the 99.95% contour of the reference population — the same convention MolProbity and Phenix use. If that file isn't loaded, RamaComp falls back to a built-in analytical approximation of the basins (four categories, indicative percentages only). Either way, for formal deposition or validation use MolProbity or Phenix directly.

## Reference data

The validation-grade contours come from the **Top8000** Ramachandran reference distributions (Richardson Lab, Duke; the same data MolProbity and Phenix use). They are not committed in raw form — they are downloaded and baked into a compact `rama-data.js` by a one-off script:

```bash
python3 bake_rama.py     # needs internet; writes rama-data.js
```

`bake_rama.py` fetches the six grids (`rama8000-general-noGPIVpreP`, `rama8000-gly-sym`, `rama8000-ileval-nopreP`, `rama8000-prepro-noGP`, `rama8000-transpro`, `rama8000-cispro`) from [`github.com/rlabduke/rotarama_data`](https://github.com/rlabduke/rotarama_data), computes the 98% / 99.95% population contours, quantises each grid to a `uint16` base64 blob, and writes `window.RAMA_DATA`. Place `rama-data.js` next to `index.html` and commit both; `index.html` loads it with a `<script>` tag and upgrades automatically (and degrades gracefully to the analytical fallback if it's missing).

Reference: Williams et al. (2018), *MolProbity: More and better reference data for improved all-atom structure validation*, **Protein Science** 27:293–315. Confirm the `chem_data` repository's terms before redistributing the baked data, and keep the citation.

### Known simplifications

- With the Top8000 data loaded: the full six MolProbity categories including cis/trans-proline (via ω) and Ile/Val. Without it, a four-category analytical fallback (Ile/Val fold into *general*; cis/trans-proline merged).
- ω is used only to split cis/trans-proline; non-proline cis-peptides and twisted peptides are not separately flagged.
- One altloc per atom (highest occupancy); first model only for multi-model files.

## Run your own copy

The canonical instance is already live at [pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/). To host your own (e.g. a fork):

1. Create a public repository named `ramacomp`.
2. Add `index.html` to the repository root, along with `README.md` and (for validation-grade contours) `rama-data.js` generated by `bake_rama.py`.
3. In the repo, go to **Settings → Pages**, set **Source** to *Deploy from a branch*, branch `main`, folder `/ (root)`, and save.
4. After a minute it goes live at `https://<your-username>.github.io/ramacomp/`.

To run it without hosting, just open `index.html` in any modern browser — no build step or server needed.

### A note on dependencies

The page pulls IBM Plex fonts and the jsPDF library from a CDN. PNG, JPEG, and SVG export work entirely offline; only PDF export needs jsPDF to have loaded. If it can't reach the CDN, the rest of the tool still works and PDF export reports the problem instead of failing silently.

## Browser support

Tested against current Chromium, Firefox, and WebKit. Uses Canvas and inline SVG; no framework, no bundler — a single self-contained HTML file.

## Data sources & credits

Structures are fetched from the [RCSB PDB](https://www.rcsb.org) and the [AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk) (Jumper et al. 2021, *Nature*; Varadi et al. 2024, *NAR*; AlphaFold DB content is CC-BY-4.0). Ramachandran reference distributions are the Top8000 dataset from the Richardson Lab, Duke (Williams et al. 2018, *Protein Science* 27:293–315). Co-developed by Pranavathiyani Gnanasekar & Claude.

## License

Released under the [MIT License](LICENSE).
