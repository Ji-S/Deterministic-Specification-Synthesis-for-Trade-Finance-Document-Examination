"""
Clause Inference & Evaluation - Integrated Execution Script

Run inference and evaluation together.

Usage Example:
    # Inference + Evaluation at once
    python3 run.py --input clause_sample/*.json --output output/
    
    # Print detailed report
    python3 run.py --input clause_sample/*.json --output output/ --verbose
"""

import asyncio
import json
import glob
import os
import sys
from pathlib import Path
from typing import List, Dict

# Module imports
from inference import run_inference, load_clause_json
from evaluation import run_evaluation


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Clause inference & evaluation (all-in-one)")
    parser.add_argument(
        "--input", "-i",
        default="clause_sample/*.json",
        help="Input JSON file pattern (glob)"
    )
    parser.add_argument(
        "--prompt", "-p",
        default=None,
        help="Prompt template file path"
    )
    parser.add_argument(
        "--output", "-o",
        default="result/qwen3.5_9b_BL",
        help="Output directory path"
    )
    parser.add_argument(
        "--model", "-m",
        default="qwen3.5_9b",
        help="Model name"
    )
    parser.add_argument(
        "--api-url",
        default=None,
        help="VLLM API URL (default: http://localhost:8000/v1)"
    )
    parser.add_argument(
        "--concurrency", "-C",
        type=int,
        default=20,
        help="Number of concurrent requests (default: 20)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed results"
    )
    parser.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Enable thinking mode for model"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Sampling seed; vary across runs (e.g., 0/1/2) to average sampling variance"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="JSON files (alternative to --input)"
    )
    
    args = parser.parse_args()
    
    # Set paths relative to current script directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(script_dir)
    
    # Process input file list
    input_files = []
    
    # Collect .json files from sys.argv (when shell expanded)
    for arg in sys.argv[2:]:
        if arg.endswith('.json') and not arg.startswith('-'):
            input_files.append(arg)
    
    # Expand with glob if shell didn't expand
    if not input_files:
        input_pattern = args.input
        if not input_pattern.startswith("/") and not os.path.isabs(input_pattern):
            input_pattern = str(project_dir / input_pattern)
        input_files = glob.glob(input_pattern)
    
    if not input_files:
        print(f"No files found matching: {args.input}")
        sys.exit(1)
    
    # Set prompt path
    prompt_path = args.prompt
    if prompt_path is None:
        # Use prompts/gen_bl_iv_prompt_simple.txt
        if os.path.exists(str(script_dir / "prompts" / "gen_bl_iv_prompt_simple.txt")):
            prompt_path = str(script_dir / "prompts" / "gen_bl_iv_prompt_simple.txt")
        else:
            prompt_path = str(script_dir / "gen_bl_iv_prompt_simple.txt")
    
    # Set output directory
    output_dir = args.output if os.path.isabs(args.output) else str(script_dir / args.output)
    
    # Run inference and evaluation
    async def run():
        # 1. Run inference
        results = await run_inference(
            input_files=input_files,
            prompt_path=prompt_path,
            output_dir=output_dir,
            model=args.model,
            api_url=args.api_url,
            concurrency=args.concurrency,
            seed=args.seed,
            enable_thinking=args.enable_thinking
        )
        
        # 2. Run evaluation
        report = run_evaluation(results, output_dir, verbose=args.verbose)
        
        return report
    
    report = asyncio.run(run())
    
    print(f"\n✅ Done! Check output directory: {output_dir}")


if __name__ == "__main__":
    main()