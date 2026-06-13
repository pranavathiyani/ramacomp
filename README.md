# RamaComp

Compare backbone **φ/ψ (Ramachandran) plots** across two or more protein structures, side by side, in the browser. Drop in PDB or mmCIF files, read the maps together, and export publication-ready figures. Nothing is uploaded — all parsing and geometry runs locally on your machine.

**▶ Live: [pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/)** — no install, nothing to set up.

*Co-developed by Pranavathiyani Gnanasekar & Claude.*

---

## Why

Most Ramachandran tools (MolProbity, RAMPAGE, RamPlot, the viewers in PyMOL/ChimeraX/VMD) are built around a single structure at a time. When you want to put a predicted model next to its experimental counterpart, or compare two refinements, or look at a handful of homologues together, you end up generating plots one by one and lining them up by hand. RamaComp does that comparison in one view, and exports the whole panel as a single figure.

## Features

- **Multiple structures at once.** Load any number of files; each gets its own plot. Choose how many sit side by side (1–5 columns, or auto).
- **PDB and mmCIF.** Author numbering is preferred when present, with fallback to label fields. First model only; the highest-occupancy alternate conformation is kept.
- **Honest reference contours** for the four standard residue classes (general, glycine, proline, pre-proline), with each residue scored against its own class.
- **Interactive.** Hover any point for chain, residue, φ, ψ, class, and region. Per-structure favoured/allowed/outlier counts, plus a clickable outlier list that highlights the point on the plot.
- **Colour by residue type or by chain**, and filter to outliers only.
- **Export in PNG, JPEG, SVG, and PDF** — both for a single plot and for a combined side-by-side comparison figure of the structures you select. SVG is true vector for the axes, points, and labels (the smooth contour field is embedded as a raster layer), so you can edit it in Illustrator or Inkscape.

## How to use

1. Open **[pranavathiyani.github.io/ramacomp](https://pranavathiyani.github.io/ramacomp/)** (or `index.html` locally).
2. Drag structure files onto the drop zone, or click **Add files**. Accepts `.pdb`, `.ent`, `.cif`, `.mmcif`.
3. Set **Columns** for the side-by-side layout, pick the **reference contour** set, and choose how points are coloured.
4. To export one plot, use the download icon on its card and pick a format.
5. To export a comparison figure, tick **compare** on the cards you want (or leave all unticked to include every plot), then **Export comparison** and choose a format. The figure layout follows your **Columns** setting.

## How it works

For each residue with an intact peptide bond on both sides:

```
φ = dihedral( C(i−1), N(i),  Cα(i), C(i)   )
ψ = dihedral( N(i),   Cα(i), C(i),  N(i+1) )
```

Dihedrals use the Praxeolitic formula (IUPAC sign convention). A residue is only plotted when the C(i−1)–N(i) and C(i)–N(i+1) peptide bonds are both shorter than 2.0 Å, so terminal residues and chain breaks are skipped rather than producing spurious angles.

Residue classes follow MolProbity precedence: **Gly → Pro → pre-Pro → general**. Each point is scored against its own class as favoured, allowed, or outlier.

### About the contours and percentages

The favoured/allowed regions are a smooth analytical model (a Gaussian mixture placed on the canonical basins), **not** the MolProbity reference densities. They are meant for reading the shape of conformational space and comparing structures against each other. The favoured/allowed/outlier percentages are indicative, not a substitute for validation-grade statistics. For deposition or structure validation, use MolProbity or Phenix.

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

## License

Released under the MIT License. Add a `LICENSE` file with the MIT text to make it explicit.
