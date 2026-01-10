"""
Semantic Query Engine

Combines intent parsing, ontology reasoning, and deterministic SQL generation.
Research-safe: No free-form NL→SQL, uses structured templates.
"""

import json
from typing import Dict, List, Optional
from semantic_query.intent_parser import IntentParser, QUERY_TEMPLATES
from semantic_query.ontology_reasoner import OntologyReasoner
from ontology import get_ontology


class SemanticQueryEngine:
    """Main query engine"""

    def __init__(self, ontology=None):
        self.ontology = ontology or get_ontology()
        self.parser = IntentParser(self.ontology)
        self.reasoner = OntologyReasoner(self.ontology)

    def execute_template_query(self, template_name: str) -> Dict:
        """
        Execute a predefined template query

        Args:
            template_name: Name of the template

        Returns:
            Query result structure
        """
        template = QUERY_TEMPLATES.get(template_name)
        if not template:
            return {'error': f'Template {template_name} not found'}

        # Build query plan
        query_plan = {
            'template': template_name,
            'description': template['description'],
            'entities': template['entities'],
            'filters': template['filters'],
            'joins': template.get('joins', [])
        }

        # Generate pseudo-SQL (demonstrative)
        sql = self._generate_sql(query_plan)

        # Return query structure
        return {
            'success': True,
            'template': template_name,
            'description': template['description'],
            'query_plan': query_plan,
            'sql': sql,
            'note': 'This would execute against the PostgreSQL database when available'
        }

    def parse_and_expand_query(self, natural_query: str) -> Dict:
        """
        Parse natural language query and expand with ontology reasoning

        Args:
            natural_query: Natural language query string

        Returns:
            Expanded query structure
        """
        # Parse intent
        intent = self.parser.parse(natural_query)

        # Expand entities using ontology
        expanded_entities = []
        for entity in intent.entities:
            expanded = self.reasoner.expand_concept(entity)
            expanded_entities.extend(expanded)

        # Resolve properties to classes
        property_classes = {}
        for entity in intent.entities:
            if entity in self.ontology.properties:
                classes = self.reasoner.resolve_property_to_class(entity)
                property_classes[entity] = classes

        # Find join paths if multiple entities
        join_path = []
        if len(intent.entities) > 1:
            join_path = self.reasoner.get_join_path(intent.entities)

        return {
            'original_query': natural_query,
            'parsed_intent': {
                'entities': intent.entities,
                'filters': intent.filters,
                'aggregations': intent.aggregations,
                'sort': intent.sort,
                'limit': intent.limit
            },
            'expanded_entities': expanded_entities,
            'property_classes': property_classes,
            'join_path': join_path
        }

    def _generate_sql(self, query_plan: Dict) -> str:
        """
        Generate deterministic SQL from query plan

        This is a simplified version for demonstration.
        In production, this would generate actual SQL.
        """
        entities = query_plan['entities']
        filters = query_plan['filters']

        # Build SELECT clause
        select_parts = [f"{e}.*" for e in entities]
        select_clause = f"SELECT {', '.join(select_parts)}"

        # Build FROM clause with joins
        from_clause = f"FROM {entities[0]}"

        joins = query_plan.get('joins', [])
        for join in joins:
            # Joins are tuples: (source, relationship, target)
            if isinstance(join, tuple):
                source, relationship, target = join
                from_clause += f"\nJOIN {target} ON {source}.id = {target}.{source.lower()}_id"
            else:
                from_clause += f"\nJOIN {join['target']} ON {join['source']}.id = {join['target']}.{join['source'].lower()}_id"

        # Build WHERE clause
        where_parts = []
        for f in filters:
            if f['operator'] == 'contains':
                where_parts.append(f"{f['field']} LIKE '%{f['value']}%'")
            elif f['operator'] == 'greater':
                where_parts.append(f"{f['field']} > {f['value']}")
            elif f['operator'] == 'equal':
                where_parts.append(f"{f['field']} = '{f['value']}'")

        where_clause = ""
        if where_parts:
            where_clause = f"\nWHERE {' AND '.join(where_parts)}"

        sql = f"{select_clause}\n{from_clause}{where_clause};"

        return sql

    def get_available_templates(self) -> List[Dict]:
        """Get list of available query templates"""
        return [
            {
                'name': name,
                'description': template['description'],
                'entities': template['entities']
            }
            for name, template in QUERY_TEMPLATES.items()
        ]


if __name__ == '__main__':
    print("=== Semantic Query Engine Test ===\n")

    engine = SemanticQueryEngine()

    # Test 1: Execute template queries
    print("Test 1: Template Queries")
    print("-" * 50)

    for template_name in ['customers_who_bought_electronics', 'high_value_tech_customers']:
        print(f"\nExecuting template: {template_name}")
        result = engine.execute_template_query(template_name)

        if result.get('success'):
            print(f"✓ {result['description']}")
            print(f"  Entities: {result['query_plan']['entities']}")
            print(f"  Filters: {result['query_plan']['filters']}")
            print(f"\n  Generated SQL:")
            for line in result['sql'].split('\n'):
                print(f"    {line}")
        else:
            print(f"✗ {result.get('error')}")

    # Test 2: Parse and expand natural queries
    print("\n\nTest 2: Natural Query Parsing & Expansion")
    print("-" * 50)

    test_queries = [
        "Customers who bought electronics",
        "Show me high value orders"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = engine.parse_and_expand_query(query)

        print(f"  Parsed entities: {result['parsed_intent']['entities']}")
        print(f"  Expanded: {result['expanded_entities']}")
        if result['parsed_intent']['filters']:
            print(f"  Filters: {result['parsed_intent']['filters']}")

    # Test 3: List available templates
    print("\n\nTest 3: Available Templates")
    print("-" * 50)

    templates = engine.get_available_templates()
    for t in templates:
        print(f"  • {t['name']}: {t['description']}")

    print("\n✓ Semantic query engine working!")
