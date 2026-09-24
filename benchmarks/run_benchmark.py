#!/usr/bin/env python3
"""Run a reproducible local benchmark against the Ollama generate API."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OLLAMA_URL = "http://127.0.0.1:11434"
MODELS = ("qwen3:8b", "qwen2.5-coder:7b", "gemma3:4b")
PROMPTS = (
    "python_refactor.txt",
    "sql_analytics.txt",
    "technical_documentation.txt",
)
TEMPERATURE = 0
SEED = 42
NUM_PREDICT = 1024
KEEP_ALIVE = 0
THINK = False
DEFAULT_REPETITIONS = 3
REQUEST_TIMEOUT_SECONDS = 900


def request_json(url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data else {}
    request = Request(url, data=data, headers=headers, method="POST" if data else "GET")

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return json.load(response)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code} from {url}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Cannot reach Ollama at {url}: {error.reason}") from error


def available_models() -> set[str]:
    payload = request_json(f"{OLLAMA_URL}/api/tags")
    return {item["name"] for item in payload.get("models", [])}


def generate(model: str, prompt: str) -> dict:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": THINK,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": TEMPERATURE,
            "seed": SEED,
            "num_predict": NUM_PREDICT,
        },
    }
    return request_json(f"{OLLAMA_URL}/api/generate", payload)


def seconds(nanoseconds: int | float | None) -> float | None:
    if nanoseconds is None:
        return None
    return float(nanoseconds) / 1_000_000_000


def rounded(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark local Ollama models using versioned prompts."
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=DEFAULT_REPETITIONS,
        help=f"Measured runs per model and task (default: {DEFAULT_REPETITIONS}).",
    )
    parser.add_argument(
        "--skip-warmup",
        action="store_true",
        help="Skip one unmeasured warm-up request for each model/task pair.",
    )
    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")

    root = Path(__file__).resolve().parent.parent
    prompt_dir = root / "benchmarks" / "prompts"
    output_root = root / "data" / "benchmarks"
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = output_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    prompts = {}
    for filename in PROMPTS:
        path = prompt_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing prompt file: {path}")
        prompts[path.stem] = path.read_text(encoding="utf-8")

    installed = available_models()
    missing = sorted(set(MODELS) - installed)
    if missing:
        raise RuntimeError(f"Missing Ollama models: {', '.join(missing)}")

    config = {
        "run_id": run_id,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "ollama_url": OLLAMA_URL,
        "models": MODELS,
        "prompts": list(prompts),
        "temperature": TEMPERATURE,
        "seed": SEED,
        "num_predict": NUM_PREDICT,
        "keep_alive": KEEP_ALIVE,
        "think": THINK,
        "repetitions": args.repetitions,
        "warmup_enabled": not args.skip_warmup,
    }
    (output_dir / "run_config.json").write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )

    rows = []
    total_runs = len(MODELS) * len(prompts) * args.repetitions
    completed = 0

    print(f"Results directory: {output_dir}")
    print(f"Measured requests: {total_runs}")
    print("Models run sequentially; do not use Ollama concurrently during this benchmark.\n")

    for model in MODELS:
        for task, prompt in prompts.items():
            if not args.skip_warmup:
                print(f"Warm-up: {model} / {task}")
                generate(model, prompt)

            for repetition in range(1, args.repetitions + 1):
                completed += 1
                print(f"[{completed}/{total_runs}] {model} / {task} / run {repetition}")

                wall_start = time.perf_counter()
                response = generate(model, prompt)
                wall_seconds = time.perf_counter() - wall_start

                response_path = output_dir / f"{model.replace(':', '_')}_{task}_{repetition}.json"
                response_path.write_text(
                    json.dumps(response, indent=2) + "\n",
                    encoding="utf-8",
                )

                eval_seconds = seconds(response.get("eval_duration"))
                prompt_eval_seconds = seconds(response.get("prompt_eval_duration"))
                load_seconds = seconds(response.get("load_duration"))
                total_seconds = seconds(response.get("total_duration"))
                eval_count = response.get("eval_count")
                tokens_per_second = (
                    float(eval_count) / eval_seconds
                    if eval_count is not None and eval_seconds and eval_seconds > 0
                    else None
                )

                rows.append(
                    {
                        "run_id": run_id,
                        "model": model,
                        "task": task,
                        "repetition": repetition,
                        "wall_seconds": rounded(wall_seconds),
                        "total_seconds": rounded(total_seconds),
                        "load_seconds": rounded(load_seconds),
                        "prompt_eval_seconds": rounded(prompt_eval_seconds),
                        "eval_seconds": rounded(eval_seconds),
                        "prompt_eval_count": response.get("prompt_eval_count"),
                        "eval_count": eval_count,
                        "tokens_per_second": rounded(tokens_per_second),
                        "response_characters": len(response.get("response", "")),
                        "done_reason": response.get("done_reason", ""),
                    }
                )

    fieldnames = list(rows[0])
    with (output_dir / "results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCompleted {completed} measured requests.")
    print(f"Summary CSV: {output_dir / 'results.csv'}")
    print("Raw responses and metrics are stored in the same results directory.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError) as error:
        print(f"Benchmark failed: {error}", file=sys.stderr)
        raise SystemExit(1)
