"""AST Generation wrapper around sqlglot."""

import sqlglot
from sqlglot.errors import ParseError

class ASTGenerator:
    """Generates Abstract Syntax Trees from SQL chunks."""

    @staticmethod
    def generate(sql_chunk: str, dialect: str = "oracle") -> sqlglot.Expression | None:
        """Parse a SQL chunk into an AST using sqlglot.
        
        Uses 'oracle' dialect as closest approximation to DB2 if 'db2' is unavailable.
        Returns None if parsing fails (e.g., proprietary syntax).
        """
        try:
            # We try parsing the statement. If it contains multiple, we just take the first.
            expressions = sqlglot.parse(sql_chunk, read=dialect)
            if expressions and len(expressions) > 0:
                return expressions[0]
            return None
        except ParseError:
            return None
