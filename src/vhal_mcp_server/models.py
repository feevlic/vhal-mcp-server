from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class VhalCategory(Enum):
    SEAT = "SEAT"
    HVAC = "HVAC"
    LIGHTS = "LIGHTS"
    POWER = "POWER"
    BODY = "BODY"
    CABIN = "CABIN"
    CLIMATE = "CLIMATE"
    DISPLAY = "DISPLAY"
    ENGINE = "ENGINE"
    INFO = "INFO"
    INSTRUMENT_CLUSTER = "INSTRUMENT_CLUSTER"
    MIRROR = "MIRROR"
    VEHICLE_MAP_SERVICE = "VEHICLE_MAP_SERVICE"
    WINDOW = "WINDOW"
    VENDOR = "VENDOR"
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
