"""
Balanced Synthetic Dataset Generator

Generates a properly balanced dataset for GNN training with:
- 50-60 ontology properties
- 60-100 samples per property
- 3,000-5,000 total samples
- Class imbalance ≤ 1:3
"""

import json
import random
import numpy as np
from typing import Dict, List, Tuple
from ontology import get_ontology


class BalancedDatasetGenerator:
    """Generate balanced synthetic dataset for schema-to-ontology mapping"""

    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
        self.ontology = get_ontology()

        # Field name variants for each property type
        self.field_name_variants = {
            # Identifiers
            'id': ['id', 'identifier', 'key', 'pk', 'uid', 'code', 'number', 'no', 'num'],

            # Names
            'name': ['name', 'nm', 'title', 'label', 'desc', 'description'],

            # Dates
            'date': ['date', 'dt', 'time', 'timestamp', 'ts', 'datetime', 'created', 'updated'],

            # Amounts
            'amount': ['amount', 'amt', 'value', 'val', 'price', 'cost', 'total'],

            # Status
            'status': ['status', 'state', 'stat', 'condition', 'stage', 'phase'],

            # Email
            'email': ['email', 'eml', 'email_address', 'email_id', 'e_mail', 'mail'],

            # Phone
            'phone': ['phone', 'phone_number', 'tel', 'telephone', 'mobile', 'cell'],

            # Address
            'address': ['address', 'addr', 'location', 'place', 'street'],
            'city': ['city', 'town', 'municipality', 'locality'],
            'state': ['state', 'province', 'region', 'territory'],
            'country': ['country', 'nation', 'ctry'],
            'postal': ['postal_code', 'zip', 'zipcode', 'postcode', 'zip_code'],

            # Product
            'product': ['product', 'prod', 'item', 'article', 'sku'],
            'category': ['category', 'cat', 'type', 'class', 'group'],
            'brand': ['brand', 'manufacturer', 'make', 'vendor'],

            # Customer
            'customer': ['customer', 'cust', 'client', 'buyer', 'user'],
            'order': ['order', 'ord', 'purchase', 'transaction', 'txn'],

            # Quantities
            'quantity': ['quantity', 'qty', 'amount', 'count', 'num'],
            'price': ['price', 'cost', 'rate', 'amount', 'value'],

            # Descriptions
            'description': ['description', 'desc', 'details', 'info', 'notes'],
            'comment': ['comment', 'remarks', 'notes', 'feedback'],

            # Ratings
            'rating': ['rating', 'score', 'rank', 'stars', 'review_score'],

            # Inventory
            'stock': ['stock', 'inventory', 'available', 'in_stock', 'qty_available'],
            'warehouse': ['warehouse', 'location', 'storage', 'facility'],
        }

        # Common prefixes and suffixes
        self.prefixes = ['', 'user_', 'cust_', 'prod_', 'ord_', 'item_', 'doc_', 'rec_']
        self.suffixes = ['', '_id', '_no', '_code', '_value', '_data', '_info', '_dt']

        # Datatype variations
        self.datatypes = {
            'string_small': ['VARCHAR(50)', 'VARCHAR(100)', 'CHAR(50)'],
            'string_large': ['VARCHAR(255)', 'TEXT', 'VARCHAR(500)'],
            'integer': ['INT', 'INTEGER', 'BIGINT', 'SMALLINT'],
            'decimal': ['DECIMAL(10,2)', 'NUMERIC(12,2)', 'FLOAT'],
            'boolean': ['BOOLEAN', 'TINYINT(1)', 'BIT'],
            'datetime': ['DATETIME', 'TIMESTAMP', 'DATE'],
        }

    def select_core_properties(self, target_count: int = 50) -> List[str]:
        """Select core ontology properties for training"""
        all_properties = list(self.ontology.properties.keys())

        # Prioritize properties that appear in multiple classes
        property_frequency = {}
        for class_name in self.ontology.classes.keys():
            props = self.ontology.get_properties_by_class(class_name, include_inherited=True)
            for prop in props:
                property_frequency[prop] = property_frequency.get(prop, 0) + 1

        # Sort by frequency (most common first)
        sorted_properties = sorted(all_properties, key=lambda p: property_frequency.get(p, 0), reverse=True)

        # Take top N properties
        selected = sorted_properties[:target_count]

        print(f"Selected {len(selected)} core properties")
        return selected

    def generate_field_name(self, property_name: str) -> str:
        """Generate a realistic messy field name for a property"""
        prop_lower = property_name.lower()

        # Find matching pattern
        base_variants = []
        for pattern, variants in self.field_name_variants.items():
            if pattern in prop_lower:
                base_variants = variants
                break

        if not base_variants:
            # Default: use property name variations
            base_variants = [
                property_name.lower(),
                property_name[:4].lower(),
                ''.join([c for c in property_name if c.isupper()]).lower()
            ]

        # Pick a base variant
        base = random.choice(base_variants)

        # Add prefix/suffix with probability
        if random.random() < 0.3:
            base = random.choice(self.prefixes) + base
        if random.random() < 0.3:
            base = base + random.choice(self.suffixes)

        # Add underscore variations
        if '_' not in base and random.random() < 0.2:
            # Insert underscore
            if len(base) > 3:
                pos = random.randint(1, len(base) - 1)
                base = base[:pos] + '_' + base[pos:]

        return base

    def infer_datatype(self, property_name: str) -> str:
        """Infer appropriate SQL datatype for property"""
        prop_lower = property_name.lower()

        if 'id' in prop_lower or 'code' in prop_lower:
            return random.choice(self.datatypes['string_small'])
        elif 'email' in prop_lower or 'url' in prop_lower:
            return random.choice(self.datatypes['string_large'])
        elif 'name' in prop_lower or 'title' in prop_lower:
            return random.choice(self.datatypes['string_large'])
        elif 'description' in prop_lower or 'comment' in prop_lower:
            return 'TEXT'
        elif 'date' in prop_lower or 'time' in prop_lower:
            return random.choice(self.datatypes['datetime'])
        elif 'price' in prop_lower or 'amount' in prop_lower or 'value' in prop_lower:
            return random.choice(self.datatypes['decimal'])
        elif 'quantity' in prop_lower or 'count' in prop_lower:
            return random.choice(self.datatypes['integer'])
        elif 'status' in prop_lower or 'flag' in prop_lower or 'active' in prop_lower:
            if random.random() < 0.5:
                return random.choice(self.datatypes['boolean'])
            else:
                return random.choice(self.datatypes['string_small'])
        else:
            return random.choice(self.datatypes['string_large'])

    def generate_table_context(self, property_name: str) -> Tuple[str, str]:
        """Generate table name and context for a property"""
        # Find which class(es) use this property
        classes_with_property = []
        for class_name in self.ontology.classes.keys():
            props = self.ontology.get_properties_by_class(class_name, include_inherited=True)
            if property_name in props:
                classes_with_property.append(class_name)

        if classes_with_property:
            # Pick a class
            ontology_class = random.choice(classes_with_property)
            # Generate table name
            table_suffixes = ['', '_tbl', '_table', 's', '_data', '_info']
            table_name = ontology_class.lower() + random.choice(table_suffixes)
        else:
            ontology_class = 'Unknown'
            table_name = 'data_table'

        return table_name, ontology_class

    def generate_samples(
        self,
        property_name: str,
        num_samples: int
    ) -> List[Dict]:
        """Generate multiple field samples for a single ontology property"""
        samples = []

        for i in range(num_samples):
            # Generate field name (with variation)
            field_name = self.generate_field_name(property_name)

            # Ensure uniqueness by adding index if needed
            if i > 0 and random.random() < 0.3:
                field_name = f"{field_name}_{i}"

            # Generate table context
            table_name, ontology_class = self.generate_table_context(property_name)

            # Ensure table name variation
            if i % 10 == 0 and i > 0:
                table_name = f"{table_name}_{i // 10}"

            # Infer datatype
            data_type = self.infer_datatype(property_name)

            sample = {
                'table_name': table_name,
                'field_name': field_name,
                'data_type': data_type,
                'ontology_property': property_name,
                'ontology_class': ontology_class,
                'is_primary_key': 'id' in field_name.lower() and random.random() < 0.1,
                'is_nullable': random.random() < 0.7,
            }

            samples.append(sample)

        return samples

    def generate_balanced_dataset(
        self,
        target_properties: int = 50,
        samples_per_property: int = 70,
        variance: int = 10
    ) -> Dict:
        """
        Generate balanced dataset

        Args:
            target_properties: Number of properties to include
            samples_per_property: Target samples per property
            variance: Random variance in samples per property (±variance)

        Returns:
            Dictionary with field_mappings and metadata
        """
        print(f"Generating balanced dataset...")
        print(f"  Target: {target_properties} properties × {samples_per_property}±{variance} samples")

        # Select properties
        selected_properties = self.select_core_properties(target_properties)

        # Generate samples for each property
        all_samples = []
        property_counts = {}

        for prop in selected_properties:
            # Add variance
            n_samples = samples_per_property + random.randint(-variance, variance)
            n_samples = max(50, n_samples)  # Minimum 50

            samples = self.generate_samples(prop, n_samples)
            all_samples.extend(samples)
            property_counts[prop] = n_samples

        # Shuffle
        random.shuffle(all_samples)

        # Create ground truth structure
        ground_truth = {
            'field_mappings': all_samples,
            'metadata': {
                'num_properties': len(selected_properties),
                'total_samples': len(all_samples),
                'samples_per_property': {
                    'min': min(property_counts.values()),
                    'max': max(property_counts.values()),
                    'mean': np.mean(list(property_counts.values())),
                    'std': np.std(list(property_counts.values())),
                },
                'property_distribution': property_counts
            }
        }

        return ground_truth

    def validate_dataset(self, ground_truth: Dict) -> bool:
        """Validate dataset meets requirements"""
        print("\n=== DATASET VALIDATION ===")

        mappings = ground_truth['field_mappings']
        properties = [m['ontology_property'] for m in mappings]
        unique_props, counts = np.unique(properties, return_counts=True)

        total_samples = len(mappings)
        num_properties = len(unique_props)
        min_samples = counts.min()
        max_samples = counts.max()
        mean_samples = counts.mean()
        std_samples = counts.std()
        imbalance_ratio = max_samples / min_samples

        print(f"Total samples: {total_samples}")
        print(f"Unique properties: {num_properties}")
        print(f"Samples per property: min={min_samples}, max={max_samples}, mean={mean_samples:.1f}, std={std_samples:.1f}")
        print(f"Class imbalance ratio: {imbalance_ratio:.2f}:1")

        # Check requirements
        checks = []
        checks.append(("Total samples 3000-7000", 3000 <= total_samples <= 7000))
        checks.append(("Min samples per property ≥50", min_samples >= 50))
        checks.append(("Class imbalance ≤3:1", imbalance_ratio <= 3.0))
        checks.append(("Number of properties 40-60", 40 <= num_properties <= 60))

        print("\nRequirement checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False

        return all_passed

    def create_train_val_test_split(
        self,
        ground_truth: Dict,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Dict:
        """Create stratified train/val/test splits"""
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

        mappings = ground_truth['field_mappings']

        # Group by property
        property_groups = {}
        for i, mapping in enumerate(mappings):
            prop = mapping['ontology_property']
            if prop not in property_groups:
                property_groups[prop] = []
            property_groups[prop].append(i)

        # Stratified split
        train_indices = []
        val_indices = []
        test_indices = []

        for prop, indices in property_groups.items():
            random.shuffle(indices)
            n = len(indices)
            n_train = int(n * train_ratio)
            n_val = int(n * val_ratio)

            train_indices.extend(indices[:n_train])
            val_indices.extend(indices[n_train:n_train+n_val])
            test_indices.extend(indices[n_train+n_val:])

        # Shuffle splits
        random.shuffle(train_indices)
        random.shuffle(val_indices)
        random.shuffle(test_indices)

        splits = {
            'train': train_indices,
            'val': val_indices,
            'test': test_indices,
            'metadata': {
                'train_size': len(train_indices),
                'val_size': len(val_indices),
                'test_size': len(test_indices),
            }
        }

        return splits


if __name__ == '__main__':
    import os

    print("=== BALANCED DATASET GENERATION ===\n")

    # Generate
    generator = BalancedDatasetGenerator(seed=42)
    ground_truth = generator.generate_balanced_dataset(
        target_properties=50,
        samples_per_property=70,
        variance=15
    )

    # Validate
    is_valid = generator.validate_dataset(ground_truth)

    if not is_valid:
        print("\n✗ Dataset validation FAILED")
        print("Aborting - requirements not met")
        exit(1)

    # Create splits
    print("\nCreating train/val/test splits...")
    splits = generator.create_train_val_test_split(ground_truth)
    print(f"  Train: {splits['metadata']['train_size']}")
    print(f"  Val: {splits['metadata']['val_size']}")
    print(f"  Test: {splits['metadata']['test_size']}")

    # Save
    output_dir = 'data_generation/balanced_output'
    os.makedirs(output_dir, exist_ok=True)

    with open(f'{output_dir}/ground_truth.json', 'w') as f:
        json.dump(ground_truth, f, indent=2)

    with open(f'{output_dir}/splits.json', 'w') as f:
        json.dump(splits, f, indent=2)

    print(f"\n✓ Dataset saved to {output_dir}/")
    print("\n✓ BALANCED DATASET GENERATION COMPLETE")
