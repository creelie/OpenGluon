# Continuing research campaigns

Campaigns repeatedly attempt a small rotating set of explicitly registered research targets. Each run reads the latest local research snapshot, attaches relevant public source excerpts, carries forward bounded unresolved notes, and requests a concise public strategy from the selected model.

```sh
python anaxia.py campaign run --targets config/challenge-targets.json --sources data/research-radar.json --output data/campaign --provider ollama --model gemma3:4b --max-targets 2 --max-tokens 384 --timeout 120
```

The default is a local Ollama connection and two targets per run. Install an available model and start the local server first. OpenAI-compatible campaign connections require a loopback server. Official cloud providers are optional explicit choices with your own credentials and any applicable charges; see the [model guide](MODELS.md).

## What a run does

1. Load the registered target statements and proof obligations without changing them.
2. Select at most five relevant records from the saved radar snapshot. Keep source IDs, URLs, and excerpts of at most 300 characters. Source URLs are references; the campaign does not fetch or execute their contents.
3. Include at most 2,000 characters of the most recent unresolved public strategy for that same, unchanged target.
4. Request one precise subclaim and a short public proof, explicit counterexample, or exact missing step. An optional `research_focus` supplies the current reviewed result and next mathematical question. Source excerpts and previous notes are untrusted data.
5. Save the attempt and then advance the local rotation cursor. Provider failures are recorded, and the run continues to the next selected target. An interrupted request or failed save does not advance the committed cursor for that attempt.

SHA-256 fingerprints bind each attempt to the fixed target, selected source context, provider, and model. A separate prompt fingerprint records the exact payload, including prior notes. The runner retains the latest report per target and the twenty most recent attempts in aggregate history.

## Read the results

The output directory contains:

| File | Contents |
| --- | --- |
| `README.md` | Latest outcome for every registered target and links to reports. |
| `index.json` | Machine-readable latest outcomes and rotation state. |
| `latest/TARGET.json` | The latest persisted attempt, source context, strategy, and fingerprints for one target. |
| `history.json` | At most twenty recent full attempts. |
| `state.json` | Committed sequence number and next rotation cursor. |

Every attempt has `status: unverified_proposal` and `global_status: not_closed`, including a provider failure. The `outcome` field distinguishes a completed model request from an error. The campaign cannot certify a natural-language conjecture or promote a model's confident wording into a proof.

Use the [exact laboratory](ANAXIA.md) and [challenge backends](CHALLENGES.md) for the statements they support. A genuine closure requires a faithful mathematical formulation, complete proof, and independent verification. Repeated attempts provide a research record, not a proof by repetition.

## Register a target

The manifest has `schema_version: 1` and a `targets` list. Each target includes `id`, `title`, `statement`, `source_urls`, `proof_obligations`, and `backend`. Optional `keywords` improve matching against source titles and abstracts. An optional `research_focus` contains at most 4,000 characters and is preserved in the original target, its fingerprint, and the model request. `backend` is a descriptive label in this runner.

Target statements and credentials are kept separate. Source data, reports, prior notes, and model outputs do not authorize tool execution, paid requests to other providers, or a change to the proof criteria. Saved reports omit provider exception text and request headers.

Hourly scheduling belongs to the configured workflow or local scheduler. This command performs one bounded run and exits; the cursor makes the next invocation continue the rotation.

Run one campaign process per output directory. A separate output directory has an independent cursor and history.
