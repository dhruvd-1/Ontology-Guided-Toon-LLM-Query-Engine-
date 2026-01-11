"""
Intent Parser Module

Extracts structured intent from natural language queries.
Research-safe: uses keyword matching and ontology-guided parsing.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class QueryIntent:
    """Parsed query intent"""
    entities: List[str]  # Ontology classes/properties mentioned
    filters: List[Dict]  # Filter conditions
    aggregations: List[str]  # Aggregation operations
    sort: Optional[str]  # Sort field
    limit: Optional[int]  # Result limit


class IntentParser:
    """Parse natural language queries into structured intent"""

    def __init__(self, ontology):
        self.ontology = ontology

        # Keywords for different intent types
        self.filter_keywords = {
            'equal': ['is', 'equals', 'equal to', 'are'],
            'greater': ['greater than', 'more than', 'above', '>', 'higher than'],
            'less': ['less than', 'below', '<', 'lower than'],
            'contains': ['contains', 'includes', 'with', 'having'],
            'range': ['between', 'from', 'to']
        }

        self.aggregation_keywords = {
            'count': ['count', 'number of', 'how many'],
            'sum': ['sum', 'total'],
            'avg': ['average', 'mean'],
            'max': ['maximum', 'highest', 'max'],
            'min': ['minimum', 'lowest', 'min']
        }

        self.sort_keywords = {
            'asc': ['ascending', 'lowest first', 'smallest first'],
            'desc': ['descending', 'highest first', 'largest first', 'top']
        }

    def parse(self, query: str) -> QueryIntent:
        """
        Parse natural language query into structured intent

        Args:
            query: Natural language query string

        Returns:
            QueryIntent object
        """
        query_lower = query.lower()

        # Extract entities (ontology classes and properties)
        entities = self._extract_entities(query_lower)

        # Extract filters
        filters = self._extract_filters(query_lower, entities)

        # Extract aggregations
        aggregations = self._extract_aggregations(query_lower)

        # Extract sort
        sort = self._extract_sort(query_lower, entities)

        # Extract limit
        limit = self._extract_limit(query_lower)

        return QueryIntent(
            entities=entities,
            filters=filters,
            aggregations=aggregations,
            sort=sort,
            limit=limit
        )

    def _extract_entities(self, query: str) -> List[str]:
        """Extract ontology entities mentioned in query"""
        entities = []

        # Check for ontology classes
        for class_name in self.ontology.classes.keys():
            if class_name.lower() in query:
                entities.append(class_name)

        # Check for ontology properties
        for prop_name in self.ontology.properties.keys():
            # Match property name or common variations
            patterns = [
                prop_name.lower(),
                re.sub(r'([a-z])([A-Z])', r'\1 \2', prop_name).lower(),  # camelCase -> camel case
            ]

            for pattern in patterns:
                if pattern in query:
                    entities.append(prop_name)
                    break

        return list(set(entities))  # Remove duplicates

    def _extract_filters(self, query: str, entities: List[str]) -> List[Dict]:
        """Extract filter conditions from query"""
        filters = []

        # Look for comparison patterns
        # Pattern: <property> <operator> <value>

        # Example patterns:
        # "price greater than 100"
        # "status is active"
        # "category contains electronics"

        for entity in entities:
            entity_pattern = entity.lower()

            # Try different filter types
            for filter_type, keywords in self.filter_keywords.items():
                for keyword in keywords:
                    pattern = f"{entity_pattern}\\s+{keyword}\\s+(\\w+|\\d+)"
                    match = re.search(pattern, query)
                    if match:
                        filters.append({
                            'field': entity,
                            'operator': filter_type,
                            'value': match.group(1)
                        })

        return filters

    def _extract_aggregations(self, query: str) -> List[str]:
        """Extract aggregation operations from query"""
        aggregations = []

        for agg_type, keywords in self.aggregation_keywords.items():
            if any(keyword in query for keyword in keywords):
                aggregations.append(agg_type)

        return aggregations

    def _extract_sort(self, query: str, entities: List[str]) -> Optional[str]:
        """Extract sort field and direction"""
        for direction, keywords in self.sort_keywords.items():
            if any(keyword in query for keyword in keywords):
                # Try to find which field to sort by
                for entity in entities:
                    if entity.lower() in query:
                        return f"{entity}:{direction}"
        return None

    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract result limit from query"""
        # Look for patterns like "top 10", "first 5", "limit 20"
        patterns = [
            r'top\s+(\d+)',
            r'first\s+(\d+)',
            r'limit\s+(\d+)',
            r'(\d+)\s+results?'
        ]

        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))

        return None


# Predefined query templates
QUERY_TEMPLATES = {
    'customers_who_bought_electronics': {
        'description': 'Customers who bought electronics',
        'entities': ['Customer', 'Order', 'Product', 'Category'],
        'filters': [
            {'field': 'categoryName', 'operator': 'contains', 'value': 'Electronics'}
        ],
        'aggregations': [],
        'joins': [
            ('Customer', 'places', 'Order'),
            ('Order', 'contains', 'Product'),
            ('Product', 'belongsTo', 'Category')
        ]
    },
    'high_value_tech_customers': {
        'description': 'High-value customers who buy tech products',
        'entities': ['Customer', 'Order', 'Product', 'LoyaltyProfile'],
        'filters': [
            {'field': 'totalAmount', 'operator': 'greater', 'value': 500},
            {'field': 'categoryName', 'operator': 'contains', 'value': 'Electronics'}
        ],
        'aggregations': ['sum', 'count'],
        'joins': [
            ('Customer', 'places', 'Order'),
            ('Customer', 'hasLoyalty', 'LoyaltyProfile'),
            ('Order', 'contains', 'Product')
        ]
    }
}


def get_query_template(template_name: str) -> Optional[Dict]:
    """Get predefined query template"""
    return QUERY_TEMPLATES.get(template_name)


if __name__ == '__main__':
    from ontology import get_ontology

    print("=== Intent Parser Test ===\n")

    ontology = get_ontology()
    parser = IntentParser(ontology)

    # Test queries
    test_queries = [
        "Customers who bought electronics",
        "Show me orders with total amount greater than 500",
        "Count the number of products in each category",
        "Top 10 customers by lifetime value"
    ]

    for query in test_queries:
        print(f"Query: {query}")
        intent = parser.parse(query)
        print(f"  Entities: {intent.entities}")
        print(f"  Filters: {intent.filters}")
        print(f"  Aggregations: {intent.aggregations}")
        print(f"  Sort: {intent.sort}")
        print(f"  Limit: {intent.limit}")
        print()

    # Test templates
    print("Available query templates:")
    for name, template in QUERY_TEMPLATES.items():
        print(f"  - {name}: {template['description']}")

    print("\n✓ Intent parser working!")
