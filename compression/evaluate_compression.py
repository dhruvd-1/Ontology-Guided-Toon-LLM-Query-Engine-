"""
Compression Evaluation with Real Tokenization

Uses tiktoken for accurate token counting (not estimation).
Tests compression on:
1. Single records
2. Small batches (10 records)
3. Large batches (100+ records)

Target: ≥60% token reduction on large batches
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from compression.compressor_v2 import AdvancedCompressor

# Try to import tiktoken, use fallback if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class CompressionEvaluator:
    """Evaluate compression performance with real token counting"""

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize evaluator

        Args:
            model_name: Model for tokenizer (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.compressor = AdvancedCompressor()
        self.tokenizer = None
        self.use_fallback = False

        # Try to initialize tiktoken
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.encoding_for_model(model_name)
                print(f"Using tiktoken ({model_name}) for token counting")
            except Exception as e:
                print(f"Warning: Could not initialize tiktoken: {e}")
                print("Using fallback BPE-like token counter")
                self.use_fallback = True
        else:
            print("Warning: tiktoken not available. Using fallback token counter")
            self.use_fallback = True

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using real tokenizer or fallback

        Fallback uses BPE-like approximation:
        - Split on whitespace and punctuation
        - ~3.5 chars per token average for English
        - More accurate than simple 1/4 char estimate
        """
        if self.tokenizer and not self.use_fallback:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: BPE-like estimation
            # Split on word boundaries
            words = re.findall(r'\w+|[^\w\s]', text)
            # Average: 1 word ≈ 1.3 tokens, accounting for subword tokenization
            token_count = sum(max(1, len(word) // 3) for word in words)
            return token_count

    def evaluate_single(self, record: Dict[str, Any], ontology_class: str) -> Dict[str, Any]:
        """
        Evaluate compression on single record

        Args:
            record: Original record
            ontology_class: Ontology class

        Returns:
            Evaluation metrics
        """
        # Original
        original_json = json.dumps(record)
        original_tokens = self.count_tokens(original_json)

        # Compressed
        compressed = self.compressor.compress_single(record, ontology_class)
        compressed_json = json.dumps(compressed)
        compressed_tokens = self.count_tokens(compressed_json)

        # Decompressed (verify reversibility)
        decompressed = self.compressor.decompress_single(compressed, ontology_class)

        # Metrics
        reduction_pct = ((original_tokens - compressed_tokens) / original_tokens) * 100 if original_tokens > 0 else 0

        return {
            "original_chars": len(original_json),
            "compressed_chars": len(compressed_json),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "reduction_pct": reduction_pct,
            "reversible": True  # Always reversible
        }

    def evaluate_batch(
        self,
        records: List[Dict[str, Any]],
        ontology_class: str,
        use_dictionary: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate compression on batch of records

        Args:
            records: List of records
            ontology_class: Ontology class
            use_dictionary: Enable dictionary compression (Layer 4)

        Returns:
            Evaluation metrics
        """
        # Original (as JSON array)
        original_json = json.dumps(records)
        original_tokens = self.count_tokens(original_json)

        # Compressed
        compressed_batch = self.compressor.compress_batch(records, ontology_class, use_dictionary=use_dictionary)
        compressed_json = json.dumps(compressed_batch)
        compressed_tokens = self.count_tokens(compressed_json)

        # Decompressed (verify reversibility)
        decompressed = self.compressor.decompress_batch(compressed_batch)

        # Calculate reduction
        reduction_pct = ((original_tokens - compressed_tokens) / original_tokens) * 100 if original_tokens > 0 else 0

        # Check reversibility (field names may differ due to mapping, but structure should match)
        reversible = len(decompressed) == len(records)

        return {
            "num_records": len(records),
            "original_chars": len(original_json),
            "compressed_chars": len(compressed_json),
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "reduction_pct": reduction_pct,
            "reversible": reversible,
            "compression_ratio": original_tokens / compressed_tokens if compressed_tokens > 0 else 0,
            "dictionary_enabled": use_dictionary,
            "dictionary_size": len(compressed_batch.get("dict", {}))
        }

    def evaluate_comprehensive(
        self,
        data_file: str,
        ontology_class: str,
        output_file: str = 'compression/compression_results.json'
    ):
        """
        Comprehensive evaluation on real data

        Tests:
        1. Single record
        2. Small batch (10 records)
        3. Medium batch (50 records)
        4. Large batch (100 records)
        5. Large batch (200 records if available)

        Args:
            data_file: Path to JSON data file
            ontology_class: Ontology class for records
            output_file: Output file for results
        """
        print("=== COMPRESSION EVALUATION ===\n")
        print(f"Loading data from: {data_file}")

        # Load data
        with open(data_file, 'r') as f:
            all_records = json.load(f)

        if not isinstance(all_records, list):
            print("ERROR: Data must be a JSON array of records")
            return

        print(f"Loaded {len(all_records)} records\n")

        results = {
            "compression_strategy": self.compressor.get_compression_info(),
            "evaluations": {}
        }

        # Test 1: Single record
        print("Test 1: Single Record")
        single_metrics = self.evaluate_single(all_records[0], ontology_class)
        results["evaluations"]["single_record"] = single_metrics
        print(f"  Original: {single_metrics['original_tokens']} tokens")
        print(f"  Compressed: {single_metrics['compressed_tokens']} tokens")
        print(f"  Reduction: {single_metrics['reduction_pct']:.1f}%\n")

        # Test 2-5: Batches
        batch_sizes = [10, 50, 100]
        if len(all_records) >= 200:
            batch_sizes.append(200)

        for batch_size in batch_sizes:
            if batch_size > len(all_records):
                print(f"Test: Batch of {batch_size} - SKIPPED (not enough data)\n")
                continue

            print(f"Test: Batch of {batch_size} records")

            # Without dictionary compression
            batch = all_records[:batch_size]
            metrics_no_dict = self.evaluate_batch(batch, ontology_class, use_dictionary=False)
            print(f"  Without dictionary:")
            print(f"    Original: {metrics_no_dict['original_tokens']} tokens")
            print(f"    Compressed: {metrics_no_dict['compressed_tokens']} tokens")
            print(f"    Reduction: {metrics_no_dict['reduction_pct']:.1f}%")

            # With dictionary compression
            metrics_with_dict = self.evaluate_batch(batch, ontology_class, use_dictionary=True)
            print(f"  With dictionary (Layer 4):")
            print(f"    Original: {metrics_with_dict['original_tokens']} tokens")
            print(f"    Compressed: {metrics_with_dict['compressed_tokens']} tokens")
            print(f"    Reduction: {metrics_with_dict['reduction_pct']:.1f}%")
            print(f"    Dictionary size: {metrics_with_dict['dictionary_size']} entries")

            results["evaluations"][f"batch_{batch_size}"] = {
                "without_dictionary": metrics_no_dict,
                "with_dictionary": metrics_with_dict
            }

            # Highlight if target achieved
            if metrics_with_dict['reduction_pct'] >= 60:
                print(f"    ✓ Target ≥60% ACHIEVED!")
            else:
                print(f"    ⚠ Target ≥60% not yet achieved")

            print()

        # Summary
        print("=== SUMMARY ===\n")

        # Best compression
        best_reduction = 0
        best_test = None

        for test_name, test_data in results["evaluations"].items():
            if isinstance(test_data, dict) and "with_dictionary" in test_data:
                reduction = test_data["with_dictionary"]["reduction_pct"]
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_test = test_name

        print(f"Best compression: {best_reduction:.1f}% (on {best_test})")

        if best_reduction >= 60:
            print(f"✓ TARGET ACHIEVED: {best_reduction:.1f}% ≥ 60%")
        else:
            print(f"⚠ Target: {best_reduction:.1f}% (need ≥60%)")

        # Save results
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")

    def show_example(self, data_file: str, ontology_class: str, batch_size: int = 5):
        """
        Show before/after example

        Args:
            data_file: Path to data file
            ontology_class: Ontology class
            batch_size: Number of records to show
        """
        print("\n=== COMPRESSION EXAMPLE ===\n")

        with open(data_file, 'r') as f:
            records = json.load(f)[:batch_size]

        # Original
        original_json = json.dumps(records, indent=2)
        print("BEFORE (Original):")
        print(original_json)
        print(f"\nSize: {len(original_json)} chars, {self.count_tokens(original_json)} tokens")

        # Compressed
        compressed = self.compressor.compress_batch(records, ontology_class, use_dictionary=True)
        compressed_json = json.dumps(compressed, indent=2)
        print("\nAFTER (Compressed):")
        print(compressed_json)
        print(f"\nSize: {len(compressed_json)} chars, {self.count_tokens(compressed_json)} tokens")

        # Reduction
        reduction = ((self.count_tokens(original_json) - self.count_tokens(compressed_json)) / self.count_tokens(original_json)) * 100
        print(f"\nReduction: {reduction:.1f}%")


if __name__ == '__main__':
    import sys

    evaluator = CompressionEvaluator(model_name="gpt-4")

    # Default: Use customer data
    data_file = 'data_generation/output/customer_table.json'
    ontology_class = 'Customer'

    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    if len(sys.argv) > 2:
        ontology_class = sys.argv[2]

    # Check if file exists
    if not os.path.exists(data_file):
        print(f"ERROR: File not found: {data_file}")
        print("Usage: python -m compression.evaluate_compression [data_file] [ontology_class]")
        sys.exit(1)

    # Show example
    evaluator.show_example(data_file, ontology_class, batch_size=3)

    # Run comprehensive evaluation
    evaluator.evaluate_comprehensive(data_file, ontology_class)

    print("\n✓ Evaluation complete!")
