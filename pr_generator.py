"""Pull Request Message Generator for VHAL Implementations

This module generates comprehensive pull request messages for VHAL property implementations,
providing structured descriptions of changes, features, and testing requirements.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PullRequestMessage:
    """Complete pull request message structure"""
    title: str
    description: str
    changes_summary: str
    technical_details: str
    testing_section: str
    breaking_changes: str
    documentation: str
    checklist: str


class VhalPullRequestGenerator:
    """Generates structured pull request messages for VHAL implementations"""
    
    @staticmethod
    def generate_pr_message(
        property_name: str,
        property_id: str,
        property_type: str,
        group: str,
        access: str,
        change_mode: str,
        description: str,
        units: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        areas: Optional[List[str]] = None,
        enum_values: Optional[Dict[str, int]] = None,
        dependencies: Optional[List[str]] = None,
        sample_rate_hz: Optional[float] = None,
        breaking_change: bool = False,
        jira_ticket: Optional[str] = None,
        reviewer_suggestions: Optional[List[str]] = None
    ) -> PullRequestMessage:
        """Generate a comprehensive pull request message for VHAL implementation"""
        
        # Generate title
        title = VhalPullRequestGenerator._generate_title(property_name, property_type, group)
        
        # Generate main description
        pr_description = VhalPullRequestGenerator._generate_description(
            property_name, description, jira_ticket
        )
        
        # Generate changes summary
        changes_summary = VhalPullRequestGenerator._generate_changes_summary(
            property_name, property_id, property_type, group, access, change_mode
        )
        
        # Generate technical details
        technical_details = VhalPullRequestGenerator._generate_technical_details(
            property_name, property_id, property_type, group, access, change_mode,
            units, min_value, max_value, areas, enum_values, dependencies, sample_rate_hz
        )
        
        # Generate testing section
        testing_section = VhalPullRequestGenerator._generate_testing_section(
            property_name, property_type, access, change_mode, areas
        )
        
        # Generate breaking changes section
        breaking_changes = VhalPullRequestGenerator._generate_breaking_changes(
            breaking_change, property_name
        )
        
        # Generate documentation section
        documentation = VhalPullRequestGenerator._generate_documentation_section(
            property_name, property_type, group
        )
        
        # Generate checklist
        checklist = VhalPullRequestGenerator._generate_checklist(
            property_type, access, areas, enum_values, reviewer_suggestions
        )
        
        return PullRequestMessage(
            title=title,
            description=pr_description,
            changes_summary=changes_summary,
            technical_details=technical_details,
            testing_section=testing_section,
            breaking_changes=breaking_changes,
            documentation=documentation,
            checklist=checklist
        )
    
    @staticmethod
    def format_pr_message(pr_message: PullRequestMessage) -> str:
        """Format the complete pull request message"""
        
        sections = [
            pr_message.description,
            "",
            "## Changes Summary",
            pr_message.changes_summary,
            "",
            "## Technical Details",
            pr_message.technical_details,
            "",
            "## Testing",
            pr_message.testing_section,
        ]
        
        if pr_message.breaking_changes.strip():
            sections.extend([
                "",
                "## Breaking Changes",
                pr_message.breaking_changes
            ])
        
        sections.extend([
            "",
            "## Documentation",
            pr_message.documentation,
            "",
            "## Checklist",
            pr_message.checklist
        ])
        
        return "\n".join(sections)
    
    @staticmethod
    def _generate_title(property_name: str, property_type: str, group: str) -> str:
        """Generate PR title"""
        group_emoji = {
            "HVAC": "🌡️",
            "SEAT": "🪑",
            "LIGHTS": "💡",
            "POWER": "🔋",
            "CLIMATE": "❄️",
            "ENGINE": "🚗",
            "INFO": "ℹ️",
            "DISPLAY": "📱",
            "BODY": "🚙",
            "CABIN": "🏠",
            "MIRROR": "🪞",
            "WINDOW": "🪟",
            "VENDOR": "🏭"
        }
        
        emoji = group_emoji.get(group, "⚙️")
        
        # Convert property name to readable format
        readable_name = property_name.replace("_", " ").title()
        
        return f"{emoji} Add {readable_name} VHAL Property ({property_type})"
    
    @staticmethod
    def _generate_description(property_name: str, description: str, jira_ticket: Optional[str]) -> str:
        """Generate main PR description"""
        
        ticket_ref = f"\n\n**Related Ticket:** {jira_ticket}" if jira_ticket else ""
        
        return f"""This PR implements the `{property_name}` VHAL property for Android Automotive OS (AAOS).

**Overview:**
{description}

**Motivation:**
This property enhances the vehicle's capability by providing standardized access to {property_name.lower().replace('_', ' ')} functionality through the Android Automotive framework.{ticket_ref}"""
    
    @staticmethod
    def _generate_changes_summary(
        property_name: str, property_id: str, property_type: str, 
        group: str, access: str, change_mode: str
    ) -> str:
        """Generate changes summary"""
        
        return f"""### Core Implementation
- **Property**: `{property_name}` (ID: `{property_id}`)
- **Type**: `{property_type}`
- **Group**: `{group}`
- **Access**: `{access}`
- **Change Mode**: `{change_mode}`

### Files Modified/Added
- `types.hal` - Added property definition and enums
- `DefaultConfig.h` - Added property configuration
- `EmulatedVehicleHal.cpp` - Implemented property handling logic
- `VehicleProperty.aidl` - Added AIDL interface definition
- `VehiclePropertyIds.java` - Added Java constants
- `CarPropertyManager.java` - Added convenience API methods
- `VehicleHalTest.cpp` - Added C++ unit tests
- `VehiclePropertyTest.java` - Added Java integration tests
- `car_emulator_config.json` - Added emulator configuration
- `car_service.te` - Added SELinux policy rules

### Integration Points
- Framework API integration through CarPropertyManager
- Emulator support for development and testing
- Proper permission and security policy configuration"""
    
    @staticmethod
    def _generate_technical_details(
        property_name: str, property_id: str, property_type: str, group: str,
        access: str, change_mode: str, units: Optional[str], min_value: Optional[float],
        max_value: Optional[float], areas: Optional[List[str]], enum_values: Optional[Dict[str, int]],
        dependencies: Optional[List[str]], sample_rate_hz: Optional[float]
    ) -> str:
        """Generate technical details section"""
        
        details = [
            f"### Property Specification",
            f"- **Property ID**: `{property_id}`",
            f"- **Data Type**: `{property_type}`",
            f"- **Property Group**: `{group}`",
            f"- **Access Mode**: `{access}`",
            f"- **Change Mode**: `{change_mode}`"
        ]
        
        if units:
            details.append(f"- **Units**: `{units}`")
        
        if min_value is not None and max_value is not None:
            details.append(f"- **Value Range**: `{min_value}` to `{max_value}`")
        
        if sample_rate_hz:
            details.append(f"- **Sample Rate**: `{sample_rate_hz} Hz`")
        
        if areas:
            details.extend([
                "",
                "### Vehicle Areas",
                f"Supports the following vehicle areas/zones:"
            ])
            for area in areas:
                details.append(f"- `{area}`")
        
        if enum_values:
            details.extend([
                "",
                "### Enumerated Values"
            ])
            for enum_name, enum_value in enum_values.items():
                details.append(f"- `{enum_name}` = `{enum_value}`")
        
        if dependencies:
            details.extend([
                "",
                "### Property Dependencies",
                "This property interacts with the following properties:"
            ])
            for dep in dependencies:
                details.append(f"- `{dep}`")
        
        details.extend([
            "",
            "### Implementation Details",
            f"- **HAL Layer**: Property defined in `types.hal` with ID `{property_id}`",
            f"- **Framework Layer**: Java API exposed through `CarPropertyManager`",
            f"- **Access Control**: {VhalPullRequestGenerator._get_access_description(access)}",
            f"- **Change Notifications**: {VhalPullRequestGenerator._get_change_mode_description(change_mode)}"
        ])
        
        return "\n".join(details)
    
    @staticmethod
    def _generate_testing_section(
        property_name: str, property_type: str, access: str, 
        change_mode: str, areas: Optional[List[str]]
    ) -> str:
        """Generate testing section"""
        
        test_cases = [
            "### Test Coverage",
            "",
            "#### Unit Tests (C++)",
            "- ✅ Property configuration validation",
            "- ✅ Property ID and type verification",
            "- ✅ Access mode compliance testing"
        ]
        
        if access in ["READ", "READ_WRITE"]:
            test_cases.append("- ✅ Property read operations")
        
        if access in ["WRITE", "READ_WRITE"]:
            test_cases.append("- ✅ Property write operations")
            test_cases.append("- ✅ Input validation and error handling")
        
        if areas:
            test_cases.append("- ✅ Multi-area/zone functionality")
        
        test_cases.extend([
            "",
            "#### Integration Tests (Java)",
            "- ✅ CarPropertyManager API functionality",
            "- ✅ Property availability verification",
            "- ✅ Framework integration testing"
        ])
        
        if change_mode in ["ON_CHANGE", "CONTINUOUS"]:
            test_cases.append("- ✅ Change notification testing")
        
        test_cases.extend([
            "",
            "#### Manual Testing",
            "- ✅ Emulator functionality verification",
            "- ✅ Property behavior validation",
            "- ✅ Error condition handling"
        ])
        
        if property_type in ["INT32", "INT64", "FLOAT"]:
            test_cases.append("- ✅ Boundary value testing")
        
        test_cases.extend([
            "",
            "### Test Commands",
            "```bash",
            "# Run C++ unit tests",
            "atest VehicleHalTest",
            "",
            "# Run Java integration tests", 
            "atest VehiclePropertyTest",
            "",
            "# Build and verify HAL",
            "mmma hardware/interfaces/automotive/vehicle/2.0/",
            "```"
        ])
        
        return "\n".join(test_cases)
    
    @staticmethod
    def _generate_breaking_changes(breaking_change: bool, property_name: str) -> str:
        """Generate breaking changes section"""
        
        if not breaking_change:
            return "No breaking changes. This is a new property addition that maintains backward compatibility."
        
        return f"""⚠️ **This PR introduces breaking changes:**

- New property `{property_name}` requires updated HAL implementations
- Emulator configurations need to be updated to support the new property
- Applications using this property will require appropriate permissions

**Migration Guide:**
1. Update HAL implementation to handle the new property
2. Update emulator configuration files
3. Add required permissions to application manifests
4. Test existing functionality to ensure no regressions"""
    
    @staticmethod
    def _generate_documentation_section(property_name: str, property_type: str, group: str) -> str:
        """Generate documentation section"""
        
        return f"""### Updated Documentation
- ✅ Property definition with comprehensive comments
- ✅ Implementation guide with step-by-step instructions
- ✅ API documentation for CarPropertyManager methods
- ✅ Usage examples for application developers

### Developer Resources
- **Property Group**: `{group}` - See [VHAL Property Groups](https://source.android.com/docs/automotive/vhal/properties)
- **Data Type**: `{property_type}` - See [VHAL Data Types](https://source.android.com/docs/automotive/vhal/property-configuration-reference)
- **Implementation**: Follow [VHAL Implementation Guide](https://source.android.com/docs/automotive/vhal/property-implementation)

### Example Usage
```java
// Get CarPropertyManager
CarPropertyManager carPropertyManager = car.getCarManager(Car.PROPERTY_SERVICE);

// Check property availability
boolean isAvailable = carPropertyManager.isPropertyAvailable(
    VehiclePropertyIds.{property_name}, 0);

// Use the property (example based on access mode)
// See generated CarPropertyManager methods for complete API
```"""
    
    @staticmethod
    def _generate_checklist(
        property_type: str, access: str, areas: Optional[List[str]], 
        enum_values: Optional[Dict[str, int]], reviewer_suggestions: Optional[List[str]]
    ) -> str:
        """Generate review checklist"""
        
        checklist_items = [
            "### Code Review Checklist",
            "",
            "#### Implementation",
            "- [ ] Property ID is unique and follows naming conventions",
            "- [ ] Property type and access mode are appropriate",
            "- [ ] HAL implementation handles all edge cases",
            "- [ ] Error handling is comprehensive and appropriate",
            "- [ ] Code follows Android Automotive coding standards"
        ]
        
        if enum_values:
            checklist_items.append("- [ ] Enum values are logical and complete")
        
        if areas:
            checklist_items.append("- [ ] Multi-area support is correctly implemented")
        
        if access in ["WRITE", "READ_WRITE"]:
            checklist_items.append("- [ ] Input validation prevents invalid values")
        
        checklist_items.extend([
            "",
            "#### Testing",
            "- [ ] All unit tests pass",
            "- [ ] Integration tests cover main use cases",
            "- [ ] Manual testing completed on emulator",
            "- [ ] No regressions in existing functionality"
        ])
        
        if property_type in ["INT32", "INT64", "FLOAT"]:
            checklist_items.append("- [ ] Boundary value testing completed")
        
        checklist_items.extend([
            "",
            "#### Documentation", 
            "- [ ] Property description is clear and comprehensive",
            "- [ ] API documentation is complete",
            "- [ ] Usage examples are provided",
            "- [ ] Implementation guide is accurate"
        ])
        
        checklist_items.extend([
            "",
            "#### Security & Permissions",
            "- [ ] SELinux policies are appropriate and minimal",
            "- [ ] Permission requirements are documented",
            "- [ ] No security vulnerabilities introduced"
        ])
        
        if reviewer_suggestions:
            checklist_items.extend([
                "",
                "#### Specific Review Points"
            ])
            for suggestion in reviewer_suggestions:
                checklist_items.append(f"- [ ] {suggestion}")
        
        checklist_items.extend([
            "",
            "#### Pre-merge Requirements",
            "- [ ] All CI/CD checks pass",
            "- [ ] Code has been reviewed by domain expert",
            "- [ ] Documentation has been updated",
            "- [ ] Breaking changes have been communicated (if applicable)"
        ])
        
        return "\n".join(checklist_items)
    
    @staticmethod
    def _get_access_description(access: str) -> str:
        """Get human readable access mode description"""
        descriptions = {
            "READ": "Property can be read by applications",
            "WRITE": "Property can be written by applications", 
            "READ_WRITE": "Property supports both read and write operations"
        }
        return descriptions.get(access, "Unknown access mode")
    
    @staticmethod
    def _get_change_mode_description(change_mode: str) -> str:
        """Get human readable change mode description"""
        descriptions = {
            "STATIC": "Property value does not change during vehicle operation",
            "ON_CHANGE": "Property value changes infrequently, notifications sent on change",
            "CONTINUOUS": "Property value changes frequently, continuous monitoring enabled"
        }
        return descriptions.get(change_mode, "Unknown change mode")
