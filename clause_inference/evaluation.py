"""
Clause Evaluation Module

This module provides evaluation functionality for clause inference results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


# ============================================================================
# Evaluation Module
# ============================================================================

import re


# Fixed operator order for reporting (matches Table 2 / Table 3 in the paper).
# Any operator not listed here is appended afterwards in alphabetical order.
OPERATOR_ORDER = ["EQUALS", "EXISTS", "CONTAINS", "LTE", "NEGATION", "GTE"]


def _ordered_operators(operator_stats: Dict) -> List[str]:
    """Return operator keys in the paper's order, with any extras appended."""
    known = [op for op in OPERATOR_ORDER if op in operator_stats]
    extras = sorted(op for op in operator_stats if op not in OPERATOR_ORDER)
    return known + extras


def normalize_value(value) -> str:
    """Normalize values for comparison
    
    - Normalize numeric expressions: "ONE (1)" -> "1", "TWO (2)" -> "2"
    - Convert strings to lowercase
    - Convert null/true to strings
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value).strip().lower()
    
    str_value = str(value).strip().lower()
    
    # Normalize numeric expressions: "ONE (1)", "TWO (2)" etc. -> extract number in parentheses
    # e.g., "ONE (1)" -> "1", "THREE (3)" -> "3"
    match = re.match(r'^[a-z]+\s*\((\d+)\)$', str_value, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return str_value


def to_bool(value):
    """Convert string to boolean"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def compare_values(inf_value, gt_value, operator: str, key: str = None) -> bool:
    """Compare Inference value with GT value
    
    Args:
        inf_value: Inferred value
        gt_value: GT value
        operator: Comparison operator (EXISTS, EQUALS, CONTAINS, LTE, GTE, NEGATION)
        key: Field key (optional, for special field handling)
    """
    # exist_on_board_date: EXISTS operator - check only value existence
    if key == "exist_on_board_date" and operator == "EXISTS":
        # If gt_value is True, return True if inf_value is not null (date exists)
        if gt_value is True:
            return inf_value is not None and inf_value is not False
        return inf_value == gt_value
    
    # on_board_date: LTE operator - exact value recovery (parsability), not constraint check
    if key == "on_board_date" and operator == "LTE":
        if inf_value is None or gt_value is None:
            return False
        # Date string comparison (YYYY-MM-DD format)
        try:
            from datetime import datetime
            inf_date = datetime.strptime(str(inf_value), "%Y-%m-%d")
            gt_date = datetime.strptime(str(gt_value), "%Y-%m-%d")
            return inf_date == gt_date
        except (ValueError, TypeError):
            return str(inf_value).strip().lower() == str(gt_value).strip().lower()
    
    # General handling
    # Convert null vs "null", true vs "true" to strings for matching
    inf_str = normalize_value(inf_value)
    gt_str = normalize_value(gt_value)
    
    if operator == "EQUALS":
        return inf_str == gt_str
    elif operator == "CONTAINS":
        return gt_str in inf_str
    elif operator == "NEGATION":
        return inf_value is None and gt_value is None
    elif operator == "GTE":
        try:
            return float(inf_value) >= float(gt_value)
        except (ValueError, TypeError):
            return inf_str == gt_str
    elif operator == "LTE":
        # Exact value recovery (parsability), not an upper-bound constraint check.
        if inf_value is True:
            return True
        if isinstance(gt_value, str) and isinstance(inf_value, str):
            # Date string comparison (assuming YYYY-MM-DD format)
            try:
                from datetime import datetime
                inf_date = datetime.strptime(str(inf_value), "%Y-%m-%d")
                gt_date = datetime.strptime(str(gt_value), "%Y-%m-%d")
                return inf_date == gt_date
            except (ValueError, TypeError):
                return inf_str == gt_str
        return inf_str == gt_str
    else:
        return inf_str == gt_str


def evaluate_single_result(result_entry: Dict) -> Dict:
    """Evaluate single file result"""
    gt_list = result_entry.get("GT", [])
    inf_list = result_entry.get("inference_result", [])
    
    # Return basic evaluation if error exists
    if result_entry.get("error"):
        return {
            "file_path": result_entry.get("file_path", ""),
            "im_path": result_entry.get("im_path", ""),
            "generated_clause": result_entry.get("generated_clause", ""),
            "metrics": {"total_gt": len(gt_list), "matched": 0, "mismatched": 0, "missing": len(gt_list), "extra": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0},
            "matches": [],
            "mismatches": [],
            "missing": [{"key": item["key"], "expected_value": item["expected_value"], "operator": item["operator"]} for item in gt_list],
            "extra": [],
            "error": result_entry.get("error")
        }
    
    if not isinstance(inf_list, list):
        return {
            "file_path": result_entry.get("file_path", ""),
            "im_path": result_entry.get("im_path", ""),
            "generated_clause": result_entry.get("generated_clause", ""),
            "metrics": {"total_gt": len(gt_list), "matched": 0, "mismatched": 0, "missing": len(gt_list), "extra": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0},
            "matches": [],
            "mismatches": [],
            "missing": [{"key": item["key"], "expected_value": item["expected_value"], "operator": item["operator"]} for item in gt_list],
            "extra": [],
            "error": "Invalid inference_result format"
        }
    
    gt_by_key = {item["key"]: item for item in gt_list}
    inf_by_key = {item["key"]: item for item in inf_list}
    
    evaluation = {
        "file_path": result_entry.get("file_path", ""),
        "im_path": result_entry.get("im_path", ""),
        "generated_clause": result_entry.get("generated_clause", ""),
        "metrics": {},
        "matches": [],
        "mismatches": [],
        "missing": [],
        "extra": [],
    }
    
    for key, gt_item in gt_by_key.items():
        if key not in inf_by_key:
            evaluation["missing"].append({
                "key": key,
                "expected_value": gt_item["expected_value"],
                "operator": gt_item["operator"]
            })
        else:
            inf_item = inf_by_key[key]
            
            # Value comparison (using GT operator)
            value_match = compare_values(
                inf_item["expected_value"],
                gt_item["expected_value"],
                gt_item["operator"],
                key
            )
            
            # Operator comparison (check if LLM extracted operator matches GT)
            operator_match = (inf_item["operator"] == gt_item["operator"])
            
            # Both value and operator must match for Match
            if value_match and operator_match:
                evaluation["matches"].append({
                    "key": key,
                    "gt_value": gt_item["expected_value"],
                    "inf_value": inf_item["expected_value"],
                    "gt_operator": gt_item["operator"],
                    "inf_operator": inf_item["operator"]
                })
            else:
                evaluation["mismatches"].append({
                    "key": key,
                    "gt_value": gt_item["expected_value"],
                    "inf_value": inf_item["expected_value"],
                    "gt_operator": gt_item["operator"],
                    "inf_operator": inf_item["operator"],
                    "value_match": value_match,
                    "operator_match": operator_match
                })
    
    for key in inf_by_key:
        if key not in gt_by_key:
            evaluation["extra"].append({
                "key": key,
                "inf_value": inf_by_key[key]["expected_value"],
                "operator": inf_by_key[key]["operator"]
            })
    
    total_gt = len(gt_list)
    matched = len(evaluation["matches"])
    
    evaluation["metrics"] = {
        "total_gt": total_gt,
        "matched": matched,
        "mismatched": len(evaluation["mismatches"]),
        "missing": len(evaluation["missing"]),
        "extra": len(evaluation["extra"]),
        "precision": matched / len(inf_list) if inf_list else 0.0,
        "recall": matched / total_gt if total_gt > 0 else 0.0,
        "key_anchored_recall": matched / (matched + len(evaluation["missing"])) if (matched + len(evaluation["missing"])) > 0 else 0.0,
    }
    evaluation["metrics"]["f1"] = (
        2 * evaluation["metrics"]["precision"] * evaluation["metrics"]["recall"] /
        (evaluation["metrics"]["precision"] + evaluation["metrics"]["recall"])
        if (evaluation["metrics"]["precision"] + evaluation["metrics"]["recall"]) > 0 
        else 0.0
    )
    evaluation["metrics"]["key_anchored_f1"] = (
        2 * evaluation["metrics"]["precision"] * evaluation["metrics"]["key_anchored_recall"] /
        (evaluation["metrics"]["precision"] + evaluation["metrics"]["key_anchored_recall"])
        if (evaluation["metrics"]["precision"] + evaluation["metrics"]["key_anchored_recall"]) > 0
        else 0.0
    )
    return evaluation


def evaluate_all_results(results: List[Dict]) -> Dict:
    """Evaluate all results and aggregate"""
    evaluations = []
    
    for result_entry in results:
        eval_result = evaluate_single_result(result_entry)
        evaluations.append(eval_result)
    
    total_metrics = {
        "total_files": len(evaluations),
        "total_gt_fields": sum(e["metrics"].get("total_gt", 0) for e in evaluations),
        "total_matched": sum(e["metrics"].get("matched", 0) for e in evaluations),
        "total_mismatched": sum(e["metrics"].get("mismatched", 0) for e in evaluations),
        "total_missing": sum(e["metrics"].get("missing", 0) for e in evaluations),
        "total_extra": sum(e["metrics"].get("extra", 0) for e in evaluations),
    }
    
    # Set default values if no GT fields or no inference results
    if total_metrics["total_gt_fields"] > 0:
        total_matched_plus_mismatched_plus_extra = (
            total_metrics["total_matched"] + total_metrics["total_mismatched"] + total_metrics["total_extra"]
        )
        total_metrics["overall_precision"] = total_metrics["total_matched"] / total_matched_plus_mismatched_plus_extra if total_matched_plus_mismatched_plus_extra > 0 else 0.0
        total_metrics["overall_recall"] = total_metrics["total_matched"] / total_metrics["total_gt_fields"]
        if (total_metrics["overall_precision"] + total_metrics["overall_recall"]) > 0:
            total_metrics["overall_f1"] = (
                2 * total_metrics["overall_precision"] * total_metrics["overall_recall"] /
                (total_metrics["overall_precision"] + total_metrics["overall_recall"])
            )
        else:
            total_metrics["overall_f1"] = 0.0
        total_matched_plus_missing = total_metrics['total_matched'] + total_metrics['total_missing']
        total_metrics["overall_key_anchored_recall"] = (total_metrics["total_matched"] / total_matched_plus_missing if total_matched_plus_missing > 0 else 0.0)
        if (total_metrics["overall_precision"] + total_metrics["overall_key_anchored_recall"]) > 0:
            total_metrics["overall_key_anchored_f1"] = (
                2 * total_metrics["overall_precision"] * total_metrics["overall_key_anchored_recall"] /
                (total_metrics["overall_precision"] + total_metrics["overall_key_anchored_recall"])
            )
        else:
            total_metrics["overall_key_anchored_f1"] = 0.0
    else:
        # No GT (inference failure, etc.)
        total_metrics["overall_precision"] = 0.0
        total_metrics["overall_recall"] = 0.0
        total_metrics["overall_f1"] = 0.0
        total_metrics["overall_key_anchored_recall"] = 0.0
        total_metrics["overall_key_anchored_f1"] = 0.0
    
    key_stats = defaultdict(lambda: {"matched": 0, "mismatched": 0, "missing": 0, "extra": 0})
    for e in evaluations:
        for item in e["matches"]:
            key_stats[item["key"]]["matched"] += 1
        for item in e["mismatches"]:
            key_stats[item["key"]]["mismatched"] += 1
        for item in e["missing"]:
            key_stats[item["key"]]["missing"] += 1
        for item in e["extra"]:
            key_stats[item["key"]]["extra"] += 1
    

    op_stats = defaultdict(lambda: {"matched": 0, "mismatched": 0, "missing": 0, "extra": 0})
    for e in evaluations:
        for m in e["matches"]:
            op_stats[m["gt_operator"]]["matched"] += 1
        for m in e["mismatches"]:
            op_stats[m["gt_operator"]]["mismatched"] += 1      
        for m in e["missing"]:
            op_stats[m["operator"]]["missing"] += 1             
        for m in e["extra"]:
            op_stats[m["operator"]]["extra"] += 1             

   
    operator_metrics = {}
    for op, s in op_stats.items():
        tp, mm, ms, ex = s["matched"], s["mismatched"], s["missing"], s["extra"]
        prec = tp / (tp + mm + ex) if (tp + mm + ex) else 0.0
        rec_ka = tp / (tp + ms) if (tp + ms) else 0.0            # key-anchored
        rec_ex = tp / (tp + mm + ms) if (tp + mm + ms) else 0.0  # exact
        f1_ka = 2*prec*rec_ka/(prec+rec_ka) if (prec+rec_ka) else 0.0
        f1_ex = 2*prec*rec_ex/(prec+rec_ex) if (prec+rec_ex) else 0.0
        operator_metrics[op] = {**s, "precision": prec,
                                "recall_ka": rec_ka, "recall_exact": rec_ex,
                                "f1_ka": f1_ka, "f1_exact": f1_ex}

    return {
        "evaluations": evaluations,
        "total_metrics": total_metrics,
        "key_statistics": dict(key_stats),
        "operator_statistics": operator_metrics
    }


# ============================================================================
# Report Output
# ============================================================================

def print_summary(report: Dict):
    """Print summary report"""
    total = report["total_metrics"]
    
    print("\n" + "=" * 60)
    print("CLAUSE INFERENCE & EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📊 Overall Metrics")
    print(f"  Total Files: {total['total_files']}")
    print(f"  Total GT Fields: {total['total_gt_fields']}")
    print(f"  Matched: {total['total_matched']}")
    print(f"  Mismatched: {total['total_mismatched']}")
    print(f"  Missing: {total['total_missing']}")
    print(f"  Extra: {total['total_extra']}")
    
    print(f"\n📈 Performance")
    print(f"  Precision: {total['overall_precision']:.2%}")
    print(f"  Recall (exact): {total['overall_recall']:.2%}")
    print(f"  Recall (key-anchored): {total['overall_key_anchored_recall']:.2%}")
    print(f"  F1 (exact): {total['overall_f1']:.2%}")
    print(f"  F1 (key-anchored): {total['overall_key_anchored_f1']:.2%}")

    # Operator-wise statistics (Table 3 form)
    op_stats = report.get("operator_statistics", {})
    if op_stats:
        print(f"\n📐 Operator-wise Statistics")
        print(f"{'Operator':<10}{'Match':>8}{'Mismatch':>10}{'Missing':>9}{'Extra':>7}"
              f"{'Prec':>8}{'R_KA':>8}{'F1_KA':>8}{'F1_ex':>8}")
        print("-" * 76)
        for op in _ordered_operators(op_stats):
            s = op_stats[op]
            print(f"{op:<10}{s['matched']:>8}{s['mismatched']:>10}{s['missing']:>9}{s['extra']:>7}"
                  f"{s['precision']:>8.3f}{s['recall_ka']:>8.3f}{s['f1_ka']:>8.3f}{s['f1_exact']:>8.3f}")

    print(f"\n📋 Key-wise Statistics")
    print(f"{'Key':<25} {'Match':>8} {'Mismatch':>10} {'Missing':>9} {'Extra':>7}")
    print("-" * 60)
    
    for key, stats in sorted(report["key_statistics"].items()):
        print(f"{key:<25} {stats['matched']:>8} {stats['mismatched']:>10} {stats['missing']:>9} {stats['extra']:>7}")


def print_verbose_report(report: Dict):
    """Print detailed report"""
    print_summary(report)
    
    print(f"\n📝 Detailed Results")
    print("-" * 60)
    for e in report["evaluations"]:
        print(f"\nFile: {e['file_path']}")
        print(f"  Image Path: {e['im_path']}")
        print(f"  Generated Clause: {e['generated_clause']}")
        print(f"  Metrics: P={e['metrics'].get('precision', 0):.2%}, R={e['metrics'].get('recall', 0):.2%}, F1={e['metrics'].get('f1', 0):.2%}")
        
        if e["matches"]:
            print(f"  ✅ Matches ({len(e['matches'])}):")
            for m in e["matches"]:
                print(f"    - {m['key']}: {m['gt_value']}")
        
        if e["mismatches"]:
            print(f"  ❌ Mismatches ({len(e['mismatches'])}):")
            for m in e["mismatches"]:
                print(f"    - {m['key']}: GT={m['gt_value']}, Inf={m['inf_value']}")
        
        if e["missing"]:
            print(f"  ⚠️  Missing ({len(e['missing'])}):")
            for m in e["missing"]:
                print(f"    - {m['key']}: {m['expected_value']}")
        
        if e["extra"]:
            print(f"  ➕ Extra ({len(e['extra'])}):")
            for m in e["extra"]:
                print(f"    - {m['key']}: {m['inf_value']}")


def save_summary(report: Dict, output_dir: str):
    """Save summary report to files"""
    # JSON report
    json_path = os.path.join(output_dir, "evaluation_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Text summary
    txt_path = os.path.join(output_dir, "summary.txt")
    total = report["total_metrics"]
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("CLAUSE INFERENCE & EVALUATION SUMMARY\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("📊 Overall Metrics\n")
        f.write(f"  Total Files: {total.get('total_files', 0)}\n")
        f.write(f"  Total GT Fields: {total.get('total_gt_fields', 0)}\n")
        f.write(f"  Matched: {total.get('total_matched', 0)}\n")
        f.write(f"  Mismatched: {total.get('total_mismatched', 0)}\n")
        f.write(f"  Missing: {total.get('total_missing', 0)}\n")
        f.write(f"  Extra: {total.get('total_extra', 0)}\n\n")
        
        f.write("📈 Performance\n")
        f.write(f"  Precision: {total.get('overall_precision', 0.0):.2%}\n")
        f.write(f"  Recall (exact): {total.get('overall_recall', 0.0):.2%}\n")
        f.write(f"  Recall (key-anchored): {total.get('overall_key_anchored_recall', 0.0):.2%}\n")
        f.write(f"  F1 (exact): {total.get('overall_f1', 0.0):.2%}\n")
        f.write(f"  F1 (key-anchored): {total.get('overall_key_anchored_f1', 0.0):.2%}\n\n")

        # Operator-wise statistics (Table 3 form)
        op_stats = report.get("operator_statistics", {})
        if op_stats:
            f.write("📐 Operator-wise Statistics\n")
            f.write(f"{'Operator':<10}{'Match':>8}{'Mismatch':>10}{'Missing':>9}{'Extra':>7}"
                    f"{'Prec':>8}{'R_KA':>8}{'F1_KA':>8}{'F1_ex':>8}\n")
            f.write("-" * 76 + "\n")
            for op in _ordered_operators(op_stats):
                s = op_stats[op]
                f.write(f"{op:<10}{s['matched']:>8}{s['mismatched']:>10}{s['missing']:>9}{s['extra']:>7}"
                        f"{s['precision']:>8.3f}{s['recall_ka']:>8.3f}{s['f1_ka']:>8.3f}{s['f1_exact']:>8.3f}\n")
            f.write("\n")

        f.write("📋 Key-wise Statistics\n")
        f.write(f"{'Key':<25} {'Match':>8} {'Mismatch':>10} {'Missing':>9} {'Extra':>7}\n")
        f.write("-" * 60 + "\n")
        
        for key, stats in sorted(report["key_statistics"].items()):
            f.write(f"{key:<25} {stats['matched']:>8} {stats['mismatched']:>10} {stats['missing']:>9} {stats['extra']:>7}\n")
    
    return json_path, txt_path


def run_evaluation(results: List[Dict], output_dir: str, verbose: bool = False) -> Dict:
    """Run evaluation and save reports"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Perform evaluation
    print("Evaluating...")
    report = evaluate_all_results(results)
    
    # Save reports
    json_path, txt_path = save_summary(report, output_dir)
    print(f"Evaluation report saved to: {json_path}")
    print(f"Summary saved to: {txt_path}")
    
    # Print report
    if verbose:
        print_verbose_report(report)
    else:
        print_summary(report)
    
    return report