# Run an existing local model reliably

Anaxia can ensure that an explicitly configured llama.cpp CPU server is available before a local research campaign. It probes the server's health and model alias, reuses a matching server, and launches the configured executable only when the port is unreachable. It never replaces another server, downloads model weights, installs binaries, or changes an external Ollama installation.

## Portable setup

Obtain a suitable CPU executable from the [official llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases). Check the archive against its published SHA-256 checksum before extracting it. The [official server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) describes GGUF models, CPU execution, model aliases and the OpenAI-compatible endpoint.

Keep a portable executable and its libraries in an ignored local directory, for example `data/local/runtime/`. Supply a GGUF file you already possess and are authorized to use. An existing Ollama model layer may already be GGUF: inspect its manifest for the model layer and use the existing blob directly, without copying or downloading gigabytes of weights. Compatibility still depends on the model architecture and runtime build.

Create **`data/local/runtime.json`** on your machine. This directory is ignored by Git because it contains machine-specific paths, logs and runtime files.

```json
{
  "schema_version": 1,
  "binary": "runtime/llama-server.exe",
  "model": "models/existing-model.gguf",
  "host": "127.0.0.1",
  "port": 18081,
  "alias": "anaxia-local-model",
  "context": 2048,
  "threads": 4,
  "startup_timeout": 30
}
```

Paths in the configuration are relative to that configuration file, or explicit absolute paths on your machine. Both files must already exist; Windows executables must use the `.exe` suffix. An optional `binary_sha256` field pins the extracted executable's SHA-256 hash. This is distinct from a release archive's checksum.

```sh
python anaxia.py runtime ensure --config data/local/runtime.json
python anaxia.py runtime status --config data/local/runtime.json
python anaxia.py models --provider openai-compatible --base-url http://127.0.0.1:18081/v1
python anaxia.py propose examples/quadratic-sos.json --provider openai-compatible --base-url http://127.0.0.1:18081/v1 --model anaxia-local-model --max-tokens 256 --output data/local/proposal.json
```

The server binds only to `127.0.0.1`, runs on the CPU with GPU layers set to zero, uses a single inference slot, disables its web interface, and starts in offline mode. On Windows its process has no visible window. It receives an argument list without a shell, and cloud API credentials are removed from its environment. Startup waits at most the configured 1–30 second interval, with bounded local health probes. Logs and the PID record remain under `data/local/`.

`ensure` is idempotent for a healthy server reporting the expected model alias. It fails visibly if another service occupies the port, a configured checksum differs, startup exits, or the health/model check does not match. `status` never starts a process. There is no automatic stop command, so Anaxia cannot terminate an unrelated process after PID reuse. A running local server can remain available for later explicitly configured local campaigns.

## Observed local smoke check

The checked-in [runtime summary](../data/model-runtime-check.json) records a real local run using a checksum-verified official portable CPU build and already installed model weights. The local proposal and two-call public reasoning loop completed. Its polynomial proof status came from the deterministic exact baseline; the small model did not produce an accepted additional certificate. The record makes no claim to solve an open conjecture. Machine paths and full model output stay in ignored local files.

Some runtime/model combinations reject grammar-constrained JSON response options. Anaxia requests plain structured JSON in its public prompt and independently validates the returned data, so unsupported grammar features do not become a requirement for local inference. Model prose and arbitrary code remain unverified advice.
