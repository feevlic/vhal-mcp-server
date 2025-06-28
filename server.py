from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import base64


class VhalCategory(Enum):
    SEAT = "SEAT"
    HVAC = "HVAC"
    GENERAL = "GENERAL"


@dataclass
class VhalProperty:
    name: str
    id: str
    category: VhalCategory
    description: str = ""


@dataclass
class SearchResult:
    url: str
    description: str
    content: Optional[str] = None


class VhalDocumentationScraper:
    BASE_URL = "https://source.android.com/docs/automotive/vhal"
    CONTENT_LIMIT = 5000
    TIMEOUT = 10
    
    KNOWN_PAGES = [
        "https://source.android.com/docs/automotive/vhal",
        "https://source.android.com/docs/automotive/vhal/properties", 
        "https://source.android.com/docs/automotive/vhal/vehicle-areas",
        "https://source.android.com/docs/automotive/vhal/diagnostics",
        "https://source.android.com/docs/automotive/vhal/hal-implementation"
    ]
    
    @staticmethod
    def scrape_page(url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=VhalDocumentationScraper.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            for element in soup(["script", "style"]):
                element.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            return clean_text[:VhalDocumentationScraper.CONTENT_LIMIT]
        except Exception:
            return None
    
    @staticmethod
    def discover_pages() -> List[str]:
        try:
            response = requests.get(VhalDocumentationScraper.BASE_URL, 
                                  timeout=VhalDocumentationScraper.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            discovered_links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('vhal' in href.lower() or 'vehicle' in href.lower()):
                    full_url = urljoin(VhalDocumentationScraper.BASE_URL, href)
                    if full_url.startswith('https://source.android.com/docs/automotive'):
                        discovered_links.append(full_url)
            
            all_links = list(set(discovered_links + VhalDocumentationScraper.KNOWN_PAGES))
            return all_links[:10]
        except Exception:
            return VhalDocumentationScraper.KNOWN_PAGES


class VhalPropertyDatabase:
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
    
    @classmethod
    def search_properties(cls, keyword: str) -> List[VhalProperty]:
        keyword_upper = keyword.upper()
        matches = []
        
        for category, properties in cls.PROPERTIES.items():
            if keyword_upper in category.value:
                for name, prop_id in properties.items():
                    matches.append(VhalProperty(name, prop_id, category))
                continue
            
            for name, prop_id in properties.items():
                if keyword_upper in name or any(kw in name for kw in keyword_upper.split()):
                    matches.append(VhalProperty(name, prop_id, category))
        
        return matches


class AndroidSourceLookup:
    AIDL_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl"
    HAL_BASE_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/"
    REFERENCE_IMPL_URL = "https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/"
    
    @staticmethod
    def generate_search_url(keyword: str) -> str:
        return f"https://cs.android.com/search?q={keyword}%20automotive%20vehicle"
    
    @classmethod
    def get_source_locations(cls) -> List[SearchResult]:
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


@dataclass
class SourceCodeFile:
    filename: str
    path: str
    url: str
    content: str
    language: str
    purpose: str
    line_count: int


@dataclass 
class VhalImplementationAnalysis:
    property_name: str
    property_id: str
    source_files: List[SourceCodeFile]
    implementation_details: Dict[str, str]
    dependencies: List[str]
    usage_examples: List[str]
    related_files: List[str]
    documentation_links: List[str]


class AndroidSourceCodeAnalyzer:
    """Analyzes Android source code to show vHAL property implementations."""
    
    # Android Googlesource URLs for different components
    # Multiple URL options in case repository structure changes
    GOOGLESOURCE_URLS = {
        "vehicle_property_aidl": [
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl?format=TEXT"
        ],
        "vehicle_area_aidl": [
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleArea.aidl?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleArea.aidl?format=TEXT"
        ],
        "vehicle_property_type_aidl": [
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehiclePropertyType.aidl?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehiclePropertyType.aidl?format=TEXT"
        ],
        "default_hal_impl": [
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/impl/default_config/config/DefaultProperties.cpp?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/automotive/vehicle/aidl/impl/default_config/config/DefaultProperties.cpp?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/impl/vhal/config/DefaultConfig.h?format=TEXT"
        ],
        "hal_interface": [
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/IVehicle.aidl?format=TEXT",
            "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/master/automotive/vehicle/aidl/android/hardware/automotive/vehicle/IVehicle.aidl?format=TEXT"
        ],
        "emulator_hal": [
            "https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/vhal/VehicleHalServer.cpp?format=TEXT",
            "https://android.googlesource.com/device/generic/car/+/refs/heads/master/emulator/vhal/VehicleHalServer.cpp?format=TEXT"
        ],
        "emulator_config": [
            "https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/vhal/DefaultConfig.h?format=TEXT",
            "https://android.googlesource.com/device/generic/car/+/refs/heads/master/emulator/vhal/DefaultConfig.h?format=TEXT"
        ]
    }
    
    TIMEOUT = 15
    
    @classmethod
    def fetch_source_file(cls, file_key: str, description: str) -> Optional[SourceCodeFile]:
        """Fetch a source file from Android Googlesource with fallback URLs."""
        urls = cls.GOOGLESOURCE_URLS.get(file_key)
        if not urls:
            return None
            
        # Try each URL until one works
        last_error = None
        for url in urls:
            try:
                response = requests.get(url, timeout=cls.TIMEOUT)
                response.raise_for_status()
                
                # Decode base64 content from Googlesource
                try:
                    decoded_content = base64.b64decode(response.text).decode('utf-8')
                except:
                    decoded_content = response.text
                
                # Extract filename from URL
                filename = url.split('/')[-1].split('?')[0]
                
                # Determine language based on file extension
                language = "cpp" if filename.endswith(('.cpp', '.cc', '.h')) else "aidl" if filename.endswith('.aidl') else "text"
                
                # Create display URL (without format=TEXT)
                display_url = url.replace('?format=TEXT', '')
                
                return SourceCodeFile(
                    filename=filename,
                    path=display_url.split('+')[0] + '+' + display_url.split('+')[1],
                    url=display_url,
                    content=decoded_content,
                    language=language,
                    purpose=description,
                    line_count=len(decoded_content.splitlines())
                )
                
            except Exception as e:
                last_error = e
                continue  # Try next URL
        
        # If all URLs failed, return error information
        return SourceCodeFile(
            filename=f"Error fetching {file_key}",
            path="N/A",
            url=str(urls[0]) if urls else "N/A",
            content=f"Error fetching file from all {len(urls)} URLs. Last error: {str(last_error)}",
            language="error",
            purpose=description,
            line_count=0
        )
    
    @classmethod
    def analyze_property_implementation(cls, property_name: str) -> VhalImplementationAnalysis:
        """Analyze how a specific vHAL property is implemented in Android source code."""
        
        # Get property ID from database
        property_id = "Unknown"
        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
            if property_name.upper() in properties:
                property_id = properties[property_name.upper()]
                break
        
        # Fetch key source files
        source_files = []
        
        # Core AIDL definitions
        vehicle_property_file = cls.fetch_source_file("vehicle_property_aidl", "Main Vehicle Property AIDL definitions")
        if vehicle_property_file:
            source_files.append(vehicle_property_file)
            
        vehicle_area_file = cls.fetch_source_file("vehicle_area_aidl", "Vehicle Area definitions for property mapping")
        if vehicle_area_file:
            source_files.append(vehicle_area_file)
            
        # HAL implementation files
        default_hal_file = cls.fetch_source_file("default_hal_impl", "Default HAL implementation with property configurations")
        if default_hal_file:
            source_files.append(default_hal_file)
            
        hal_interface_file = cls.fetch_source_file("hal_interface", "Main vHAL interface definition")
        if hal_interface_file:
            source_files.append(hal_interface_file)
            
        # Emulator implementation (for testing/reference)
        emulator_hal_file = cls.fetch_source_file("emulator_hal", "Emulator HAL server implementation")
        if emulator_hal_file:
            source_files.append(emulator_hal_file)
            
        emulator_config_file = cls.fetch_source_file("emulator_config", "Emulator default configuration")
        if emulator_config_file:
            source_files.append(emulator_config_file)
        
        # Analyze implementation details
        implementation_details = cls._extract_implementation_details(property_name, property_id, source_files)
        
        # Find dependencies and related files
        dependencies = cls._find_dependencies(property_name, source_files)
        
        # Generate usage examples
        usage_examples = cls._generate_usage_examples(property_name, property_id, implementation_details)
        
        # Related files and documentation
        related_files = cls._get_related_files(property_name)
        documentation_links = cls._get_documentation_links(property_name)
        
        return VhalImplementationAnalysis(
            property_name=property_name,
            property_id=property_id,
            source_files=source_files,
            implementation_details=implementation_details,
            dependencies=dependencies,
            usage_examples=usage_examples,
            related_files=related_files,
            documentation_links=documentation_links
        )
    
    @staticmethod
    def _extract_implementation_details(property_name: str, property_id: str, source_files: List[SourceCodeFile]) -> Dict[str, str]:
        """Extract implementation details from source files."""
        details = {}
        
        for file in source_files:
            if not file.content or file.language == "error":
                continue
                
            content_lines = file.content.splitlines()
            
            # Look for property definition
            for i, line in enumerate(content_lines):
                if property_name.upper() in line.upper() or (property_id != "Unknown" and property_id in line):
                    # Extract context around the property definition
                    start_line = max(0, i - 3)
                    end_line = min(len(content_lines), i + 4)
                    context = "\n".join(f"{j+1:4d}: {content_lines[j]}" for j in range(start_line, end_line))
                    
                    details[f"{file.filename}_definition"] = f"Property definition in {file.filename}:\n```{file.language}\n{context}\n```"
                    break
            
            # Look for configuration details
            if "config" in file.filename.lower() or "default" in file.filename.lower():
                config_patterns = ["VehicleAreaConfig", "configArray", "VehiclePropertyAccess", "VehiclePropertyChangeMode"]
                for pattern in config_patterns:
                    if pattern in file.content:
                        details[f"{file.filename}_config"] = f"Configuration found in {file.filename} (contains {pattern})"
        
        return details
    
    @staticmethod
    def _find_dependencies(property_name: str, source_files: List[SourceCodeFile]) -> List[str]:
        """Find dependencies for the property."""
        dependencies = set()
        
        # Common dependencies based on property category
        if "SEAT" in property_name.upper():
            dependencies.update(["VehicleAreaSeat", "VehiclePropertyAccess.READ_WRITE", "VehiclePropertyChangeMode.ON_CHANGE"])
        elif "HVAC" in property_name.upper():
            dependencies.update(["VehicleAreaSeat or VehicleAreaGlobal", "VehiclePropertyAccess.READ_WRITE", "VehiclePropertyChangeMode.ON_CHANGE"])
        
        # Look for actual dependencies in source files
        for file in source_files:
            if file.content and property_name.upper() in file.content.upper():
                if "VehicleArea" in file.content:
                    dependencies.add("VehicleArea definitions")
                if "VehiclePropertyType" in file.content:
                    dependencies.add("VehiclePropertyType definitions")
                if "android.hardware.automotive.vehicle" in file.content:
                    dependencies.add("Vehicle HAL AIDL interface")
        
        return list(dependencies)
    
    @staticmethod
    def _generate_usage_examples(property_name: str, property_id: str, implementation_details: Dict[str, str]) -> List[str]:
        """Generate usage examples for the property."""
        examples = []
        
        # Basic usage example
        examples.append(f"""// Basic property access example
VehiclePropValue propValue;
propValue.prop = {property_id};  // {property_name}
propValue.areaId = VEHICLE_AREA_SEAT_ROW_1_LEFT;  // Example area
// Set or get property value through vHAL interface""")
        
        # Configuration example
        if "SEAT" in property_name.upper():
            examples.append(f"""// Seat property configuration example
VehiclePropConfig config;
config.prop = {property_id};
config.access = VehiclePropertyAccess.READ_WRITE;
config.changeMode = VehiclePropertyChangeMode.ON_CHANGE;
config.areaConfigs = {{/* seat area configurations */}};""")
        elif "HVAC" in property_name.upper():
            examples.append(f"""// HVAC property configuration example
VehiclePropConfig config;
config.prop = {property_id};
config.access = VehiclePropertyAccess.READ_WRITE;
config.changeMode = VehiclePropertyChangeMode.ON_CHANGE;
config.areaConfigs = {{/* climate area configurations */}};""")
        
        return examples
    
    @staticmethod
    def _get_related_files(property_name: str) -> List[str]:
        """Get list of related implementation files."""
        base_files = [
            "VehicleProperty.aidl - Property ID definitions",
            "VehicleArea.aidl - Area type definitions", 
            "VehiclePropertyType.aidl - Data type definitions",
            "IVehicle.aidl - Main HAL interface",
            "DefaultProperties.cpp - Default property configurations"
        ]
        
        category_files = []
        if "SEAT" in property_name.upper():
            category_files = [
                "Seat-specific configuration files",
                "Memory management implementations",
                "Position control algorithms"
            ]
        elif "HVAC" in property_name.upper():
            category_files = [
                "Climate control implementations",
                "Temperature sensor integrations",
                "Fan control algorithms"
            ]
        
        return base_files + category_files
    
    @staticmethod
    def _get_documentation_links(property_name: str) -> List[str]:
        """Get relevant documentation links."""
        return [
            "https://source.android.com/docs/automotive/vhal - Main vHAL documentation",
            "https://source.android.com/docs/automotive/vhal/properties - Property specifications",
            "https://source.android.com/docs/automotive/vhal/vehicle-areas - Area mapping details",
            "https://cs.android.com/search?q=" + quote(property_name + " automotive vehicle") + " - Android Code Search"
        ]


@dataclass
class PropertyRelationship:
    property_name: str
    relationship_type: str
    description: str
    priority: int = 1


@dataclass
class PropertyImplementationStep:
    step_number: int
    title: str
    properties: List[str]
    description: str
    dependencies: List[str] = field(default_factory=list)
    considerations: List[str] = field(default_factory=list)


@dataclass
class PropertyEcosystem:
    primary_property: str
    category: VhalCategory
    related_properties: List[PropertyRelationship]
    implementation_steps: List[PropertyImplementationStep]
    dependencies: Dict[str, List[str]]
    usage_notes: List[str]


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


class VhalSummarizer:
    MAX_SECTIONS = 3
    SECTION_LIMIT = 2000
    SUMMARY_LIMIT = 4000
    
    @staticmethod
    def extract_keywords(question: str) -> List[str]:
        return re.findall(r'\b\w+\b', question.lower())
    
    @staticmethod
    def score_content(content: str, keywords: List[str]) -> int:
        content_lower = content.lower()
        return sum(1 for keyword in keywords if keyword in content_lower)
    
    @classmethod
    def summarize_documentation(cls, question: str, content_sections: List[str]) -> str:
        keywords = cls.extract_keywords(question)
        scored_sections = []
        
        for section in content_sections:
            if not section.strip():
                continue
            score = cls.score_content(section, keywords)
            if score > 0:
                scored_sections.append((score, section[:cls.SECTION_LIMIT]))
        
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_sections:
            fallback = "\n".join(content_sections)[:1500]
            return f"No specific information found for '{question}'. General vHAL overview:\n\n{fallback}..."
        
        summary_parts = [f"vHAL Summary for: '{question}'\n"]
        for _, section in scored_sections[:cls.MAX_SECTIONS]:
            summary_parts.append(section)
            summary_parts.append("\n" + "="*50 + "\n")
        
        summary = "\n".join(summary_parts)
        if len(summary) > cls.SUMMARY_LIMIT:
            summary = summary[:cls.SUMMARY_LIMIT] + "\n\n[Summary truncated]"
        
        return summary


mcp = FastMCP("vHAL MCP Server")


@mcp.tool()
def summarize_vhal(question: str) -> str:
    """Summarize vHAL implementation based on a question.
    
    Args:
        question: Question about vHAL implementation
        
    Returns:
        Summary of relevant vHAL information from Android documentation
    """
    try:
        pages = VhalDocumentationScraper.discover_pages()
        content_sections = []
        
        for page_url in pages:
            content = VhalDocumentationScraper.scrape_page(page_url)
            if content:
                content_sections.append(content)
        
        return VhalSummarizer.summarize_documentation(question, content_sections)
        
    except Exception as e:
        return f"Error generating vHAL summary: {str(e)}"

# Add a tool for looking up Android source code
@mcp.tool()
def lookup_android_source_code(keyword: str, category: str = "vhal") -> str:
    """Lookup Android source code for a given keyword.
    
    Args:
        keyword: Search term (e.g., "SEAT", "HVAC", "vehicle properties")
        category: Category to focus search on (default: "vhal")
        
    Returns:
        Detailed information about the source code location and content
    """
    try:
        property_matches = VhalPropertyDatabase.search_properties(keyword)
        source_locations = AndroidSourceLookup.get_source_locations()
        search_url = AndroidSourceLookup.generate_search_url(keyword)
        
        result_parts = [
            f"Android Source Code Lookup for: '{keyword}'\n",
            "=" * 50
        ]
        
        if property_matches:
            result_parts.append("\n## Vehicle Property Definitions:")
            
            categories = {}
            for prop in property_matches:
                if prop.category not in categories:
                    categories[prop.category] = []
                categories[prop.category].append(prop)
            
            for category, props in categories.items():
                result_parts.append(f"\n### {category.value} Properties:")
                for prop in props:
                    result_parts.append(f"  - {prop.name}: {prop.id}")
        
        result_parts.append("\n## Source Code Locations:")
        for location in source_locations:
            result_parts.append(f"\n### {location.description}:")
            result_parts.append(f"URL: {location.url}")
        
        result_parts.append(f"\n## Search URL:")
        result_parts.append(f"Android Code Search: {search_url}")
        
        if any("SEAT" in prop.name for prop in property_matches):
            result_parts.extend([
                "\n## Seat Property Usage:",
                "- Area Type: VehicleAreaSeat (typically 0x05000000 base)",
                "- Data Type: Usually INT32 for positions, BOOLEAN for states",
                "- Access: Most seat properties are READ_WRITE",
                "- Change Mode: ON_CHANGE for most properties"
            ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error during Android source code lookup: {str(e)}"


@mcp.tool()
def discover_related_properties(property_or_category: str) -> str:
    """Discover related properties, dependencies, and implementation order for vHAL properties.
    
    Args:
        property_or_category: Property name (e.g., "SEAT_MEMORY_SELECT") or category (e.g., "SEAT_MEMORY", "HVAC_BASIC")
        
    Returns:
        Comprehensive analysis of related properties, dependencies, and suggested implementation order
    """
    try:
        ecosystem = VhalPropertyRelationshipAnalyzer.analyze_property_relationships(property_or_category)
        
        result_parts = [
            f"Property Ecosystem Analysis for: '{ecosystem.primary_property}'\n",
            "=" * 70,
            f"\nCategory: {ecosystem.category.value}"
        ]
        
        # Related Properties Section
        if ecosystem.related_properties:
            result_parts.append("\n\nRelated Properties:")
            
            # Group by relationship type and priority
            grouped_props = {}
            for prop in ecosystem.related_properties:
                if prop.relationship_type not in grouped_props:
                    grouped_props[prop.relationship_type] = []
                grouped_props[prop.relationship_type].append(prop)
            
            # Sort relationship types by priority
            priority_order = ["core_properties", "movement_properties", "dependent_properties", 
                            "related_properties", "optional_properties", "advanced_properties"]
            
            for rel_type in priority_order:
                if rel_type in grouped_props:
                    props = sorted(grouped_props[rel_type], key=lambda x: x.priority)
                    result_parts.append(f"\n### {rel_type.replace('_', ' ').title()}:")
                    
                    for prop in props:
                        # Get property ID if available
                        prop_id = ""
                        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
                            if prop.property_name in properties:
                                prop_id = f" ({properties[prop.property_name]})"
                                break
                        
                        result_parts.append(f"  • {prop.property_name}{prop_id}")
                        result_parts.append(f"    {prop.description}")
        
        # Dependencies Section
        if ecosystem.dependencies:
            result_parts.append("\n\nDependencies:")
            for prop, deps in ecosystem.dependencies.items():
                result_parts.append(f"\n• {prop} depends on:")
                for dep in deps:
                    result_parts.append(f"  - {dep}")
        
        # Implementation Steps Section
        if ecosystem.implementation_steps:
            result_parts.append("\n\nSuggested Implementation Order:")
            
            for step in ecosystem.implementation_steps:
                result_parts.append(f"\n### Step {step.step_number}: {step.title}")
                result_parts.append(f"**Description:** {step.description}")
                
                if step.properties:
                    result_parts.append("\n**Properties to implement:**")
                    for prop in step.properties:
                        # Get property ID
                        prop_id = ""
                        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
                            if prop in properties:
                                prop_id = f" ({properties[prop]})"
                                break
                        result_parts.append(f"  • {prop}{prop_id}")
                
                if step.dependencies:
                    result_parts.append("\n**Dependencies:**")
                    for dep in step.dependencies:
                        result_parts.append(f"  • {dep}")
                
                if step.considerations:
                    result_parts.append("\n**Implementation considerations:**")
                    for consideration in step.considerations:
                        result_parts.append(f"  • {consideration}")
                        
                result_parts.append("")  # Add spacing
        
        # Usage Notes Section
        if ecosystem.usage_notes:
            result_parts.append("\nImplementation Notes:")
            for note in ecosystem.usage_notes:
                result_parts.append(f"• {note}")
        
        # Additional Resources Section
        result_parts.extend([
            "\n\nAdditional Resources:",
            "• Use `lookup_android_source_code()` to find implementation examples",
            "• Use `summarize_vhal()` for detailed documentation on specific topics",
            "• Refer to Android vHAL documentation: https://source.android.com/docs/automotive/vhal"
        ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error analyzing property relationships: {str(e)}"


@mcp.tool()
def analyze_vhal_implementation(property_name: str) -> str:
    """Analyze Android source code to show how a vHAL property is implemented, including actual source code, file locations, and usage examples.
    
    Args:
        property_name: The vHAL property name to analyze (e.g., "HVAC_STEERING_WHEEL_HEAT", "SEAT_MEMORY_SELECT")
        
    Returns:
        Comprehensive analysis of the property implementation including source code, dependencies, and usage examples
    """
    try:
        analysis = AndroidSourceCodeAnalyzer.analyze_property_implementation(property_name)
        
        result_parts = [
            f"vHAL Implementation Analysis for: '{analysis.property_name}'\n",
            "=" * 80,
            f"\nProperty ID: {analysis.property_id}"
        ]
        
        # Source Files Section
        if analysis.source_files:
            result_parts.append("\n\nSource Files Analysis:")
            
            for i, file in enumerate(analysis.source_files, 1):
                result_parts.append(f"\n### {i}. {file.filename}")
                result_parts.append(f"**Purpose:** {file.purpose}")
                result_parts.append(f"**Language:** {file.language}")
                result_parts.append(f"**Lines:** {file.line_count}")
                result_parts.append(f"**Path:** {file.path}")
                result_parts.append(f"**URL:** {file.url}")
                
                if file.content and file.language != "error":
                    # Show first 30 lines of code with line numbers
                    lines = file.content.splitlines()[:30]
                    if lines:
                        result_parts.append(f"\n**Source Code Preview:**")
                        result_parts.append(f"```{file.language}")
                        for line_num, line in enumerate(lines, 1):
                            result_parts.append(f"{line_num:4d}: {line}")
                        if len(file.content.splitlines()) > 30:
                            result_parts.append("...")
                            result_parts.append(f"[File continues for {file.line_count - 30} more lines]")
                        result_parts.append("```")
                elif file.language == "error":
                    result_parts.append(f"\n**Error:** {file.content}")
                
                result_parts.append("")  # Add spacing
        
        # Implementation Details Section
        if analysis.implementation_details:
            result_parts.append("\n\nImplementation Details:")
            for detail_key, detail_value in analysis.implementation_details.items():
                result_parts.append(f"\n### {detail_key.replace('_', ' ').title()}")
                result_parts.append(detail_value)
        
        # Dependencies Section
        if analysis.dependencies:
            result_parts.append("\n\nDependencies:")
            for dependency in analysis.dependencies:
                result_parts.append(f"• {dependency}")
        
        # Usage Examples Section
        if analysis.usage_examples:
            result_parts.append("\n\nUsage Examples:")
            for i, example in enumerate(analysis.usage_examples, 1):
                result_parts.append(f"\n### Example {i}:")
                result_parts.append(f"```cpp\n{example}\n```")
        
        # Related Files Section
        if analysis.related_files:
            result_parts.append("\n\nRelated Implementation Files:")
            for related_file in analysis.related_files:
                result_parts.append(f"• {related_file}")
        
        # Documentation Links Section
        if analysis.documentation_links:
            result_parts.append("\n\nDocumentation & Resources:")
            for link in analysis.documentation_links:
                result_parts.append(f"• {link}")
        
        # Implementation Tips Section
        result_parts.extend([
            "\n\nImplementation Tips:",
            "• Study the AIDL definitions to understand data types and structure",
            "• Check DefaultProperties.cpp for configuration examples",
            "• Use the emulator implementation as a reference for testing",
            "• Follow the pattern established in existing properties for consistency",
            "• Pay attention to area mapping and access control requirements"
        ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error analyzing vHAL implementation: {str(e)}"


# Make sure the server can be run directly
if __name__ == "__main__":
    mcp.run()
