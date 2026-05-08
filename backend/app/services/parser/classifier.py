"""SQL Object classification and metadata extraction."""

import re

# Regex patterns for fast fallback metadata extraction
TYPE_PATTERN = re.compile(r"^\s*CREATE\s+(OR\s+REPLACE\s+)?(UNIQUE\s+)?([A-Z]+)", re.IGNORECASE)
ALTER_PATTERN = re.compile(r"^\s*ALTER\s+([A-Z]+)", re.IGNORECASE)
DROP_PATTERN = re.compile(r"^\s*DROP\s+([A-Z]+)", re.IGNORECASE)
NAME_PATTERN = re.compile(r"^\s*(?:CREATE|ALTER|DROP)\s+(?:OR\s+REPLACE\s+)?(?:UNIQUE\s+)?(?:[A-Z]+\s+)([A-Z0-9_]+\.)?([A-Z0-9_]+)", re.IGNORECASE)

class ObjectClassifier:
    """Classifies SQL chunks into types and extracts object names."""

    @staticmethod
    def classify(sql_chunk: str) -> dict[str, str | None]:
        """Classify the SQL chunk and return its metadata.
        
        Returns:
            dict with keys: 'object_type', 'object_name', 'schema'
        """
        result = {
            "object_type": "UNKNOWN",
            "object_name": None,
            "schema": None
        }

        # Try to match CREATE
        create_match = TYPE_PATTERN.search(sql_chunk)
        if create_match:
            result["object_type"] = create_match.group(3).upper()
        else:
            alter_match = ALTER_PATTERN.search(sql_chunk)
            if alter_match:
                result["object_type"] = "ALTER_" + alter_match.group(1).upper()
            else:
                drop_match = DROP_PATTERN.search(sql_chunk)
                if drop_match:
                    result["object_type"] = "DROP_" + drop_match.group(1).upper()

        # Try to extract the name
        name_match = NAME_PATTERN.search(sql_chunk)
        if name_match:
            schema_group = name_match.group(1)
            if schema_group:
                result["schema"] = schema_group.rstrip(".")
            result["object_name"] = name_match.group(2)

        return result
