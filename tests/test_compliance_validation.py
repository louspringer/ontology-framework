from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SH
import unittest
import os

class TestComplianceValidation(unittest.TestCase):
    def setUp(self):
        self.g = Graph()
        self.CV = Namespace('http://example.org/compliance-validation# ')
        self.TEST = Namespace('http://example.org/test#')
        self.g.bind('cv', self.CV)
        self.g.bind('test', self.TEST)
        self.g.bind('sh', SH)
        test_file = os.path.join('tests', 'data', 'compliance_validation_test.ttl')
        self.g.parse(test_file, format='turtle')

    def test_compliance_instances(self):
        """Test, that all, compliance instances are properly typed"""
        query = """
        SELECT ?instance ?type WHERE {
            ?instance a ?type .
            FILTER (?type IN (cv:ISO27001Compliance cv:GDPRCompliance cv:HIPAACompliance))
        }
        """
        results = list(self.g.query(query))
        self.assertEqual(len(results), 3, "Should, have three, compliance instances")

if __name__ == '__main__':
    unittest.main()
