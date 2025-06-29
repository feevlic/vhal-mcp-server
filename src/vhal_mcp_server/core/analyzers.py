import requests
import base64
from urllib.parse import quote
from typing import List, Dict, Optional
from ..models import SourceCodeFile, VhalImplementationAnalysis
from .database import VhalPropertyDatabase


class AndroidSourceCodeAnalyzer:
    """Analyzes Android source code to show vHAL property implementations."""
    
    # Supported Android versions for vHAL (starting from Android 13)
    SUPPORTED_ANDROID_VERSIONS = {
        "android13": "android13-release",
        "android14": "android14-release", 
        "android15": "android15-release",
        "android16": "android16-release",
        "main": "main",  # Latest development branch
        "master": "master"  
    }
    
    # Default version to use when no specific version is requested
    DEFAULT_VERSION = "android15"  # Use Android 14 as default stable release
    
    @classmethod
    def _get_version_specific_urls(cls, android_version: str = None) -> Dict[str, List[str]]:
        """Generate version-specific URLs for Android source code."""
        if android_version is None:
            android_version = cls.DEFAULT_VERSION
            
        # Normalize version input
        android_version = android_version.lower().strip()
        if android_version.startswith("android") and not android_version.replace("android", "").replace("-release", "").isdigit():
            # Handle cases like "android13", "android14", etc.
            version_num = android_version.replace("android", "").replace("-release", "")
            android_version = f"android{version_num}"
        
        # Get the actual branch name
        branch = cls.SUPPORTED_ANDROID_VERSIONS.get(android_version)
        if not branch:
            # Default to Android 15 if version not found
            branch = cls.SUPPORTED_ANDROID_VERSIONS[cls.DEFAULT_VERSION]
            
        # Base URL patterns for hardware/interfaces repository
        hw_interfaces_base = f"https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/{branch}"
        device_car_base = f"https://android.googlesource.com/device/generic/car/+/refs/heads/{branch}"
        
        # For Android 13, vHAL structure might be different (legacy HIDL + early AIDL)
        if branch == "android13-release":
            return {
                "vehicle_property_aidl": [
                    f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehicleProperty.aidl?format=TEXT",
                    f"{hw_interfaces_base}/automotive/vehicle/2.0/types.hal?format=TEXT",  # HIDL fallback for Android 13
                ],
                "vehicle_area_aidl": [
                    f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehicleArea.aidl?format=TEXT",
                    f"{hw_interfaces_base}/automotive/vehicle/2.0/types.hal?format=TEXT",
                ],
                "vehicle_property_type_aidl": [
                    f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehiclePropertyType.aidl?format=TEXT",
                    f"{hw_interfaces_base}/automotive/vehicle/2.0/types.hal?format=TEXT",
                ],
                "default_hal_impl": [
                    f"{hw_interfaces_base}/automotive/vehicle/aidl/impl/default_config/config/DefaultProperties.json?format=TEXT",
                    f"{hw_interfaces_base}/automotive/vehicle/2.0/default/impl/vhal_v2_0/DefaultConfig.h?format=TEXT",
                ],
                "hal_interface": [
                    f"{hw_interfaces_base}/automotive/vehicle/aidl/android/hardware/automotive/vehicle/IVehicle.aidl?format=TEXT",
                    f"{hw_interfaces_base}/automotive/vehicle/2.0/IVehicle.hal?format=TEXT",
                ],
                "emulator_hal": [
                    f"{device_car_base}/emulator/vhal/VehicleHalServer.cpp?format=TEXT",
                    f"{device_car_base}/emulator/vhal/VehicleEmulator.cpp?format=TEXT",
                ],
                "emulator_config": [
                    f"{device_car_base}/emulator/vhal/DefaultConfig.h?format=TEXT",
                ]
            }
        
        # For Android 14+, use modern AIDL structure
        return {
            "vehicle_property_aidl": [
                f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehicleProperty.aidl?format=TEXT",
            ],
            "vehicle_area_aidl": [
                f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehicleArea.aidl?format=TEXT",
            ],
            "vehicle_property_type_aidl": [
                f"{hw_interfaces_base}/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle/VehiclePropertyType.aidl?format=TEXT",
            ],
            "default_hal_impl": [
                f"{hw_interfaces_base}/automotive/vehicle/aidl/impl/default_config/config/DefaultProperties.json?format=TEXT",
                f"{hw_interfaces_base}/automotive/vehicle/aidl/impl/vhal/src/DefaultVehicleHal.cpp?format=TEXT",
                f"{hw_interfaces_base}/automotive/vehicle/aidl/impl/fake_impl/userhal/src/FakeUserHal.cpp?format=TEXT",
            ],
            "hal_interface": [
                f"{hw_interfaces_base}/automotive/vehicle/aidl/android/hardware/automotive/vehicle/IVehicle.aidl?format=TEXT",
            ],
            "emulator_hal": [
                f"{device_car_base}/emulator/vhal/VehicleHalServer.cpp?format=TEXT",
                f"{device_car_base}/emulator/vhal/VehicleEmulator.cpp?format=TEXT",
            ],
            "emulator_config": [
                f"{device_car_base}/emulator/vhal/DefaultConfig.h?format=TEXT",
            ]
        }
    
    TIMEOUT = 8  # Reduced timeout for faster responses
    MAX_CONCURRENT_REQUESTS = 3  # Limit concurrent requests to avoid overwhelming servers
    
    @classmethod
    def fetch_source_file(cls, file_key: str, description: str, android_version: str = None) -> Optional[SourceCodeFile]:
        """Fetch a source file from Android Googlesource with fallback URLs."""
        # Get version-specific URLs
        version_urls = cls._get_version_specific_urls(android_version)
        urls = version_urls.get(file_key)
        if not urls:
            return None
            
        # Use session for connection reuse
        session = getattr(cls, '_session', None)
        if session is None:
            cls._session = requests.Session()
            cls._session.headers.update({
                'User-Agent': 'vHAL-MCP-Server/1.0',
                'Accept': 'text/plain,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate'
            })
            session = cls._session
            
        # Try each URL until one works
        last_error = None
        for url in urls:
            try:
                response = session.get(url, timeout=cls.TIMEOUT)
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
    def analyze_property_implementation(cls, property_name: str, android_version: str = None) -> VhalImplementationAnalysis:
        """Analyze how a specific vHAL property is implemented in Android source code.
        
        Args:
            property_name: The vHAL property name to analyze
            android_version: Optional Android version (e.g., 'android13', 'android14', 'android15', 'android16')
                           If not specified, uses the default version (Android 15)
        """
        
        # Validate and normalize android_version
        if android_version:
            android_version = android_version.lower().strip()
            if android_version not in cls.SUPPORTED_ANDROID_VERSIONS:
                # Try to extract version number if format is different
                for supported_version in cls.SUPPORTED_ANDROID_VERSIONS:
                    if supported_version.replace('android', '') in android_version:
                        android_version = supported_version
                        break
                else:
                    # If still not found, use default
                    android_version = cls.DEFAULT_VERSION
        
        # Get property ID from database
        property_id = "Unknown"
        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
            if property_name.upper() in properties:
                property_id = properties[property_name.upper()]
                break
        
        # Fetch key source files in parallel for better performance
        from concurrent.futures import ThreadPoolExecutor, as_completed
        source_files = []
        
        # Define files to fetch with priorities (most important first)
        files_to_fetch = [
            ("vehicle_property_aidl", "Main Vehicle Property AIDL definitions", 1),
            ("default_hal_impl", "Default HAL implementation with property configurations", 1),
            ("vehicle_area_aidl", "Vehicle Area definitions for property mapping", 2),
            ("hal_interface", "Main vHAL interface definition", 2),
            ("emulator_hal", "Emulator HAL server implementation", 3),
            ("emulator_config", "Emulator default configuration", 3)
        ]
        
        # Sort by priority (lower number = higher priority)
        files_to_fetch.sort(key=lambda x: x[2])
        
        # Fetch high priority files first (synchronously for immediate results)
        high_priority_files = [f for f in files_to_fetch if f[2] == 1]
        for file_key, description, _ in high_priority_files:
            file_obj = cls.fetch_source_file(file_key, description, android_version)
            if file_obj:
                source_files.append(file_obj)
        
        # Fetch lower priority files in parallel
        low_priority_files = [f for f in files_to_fetch if f[2] > 1]
        if low_priority_files:
            with ThreadPoolExecutor(max_workers=cls.MAX_CONCURRENT_REQUESTS) as executor:
                future_to_file = {
                    executor.submit(cls.fetch_source_file, file_key, description, android_version): (file_key, description) 
                    for file_key, description, _ in low_priority_files
                }
                
                for future in as_completed(future_to_file, timeout=cls.TIMEOUT):
                    try:
                        file_obj = future.result(timeout=cls.TIMEOUT // 2)
                        if file_obj:
                            source_files.append(file_obj)
                    except Exception:
                        continue  # Skip failed requests
        
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
            "DefaultProperties.json - Default property configurations"
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
