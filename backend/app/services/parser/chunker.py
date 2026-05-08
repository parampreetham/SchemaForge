"""DDL Chunking service for splitting monolithic DB2 files."""

import re

class DDLChunker:
    """Splits a DB2 DDL file into individual executable statements."""

    @staticmethod
    def chunk_ddl(sql_text: str) -> list[str]:
        """Split SQL text into discrete statements.
        
        Handles string literals and basic BEGIN...END block nesting.
        """
        chunks = []
        current_chunk = []
        
        # State tracking
        in_string = False
        in_multiline_comment = False
        in_single_line_comment = False
        block_depth = 0
        
        i = 0
        length = len(sql_text)
        
        while i < length:
            char = sql_text[i]
            next_char = sql_text[i+1] if i + 1 < length else ""
            
            # Handle comments and strings first
            if not in_string and not in_multiline_comment and not in_single_line_comment:
                if char == "-" and next_char == "-":
                    in_single_line_comment = True
                    current_chunk.append(char)
                    i += 1
                    continue
                elif char == "/" and next_char == "*":
                    in_multiline_comment = True
                    current_chunk.append(char)
                    i += 1
                    continue
                elif char == "'":
                    in_string = True
            elif in_single_line_comment:
                if char == "\n":
                    in_single_line_comment = False
            elif in_multiline_comment:
                if char == "*" and next_char == "/":
                    in_multiline_comment = False
                    current_chunk.append(char)
                    current_chunk.append(next_char)
                    i += 2
                    continue
            elif in_string:
                if char == "'":
                    # Check for escaped quotes ''
                    if next_char == "'":
                        current_chunk.append(char)
                        i += 1
                    else:
                        in_string = False
            
            # Keyword detection for BEGIN/END blocks (rough heuristic)
            if not in_string and not in_single_line_comment and not in_multiline_comment:
                # Look ahead for word boundaries
                # This is a simple lookbehind/lookahead equivalent manually
                prev_char = sql_text[i-1] if i > 0 else " "
                if not prev_char.isalnum() and prev_char != "_":
                    # Check "BEGIN"
                    if sql_text[i:i+5].upper() == "BEGIN":
                        end_char = sql_text[i+5] if i+5 < length else " "
                        if not end_char.isalnum() and end_char != "_":
                            block_depth += 1
                    # Check "END"
                    elif sql_text[i:i+3].upper() == "END":
                        end_char = sql_text[i+3] if i+3 < length else " "
                        if not end_char.isalnum() and end_char != "_":
                            block_depth = max(0, block_depth - 1)
                
                if char == ";":
                    # If we are at depth 0, this is a statement terminator
                    if block_depth == 0:
                        chunk_str = "".join(current_chunk).strip()
                        if chunk_str:
                            chunks.append(chunk_str)
                        current_chunk = []
                        i += 1
                        continue

            current_chunk.append(char)
            i += 1

        # Add any remaining text
        final_chunk = "".join(current_chunk).strip()
        if final_chunk:
            chunks.append(final_chunk)

        return chunks
