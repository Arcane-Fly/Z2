#!/usr/bin/env python3
"""
Validate all JSON Schema contracts and examples.

This script validates:
1. All JSON schema files are valid JSON and valid schemas
2. All example fixtures validate against their schemas
3. Schemas reference existing files

Usage:
    python scripts/validate_contracts.py
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple

from jsonschema import Draft202012Validator, ValidationError
from jsonschema.validators import validator_for


def validate_json_file(file_path: Path) -> Tuple[bool, str]:
    """Validate that a file contains valid JSON.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_schema_file(file_path: Path) -> Tuple[bool, str]:
    """Validate that a file contains a valid JSON Schema.
    
    Args:
        file_path: Path to schema file
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            schema = json.load(f)
        
        # Check that it's a valid schema
        validator_class = validator_for(schema)
        validator_class.check_schema(schema)
        
        return True, ""
    except ValidationError as e:
        return False, f"Invalid schema: {e.message}"
    except Exception as e:
        return False, f"Error validating schema: {e}"


def validate_example_against_schema(
    example_data: dict,
    schema_path: Path
) -> Tuple[bool, str]:
    """Validate example data against a schema.
    
    Args:
        example_data: Example data to validate
        schema_path: Path to schema file
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(example_data))
        
        if errors:
            error_msgs = [f"  - {e.path}: {e.message}" for e in errors[:3]]
            return False, "Validation errors:\n" + "\n".join(error_msgs)
        
        return True, ""
    except Exception as e:
        return False, f"Error validating: {e}"


def main():
    """Main validation function."""
    # Get contracts directory
    script_dir = Path(__file__).parent
    contracts_dir = script_dir.parent.parent / "contracts"
    
    if not contracts_dir.exists():
        print(f"❌ Contracts directory not found: {contracts_dir}")
        sys.exit(1)
    
    print("🔍 Validating MCP Server Contracts")
    print("=" * 60)
    
    errors: List[str] = []
    warnings: List[str] = []
    validated_count = 0
    
    # 1. Validate all schema files
    print("\n📋 Validating schema files...")
    schema_files = list(contracts_dir.rglob("*.json"))
    schema_files = [f for f in schema_files if "examples" not in f.parts]
    
    for schema_file in schema_files:
        rel_path = schema_file.relative_to(contracts_dir)
        
        # Validate JSON syntax
        success, error = validate_json_file(schema_file)
        if not success:
            errors.append(f"  ❌ {rel_path}: {error}")
            continue
        
        # Validate schema structure
        success, error = validate_schema_file(schema_file)
        if not success:
            errors.append(f"  ❌ {rel_path}: {error}")
            continue
        
        print(f"  ✅ {rel_path}")
        validated_count += 1
    
    # 2. Validate example fixtures
    print("\n📝 Validating example fixtures...")
    examples_dir = contracts_dir / "examples"
    
    if examples_dir.exists():
        example_files = list(examples_dir.glob("*.json"))
        
        for example_file in example_files:
            rel_path = example_file.relative_to(contracts_dir)
            
            # Load example
            success, error = validate_json_file(example_file)
            if not success:
                errors.append(f"  ❌ {rel_path}: {error}")
                continue
            
            with open(example_file) as f:
                example = json.load(f)
            
            # Determine schema paths from filename
            # e.g., mcp.initialize.example.json -> mcp/initialize.request.json
            if example_file.stem == "error.example":
                # Special case for error examples
                if "examples" in example:
                    all_valid = True
                    for ex in example["examples"]:
                        schema_path = contracts_dir / "shared" / "error.envelope.json"
                        success, error = validate_example_against_schema(
                            ex["payload"],
                            schema_path
                        )
                        if not success:
                            errors.append(
                                f"  ❌ {rel_path} ({ex['name']}): {error}"
                            )
                            all_valid = False
                    
                    if all_valid:
                        print(f"  ✅ {rel_path}")
                        validated_count += 1
            else:
                # Standard request/response examples
                parts = example_file.stem.replace(".example", "").split(".")
                if len(parts) == 2:
                    server, operation = parts
                    
                    # Validate request if present
                    if "request" in example:
                        schema_path = contracts_dir / server / f"{operation}.request.json"
                        if schema_path.exists():
                            success, error = validate_example_against_schema(
                                example["request"],
                                schema_path
                            )
                            if not success:
                                errors.append(f"  ❌ {rel_path} (request): {error}")
                            else:
                                print(f"  ✅ {rel_path} (request)")
                                validated_count += 1
                        else:
                            warnings.append(
                                f"  ⚠️  {rel_path}: Schema not found: {schema_path.name}"
                            )
                    
                    # Validate response if present
                    if "response" in example:
                        schema_path = contracts_dir / server / f"{operation}.response.json"
                        if schema_path.exists():
                            success, error = validate_example_against_schema(
                                example["response"],
                                schema_path
                            )
                            if not success:
                                errors.append(f"  ❌ {rel_path} (response): {error}")
                            else:
                                print(f"  ✅ {rel_path} (response)")
                                validated_count += 1
                        else:
                            warnings.append(
                                f"  ⚠️  {rel_path}: Schema not found: {schema_path.name}"
                            )
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Validation Summary")
    print(f"  ✅ Validated: {validated_count} items")
    
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(warning)
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors:
            print(error)
        print("\n🔴 Validation FAILED")
        sys.exit(1)
    else:
        print("\n🎉 All contracts are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
