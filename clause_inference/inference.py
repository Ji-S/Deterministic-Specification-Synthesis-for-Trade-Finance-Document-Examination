"""
Clause Inference Module

This module provides inference functionality for clause text analysis.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Import vllm_client
from vllm_client import VLLMClient


def load_prompt(prompt_path: str) -> str:
    """Load prompt from file"""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def load_clause_json(file_path: str) -> Dict:
    """Load clause JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # If it's an extracted empty item array (list with clause_text only)
    if isinstance(data, list):
        return {"clauses": data, "is_extracted": True}
    
    return data


def build_prompt(prompt_template: str, clause_text: str) -> str:
    """Build prompt by inserting clause text into template"""
    return prompt_template.replace("{clause_text}", clause_text)


async def infer_single_clause(
    client: VLLMClient,
    prompt_template: str,
    clause_text: str,
    model: str = "",
    seed: int = 42
) -> Dict:
    """Extract information from single clause text.

    Decoding params are fixed (Qwen3.5 recommended) inside the client; only
    `seed` is variable so callers can average multiple runs.
    """
    prompt = build_prompt(prompt_template, clause_text)

    result = await client.call(
        prompt=prompt,
        model=model,
        seed=seed
    )

    return result


async def run_inference(
    input_files: List[str],
    prompt_path: str,
    output_dir: str,
    model: str = "qwen3.5_9b",
    api_url: str = "http://localhost:8000/v1",
    concurrency: int = 10,
    seed: int = 42,
    enable_thinking: bool = False
) -> List[Dict]:
    """Run inference (parallel processing)"""
    # Load prompt
    prompt_template = load_prompt(prompt_path)
    
    print(f"Processing {len(input_files)} files with concurrency={concurrency}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create VLLMClient
    async with VLLMClient(api_url=api_url, model_name=model, enable_thinking=enable_thinking) as client:
        # Control concurrency with Semaphore
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_single_file(file_path: str) -> Dict:
            """Process single file (controlled by semaphore)"""
            async with semaphore:
                print(f"  Starting: {os.path.basename(file_path)}")
                
                # Load JSON file
                data = load_clause_json(file_path)
                
                # If it's an extracted empty item array (use clause_text key)
                if data.get("is_extracted"):
                    clause_text = data.get("clauses", [{}])[0].get("clause_text", "") if data.get("clauses") else ""
                    is_extracted_list = True
                else:
                    clause_text = data.get("generated_clause", "")
                    is_extracted_list = False
                
                if not clause_text:
                    print(f"  Warning: No 'clause_text' or 'generated_clause' found in {file_path}")
                    return {
                        "file_path": file_path,
                        "im_path": data.get("im_path", ""),
                        "generated_clause": "",
                        "GT": data.get("GT", []),
                        "inference_result": {},
                        "raw_response": "",
                        "error": "No clause_text found"
                    }
                
                # Perform inference
                result = await infer_single_clause(client, prompt_template, clause_text, model, seed=seed)
                
                # Store result
                raw_resp = result.get("raw_response", "")
                raw_reasoning = result.get("raw_reasoning", "")
                inf_result = result.get("result", {})
                
                # Debug output if raw_response is None or empty
                if not raw_resp:
                    print(f"  Warning: Empty raw_response - {os.path.basename(file_path)}")
                
                result_entry = {
                    "file_path": file_path,
                    "im_path": data.get("im_path", ""),
                    "generated_clause": clause_text,
                    "GT": data.get("GT", []),
                    "inference_result": inf_result,
                    "raw_response": raw_resp if raw_resp else "",
                    "raw_reasoning": raw_reasoning if raw_reasoning else "",
                    "error": result.get("error", None)
                }
                
                if result.get("error"):
                    print(f"  Error: {result.get('error')} - {os.path.basename(file_path)}")
                elif inf_result:
                    print(f"  Done: {len(inf_result) if isinstance(inf_result, list) else 'dict'} fields - {os.path.basename(file_path)}")
                else:
                    print(f"  Warning: No result - {os.path.basename(file_path)}")
                    print(f"    raw_response (first 200 chars): {raw_resp[:200] if raw_resp else 'None'}")
                
                return result_entry
        
        # Process all files in parallel
        tasks = [process_single_file(file_path) for file_path in input_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  Exception: {result} - {input_files[i]}")
                processed_results.append({
                    "file_path": input_files[i],
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        # Save inference results
        inference_path = os.path.join(output_dir, "inference_result.json")
        with open(inference_path, "w", encoding="utf-8") as f:
            json.dump(processed_results, f, indent=2, ensure_ascii=False)
        print(f"\nInference results saved to: {inference_path}")
        
        return processed_results