import unittest
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from rdflib.compare import isomorphic

class TestInfrastructureOntology(unittest.TestCase):
    def setUp(self):
        # Create a new graph and load the infrastructure ontology
        self.g = Graph()
        self.g.parse("infrastructure.ttl", format="turtle")
        
        # Define namespaces
        self.INF = Namespace("http://example.org/infrastructure#")
        self.AZURE = Namespace("http://example.org/azure#")
        self.GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        self.SH = SH

    def test_required_prefixes(self):
        """Test that all required prefixes are present"""
        required_prefixes = {
            "rdf": URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            "rdfs": URIRef("http://www.w3.org/2000/01/rdf-schema#"),
            "owl": URIRef("http://www.w3.org/2002/07/owl#"),
            "xsd": URIRef("http://www.w3.org/2001/XMLSchema#"),
            "sh": URIRef("http://www.w3.org/ns/shacl#")
        }
        
        # Convert the generator to a dictionary
        namespaces = dict(self.g.namespaces())
        
        for prefix, uri in required_prefixes.items():
            self.assertIn(prefix, namespaces, f"Missing required prefix: {prefix}")
            self.assertEqual(namespaces[prefix], uri, f"Wrong URI for prefix {prefix}")

    def test_class_labels_and_comments(self):
        """Test that all classes have labels and comments"""
        for s, p, o in self.g.triples((None, RDF.type, OWL.Class)):
            if str(s).startswith(str(self.INF)):
                label = self.g.value(s, RDFS.label)
                comment = self.g.value(s, RDFS.comment)
                self.assertIsNotNone(label, f"Class {s} missing label")
                self.assertIsNotNone(comment, f"Class {s} missing comment")

    def test_property_domains_and_ranges(self):
        """Test that all properties have domains and ranges"""
        # Define expected domains for properties
        expected_domains = {
            self.INF.hasIPAddress: [self.INF.NetworkInterface, self.INF.PublicIPAddress],
            self.INF.hasName: None,  # Global property
            self.INF.hasLocation: None,  # Global property
            self.INF.hasSize: self.INF.VirtualMachine,
            self.INF.hasShutdownTime: self.INF.AutoShutdown,
            self.INF.hasNotificationTime: self.INF.AutoShutdown,
            self.INF.hasPriority: self.INF.SecurityRule,
            self.INF.hasProtocol: self.INF.SecurityRule,
            self.INF.hasPort: self.INF.SecurityRule
        }
        
        for s, p, o in self.g.triples((None, RDF.type, OWL.ObjectProperty)):
            if str(s).startswith(str(self.INF)):
                domain = self.g.value(s, RDFS.domain)
                range_ = self.g.value(s, RDFS.range)
                self.assertIsNotNone(domain, f"Property {s} missing domain")
                self.assertIsNotNone(range_, f"Property {s} missing range")

        for s, p, o in self.g.triples((None, RDF.type, OWL.DatatypeProperty)):
            if str(s).startswith(str(self.INF)):
                domain = self.g.value(s, RDFS.domain)
                range_ = self.g.value(s, RDFS.range)
                expected_domain = expected_domains.get(s)
                if expected_domain is not None:
                    if isinstance(expected_domain, list):
                        self.assertTrue(any(domain == d for d in expected_domain), 
                                      f"Property {s} has wrong domain: {domain}")
                    else:
                        self.assertEqual(domain, expected_domain, 
                                       f"Property {s} has wrong domain: {domain}")
                self.assertIsNotNone(range_, f"Property {s} missing range")

    def test_shacl_shapes(self):
        """Test that all classes have corresponding SHACL shapes"""
        classes = set()
        for s, p, o in self.g.triples((None, RDF.type, OWL.Class)):
            if str(s).startswith(str(self.INF)):
                classes.add(s)

        shapes = set()
        for s, p, o in self.g.triples((None, RDF.type, SH.NodeShape)):
            if str(s).startswith(str(self.INF)):
                target_class = self.g.value(s, SH.targetClass)
                shapes.add(target_class)

        self.assertEqual(classes, shapes, "Not all classes have corresponding SHACL shapes")

    def test_instances(self):
        """Test that all instances have required properties"""
        required_properties = {
            self.INF.VirtualMachine: [self.INF.hasName, self.INF.hasLocation, self.INF.hasSize],
            self.INF.NetworkInterface: [self.INF.hasName, self.INF.hasIPAddress],
            self.INF.NetworkSecurityGroup: [self.INF.hasName],
            self.INF.PublicIPAddress: [self.INF.hasName, self.INF.hasIPAddress],
            self.INF.Subnet: [self.INF.hasName],
            self.INF.SecurityRule: [self.INF.hasName, self.INF.hasPriority, self.INF.hasProtocol, self.INF.hasPort],
            self.INF.AutoShutdown: [self.INF.hasShutdownTime, self.INF.hasNotificationTime],
            self.INF.SpotInstance: [self.INF.hasName]
        }

        for instance_type, properties in required_properties.items():
            for s, p, o in self.g.triples((None, RDF.type, instance_type)):
                for prop in properties:
                    value = self.g.value(s, prop)
                    self.assertIsNotNone(value, f"Instance {s} missing required property {prop}")

    def test_guidance_compliance(self):
        """Test compliance with guidance ontology"""
        # Check for guidance relationships
        guidance_relationships = [
            (self.INF.VirtualMachine, self.GUIDANCE.hasValidationRule),
            (self.INF.NetworkInterface, self.GUIDANCE.hasValidationRule),
            (self.INF.NetworkSecurityGroup, self.GUIDANCE.hasValidationRule),
            (self.INF.PublicIPAddress, self.GUIDANCE.hasValidationRule),
            (self.INF.SecurityRule, self.GUIDANCE.hasValidationRule),
            (self.INF.Subnet, self.GUIDANCE.hasValidationRule),
            (self.INF.AutoShutdown, self.GUIDANCE.hasValidationRule),
            (self.INF.SpotInstance, self.GUIDANCE.hasValidationRule)
        ]

        for subject, predicate in guidance_relationships:
            has_relationship = False
            for s, p, o in self.g.triples((subject, predicate, None)):
                has_relationship = True
                break
            self.assertTrue(has_relationship, f"Missing guidance relationship for {subject}")

if __name__ == '__main__':
    unittest.main() 