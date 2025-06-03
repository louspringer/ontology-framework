import os
import tempfile
from pathlib import Path
from scripts.inventory_example_org import ExampleOrgInventory

def test_scan_file():
    """Test scanning a single file for example.org usage."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
        f.write("""
@prefix ex: <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# > .

ex:Test a rdf:Class .
        """)
        f.flush()
        
        inventory = ExampleOrgInventory()
        inventory.scan_file(Path(f.name))
        
        assert str(f.name) in inventory.results
        assert len(inventory.results[str(f.name)]) == 1
        assert inventory.results[str(f.name)][0][0] == 2  # Line number
        assert "example.org" in inventory.results[str(f.name)][0][1]  # Line content
        
        os.unlink(f.name)

def test_scan_directory():
    """Test scanning a directory for example.org usage."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        files = {
            'test1.ttl': '@prefix ex: <http://example.org/> .',
            'test2.py': 'import ontology_framework  # example.org reference',
            'test3.md': '[Example](http://example.org/)',
            'test4.txt': 'No example.org here'
        }
        
        for filename, content in files.items():
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write(content)
        
        inventory = ExampleOrgInventory(temp_dir)
        inventory.scan_directory()
        
        # Should find example.org in .ttl, .py, and .md files
        assert len(inventory.results) == 3
        for ext in ['.ttl', '.py', '.md']:
            assert any(ext in f for f in inventory.results.keys())
        
        # Should not find example.org in .txt file
        assert not any('.txt' in f for f in inventory.results.keys())

def test_generate_report():
    """Test report generation."""
    inventory = ExampleOrgInventory()
    inventory.results = {
        'test.ttl': [(1, '@prefix ex: <http://example.org/> .')]
    }
    
    report = inventory.generate_report()
    assert '# Example.org Usage Inventory' in report
    assert '## test.ttl' in report
    assert 'Line 1: @prefix ex: <http://example.org/> .' in report

def test_save_report():
    """Test saving the report to a file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md',
        delete=False) as f:
        inventory = ExampleOrgInventory()
        inventory.results = {
            'test.ttl': [(1, '@prefix ex: <http://example.org/> .')]
        }
        inventory.save_report(f.name)
        
        with open(f.name, 'r') as report:
            content = report.read()
            assert '# Example.org Usage Inventory' in content
            assert '## test.ttl' in content
            assert 'Line 1: @prefix ex: <http://example.org/> .' in content
        
        os.unlink(f.name) 