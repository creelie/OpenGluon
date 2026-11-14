# Models and public proof dialogue

Anaxia can use an installed local model through Ollama or a running llama.cpp-compatible server. Optional adapters also call the official Claude, OpenAI and Kimi APIs. These are inference adapters: the repository does not contain proprietary model weights, the complete ChatGPT/Claude/Kimi products, or a new trained superintelligence.

## Start with an installed local model

List the models already available on a running Ollama server:

```sh
python anaxia.py models --provider ollama
```

Use an exact name from that inventory. The following model name is an example and must already be installed:

```sh
python anaxia.py propose examples/quadratic-sos.json --provider ollama --model gemma3:4b --max-tokens 512 --timeout 120 --output data/local-proposal.json
python anaxia.py reason examples/quartic-sos.json --provider ollama --model gemma3:4b --rounds 2 --max-tokens 768 --timeout 120 --output data/local-reasoning.json
```

`models` is a read-only local inventory and reachability check. It does not pull, train or install weights. Local runtime installation, model licensing, memory and disk requirements remain the responsibility of the selected runtime and model. Larger installed models can require more memory than the machine has available.

For a running llama.cpp server with an OpenAI-compatible API:

```sh
python anaxia.py models --provider openai-compatible --base-url http://127.0.0.1:8080/v1
python anaxia.py reason examples/quartic-sos.json --provider openai-compatible --base-url http://127.0.0.1:8080/v1 --model YOUR_SERVED_MODEL --rounds 2 --output data/llama-reasoning.json
```

[Ollama chat](https://docs.ollama.com/api/chat) supplies inference through `/api/chat`; its [model inventory](https://docs.ollama.com/api/tags) is `/api/tags`. [llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) describes its compatible chat-completion endpoints. Anaxia sends bounded, non-streaming requests and does not execute model-generated code.

## What a reasoning run produces

The `reason` command accepts the explicit polynomial task schema used by `solve`. It first computes and verifies a deterministic baseline. Each round then requests a concise public strategy and candidate evidence, checks that evidence exactly, and obtains a public critique. Failed candidates and critique become feedback for the next round. The default is two rounds, with a hard limit of four and at most two model calls per round. A verified global SOS identity or exact counterexample stops further rounds.

Only rational SOS certificates and integer counterexample witnesses are accepted from the model. Every identity must match the original polynomial coefficient by coefficient; witnesses must lie inside its original domain. The polynomial, variables and domain are fixed throughout. A model's claimed proof status, replacement task, critic approval or persuasive prose cannot upgrade the result. Finite checks keep their finite scope. Each output records the baseline, public strategy summaries, critiques, exact evidence checks, statement hash and final independently checked result.

The dialogue requests public mathematical summaries, not private chain-of-thought. Provider thinking/reasoning fields are discarded; marked inline thinking blocks are removed. Anaxia never runs generated Python, shell commands, downloaded code, or requested model tools. Prompts are an assistance layer; proof soundness comes from the exact verifier.

`propose` also accepts informal JSON research descriptions and source excerpts. It always labels its output `unverified_proposal`. Those descriptions need an explicit supported formalization before entering `reason`; the adapter does not turn an arXiv abstract into a proved conjecture.

## Optional cloud APIs

Choose the provider and model explicitly. These commands make billable inference requests when valid credentials are supplied; none run in hourly discovery or registered deterministic experiments.

| Provider | Required environment variable | API |
| --- | --- | --- |
| `anthropic` | `ANTHROPIC_API_KEY` | Official Claude Messages API |
| `openai` | `OPENAI_API_KEY` | Official OpenAI Chat Completions API |
| `kimi` | `MOONSHOT_API_KEY` | Official Moonshot/Kimi Chat Completions API |

```sh
python anaxia.py propose examples/quadratic-sos.json --provider anthropic --model YOUR_CLAUDE_API_MODEL --output data/claude-proposal.json
python anaxia.py propose examples/quadratic-sos.json --provider openai --model YOUR_OPENAI_API_MODEL --output data/openai-proposal.json
python anaxia.py propose examples/quadratic-sos.json --provider kimi --model YOUR_KIMI_API_MODEL --output data/kimi-proposal.json
```

Use model identifiers available to your account. Subscription access to a chat product does not supply an API credential through Anaxia. No credentials are written to configuration files or reports. Legacy `propose TASK --model MODEL --output FILE` calls retain their original Anthropic default; the recommended local commands explicitly select `--provider ollama`. `reason` and `models` default to Ollama.

The adapters follow the official [Claude Messages API](https://platform.claude.com/docs/en/api/messages), [OpenAI Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), and [Kimi Chat Completions API](https://platform.kimi.ai/docs/api/chat). OpenAI requests use `max_completion_tokens`; compatible and Kimi chat requests use `max_tokens`. Model-dependent feature availability and service limits remain those of the provider.

## Configuration and bounds

[`config/model-profiles.json`](../config/model-profiles.json) contains editable configuration examples and recommends the local Ollama profile. The file does not load models or change CLI defaults: pass the selected profile values as flags. Local requests carry no cloud credentials. Ollama accepts loopback hosts only. Custom compatible endpoints accept loopback HTTP or an explicitly configured public HTTPS host; cloud-compatible authentication uses only `OPENAI_COMPATIBLE_API_KEY`, never another provider's key. Model inventory remains local-only.

Official cloud endpoints are fixed, redirects are disabled, and custom HTTPS hosts are checked for public address resolution. The task/source content cannot choose a network destination. Input is limited to 100 KB, response bodies to 1 MB, output to 1–8192 requested tokens per call, and timeouts to 1–300 seconds per request. There are no automatic retries, purchases or model downloads. Provider failures return a clean error without saving a successful proof report. `reason` exits with code 3 for inconclusive mathematics, 2 for invalid input or provider errors, and 0 for checked proof, bounded-check or counterexample outcomes.
