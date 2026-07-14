# Figure sources

Figures 1, 2, 3, and 5 are stored as Mermaid (`.mmd`) source files so that their conceptual content remains version controlled and editable. Figure 4 is produced automatically by the Python replication pipeline.

## Render Mermaid figures locally

With Node.js installed:

```bash
npx -y @mermaid-js/mermaid-cli -i figures/figure_1_evolution.mmd -o figures/rendered/figure_1_evolution.png -b transparent
```

Repeat for the remaining `.mmd` files, or use:

```bash
bash scripts/render_mermaid_figures.sh
```

The diagrams contain no empirical data. They are manuscript figures that describe the conceptual architecture, workflow, and evaluation pathway.
