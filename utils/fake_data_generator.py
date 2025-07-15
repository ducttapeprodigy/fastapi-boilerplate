import random
import uuid
from faker import Faker
from typing import List, Dict, Optional
import json

class HierarchicalDataGenerator:
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data generator with optional seed for reproducible results.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Define object types and their typical hierarchy
        self.object_types = {
            'datacenter': {'can_have_children': True, 'typical_children': ['sec_zone', 'datacenter', 'network']},
            'sec_zone': {'can_have_children': True, 'typical_children': ['network']},
            'network': {'can_have_children': True, 'typical_children': ['host']},
            'host': {'can_have_children': False, 'typical_children': []},
            #'vm': {'can_have_children': True, 'typical_children': ['service']},
            #'container': {'can_have_children': True, 'typical_children': ['service']},
            #'service': {'can_have_children': False, 'typical_children': []},
            #'port': {'can_have_children': False, 'typical_children': []}
        }
        
        self.security_zones = ['DMZ', 'Internal', 'External', 'Management', 'Production', 'Development']
        self.statuses = ['Active', 'Inactive', 'Maintenance', 'Error', 'Pending']
        
    def generate_object_id(self) -> str:
        """Generate a unique object ID."""
        return str(uuid.uuid4())
    
    def generate_config_id(self) -> str:
        """Generate a configuration ID."""
        return f"CFG-{random.randint(10000, 99999)}"
    
    def generate_ip_address(self) -> str:
        """Generate a realistic IP address."""
        return self.fake.ipv4()
    
    def generate_percent_utilized(self) -> float:
        """Generate a realistic utilization percentage."""
        return round(random.uniform(0.0, 100.0), 2)
    
    def create_base_record(self, object_type: str, parent_id: Optional[str] = None) -> Dict:
        """
        Create a base record with all required fields.
        
        Args:
            object_type: Type of object to create
            parent_id: ID of parent object (if any)
            
        Returns:
            Dictionary containing base record data
        """
        return {
            'object_id': self.generate_object_id(),
            'sec_zone': random.choice(self.security_zones),
            'config_id': self.generate_config_id(),
            'parent_id': parent_id,
            'ip_address': self.generate_ip_address(),
            'object_type': object_type,
            'status': random.choice(self.statuses) if object_type != "host" else "",
            'percent_utilized': self.generate_percent_utilized() if object_type != "host" else 0.0,
            'immediate_children': []  # Will be populated later
        }
    
    def generate_hierarchical_data(self, num_root_objects: int = 3, max_depth: int = 4, 
                                 max_children_per_node: int = 5) -> List[Dict]:
        """
        Generate hierarchical data with relationships.
        
        Args:
            num_root_objects: Number of root-level objects
            max_depth: Maximum depth of hierarchy
            max_children_per_node: Maximum children per parent
            
        Returns:
            List of dictionaries containing the generated data
        """
        all_records = []
        
        # Create root objects (typically datacenters)
        root_objects = []
        for _ in range(num_root_objects):
            root_record = self.create_base_record('datacenter')
            root_objects.append(root_record)
            all_records.append(root_record)
        
        # Generate hierarchical structure
        self._generate_children_recursive(root_objects, all_records, max_depth - 1, max_children_per_node)
        
        # Update immediate_children lists
        self._update_immediate_children(all_records)
        
        return all_records
    
    def _generate_children_recursive(self, parent_objects: List[Dict], all_records: List[Dict], 
                                   remaining_depth: int, max_children: int):
        """
        Recursively generate children for parent objects.
        
        Args:
            parent_objects: List of parent objects to generate children for
            all_records: List to store all generated records
            remaining_depth: Remaining depth for recursion
            max_children: Maximum children per parent
        """
        if remaining_depth <= 0:
            return
        
        next_level_objects = []
        
        for parent in parent_objects:
            parent_type = parent['object_type']
            
            # Check if this object type can have children
            if not self.object_types[parent_type]['can_have_children']:
                continue
            
            # Determine number of children (0 to max_children)
            num_children = random.randint(0, max_children)
            
            # Get possible child types
            possible_children = self.object_types[parent_type]['typical_children']
            if not possible_children:
                continue
            
            # Generate children
            for _ in range(num_children):
                child_type = random.choice(possible_children)
                child_record = self.create_base_record(child_type, parent['object_id'])
                all_records.append(child_record)
                next_level_objects.append(child_record)
        
        # Recursively generate next level
        if next_level_objects:
            self._generate_children_recursive(next_level_objects, all_records, remaining_depth - 1, max_children)
    
    def _update_immediate_children(self, all_records: List[Dict]):
        """
        Update immediate_children lists for all records.
        
        Args:
            all_records: List of all records to update
        """
        # Create a mapping of parent_id to children
        parent_to_children = {}
        
        for record in all_records:
            parent_id = record['parent_id']
            if parent_id:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(record['object_id'])
        
        # Update immediate_children for each record
        for record in all_records:
            object_id = record['object_id']
            if object_id in parent_to_children:
                record['immediate_children'] = parent_to_children[object_id]
    
    # def generate_flat_data(self, num_records: int = 50) -> List[Dict]:
    #     """
    #     Generate flat data with some random relationships.
        
    #     Args:
    #         num_records: Number of records to generate
            
    #     Returns:
    #         List of dictionaries containing the generated data
    #     """
    #     records = []
        
    #     # Generate all records first
    #     for _ in range(num_records):
    #         object_type = random.choice(list(self.object_types.keys()))
    #         record = self.create_base_record(object_type)
    #         records.append(record)
        
    #     # Randomly assign some parent-child relationships
    #     for i, record in enumerate(records):
    #         # 30% chance of having a parent
    #         if random.random() < 0.3 and i > 0:
    #             # Choose a random earlier record as parent
    #             potential_parents = [r for r in records[:i] 
    #                                if self.object_types[r['object_type']]['can_have_children']]
    #             if potential_parents:
    #                 parent = random.choice(potential_parents)
    #                 record['parent_id'] = parent['object_id']
        
    #     # Update immediate_children
    #     self._update_immediate_children(records)
        
    #     return records
    
    def save_to_json(self, data: List[Dict], filename: str = "generated_data.json"):
        """
        Save generated data to JSON file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")
    
    def print_hierarchy(self, data: List[Dict]):
        """
        Print the hierarchical structure of the data.
        
        Args:
            data: List of dictionaries to print
        """
        # Find root objects (no parent)
        root_objects = [record for record in data if record['parent_id'] is None]
        
        print("Hierarchical Structure:")
        print("=" * 50)
        
        for root in root_objects:
            self._print_object_recursive(root, data, 0)
    
    def _print_object_recursive(self, obj: Dict, all_data: List[Dict], depth: int):
        """
        Recursively print object hierarchy.
        
        Args:
            obj: Current object to print
            all_data: All data records
            depth: Current depth for indentation
        """
        indent = "  " * depth
        print(f"{indent}{obj['object_type']} ({obj['object_id'][:8]}...) - {obj['status']} - {obj['percent_utilized']}%")
        
        # Print children
        children = [record for record in all_data if record['parent_id'] == obj['object_id']]
        for child in children:
            self._print_object_recursive(child, all_data, depth + 1)


# Example usage
if __name__ == "__main__":
    # Initialize generator
    generator = HierarchicalDataGenerator(seed=42)  # Use seed for reproducible results
    
    # Generate hierarchical data
    print("Generating hierarchical data...")
    hierarchical_data = generator.generate_hierarchical_data(
        num_root_objects=10,
        max_depth=5,
        max_children_per_node=5
    )
    
    print(f"Generated {len(hierarchical_data)} records")
    
    # Print first few records
    print("\nFirst 3 records:")
    for i, record in enumerate(hierarchical_data[:3]):
        print(f"Record {i+1}:")
        for key, value in record.items():
            print(f"  {key}: {value}")
        print()
    
    # Print hierarchy
    generator.print_hierarchy(hierarchical_data)
    
    # Save to JSON
    generator.save_to_json(hierarchical_data, "hierarchical_data.json")
    print("==========================")
    print(f"Data generation complete. {len(hierarchical_data)} records saved to 'hierarchical_data.json'.")