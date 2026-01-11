"""
Synthetic Data Generator

Generates realistic synthetic data records based on schemas.
"""

import json
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

from data_generation.synthetic_schema import SchemaTable, SchemaField


class SyntheticDataGenerator:
    """Generates realistic synthetic data"""

    def __init__(self, seed: int = 42):
        self.faker = Faker()
        Faker.seed(seed)
        random.seed(seed)

    def generate_value(self, field: SchemaField, record_id: int) -> Any:
        """Generate a realistic value for a field"""
        prop_name = field.ontology_property.lower()
        data_type = field.data_type.upper()

        # Handle IDs
        if field.is_primary_key or 'id' in prop_name:
            return f"{field.ontology_class[:3].upper()}-{record_id:06d}"

        # Handle specific properties with realistic data
        if 'email' in prop_name:
            return self.faker.email()
        elif 'firstname' in prop_name or 'fname' in prop_name:
            return self.faker.first_name()
        elif 'lastname' in prop_name or 'lname' in prop_name:
            return self.faker.last_name()
        elif 'phone' in prop_name:
            return self.faker.phone_number()
        elif 'dateofbirth' in prop_name or 'dob' in prop_name:
            return self.faker.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
        elif 'street' in prop_name or 'address' in prop_name:
            return self.faker.street_address()
        elif 'city' in prop_name:
            return self.faker.city()
        elif 'state' in prop_name:
            return self.faker.state()
        elif 'postal' in prop_name or 'zip' in prop_name:
            return self.faker.postcode()
        elif 'country' in prop_name:
            return self.faker.country()
        elif 'product' in prop_name and 'name' in prop_name:
            categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
            items = ['Pro', 'Elite', 'Classic', 'Premium', 'Standard']
            return f"{random.choice(categories)} {random.choice(items)} {random.randint(1000, 9999)}"
        elif 'brand' in prop_name:
            return random.choice(['Samsung', 'Apple', 'Sony', 'LG', 'Nike', 'Adidas', 'Dell', 'HP'])
        elif 'category' in prop_name and 'name' in prop_name:
            return random.choice(['Electronics', 'Phones', 'Laptops', 'Tablets', 'Accessories', 'Clothing', 'Shoes'])
        elif 'sku' in prop_name:
            return f"SKU-{random.randint(100000, 999999)}"
        elif 'description' in prop_name or 'desc' in prop_name:
            return self.faker.text(max_nb_chars=200)
        elif 'subject' in prop_name:
            return random.choice([
                'Order delivery issue',
                'Product defect',
                'Payment problem',
                'Return request',
                'General inquiry'
            ])
        elif 'vendor' in prop_name and 'name' in prop_name:
            return self.faker.company()
        elif 'carrier' in prop_name:
            return random.choice(['FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics'])
        elif 'tracking' in prop_name:
            return f"TRK{random.randint(10**10, 10**11-1)}"
        elif 'warehouse' in prop_name:
            return f"WH-{random.choice(['EAST', 'WEST', 'NORTH', 'SOUTH'])}-{random.randint(1, 20)}"

        # Handle status/state fields
        elif 'orderstatus' in prop_name or ('order' in prop_name and 'status' in prop_name):
            return random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered'])
        elif 'paymentstatus' in prop_name or ('payment' in prop_name and 'status' in prop_name):
            return random.choice(['pending', 'completed', 'failed'])
        elif 'shipmentstatus' in prop_name or ('shipment' in prop_name and 'status' in prop_name):
            return random.choice(['preparing', 'in_transit', 'delivered'])
        elif 'status' in prop_name:
            return random.choice(['active', 'inactive', 'pending'])

        # Handle tier/level fields
        elif 'tier' in prop_name or 'level' in prop_name:
            return random.choice(['bronze', 'silver', 'gold', 'platinum'])

        # Handle method/type fields
        elif 'paymentmethod' in prop_name:
            return random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer'])
        elif 'shippingmethod' in prop_name:
            return random.choice(['standard', 'express', 'overnight', 'economy'])
        elif 'addresstype' in prop_name:
            return random.choice(['shipping', 'billing', 'both'])
        elif 'discounttype' in prop_name:
            return random.choice(['percentage', 'fixed_amount', 'free_shipping'])
        elif 'transactiontype' in prop_name:
            return random.choice(['sale', 'refund', 'adjustment'])
        elif 'priority' in prop_name:
            return random.choice(['low', 'medium', 'high', 'critical'])

        # Handle numeric types
        elif 'INT' in data_type or 'SMALLINT' in data_type or 'BIGINT' in data_type:
            if 'price' in prop_name or 'amount' in prop_name or 'total' in prop_name or 'value' in prop_name:
                return round(random.uniform(10, 1000), 2)
            elif 'quantity' in prop_name or 'qty' in prop_name or 'count' in prop_name or 'items' in prop_name:
                return random.randint(1, 100)
            elif 'rating' in prop_name or 'stars' in prop_name:
                return random.randint(1, 5)
            elif 'points' in prop_name:
                return random.randint(0, 10000)
            elif 'helpful' in prop_name:
                return random.randint(0, 50)
            elif 'level' in prop_name:
                return random.randint(0, 5)
            elif 'warranty' in prop_name:
                return random.randint(6, 36)
            elif 'battery' in prop_name:
                return random.randint(2000, 5000)
            elif 'storage' in prop_name:
                return random.choice([64, 128, 256, 512, 1024])
            elif 'ram' in prop_name:
                return random.choice([4, 8, 16, 32, 64])
            else:
                return random.randint(1, 1000)

        # Handle decimal/float types
        elif 'DECIMAL' in data_type or 'NUMERIC' in data_type or 'FLOAT' in data_type or 'DOUBLE' in data_type:
            if 'price' in prop_name or 'amount' in prop_name or 'total' in prop_name or 'value' in prop_name:
                return round(random.uniform(10, 1000), 2)
            elif 'rating' in prop_name:
                return round(random.uniform(1, 5), 1)
            elif 'weight' in prop_name:
                return round(random.uniform(0.1, 50), 2)
            elif 'screen' in prop_name:
                return round(random.uniform(5.0, 17.0), 1)
            else:
                return round(random.uniform(1, 100), 2)

        # Handle boolean types
        elif 'BOOLEAN' in data_type or 'BOOL' in data_type or 'BIT' in data_type or 'TINYINT(1)' in data_type:
            if 'verified' in prop_name:
                return random.choice([True, False])
            elif 'active' in prop_name:
                return True
            else:
                return random.choice([True, False])

        # Handle date/datetime types
        elif 'DATE' in data_type or 'TIMESTAMP' in data_type:
            if 'birth' in prop_name:
                return self.faker.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
            elif 'registration' in prop_name or 'created' in prop_name or 'join' in prop_name:
                days_ago = random.randint(1, 365 * 3)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif 'order' in prop_name or 'payment' in prop_name or 'transaction' in prop_name:
                days_ago = random.randint(1, 180)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif 'review' in prop_name:
                days_ago = random.randint(1, 90)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif 'shipment' in prop_name or 'delivery' in prop_name:
                days_ago = random.randint(0, 30)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif 'start' in prop_name:
                days_ago = random.randint(0, 30)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            elif 'end' in prop_name or 'expiry' in prop_name:
                days_ahead = random.randint(1, 90)
                return (datetime.now() + timedelta(days=days_ahead)).isoformat()
            elif 'modified' in prop_name or 'updated' in prop_name:
                days_ago = random.randint(0, 30)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()
            else:
                days_ago = random.randint(1, 365)
                return (datetime.now() - timedelta(days=days_ago)).isoformat()

        # Handle text/varchar types
        elif 'TEXT' in data_type or 'VARCHAR' in data_type or 'CHAR' in data_type:
            if 'currency' in prop_name:
                return random.choice(['USD', 'EUR', 'GBP', 'JPY'])
            elif 'dimensions' in prop_name:
                return f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm"
            elif 'voltage' in prop_name:
                return random.choice(['110V', '220V', '240V'])
            elif 'os' in prop_name or 'operating' in prop_name:
                return random.choice(['iOS', 'Android', 'Windows', 'macOS'])
            elif 'processor' in prop_name:
                return random.choice(['Intel i5', 'Intel i7', 'AMD Ryzen 5', 'AMD Ryzen 7', 'Apple M1'])
            elif 'graphics' in prop_name:
                return random.choice(['NVIDIA RTX 3060', 'AMD Radeon RX 6700', 'Intel Iris', 'Integrated'])
            elif 'code' in prop_name:
                return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            elif 'reference' in prop_name:
                return f"REF-{random.randint(100000, 999999)}"
            else:
                # Generic text
                return self.faker.catch_phrase()

        # Default fallback
        return self.faker.word()

    def generate_records(self, schema: SchemaTable, num_records: int = 1000) -> List[Dict]:
        """Generate synthetic records for a schema"""
        records = []

        for i in range(1, num_records + 1):
            record = {}
            for field in schema.fields:
                value = self.generate_value(field, i)
                record[field.field_name] = value
            records.append(record)

        return records

    def generate_all_data(self, schemas: List[SchemaTable], num_records: int = 1000) -> Dict[str, List[Dict]]:
        """Generate data for all schemas"""
        all_data = {}

        for schema in schemas:
            records = self.generate_records(schema, num_records)
            all_data[schema.table_name] = records

        return all_data


def save_data_to_files(data: Dict[str, List[Dict]], ground_truth: Dict, output_dir: str = 'data_generation/output'):
    """Save generated data and ground truth to files"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Save each table's data as JSON
    for table_name, records in data.items():
        filepath = os.path.join(output_dir, f"{table_name}.json")
        with open(filepath, 'w') as f:
            json.dump(records, f, indent=2, default=str)
        print(f"Saved {len(records)} records to {filepath}")

    # Save ground truth mapping
    gt_filepath = os.path.join(output_dir, 'ground_truth_mapping.json')
    with open(gt_filepath, 'w') as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Saved ground truth mapping to {gt_filepath}")

    # Save consolidated data
    consolidated = {
        'tables': data,
        'ground_truth': ground_truth,
        'metadata': {
            'num_tables': len(data),
            'total_records': sum(len(records) for records in data.values()),
            'generated_at': datetime.now().isoformat()
        }
    }

    consolidated_filepath = os.path.join(output_dir, 'consolidated_data.json')
    with open(consolidated_filepath, 'w') as f:
        json.dump(consolidated, f, indent=2, default=str)
    print(f"Saved consolidated data to {consolidated_filepath}")


def validate_data_distribution(data: Dict[str, List[Dict]]):
    """Validate data distributions and sanity checks"""
    print("\n=== Data Validation Report ===")

    total_records = 0
    for table_name, records in data.items():
        print(f"\nTable: {table_name}")
        print(f"  Records: {len(records)}")
        total_records += len(records)

        if records:
            # Sample first record
            sample = records[0]
            print(f"  Fields: {len(sample)}")

            # Check for nulls
            null_counts = {k: sum(1 for r in records if r.get(k) is None) for k in sample.keys()}
            if any(null_counts.values()):
                print(f"  Null values found in: {[k for k, v in null_counts.items() if v > 0]}")

            # Check for duplicates in ID fields
            id_fields = [k for k in sample.keys() if 'id' in k.lower()]
            for id_field in id_fields:
                values = [r.get(id_field) for r in records]
                unique_values = len(set(values))
                if unique_values != len(values):
                    print(f"  WARNING: Duplicate values in {id_field}")
                else:
                    print(f"  ✓ {id_field} has unique values")

    print(f"\nTotal records across all tables: {total_records}")
    print("✓ Data validation complete")


if __name__ == '__main__':
    from ontology import get_ontology
    from data_generation.synthetic_schema import generate_synthetic_schemas

    print("=== Synthetic Data Generation ===\n")

    # Load ontology
    print("Loading ontology...")
    ontology = get_ontology()

    # Generate schemas
    print("Generating schemas...")
    schemas, ground_truth = generate_synthetic_schemas(ontology, num_tables=10)
    print(f"Generated {len(schemas)} schemas")

    # Generate data
    print("\nGenerating synthetic data (1000 records per table)...")
    generator = SyntheticDataGenerator(seed=42)
    data = generator.generate_all_data(schemas, num_records=1000)

    # Validate data
    validate_data_distribution(data)

    # Save to files
    print("\nSaving data to files...")
    save_data_to_files(data, ground_truth)

    print("\n✓ Data generation complete!")
