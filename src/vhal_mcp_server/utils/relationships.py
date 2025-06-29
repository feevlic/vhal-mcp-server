from typing import Optional, Dict, List
from ..models import (
    VhalCategory, PropertyRelationship, PropertyImplementationStep, 
    PropertyEcosystem
)
from ..core.database import VhalPropertyDatabase


class VhalPropertyRelationshipAnalyzer:
    """Analyzes relationships between vHAL properties and provides implementation guidance."""
    
    # Define property relationships and dependencies
    PROPERTY_RELATIONSHIPS = {
        # SEAT Properties Ecosystem
        "SEAT_MEMORY": {
            "core_properties": ["SEAT_MEMORY_SELECT", "SEAT_MEMORY_SET"],
            "dependent_properties": [
                "SEAT_FORE_AFT_POS", "SEAT_BACKREST_ANGLE_1_POS", "SEAT_HEIGHT_POS",
                "SEAT_TILT_POS", "SEAT_LUMBAR_FORE_AFT_POS", "SEAT_HEADREST_HEIGHT_POS"
            ],
            "optional_properties": [
                "SEAT_BELT_HEIGHT_POS", "SEAT_DEPTH_POS", "SEAT_LUMBAR_SIDE_SUPPORT_POS",
                "SEAT_HEADREST_ANGLE_POS", "SEAT_HEADREST_FORE_AFT_POS"
            ]
        },
        "SEAT_POSITION": {
            "core_properties": ["SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS", "SEAT_BACKREST_ANGLE_1_POS"],
            "movement_properties": ["SEAT_FORE_AFT_MOVE", "SEAT_HEIGHT_MOVE", "SEAT_BACKREST_ANGLE_1_MOVE"],
            "advanced_properties": [
                "SEAT_TILT_POS", "SEAT_TILT_MOVE", "SEAT_DEPTH_POS", "SEAT_DEPTH_MOVE",
                "SEAT_BACKREST_ANGLE_2_POS", "SEAT_BACKREST_ANGLE_2_MOVE"
            ]
        },
        "SEAT_LUMBAR": {
            "core_properties": ["SEAT_LUMBAR_FORE_AFT_POS", "SEAT_LUMBAR_FORE_AFT_MOVE"],
            "related_properties": ["SEAT_LUMBAR_SIDE_SUPPORT_POS", "SEAT_LUMBAR_SIDE_SUPPORT_MOVE"],
            "dependent_on": ["SEAT_FORE_AFT_POS", "SEAT_BACKREST_ANGLE_1_POS"]
        },
        "SEAT_HEADREST": {
            "core_properties": ["SEAT_HEADREST_HEIGHT_POS", "SEAT_HEADREST_HEIGHT_MOVE"],
            "optional_properties": [
                "SEAT_HEADREST_ANGLE_POS", "SEAT_HEADREST_ANGLE_MOVE",
                "SEAT_HEADREST_FORE_AFT_POS", "SEAT_HEADREST_FORE_AFT_MOVE"
            ],
            "dependent_on": ["SEAT_HEIGHT_POS", "SEAT_BACKREST_ANGLE_1_POS"]
        },
        "SEAT_BELT": {
            "core_properties": ["SEAT_BELT_BUCKLED"],
            "optional_properties": ["SEAT_BELT_HEIGHT_POS", "SEAT_BELT_HEIGHT_MOVE"],
            "safety_critical": True
        },
        
        # HVAC Properties Ecosystem
        "HVAC_BASIC": {
            "core_properties": ["HVAC_POWER_ON", "HVAC_TEMPERATURE_SET", "HVAC_FAN_SPEED"],
            "dependent_properties": ["HVAC_TEMPERATURE_CURRENT", "HVAC_ACTUAL_FAN_SPEED_RPM"]
        },
        "HVAC_AIRFLOW": {
            "core_properties": ["HVAC_FAN_SPEED", "HVAC_FAN_DIRECTION"],
            "related_properties": ["HVAC_FAN_DIRECTION_AVAILABLE", "HVAC_ACTUAL_FAN_SPEED_RPM"],
            "dependent_on": ["HVAC_POWER_ON"]
        },
        "HVAC_TEMPERATURE": {
            "core_properties": ["HVAC_TEMPERATURE_SET", "HVAC_TEMPERATURE_CURRENT"],
            "related_properties": ["HVAC_TEMPERATURE_DISPLAY_UNITS"],
            "dependent_on": ["HVAC_POWER_ON"]
        },
        "HVAC_AC": {
            "core_properties": ["HVAC_AC_ON"],
            "related_properties": ["HVAC_MAX_AC_ON", "HVAC_AUTO_ON"],
            "dependent_on": ["HVAC_POWER_ON", "HVAC_FAN_SPEED"]
        },
        "HVAC_DEFROST": {
            "core_properties": ["HVAC_DEFROSTER"],
            "related_properties": ["HVAC_MAX_DEFROST_ON"],
            "dependent_on": ["HVAC_POWER_ON", "HVAC_FAN_SPEED"]
        },
        "HVAC_RECIRCULATION": {
            "core_properties": ["HVAC_RECIRC_ON"],
            "related_properties": ["HVAC_AUTO_RECIRC_ON"],
            "dependent_on": ["HVAC_POWER_ON"]
        },
        "HVAC_HEATED_SURFACES": {
            "core_properties": ["HVAC_SEAT_TEMPERATURE"],
            "optional_properties": ["HVAC_STEERING_WHEEL_HEAT", "HVAC_SIDE_MIRROR_HEAT"],
            "related_properties": ["HVAC_SEAT_VENTILATION"]
        }
    }
    
    IMPLEMENTATION_PATTERNS = {
        "SEAT_MEMORY": [
            PropertyImplementationStep(
                1, "Implement Basic Position Properties",
                ["SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS", "SEAT_BACKREST_ANGLE_1_POS"],
                "Start with fundamental seat positioning that all memory systems require.",
                [],
                ["Ensure proper area mapping for multi-seat vehicles", "Validate position ranges"]
            ),
            PropertyImplementationStep(
                2, "Add Movement Control",
                ["SEAT_FORE_AFT_MOVE", "SEAT_HEIGHT_MOVE", "SEAT_BACKREST_ANGLE_1_MOVE"],
                "Implement movement commands that correspond to position properties.",
                ["SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS", "SEAT_BACKREST_ANGLE_1_POS"],
                ["Implement proper bounds checking", "Handle movement conflicts"]
            ),
            PropertyImplementationStep(
                3, "Implement Memory Core",
                ["SEAT_MEMORY_SELECT", "SEAT_MEMORY_SET"],
                "Add memory selection and storage functionality.",
                ["SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS", "SEAT_BACKREST_ANGLE_1_POS"],
                ["Design memory storage format", "Handle user authentication", "Implement recall sequences"]
            ),
            PropertyImplementationStep(
                4, "Add Advanced Features",
                ["SEAT_TILT_POS", "SEAT_LUMBAR_FORE_AFT_POS", "SEAT_HEADREST_HEIGHT_POS"],
                "Extend with advanced positioning features as needed.",
                ["SEAT_MEMORY_SELECT", "SEAT_MEMORY_SET"],
                ["Consider vehicle-specific capabilities", "Maintain backward compatibility"]
            )
        ],
        
        "HVAC_BASIC": [
            PropertyImplementationStep(
                1, "Implement Power Control",
                ["HVAC_POWER_ON"],
                "Start with basic HVAC system power control.",
                [],
                ["Handle system startup sequences", "Manage power dependencies"]
            ),
            PropertyImplementationStep(
                2, "Add Core Climate Control",
                ["HVAC_TEMPERATURE_SET", "HVAC_FAN_SPEED"],
                "Implement basic temperature and fan speed control.",
                ["HVAC_POWER_ON"],
                ["Validate temperature ranges", "Handle fan speed curves"]
            ),
            PropertyImplementationStep(
                3, "Add Feedback Properties",
                ["HVAC_TEMPERATURE_CURRENT", "HVAC_ACTUAL_FAN_SPEED_RPM"],
                "Provide current state feedback to applications.",
                ["HVAC_TEMPERATURE_SET", "HVAC_FAN_SPEED"],
                ["Implement sensor integration", "Handle update frequencies"]
            ),
            PropertyImplementationStep(
                4, "Extend with Advanced Features",
                ["HVAC_FAN_DIRECTION", "HVAC_AC_ON", "HVAC_AUTO_ON"],
                "Add advanced HVAC features and automation.",
                ["HVAC_TEMPERATURE_SET", "HVAC_FAN_SPEED"],
                ["Consider climate zone management", "Implement auto mode logic"]
            )
        ]
    }
    
    @classmethod
    def find_property_ecosystem(cls, property_input: str) -> Optional[str]:
        """Find which ecosystem a property belongs to."""
        property_upper = property_input.upper()
        
        # Direct property name match
        for ecosystem, config in cls.PROPERTY_RELATIONSHIPS.items():
            for prop_list in config.values():
                if isinstance(prop_list, list) and property_upper in prop_list:
                    return ecosystem
                elif isinstance(prop_list, str) and property_upper == prop_list:
                    return ecosystem
        
        # Partial name matching
        for ecosystem in cls.PROPERTY_RELATIONSHIPS.keys():
            if any(keyword in property_upper for keyword in ecosystem.split('_')):
                return ecosystem
        
        # Category-based matching
        if "SEAT" in property_upper:
            return "SEAT_POSITION"  # Default seat ecosystem
        elif "HVAC" in property_upper:
            return "HVAC_BASIC"  # Default HVAC ecosystem
            
        return None
    
    @classmethod
    def analyze_property_relationships(cls, property_input: str) -> PropertyEcosystem:
        """Analyze relationships for a given property or category."""
        ecosystem_key = cls.find_property_ecosystem(property_input)
        
        if not ecosystem_key:
            # Create a minimal ecosystem for unknown properties
            return PropertyEcosystem(
                primary_property=property_input,
                category=VhalCategory.GENERAL,
                related_properties=[],
                implementation_steps=[],
                dependencies={},
                usage_notes=["Property not found in known ecosystems. Consider checking property name or implementing as custom property."]
            )
        
        config = cls.PROPERTY_RELATIONSHIPS[ecosystem_key]
        category = VhalCategory.SEAT if "SEAT" in ecosystem_key else VhalCategory.HVAC
        
        # Build relationships
        relationships = []
        dependencies = {}
        
        for rel_type, properties in config.items():
            if isinstance(properties, list):
                for prop in properties:
                    if rel_type == "dependent_on":
                        dependencies[property_input] = properties
                    else:
                        relationships.append(PropertyRelationship(
                            property_name=prop,
                            relationship_type=rel_type,
                            description=cls._get_relationship_description(rel_type, prop),
                            priority=cls._get_relationship_priority(rel_type)
                        ))
        
        # Get implementation steps
        implementation_steps = cls.IMPLEMENTATION_PATTERNS.get(ecosystem_key, [])
        
        # Generate usage notes
        usage_notes = cls._generate_usage_notes(ecosystem_key, config)
        
        return PropertyEcosystem(
            primary_property=property_input,
            category=category,
            related_properties=relationships,
            implementation_steps=implementation_steps,
            dependencies=dependencies,
            usage_notes=usage_notes
        )
    
    @staticmethod
    def _get_relationship_description(rel_type: str, prop: str) -> str:
        """Generate description for property relationships."""
        descriptions = {
            "core_properties": f"Essential property: {prop} is fundamental to this feature",
            "dependent_properties": f"Dependent property: {prop} relies on core properties",
            "optional_properties": f"Optional property: {prop} provides additional functionality",
            "movement_properties": f"Movement control: {prop} controls dynamic positioning",
            "advanced_properties": f"Advanced feature: {prop} provides enhanced capabilities",
            "related_properties": f"Related property: {prop} works together with core features",
            "safety_critical": f"Safety critical: {prop} has safety implications"
        }
        return descriptions.get(rel_type, f"Related property: {prop}")
    
    @staticmethod
    def _get_relationship_priority(rel_type: str) -> int:
        """Get priority for relationship types."""
        priorities = {
            "core_properties": 1,
            "dependent_properties": 2,
            "movement_properties": 2,
            "related_properties": 3,
            "optional_properties": 4,
            "advanced_properties": 4,
            "safety_critical": 1
        }
        return priorities.get(rel_type, 3)
    
    @staticmethod
    def _generate_usage_notes(ecosystem_key: str, config: Dict) -> List[str]:
        """Generate usage notes for the ecosystem."""
        notes = []
        
        if "SEAT" in ecosystem_key:
            notes.extend([
                "Seat properties typically use VehicleAreaSeat for area mapping",
                "Position properties usually have corresponding movement properties",
                "Memory features require careful sequencing during recall operations",
                "Consider user authentication for memory set operations"
            ])
            
            if "MEMORY" in ecosystem_key:
                notes.append("Memory systems should store all adjustable position properties")
            if "BELT" in ecosystem_key:
                notes.append("Safety critical: Belt properties may have regulatory requirements")
                
        elif "HVAC" in ecosystem_key:
            notes.extend([
                "HVAC properties often use VehicleAreaSeat or VehicleAreaGlobal for area mapping",
                "Temperature properties should support both Celsius and Fahrenheit",
                "Fan properties need to handle multiple speed ranges",
                "Auto mode features require integration with climate sensors"
            ])
            
            if "HEATED" in ecosystem_key:
                notes.append("Heated surface properties may have safety timeouts")
                
        if config.get("safety_critical"):
            notes.append("Safety Critical: This ecosystem includes safety-critical properties")
            
        return notes
