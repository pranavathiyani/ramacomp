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
- **Reference contours** for the four standard residue classes (general, glycine, proline, pre-proline), each residue scored against its own class. Thresholds are calibrated to MolProbity-like coverage (~98% favoured for a canonical structure).
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

Residue classes follow MolProbity precedence: **Gly → Pro → pre-Pro → general**. Each point is scored against its own class as favoured, allowed, or outlier.

### About the contours and percentages

The favoured/allowed regions are a smooth analytical model (a Gaussian mixture on the canonical basins), **not** the MolProbity reference densities. The thresholds are calibrated so a structure following the canonical distribution reads about 98% favoured / 2% allowed, mirroring the MolProbity convention — but the model is still an approximation. Read it for the shape of conformational space and for comparing structures; treat the percentages as indicative, not validation-grade. For deposition or structure validation, use MolProbity or Phenix.

### Known simplifications

- Four residue classes, not MolProbity's six. Ile/Val are folded into *general*; cis- and trans-proline are not separated.
- The ω (peptide) angle is not computed, so cis-peptides are not flagged.
- One altloc per atom (highest occupancy); first model only for multi-model files.

## Run your own copy

The canonical instance is already live at [pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/). To host your own (e.g. a fork):

1. Create a public repository named `ramacomp`.
2. Add `index.html` to the repository root, along with `README.md`.
3. In the repo, go to **Settings → Pages**, set **Source** to *Deploy from a branch*, branch `main`, folder `/ (root)`, and save.
4. After a minute it goes live at `https://<your-username>.github.io/ramacomp/`.

To run it without hosting, just open `index.html` in any modern browser — no build step or server needed.

### A note on dependencies

The page pulls IBM Plex fonts and the jsPDF library from a CDN. PNG, JPEG, and SVG export work entirely offline; only PDF export needs jsPDF to have loaded. If it can't reach the CDN, the rest of the tool still works and PDF export reports the problem instead of failing silently.

## Browser support

Tested against current Chromium, Firefox, and WebKit. Uses Canvas and inline SVG; no framework, no bundler — a single self-contained HTML file.

## Data sources & credits

Structures are fetched from the [RCSB PDB](https://www.rcsb.org) and the [AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk) (Jumper et al. 2021, *Nature*; Varadi et al. 2024, *NAR*; AlphaFold DB content is CC-BY-4.0). Co-developed by Pranavathiyani Gnanasekar & Claude.

## License

Released under the [MIT License](LICENSE).
