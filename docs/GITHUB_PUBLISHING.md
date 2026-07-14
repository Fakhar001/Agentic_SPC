# GitHub publishing guide

## 1. Create the GitHub repository

Create a new empty repository named:

```text
agentic-spc-healthcare-reference
```

Recommended settings:

- Visibility: public after manuscript and institutional review; otherwise private.
- Do not initialize the repository with a README, `.gitignore`, or license because this package already contains them.
- Suggested description: `Deterministic synthetic reference implementation for Agentic Statistical Process Control.`

## 2. Upload from your computer

Open a terminal in the extracted project folder and run:

```bash
git init
git branch -M main
git add .
git commit -m "Initial reproducible Agentic SPC reference implementation"
git remote add origin https://github.com/YOUR-ACCOUNT/agentic-spc-healthcare-reference.git
git push -u origin main
```

GitHub will request authentication through the browser, Git Credential Manager, or a personal access token, depending on your Git configuration.

## 3. Verify the online repository

After the first push:

1. Open the **Actions** tab and confirm that the `Reproducibility checks` workflow succeeds.
2. Review the generated workflow log to confirm that unit tests, deterministic replication, and result verification pass.
3. Confirm that `outputs/` and `data/` are absent from the repository unless you intentionally add a static release artifact.
4. Confirm that `CITATION.cff`, `LICENSE`, `README.md`, and the five figure sources are visible.

## 4. Create a versioned release

When the manuscript is ready to submit, create a GitHub release tagged:

```text
v0.2.1
```

Use this release note:

```text
This release reproduces the deterministic synthetic healthcare reference scenario reported in the Agentic SPC manuscript. It includes data-quality qualification, frozen Phase I risk adjustment, residual-EWMA monitoring, contextual validation, governance-gated workflow decisions, a tamper-evident prototype audit ledger, and stress-test evaluation.
```

Before release, update the following metadata if needed:

- `CITATION.cff`: authors, manuscript title, DOI, and repository URL;
- `README.md`: final manuscript citation and project description;
- `LICENSE`: copyright holders if the project has co-authors;
- `.github/workflows/ci.yml`: Python versions required by your final environment.

## 5. Recommended scholarly-release practice

For a journal submission, cite the GitHub release tag rather than an unversioned branch. If the journal or institution requires a persistent archival identifier, connect the repository to an archival service and archive the tagged release. Add the resulting DOI to `CITATION.cff` and the manuscript after it has been issued.

## Security and data note

The repository contains no patient, industrial, or confidential operational data. Do not upload real source data, credentials, database dumps, access tokens, protected SOPs, or personally identifiable information to a public repository.
