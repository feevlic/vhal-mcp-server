"""Database and lookup functionality for vHAL properties.

This module contains property databases and Android source code lookup utilities.
Optimized with caching and efficient search algorithms.
"""
from urllib.parse import quote
from typing import List, Dict, Set
from functools import lru_cache
from models import VhalProperty, VhalCategory, SearchResult


class VhalPropertyDatabase:
    """Optimized database of vHAL properties with efficient search indexing."""
    
    PROPERTIES = {
        VhalCategory.SEAT: {
            "SEAT_MEMORY_SELECT": "0x0B56",
            "SEAT_MEMORY_SET": "0x0B57",
            "SEAT_BELT_BUCKLED": "0x0B58",
            "SEAT_BELT_HEIGHT_POS": "0x0B59",
            "SEAT_BELT_HEIGHT_MOVE": "0x0B5A",
            "SEAT_FORE_AFT_POS": "0x0B5B",
            "SEAT_FORE_AFT_MOVE": "0x0B5C",
            "SEAT_BACKREST_ANGLE_1_POS": "0x0B5D",
            "SEAT_BACKREST_ANGLE_1_MOVE": "0x0B5E",
            "SEAT_BACKREST_ANGLE_2_POS": "0x0B5F",
            "SEAT_BACKREST_ANGLE_2_MOVE": "0x0B60",
            "SEAT_HEIGHT_POS": "0x0B61",
            "SEAT_HEIGHT_MOVE": "0x0B62",
            "SEAT_DEPTH_POS": "0x0B63",
            "SEAT_DEPTH_MOVE": "0x0B64",
            "SEAT_TILT_POS": "0x0B65",
            "SEAT_TILT_MOVE": "0x0B66",
            "SEAT_LUMBAR_FORE_AFT_POS": "0x0B67",
            "SEAT_LUMBAR_FORE_AFT_MOVE": "0x0B68",
            "SEAT_LUMBAR_SIDE_SUPPORT_POS": "0x0B69",
            "SEAT_LUMBAR_SIDE_SUPPORT_MOVE": "0x0B6A",
            "SEAT_HEADREST_HEIGHT_POS": "0x0B6B",
            "SEAT_HEADREST_HEIGHT_MOVE": "0x0B6C",
            "SEAT_HEADREST_ANGLE_POS": "0x0B6D",
            "SEAT_HEADREST_ANGLE_MOVE": "0x0B6E",
            "SEAT_HEADREST_FORE_AFT_POS": "0x0B6F",
            "SEAT_HEADREST_FORE_AFT_MOVE": "0x0B70"
        },
        VhalCategory.HVAC: {
            "HVAC_FAN_SPEED": "0x0A01",
            "HVAC_FAN_DIRECTION": "0x0A02",
            "HVAC_TEMPERATURE_CURRENT": "0x0A03",
            "HVAC_TEMPERATURE_SET": "0x0A04",
            "HVAC_DEFROSTER": "0x0A05",
            "HVAC_AC_ON": "0x0A06",
            "HVAC_MAX_AC_ON": "0x0A07",
            "HVAC_MAX_DEFROST_ON": "0x0A08",
            "HVAC_RECIRC_ON": "0x0A09",
            "HVAC_DUAL_ON": "0x0A0A",
            "HVAC_AUTO_ON": "0x0A0B",
            "HVAC_SEAT_TEMPERATURE": "0x0A0C",
            "HVAC_SIDE_MIRROR_HEAT": "0x0A0D",
            "HVAC_STEERING_WHEEL_HEAT": "0x0A0E",
            "HVAC_TEMPERATURE_DISPLAY_UNITS": "0x0A0F",
            "HVAC_ACTUAL_FAN_SPEED_RPM": "0x0A10",
            "HVAC_POWER_ON": "0x0A11",
            "HVAC_FAN_DIRECTION_AVAILABLE": "0x0A12",
            "HVAC_AUTO_RECIRC_ON": "0x0A13",
            "HVAC_SEAT_VENTILATION": "0x0A14"
        }
    }
    
    # Build search indexes for faster lookups
    _keyword_index: Dict[str, Set[str]] = None
    _category_index: Dict[VhalCategory, List[VhalProperty]] = None
    _exact_match_index: Dict[str, VhalProperty] = None
    _partial_match_index: Dict[str, List[VhalProperty]] = None
    
    @classmethod
    def _build_indexes(cls) -> None:
        """Build comprehensive search indexes for faster property lookups."""
        if cls._keyword_index is not None:
            return  # Already built
        
        cls._keyword_index = {}
        cls._category_index = {}
        cls._exact_match_index = {}
        cls._partial_match_index = {}
        
        for category, properties in cls.PROPERTIES.items():
            cls._category_index[category] = []
            
            for name, prop_id in properties.items():
                prop = VhalProperty(name, prop_id, category)
                cls._category_index[category].append(prop)
                
                # Build exact match index (fastest lookup)
                cls._exact_match_index[name] = prop
                cls._exact_match_index[name.lower()] = prop
                
                # Index by keywords (parts of property name)
                keywords = name.split('_')
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword not in cls._keyword_index:
                        cls._keyword_index[keyword] = set()
                    if keyword_lower not in cls._keyword_index:
                        cls._keyword_index[keyword_lower] = set()
                    cls._keyword_index[keyword].add(name)
                    cls._keyword_index[keyword_lower].add(name)
                    
                    # Build partial match index for substrings
                    if keyword_lower not in cls._partial_match_index:
                        cls._partial_match_index[keyword_lower] = []
                    cls._partial_match_index[keyword_lower].append(prop)
                
                # Also index the full name for partial matching
                name_lower = name.lower()
                if name_lower not in cls._partial_match_index:
                    cls._partial_match_index[name_lower] = []
                cls._partial_match_index[name_lower].append(prop)
    
    @classmethod
    @lru_cache(maxsize=256)  # Increased cache size for better hit rate
    def search_properties(cls, keyword: str) -> List[VhalProperty]:
        """Highly optimized search for properties matching a keyword."""
        cls._build_indexes()  # Ensure indexes are built
        
        if not keyword.strip():
            return []
        
        keyword_upper = keyword.upper()
        keyword_lower = keyword.lower()
        matches = []
        matched_names = set()
        
        # 1. Ultra-fast exact match check first
        if keyword_upper in cls._exact_match_index:
            return [cls._exact_match_index[keyword_upper]]
        if keyword_lower in cls._exact_match_index:
            return [cls._exact_match_index[keyword_lower]]
        
        # 2. Fast category-based search
        for category in cls.PROPERTIES:
            if keyword_upper in category.value:
                matches.extend(cls._category_index[category])
                matched_names.update(prop.name for prop in cls._category_index[category])
                # If we found category matches, return early for speed
                if matches:
                    return matches
        
        # 3. Fast keyword-based search using pre-built indexes
        search_terms = keyword_lower.split()
        for term in search_terms:
            if term in cls._keyword_index:
                for prop_name in cls._keyword_index[term]:
                    if prop_name not in matched_names:
                        # Use exact match index for O(1) lookup
                        if prop_name in cls._exact_match_index:
                            matches.append(cls._exact_match_index[prop_name])
                            matched_names.add(prop_name)
        
        # 4. Partial match search using pre-built index
        if not matches:
            for term in search_terms:
                if term in cls._partial_match_index:
                    for prop in cls._partial_match_index[term]:
                        if prop.name not in matched_names:
                            matches.append(prop)
                            matched_names.add(prop.name)
        
        # 5. Fallback: substring matching (only if nothing found)
        if not matches:
            for category, properties in cls.PROPERTIES.items():
                for name, prop_id in properties.items():
                    if (keyword_upper in name or keyword_lower in name.lower() or 
                        any(term in name.lower() for term in search_terms)):
                        if name not in matched_names:
                            matches.append(VhalProperty(name, prop_id, category))
                            matched_names.add(name)
        
        # Sort by relevance: exact > starts_with > contains
        exact_matches = [m for m in matches if keyword_upper == m.name]
        starts_with_matches = [m for m in matches if m.name.startswith(keyword_upper) and keyword_upper != m.name]
        contains_matches = [m for m in matches if keyword_upper in m.name and not m.name.startswith(keyword_upper)]
        other_matches = [m for m in matches if keyword_upper not in m.name]
        
        return exact_matches + starts_with_matches + contains_matches + other_matches
    
    @classmethod
    def get_properties_by_category(cls, category: VhalCategory) -> List[VhalProperty]:
        """Get all properties for a specific category."""
        cls._build_indexes()
        return cls._category_index.get(category, [])
    
    @classmethod
    @lru_cache(maxsize=64)  # Cache exact lookups
    def get_property_by_name(cls, name: str) -> VhalProperty:
        """Get a specific property by exact name match - optimized with direct index lookup."""
        cls._build_indexes()  # Ensure indexes are built
        
        # Use exact match index for O(1) lookup
        name_upper = name.upper()
        if name_upper in cls._exact_match_index:
            return cls._exact_match_index[name_upper]
        
        # Fallback to original method if not in index
        for category, properties in cls.PROPERTIES.items():
            if name_upper in properties:
                return VhalProperty(name_upper, properties[name_upper], category)
        return None


class AndroidSourceLookup:
    """Utility for looking up Android source code locations."""
    
    AIDL_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl"
    HAL_BASE_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/"
    REFERENCE_IMPL_URL = "https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/"
    
    @staticmethod
    def generate_search_url(keyword: str) -> str:
        """Generate Android Code Search URL for a keyword."""
        return f"https://cs.android.com/search?q={keyword}%20automotive%20vehicle"
    
    @classmethod
    def get_source_locations(cls) -> List[SearchResult]:
        """Get predefined source code locations."""
        return [
            SearchResult(
                url=cls.AIDL_URL,
                description="Vehicle Property AIDL Definition"
            ),
            SearchResult(
                url=cls.HAL_BASE_URL,
                description="HAL Implementation Directory"
            ),
            SearchResult(
                url=cls.REFERENCE_IMPL_URL,
                description="Reference Implementation"
            )
        ]
