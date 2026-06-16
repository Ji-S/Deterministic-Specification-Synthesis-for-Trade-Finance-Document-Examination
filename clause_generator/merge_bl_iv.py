"""
Merge BL and IV JSON files into a single file with ++ separator for generated_clause
"""

import json
import os
import glob
import random
from pathlib import Path
from typing import Dict, List, Optional

def load_json(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def merge_bl_iv(bl_file: str, iv_file: str, output_path: str):
    """
    Merge BL and IV files:
    - generated_clause: "++ [BL clause] ++ [IV clause]"
    - GT: Add "doc": "BL" or "doc": "IV" to each item
    - im_path: Separate into BL_im_path and IV_im_path
    """
    bl_data = load_json(bl_file)
    iv_data = load_json(iv_file)
    
    # Merge generated_clause (using ++ separator)
    bl_clause = bl_data.get("generated_clause", "")
    iv_clause = iv_data.get("generated_clause", "")
    merged_clause = f"++ {bl_clause} ++ {iv_clause}"
    
    # Merge GT arrays (add doc field)
    merged_gt = []
    
    # BL GT items
    for item in bl_data.get("GT", []):
        merged_gt.append({
            "doc": "BL",
            "key": item["key"],
            "expected_value": item["expected_value"],
            "operator": item["operator"]
        })
    
    # IV GT items
    for item in iv_data.get("GT", []):
        merged_gt.append({
            "doc": "IV",
            "key": item["key"],
            "expected_value": item["expected_value"],
            "operator": item["operator"]
        })
    
    # Create merged data
    merged_data = {
        "im_path": [bl_data.get("im_path", ""), iv_data.get("im_path", "")],
        "generated_clause": merged_clause,
        "GT": merged_gt
    }
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    print(f"Merged: {os.path.basename(bl_file)} + {os.path.basename(iv_file)} -> {output_path}")
    return merged_data


def extract_file_number(file_name: str) -> str:
    """Extract identifier from filename (e.g., dummy_01_BL.json -> 01, dummy_02_IV.json -> 02)"""
    # Filename format: dummy_XX_BL.json or dummy_XX_IV.json
    parts = file_name.replace(".json", "").split("_")
    # Return second part (number)
    if len(parts) >= 2:
        return parts[1]  # "01", "02", etc.
    return parts[-1] if parts else ""


def get_all_files(bl_dir: str, iv_dir: str) -> tuple:
    """
    Return list of BL and IV files
    """
    bl_files = glob.glob(os.path.join(bl_dir, "*.json"))
    iv_files = glob.glob(os.path.join(iv_dir, "*.json"))
    
    return bl_files, iv_files


def create_random_pairs(bl_files: List[str], iv_files: List[str], seed: int = 42) -> List[tuple]:
    """
    Randomly pair BL and IV files
    """
    random.seed(seed)
    
    # Shuffle IV files randomly
    iv_shuffled = iv_files.copy()
    random.shuffle(iv_shuffled)
    
    # Match to number of BL files (BL is the base)
    pairs = []
    for i, bl_file in enumerate(bl_files):
        iv_idx = i % len(iv_shuffled)
        pairs.append((bl_file, iv_shuffled[iv_idx]))
    
    return pairs


def merge_all_random(bl_dir: str, iv_dir: str, output_dir: str, seed: int = 42):
    """Randomly match and merge BL and IV files"""
    bl_files, iv_files = get_all_files(bl_dir, iv_dir)
    print(f"Found {len(bl_files)} BL files and {len(iv_files)} IV files")
    
    pairs = create_random_pairs(bl_files, iv_files, seed)
    print(f"Created {len(pairs)} random pairs (seed={seed})")
    
    # Clean output directory (remove existing files)
    if os.path.exists(output_dir):
        for f in glob.glob(os.path.join(output_dir, "*.json")):
            os.remove(f)
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    for bl_file, iv_file in pairs:
        bl_num = extract_file_number(os.path.basename(bl_file))
        iv_num = extract_file_number(os.path.basename(iv_file))
        
        # Output filename: BL_XXXXXX_IV_XXXXXX.json
        output_name = f"BL_{bl_num}_IV_{iv_num}.json"
        output_path = os.path.join(output_dir, output_name)
        
        merge_bl_iv(bl_file, iv_file, output_path)
