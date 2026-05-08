"""Prompt templates for AI Translation Engine."""

SYSTEM_PROMPT_V1 = """You are an expert database migration assistant specializing in translating DB2 SQL to Azure SQL (T-SQL).
Your sole purpose is to receive DB2 SQL and output the exact equivalent Azure SQL.

CRITICAL INSTRUCTIONS:
1. ONLY return the converted T-SQL. Do not include any explanations, greetings, or warnings.
2. Put the converted T-SQL inside a markdown sql block, like this:
```sql
<your converted code here>
```
3. Ensure all proprietary DB2 syntax is removed or mapped to Azure SQL equivalents.
4. Maintain exactly the same business logic.
"""

USER_PROMPT_TEMPLATE_V1 = """Convert the following DB2 {object_type} to Azure SQL:

```sql
{original_sql}
```
"""

PROMPTS = {
    "v1.0": {
        "system": SYSTEM_PROMPT_V1,
        "user": USER_PROMPT_TEMPLATE_V1
    }
}

def get_prompt(version: str, object_type: str, original_sql: str) -> tuple[str, str]:
    """Retrieve formatted system and user prompts.
    
    Args:
        version: The prompt version to use (e.g., 'v1.0').
        object_type: The type of the object (e.g., 'PROCEDURE').
        original_sql: The DB2 SQL to translate.
        
    Returns:
        tuple[str, str]: (system_prompt, user_prompt)
    """
    templates = PROMPTS.get(version, PROMPTS["v1.0"])
    sys_prompt = templates["system"]
    usr_prompt = templates["user"].format(
        object_type=object_type,
        original_sql=original_sql
    )
    return sys_prompt, usr_prompt
