#!/usr/bin/env python3
"""
BL/IV Clause Generator CLI

Read JSON files from split_extracted_bl directory
Generate JSON files with generated_clause and GT in gen2_BL/ folder

Read JSON files from split_extracted_iv directory
Generate JSON files with generated_clause and GT in gen_iv/ folder
"""

import argparse
import json
import os
import random

from .bl_generator import build_requirement_with_gt
from .iv_generator import generate_iv_with_gt
from .merge_bl_iv import merge_all_random, merge_bl_iv, extract_file_number


def process_bl_files(input_dir: str, output_dir: str) -> None:
    """
    Process BL JSON files from input directory and generate output files
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
    """
    # Create output folder
    os.makedirs(output_dir, exist_ok=True)
    
    # Count processed files
    processed_count = 0
    error_count = 0
    
    # Fixed seed for reproducible synthesis
    # (seeded once; the RNG stream continues across files so each file still differs)
    random.seed(42)

    # Process all JSON files in input folder
    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".json"):
            continue
        
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            # Read original JSON
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract im_path
            im_path = data.get("im_path", "")
            
            bl_data = data.get("full_bl_extraction", {}) or data.get("bl_extraction", {})
            
            # Check if notify_party is "SAME AS CONSIGNEE" in full_bl_extraction
            original_bl = data.get("full_bl_extraction", {}) or data.get("bl_extraction", {})
            bl_data["is_same_as_consignee"] = (original_bl.get("notify_party", "") == "SAME AS CONSIGNEE")
            
            # Add consignee, notify_party to BL data (dict format)
            bl_data["consignee"] = data.get("consignee", {})
            bl_data["notify_party"] = data.get("notify_party", {})
            
            # Generate requirement and GT
            generated_clause, gt = build_requirement_with_gt(bl_data)
            
            # Build output JSON
            output_data = {
                "im_path": im_path,
                "generated_clause": generated_clause,
                "GT": gt
            }
            
            # Save
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processed_count += 1
            print(f"[{processed_count}] {filename} -> {output_path}")
        
        except Exception as e:
            error_count += 1
            print(f"[ERROR] {filename}: {str(e)}")
    
    print(f"\nCompleted: {processed_count} files processed, {error_count} errors")


def process_iv_files(input_dir: str, output_dir: str) -> None:
    """
    Process IV JSON files from input directory and generate output files
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
    """
    # Create output folder
    os.makedirs(output_dir, exist_ok=True)
    
    # Count processed files
    processed_count = 0
    error_count = 0
    
    # Fixed seed for reproducible synthesis
    # (seeded once; the RNG stream continues across files so each file still differs)
    random.seed(42)

    # Process all JSON files in input folder
    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".json"):
            continue
        
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            # Read original JSON
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract im_path
            im_path = data.get("im_path", "")
            
            # Extract IV data (original_iv_extraction or full_iv_extraction)
            original_iv = data.get("original_iv_extraction", {}) or data.get("full_iv_extraction", {})
            
            # exporter, buyer, consignee are retrieved from top level as dict
            iv_data = {
                "exporter": data.get("exporter", {}),
                "buyer": data.get("buyer", {}),
                "consignee": data.get("consignee", {}),
                "invoice_number": original_iv.get("invoice_number", ""),
                "invoice_date": original_iv.get("invoice_date", ""),
                "lc_number": original_iv.get("lc_number", ""),
                "currency": original_iv.get("currency", ""),
                "total_amount": original_iv.get("total_amount", ""),
                "country_of_origin": original_iv.get("country_of_origin", ""),
                "trade_terms": original_iv.get("trade_terms", ""),
                "goods_description": original_iv.get("goods_description", [])
            }
            
            # Generate clause and GT
            generated_clause, gt = generate_iv_with_gt(iv_data)
            
            # Build output JSON
            output_data = {
                "im_path": im_path,
                "generated_clause": generated_clause,
                "GT": gt
            }
            
            # Save
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            processed_count += 1
            print(f"[{processed_count}] {filename} -> {output_path}")
        
        except Exception as e:
            error_count += 1
            print(f"[ERROR] {filename}: {str(e)}")
    
    print(f"\nCompleted: {processed_count} files processed, {error_count} errors")


def cmd_generate(args) -> None:
    """Handle the `generate` subcommand."""
    if args.type == "bl":
        input_dir = args.input_dir or "dataset/BL"
        output_dir = args.output_dir or "dataset/generated/BL"
        process_bl_files(input_dir, output_dir)
    else:  # iv
        input_dir = args.input_dir or "dataset/IV"
        output_dir = args.output_dir or "dataset/generated/IV"
        process_iv_files(input_dir, output_dir)


def cmd_merge(args) -> None:
    """Handle the `merge` subcommand."""
    if args.bl_file and args.iv_file:
        # Merge a single specified BL/IV pair
        output = args.output
        if not output:
            bl_num = extract_file_number(os.path.basename(args.bl_file))
            iv_num = extract_file_number(os.path.basename(args.iv_file))
            output = os.path.join(args.output_dir, f"BL_{bl_num}_IV_{iv_num}.json")
        merge_bl_iv(args.bl_file, args.iv_file, output)
    else:
        # Randomly pair and merge all BL/IV outputs
        merge_all_random(args.bl_dir, args.iv_dir, args.output_dir)


def main():
    """Unified CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="clause_generator",
        description="Clause Generator - synthesize clauses + GT and merge BL/IV outputs",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- generate ----
    gen = subparsers.add_parser(
        "generate",
        help="Generate clauses and GT from BL or IV documents",
    )
    gen.add_argument(
        "--type",
        type=str,
        choices=["bl", "iv"],
        default="bl",
        help="Document type to process (bl: Bill of Lading, iv: Invoice)",
    )
    gen.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Input directory path (default: dataset/BL or dataset/IV)",
    )
    gen.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory path (default: dataset/generated/BL or .../IV)",
    )
    gen.set_defaults(func=cmd_generate)

    # ---- merge ----
    mrg = subparsers.add_parser(
        "merge",
        help="Merge generated BL and IV outputs into paired specifications",
    )
    mrg.add_argument("--bl-dir", default="dataset/generated/BL", help="Generated BL directory")
    mrg.add_argument("--iv-dir", default="dataset/generated/IV", help="Generated IV directory")
    mrg.add_argument("--output-dir", default="dataset/generated/merged", help="Merged output directory")
    mrg.add_argument("--bl-file", default=None, help="Specific BL file to merge")
    mrg.add_argument("--iv-file", default=None, help="Specific IV file to merge")
    mrg.add_argument("--output", default=None, help="Specific output file path (with --bl-file/--iv-file)")
    mrg.set_defaults(func=cmd_merge)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()