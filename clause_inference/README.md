# clause_inference - Clause Inference & Evaluation

This module performs inference on generated clause texts using LLM and evaluates the results against Ground Truth (GT).

## Directory Structure

```
clause_inference/
├── run.py              # Main script (inference + evaluation)
├── inference.py        # LLM inference module
├── evaluation.py       # Evaluation module
├── vllm_client.py      # VLLM API client
└── prompts/
    └── gen_bl_iv_prompt_simple.txt  # Inference prompt
```

## File Descriptions

| File | Description |
|------|-------------|
| `run.py` | Integrated script for inference and evaluation |
| `inference.py` | Extract information from clauses using LLM |
| `evaluation.py` | Compare extracted results with GT |
| `vllm_client.py` | VLLM API client |

## Usage

### Run Inference + Evaluation

```bash
cd clause_inference

# Basic usage (qwen3.5_9b, enable-thinking)
python3 run.py \
  --input ../dataset/generated/merged/*.json \
  --output result/qwen3.5_9b_thinking \
  --model qwen3.5_9b \
  --api-url "http://127.0.0.1:8000/v1" \
  --enable-thinking \
  --verbose
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Input JSON file pattern | `clause_sample/*.json` |
| `--output`, `-o` | Output directory | `result/qwen3.5_9b_BL` |
| `--model`, `-m` | Model name | `qwen3.5_9b` |
| `--api-url` | VLLM API URL | `http://127.0.0.1:8000/v1` |
| `--concurrency`, `-C` | Concurrent requests | `20` |
| `--enable-thinking` | Enable thinking mode | `False` |
| `--verbose`, `-v` | Detailed output | `False` |

### Example

```bash
# With thinking mode, concurrency 1
python3 run.py --input ../dataset/generated/merged/*.json \
  --output result/output \
  --model qwen3.5_9b \
  --api-url "http://127.0.0.1:8000/v1" \
  --enable-thinking \
  --concurrency 1 \
  --verbose
```

## Output Files

- `inference_result.json` - LLM inference results
- `evaluation_report.json` - Detailed evaluation report
- `summary.txt` - Evaluation summary

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Precision** | Ratio of correctly extracted items |
| **Recall** | Ratio of GT items correctly extracted |
| **F1-Score** | Harmonic mean of Precision and Recall |