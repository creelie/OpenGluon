# Automatic upstream updates

Anaxia's Refresh public research sources workflow checks all public repositories under google, google-deepmind, quantumlib and creelie hourly at minute 7 UTC. New repositories and changed push/update timestamps enter the source inventory. For creelie, changed source records and new releases are refreshed incrementally. Managed workspace entries suppress self-trigger loops. This is public source indexing, not automatic execution or proof verification.

The OpenGluon Sync quantumlib workflow checks upstream metadata hourly at minute 17 UTC. It can also be run from Actions → Sync quantumlib → Run workflow. When Anaxia's pin changes, OpenGluon transfers its refreshed source catalogues and regenerates the source-count graphic.

The job updates all public quantumlib repositories, including newly discovered ones, plus the selected mathematical libraries, Anaxia, and the selected `harmonic-ai/IMO2025` and `harmonic-ai/aristotle` sources. It records exact commit IDs in the two lock files and updates the submodule gitlinks. The workflow does not execute upstream code, install dependencies or start Aristotle API jobs. A repository missing from a later quantumlib inventory is retained with its previous pin and an explicit availability note.

Harmonic is a curated selection: new repositories in that organization are not automatically imported. The existing toolkit sync follows the default branches of the two selected repositories. Recorded roles, toolchain and license notes describe the captured source and should be reviewed when upstream capabilities or requirements change.

The workflow uses the built-in GITHUB_TOKEN with contents: write. No personal token or new secret is required. Updates are committed under Deep Bhattacharjee's configured project identity. Full histories and original attribution remain in upstream repositories.

GitHub schedules are polling, not an immediate notification from Google. Scheduled runs can be delayed or disabled after prolonged inactivity. Protection rules can block pushes. The workflow logs and manual trigger remain available for diagnosis.

Remote updates do not alter a local checkout automatically. Update it with:

```sh
git pull --ff-only
git submodule update --init --recursive
python opengluon.py doctor
```

Source pins track current default branches. Published mathematical claims retain their original proof scope; synchronization does not certify them.
