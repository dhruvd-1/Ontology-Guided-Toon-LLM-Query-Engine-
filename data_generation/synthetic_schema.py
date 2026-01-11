"""
Synthetic Schema Generator

Generates realistic but messy database schemas with:
- Abbreviated/messy field names
- Realistic datatypes
- Ground truth mappings to ontology
"""

import json
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SchemaField:
    """Represents a field in a database schema"""
    field_name: str  # Messy name (e.g., cust_eml)
    data_type: str
    ontology_class: str
    ontology_property: str
    is_nullable: bool = False
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_table: str = None


@dataclass
class SchemaTable:
    """Represents a database table"""
    table_name: str
    ontology_class: str
    fields: List[SchemaField]


class SyntheticSchemaGenerator:
    """Generates synthetic schemas with messy names"""

    # Messy name patterns for different properties
    MESSY_PATTERNS = {
        'customerId': ['cust_id', 'customer_id', 'cust_no', 'custid', 'c_id'],
        'email': ['cust_eml', 'email_addr', 'eml', 'email_id', 'e_mail'],
        'firstName': ['fname', 'first_nm', 'f_name', 'first_name', 'fn'],
        'lastName': ['lname', 'last_nm', 'l_name', 'last_name', 'ln'],
        'phoneNumber': ['phone_no', 'ph_num', 'phone', 'tel', 'phone_nbr'],
        'dateOfBirth': ['dob', 'birth_dt', 'birth_date', 'date_birth', 'bday'],
        'registrationDate': ['reg_date', 'reg_dt', 'registered_on', 'signup_date', 'created_at'],
        'customerTier': ['cust_tier', 'tier', 'membership_lvl', 'cust_level', 'tier_type'],
        'orderId': ['order_id', 'ord_id', 'order_no', 'ord_num', 'o_id'],
        'orderDate': ['ord_date', 'order_dt', 'placed_on', 'order_time', 'ord_ts'],
        'totalAmount': ['ord_val', 'total_amt', 'order_total', 'amount', 'total_value'],
        'orderStatus': ['ord_status', 'status', 'order_state', 'ord_stat', 'state'],
        'shippingMethod': ['ship_method', 'shipping_type', 'delivery_method', 'ship_mthd', 'del_type'],
        'trackingNumber': ['tracking_no', 'track_num', 'tracking_id', 'trk_no', 'track_nbr'],
        'productId': ['prod_id', 'product_id', 'prod_no', 'p_id', 'item_id'],
        'productName': ['prod_name', 'product_nm', 'item_name', 'prod_desc', 'p_name'],
        'description': ['desc', 'description', 'prod_desc', 'details', 'item_desc'],
        'price': ['price', 'prod_price', 'unit_price', 'cost', 'amount'],
        'sku': ['sku', 'sku_code', 'prod_sku', 'item_code', 'product_code'],
        'weight': ['wt', 'weight', 'prod_weight', 'item_weight', 'wgt'],
        'dimensions': ['dims', 'dimensions', 'size', 'prod_dims', 'measurements'],
        'brand': ['brand', 'brand_name', 'manufacturer', 'make', 'prod_brand'],
        'categoryId': ['cat_id', 'category_id', 'cat_no', 'category_code', 'cat'],
        'categoryName': ['cat_name', 'category_nm', 'cat_desc', 'category', 'cat_title'],
        'parentCategory': ['parent_cat', 'parent_id', 'parent_category', 'parent_cat_id', 'super_cat'],
        'paymentId': ['payment_id', 'pay_id', 'payment_no', 'pay_num', 'txn_id'],
        'paymentMethod': ['pay_method', 'payment_type', 'pay_type', 'payment_mode', 'pay_mthd'],
        'paymentDate': ['pay_date', 'payment_dt', 'paid_on', 'payment_time', 'pay_ts'],
        'amount': ['amount', 'amt', 'pay_amount', 'payment_amt', 'value'],
        'transactionId': ['txn_id', 'transaction_id', 'trans_id', 'trx_id', 'transaction_no'],
        'paymentStatus': ['pay_status', 'payment_state', 'pay_stat', 'status', 'payment_status'],
        'addressId': ['addr_id', 'address_id', 'addr_no', 'location_id', 'add_id'],
        'addressType': ['addr_type', 'address_type', 'location_type', 'addr_cat', 'add_type'],
        'streetAddress': ['street', 'street_addr', 'address1', 'street_address', 'addr_line1'],
        'city': ['city', 'city_name', 'town', 'city_nm', 'locality'],
        'state': ['state', 'state_name', 'province', 'region', 'state_code'],
        'postalCode': ['postal_code', 'zip', 'zip_code', 'postcode', 'postal'],
        'country': ['country', 'country_name', 'nation', 'country_code', 'ctry'],
        'reviewId': ['review_id', 'rev_id', 'review_no', 'feedback_id', 'r_id'],
        'rating': ['rating', 'score', 'stars', 'review_rating', 'rate'],
        'reviewText': ['review_txt', 'review_text', 'comment', 'feedback', 'review_body'],
        'reviewDate': ['review_dt', 'review_date', 'reviewed_on', 'feedback_date', 'rev_date'],
        'verified': ['verified', 'is_verified', 'verified_purchase', 'verified_flag', 'is_verified_buyer'],
        'helpfulCount': ['helpful_cnt', 'helpful_count', 'likes', 'upvotes', 'helpful_votes'],
        'vendorId': ['vendor_id', 'vendor_no', 'seller_id', 'v_id', 'supplier_id'],
        'vendorName': ['vendor_name', 'vendor_nm', 'seller_name', 'supplier_name', 'v_name'],
        'contactEmail': ['contact_eml', 'vendor_email', 'contact_email', 'email', 'vendor_eml'],
        'activeStatus': ['active', 'is_active', 'status', 'active_flag', 'enabled'],
        'cartId': ['cart_id', 'basket_id', 'shopping_cart_id', 'cart_no', 'c_id'],
        'createdDate': ['created_dt', 'created_date', 'created_at', 'create_date', 'created_on'],
        'lastModified': ['modified_dt', 'last_modified', 'updated_at', 'last_update', 'modified_on'],
        'totalItems': ['total_items', 'item_count', 'num_items', 'items_cnt', 'total_qty'],
        'subtotal': ['subtotal', 'sub_total', 'cart_total', 'basket_total', 'item_total'],
        'discountId': ['discount_id', 'disc_id', 'promo_id', 'discount_no', 'd_id'],
        'discountCode': ['disc_code', 'discount_code', 'promo_code', 'coupon_code', 'voucher_code'],
        'discountType': ['disc_type', 'discount_type', 'promo_type', 'discount_cat', 'disc_category'],
        'discountValue': ['disc_value', 'discount_amt', 'discount_value', 'disc_amt', 'promo_value'],
        'startDate': ['start_dt', 'start_date', 'valid_from', 'from_date', 'start_on'],
        'endDate': ['end_dt', 'end_date', 'valid_until', 'expiry_date', 'expires_on'],
        'shipmentId': ['shipment_id', 'ship_id', 'delivery_id', 'ship_no', 's_id'],
        'carrier': ['carrier', 'carrier_name', 'shipper', 'shipping_carrier', 'courier'],
        'shipmentDate': ['ship_date', 'shipped_on', 'dispatch_date', 'ship_dt', 'dispatched_at'],
        'estimatedDelivery': ['est_delivery', 'eta', 'estimated_arrival', 'expected_delivery', 'est_del_dt'],
        'actualDelivery': ['actual_delivery', 'delivered_on', 'delivery_date', 'actual_del_dt', 'delivered_at'],
        'shipmentStatus': ['ship_status', 'shipment_state', 'delivery_status', 'ship_stat', 'tracking_status'],
        'inventoryId': ['inv_id', 'inventory_id', 'stock_id', 'inv_no', 'inventory_no'],
        'quantity': ['qty', 'quantity', 'stock_qty', 'available_qty', 'stock_count'],
        'warehouseLocation': ['warehouse', 'warehouse_loc', 'location', 'storage_loc', 'wh_location'],
        'reorderLevel': ['reorder_lvl', 'reorder_level', 'min_stock', 'reorder_point', 'min_qty'],
        'transactionType': ['txn_type', 'transaction_type', 'trans_type', 'trx_type', 'txn_category'],
        'currency': ['currency', 'currency_code', 'curr', 'currency_type', 'curr_code'],
        'transactionDate': ['txn_date', 'transaction_dt', 'trans_date', 'txn_ts', 'transaction_time'],
        'status': ['status', 'state', 'current_status', 'stat', 'status_code'],
        'ticketId': ['ticket_id', 'ticket_no', 'support_id', 'case_id', 't_id'],
        'subject': ['subject', 'ticket_subject', 'title', 'issue_title', 'topic'],
        'priority': ['priority', 'priority_level', 'urgency', 'importance', 'priority_type'],
        'loyaltyId': ['loyalty_id', 'loyalty_no', 'rewards_id', 'l_id', 'loyalty_program_id'],
        'points': ['points', 'reward_points', 'loyalty_points', 'pts', 'points_balance'],
        'tier': ['tier', 'loyalty_tier', 'level', 'membership_tier', 'tier_level'],
        'lifetimeValue': ['ltv', 'lifetime_value', 'customer_ltv', 'total_value', 'life_value'],
    }

    # Datatype mappings
    DATATYPE_MAP = {
        'string': ['VARCHAR(255)', 'TEXT', 'VARCHAR(100)', 'CHAR(50)'],
        'integer': ['INT', 'INTEGER', 'BIGINT', 'SMALLINT'],
        'decimal': ['DECIMAL(10,2)', 'NUMERIC(12,2)', 'FLOAT', 'DOUBLE'],
        'boolean': ['BOOLEAN', 'TINYINT(1)', 'BIT', 'BOOL'],
        'date': ['DATE', 'DATETIME', 'TIMESTAMP'],
        'datetime': ['DATETIME', 'TIMESTAMP', 'TIMESTAMP WITH TIME ZONE'],
        'text': ['TEXT', 'LONGTEXT', 'VARCHAR(1000)', 'CLOB'],
    }

    def __init__(self, ontology):
        self.ontology = ontology

    def generate_messy_field_name(self, property_name: str) -> str:
        """Generate a messy field name for a property"""
        if property_name in self.MESSY_PATTERNS:
            return random.choice(self.MESSY_PATTERNS[property_name])
        # Default: abbreviate or lowercase with underscore
        return property_name.lower()

    def get_sql_datatype(self, ontology_datatype: str) -> str:
        """Map ontology datatype to SQL datatype"""
        if ontology_datatype in self.DATATYPE_MAP:
            return random.choice(self.DATATYPE_MAP[ontology_datatype])
        return 'VARCHAR(255)'  # Default

    def generate_table_schema(self, class_name: str) -> SchemaTable:
        """Generate a schema for a single table"""
        ontology_class = self.ontology.get_class(class_name)
        if not ontology_class:
            return None

        # Generate messy table name
        table_name = class_name.lower() + random.choice(['_tbl', '_table', 's', '_data', ''])

        fields = []

        # Get all properties for this class
        properties = self.ontology.get_properties_by_class(class_name, include_inherited=True)

        for i, prop_name in enumerate(properties):
            prop = self.ontology.get_property(prop_name)
            if not prop:
                continue

            # Generate messy field name
            messy_name = self.generate_messy_field_name(prop_name)

            # Get SQL datatype
            sql_type = self.get_sql_datatype(prop.datatype)

            # Check if primary key (usually first field or ID field)
            is_pk = i == 0 or 'id' in prop_name.lower()

            fields.append(SchemaField(
                field_name=messy_name,
                data_type=sql_type,
                ontology_class=class_name,
                ontology_property=prop_name,
                is_nullable=not is_pk,
                is_primary_key=is_pk,
                is_foreign_key=False
            ))

        return SchemaTable(
            table_name=table_name,
            ontology_class=class_name,
            fields=fields
        )

    def generate_schema_for_classes(self, class_names: List[str]) -> List[SchemaTable]:
        """Generate schemas for multiple classes"""
        schemas = []
        for class_name in class_names:
            schema = self.generate_table_schema(class_name)
            if schema:
                schemas.append(schema)
        return schemas

    def generate_ground_truth_mapping(self, schemas: List[SchemaTable]) -> Dict:
        """Generate ground truth mapping from schema fields to ontology properties"""
        mapping = {
            'tables': {},
            'field_mappings': []
        }

        for schema in schemas:
            table_info = {
                'table_name': schema.table_name,
                'ontology_class': schema.ontology_class,
                'fields': []
            }

            for field in schema.fields:
                field_mapping = {
                    'table_name': schema.table_name,
                    'field_name': field.field_name,
                    'data_type': field.data_type,
                    'ontology_class': field.ontology_class,
                    'ontology_property': field.ontology_property,
                    'is_primary_key': field.is_primary_key,
                    'is_nullable': field.is_nullable
                }

                table_info['fields'].append(field_mapping)
                mapping['field_mappings'].append(field_mapping)

            mapping['tables'][schema.table_name] = table_info

        return mapping


def generate_synthetic_schemas(ontology, num_tables: int = 10) -> Tuple[List[SchemaTable], Dict]:
    """Generate synthetic schemas and ground truth mapping"""
    generator = SyntheticSchemaGenerator(ontology)

    # Select classes to generate schemas for
    all_classes = list(ontology.classes.keys())

    # Prioritize base classes (non-hierarchical)
    base_classes = [name for name, cls in ontology.classes.items() if cls.parent is None]
    selected_classes = base_classes[:num_tables]

    # Generate schemas
    schemas = generator.generate_schema_for_classes(selected_classes)

    # Generate ground truth mapping
    ground_truth = generator.generate_ground_truth_mapping(schemas)

    return schemas, ground_truth


if __name__ == '__main__':
    from ontology import get_ontology

    print("Generating synthetic schemas...")
    ontology = get_ontology()

    schemas, ground_truth = generate_synthetic_schemas(ontology, num_tables=10)

    print(f"\nGenerated {len(schemas)} table schemas:")
    for schema in schemas:
        print(f"\n  Table: {schema.table_name} (maps to {schema.ontology_class})")
        print(f"  Fields: {len(schema.fields)}")
        for field in schema.fields[:3]:  # Show first 3 fields
            print(f"    - {field.field_name} ({field.data_type}) -> {field.ontology_property}")

    print(f"\nGround truth mappings: {len(ground_truth['field_mappings'])} field mappings")
