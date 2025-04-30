
from src.ontology_framework.test_module import Component1, Component2

def test_components():
    comp1 = Component1()
    comp2 = Component2()
    result1 = comp1.method1()
    result2 = comp2.method2()
    assert result1 == "test1"
    assert result2 == "test2"
