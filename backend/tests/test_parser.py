"""Tests for the Schema Parsing Engine."""

from app.services.parser import DDLChunker, ObjectClassifier, DependencyGraph


def test_ddl_chunker_basic():
    """Test chunking simple statements without complex blocks."""
    sql = "CREATE TABLE T1 (ID INT);\nALTER TABLE T1 ADD C INT;\n"
    chunks = DDLChunker.chunk_ddl(sql)
    assert len(chunks) == 2
    assert chunks[0] == "CREATE TABLE T1 (ID INT)"
    assert chunks[1] == "ALTER TABLE T1 ADD C INT"


def test_ddl_chunker_blocks():
    """Test chunking handles BEGIN...END blocks without splitting."""
    sql = """
    CREATE PROCEDURE P1()
    BEGIN
        DECLARE X INT;
        SET X = 1;
    END;
    
    CREATE TABLE T2 (ID INT);
    """
    chunks = DDLChunker.chunk_ddl(sql)
    assert len(chunks) == 2
    assert "BEGIN" in chunks[0]
    assert "SET X = 1;" in chunks[0]
    assert "CREATE TABLE T2" in chunks[1]


def test_classifier_table():
    """Test classification of a CREATE TABLE statement."""
    sql = "CREATE TABLE SCHEMA.EMPLOYEE (ID INT)"
    meta = ObjectClassifier.classify(sql)
    assert meta["object_type"] == "TABLE"
    assert meta["object_name"] == "EMPLOYEE"
    assert meta["schema"] == "SCHEMA"


def test_classifier_alter():
    """Test classification of an ALTER TABLE statement."""
    sql = "ALTER TABLE SCHEMA.EMPLOYEE ADD CONSTRAINT FK1 FOREIGN KEY (ID) REFERENCES D(ID)"
    meta = ObjectClassifier.classify(sql)
    assert meta["object_type"] == "ALTER_TABLE"
    assert meta["object_name"] == "EMPLOYEE"
    assert meta["schema"] == "SCHEMA"


def test_dependency_graph():
    """Test that a topological sort correctly orders foreign key references."""
    graph = DependencyGraph()
    # Add chunks out of order
    graph.add_chunk("c1", "ALTER TABLE T2 ADD CONSTRAINT FK FOREIGN KEY (T1_ID) REFERENCES T1(ID)")
    graph.add_chunk("c2", "CREATE TABLE T1 (ID INT)")
    graph.add_chunk("c3", "CREATE TABLE T2 (ID INT, T1_ID INT)")
    
    ordered = graph.get_ordered_chunks()
    
    # Extract names in order
    names = [node["object_name"] for node in ordered if node["object_name"]]
    
    # T1 must come before T2
    assert "T1" in names
    assert "T2" in names
    assert names.index("T1") < names.index("T2")
