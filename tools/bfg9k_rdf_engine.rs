use wasm_bindgen::prelude::*;
use oxigraph::sparql::{QueryResults, QuerySolution};
use oxigraph::store::{Store, StoreBuilder};
use oxigraph::model::{Graph, NamedNode, Triple};
use oxigraph::io::GraphFormat;
use std::io::Cursor;

#[wasm_bindgen]
pub struct RDFEngine {
    store: Store,
}

#[wasm_bindgen]
impl RDFEngine {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        let store = StoreBuilder::new().build();
        RDFEngine { store }
    }

    #[wasm_bindgen]
    pub fn execute_query(&self, query: &str) -> Result<JsValue, JsError> {
        let results = self.store.query(query)?;
        let json_results = match results {
            QueryResults::Solutions(solutions) => {
                let mut rows = Vec::new();
                for solution in solutions {
                    let mut row = serde_json::Map::new();
                    for (var, term) in solution.iter() {
                        row.insert(var.to_string(), term.to_string().into());
                    }
                    rows.push(serde_json::Value::Object(row));
                }
                serde_json::Value::Array(rows)
            }
            QueryResults::Boolean(value) => value.into(),
            QueryResults::Graph(graph) => {
                let mut triples = Vec::new();
                for triple in graph.iter() {
                    triples.push(format!("{} {} {}", triple.subject, triple.predicate, triple.object));
                }
                serde_json::Value::Array(triples.into_iter().map(|s| s.into()).collect())
            }
        };
        Ok(serde_wasm_bindgen::to_value(&json_results)?)
    }

    #[wasm_bindgen]
    pub fn execute_update(&mut self, ttl: &str) -> Result<bool, JsError> {
        let mut graph = Graph::new();
        let cursor = Cursor::new(ttl.as_bytes());
        graph.read_from(cursor, GraphFormat::Turtle)?;
        
        for triple in graph.iter() {
            self.store.insert(triple)?;
        }
        Ok(true)
    }

    #[wasm_bindgen]
    pub fn execute_validation(&self, ttl: &str) -> Result<JsValue, JsError> {
        let mut graph = Graph::new();
        let cursor = Cursor::new(ttl.as_bytes());
        graph.read_from(cursor, GraphFormat::Turtle)?;

        // Basic validation rules
        let mut validation_results = Vec::new();
        
        // Check for required properties
        let required_props = ["rdfs:label", "rdfs:comment"];
        for triple in graph.iter() {
            if let Some(pred) = triple.predicate.as_named() {
                if !required_props.contains(&pred.as_str()) {
                    validation_results.push(format!(
                        "Warning: Triple {} {} {} uses non-standard predicate",
                        triple.subject, triple.predicate, triple.object
                    ));
                }
            }
        }

        // Check for class definitions
        let has_classes = graph.iter().any(|t| {
            t.predicate.as_named().map_or(false, |p| p.as_str() == "rdf:type") &&
            t.object.as_named().map_or(false, |o| o.as_str() == "owl:Class")
        });

        if !has_classes {
            validation_results.push("Error: No owl:Class definitions found".to_string());
        }

        Ok(serde_wasm_bindgen::to_value(&validation_results)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_validation() {
        let engine = RDFEngine::new();
        let ttl = r#"
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .

            :TestClass a owl:Class ;
                rdfs:label "Test Class" ;
                rdfs:comment "A test class" .
        "#;
        
        let results = engine.execute_validation(ttl).unwrap();
        let results: Vec<String> = serde_wasm_bindgen::from_value(results).unwrap();
        assert!(results.is_empty());
    }
} 