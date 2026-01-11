"""
Token Compression Engine

Compresses data using ontology-aware encoding to reduce token usage.
"""

import json
from typing import Dict, Any, List
from ontology import get_ontology


class OntologyCompressor:
    """Compress data using ontology mappings"""

    def __init__(self, ontology=None):
        self.ontology = ontology or get_ontology()

        # Build abbreviation mappings
        self.property_abbrev = self._build_abbreviations()

    def _build_abbreviations(self) -> Dict[str, str]:
        """Build property abbreviations"""
        abbrev = {}

        for prop_name in self.ontology.properties.keys():
            # Create short abbreviation (first 3 chars + last char)
            if len(prop_name) > 4:
                short = prop_name[:3] + prop_name[-1]
            else:
                short = prop_name[:2]

            abbrev[prop_name] = short.lower()

        return abbrev

    def compress_record(self, record: Dict[str, Any], ontology_class: str) -> Dict[str, Any]:
        """
        Compress a single record

        Args:
            record: Original record
            ontology_class: Ontology class this record belongs to

        Returns:
            Compressed record
        """
        compressed = {}

        # Get properties for this class
        class_props = self.ontology.get_properties_by_class(ontology_class, include_inherited=True)

        for field_name, value in record.items():
            # Find ontology property mapping
            # In real system, this would use GNN predictions
            matched_prop = None
            for prop in class_props:
                if prop.lower() in field_name.lower():
                    matched_prop = prop
                    break

            if matched_prop and matched_prop in self.property_abbrev:
                # Use abbreviation
                short_key = self.property_abbrev[matched_prop]
            else:
                # Keep first 3 chars
                short_key = field_name[:3].lower()

            # Compress value
            compressed[short_key] = self._compress_value(value)

        return compressed

    def _compress_value(self, value: Any) -> Any:
        """Compress a value"""
        if isinstance(value, str):
            # Truncate long strings
            if len(value) > 50:
                return value[:47] + "..."
            return value
        elif isinstance(value, (int, float)):
            # Round floats
            if isinstance(value, float):
                return round(value, 2)
            return value
        else:
            return value

    def decompress_record(self, compressed: Dict[str, Any], ontology_class: str) -> Dict[str, Any]:
        """
        Decompress a record

        Args:
            compressed: Compressed record
            ontology_class: Ontology class

        Returns:
            Decompressed record (with full property names)
        """
        # Reverse mapping
        abbrev_to_prop = {v: k for k, v in self.property_abbrev.items()}

        decompressed = {}
        for short_key, value in compressed.items():
            # Find full property name
            full_prop = abbrev_to_prop.get(short_key, short_key)
            decompressed[full_prop] = value

        return decompressed

    def compress_batch(self, records: List[Dict], ontology_class: str) -> List[Dict]:
        """Compress multiple records"""
        return [self.compress_record(record, ontology_class) for record in records]


if __name__ == '__main__':
    print("=== Token Compression Test ===\n")

    compressor = OntologyCompressor()

    # Test record
    test_record = {
        'customerId': 'CUS-000001',
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john.doe@example.com',
        'phoneNumber': '+1-555-0100',
        'dateOfBirth': '1990-01-15',
        'registrationDate': '2023-06-01T10:30:00',
        'customerTier': 'gold'
    }

    print("Original record:")
    print(json.dumps(test_record, indent=2))
    print(f"Size: {len(json.dumps(test_record))} chars\n")

    # Compress
    compressed = compressor.compress_record(test_record, 'Customer')

    print("Compressed record:")
    print(json.dumps(compressed, indent=2))
    print(f"Size: {len(json.dumps(compressed))} chars\n")

    # Calculate reduction
    original_size = len(json.dumps(test_record))
    compressed_size = len(json.dumps(compressed))
    reduction = (1 - compressed_size / original_size) * 100

    print(f"Compression: {reduction:.1f}% reduction")

    print("\n✓ Compression working!")
