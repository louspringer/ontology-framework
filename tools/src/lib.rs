use wasm_bindgen::prelude::*;
use serde::{Serialize, Deserialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize)]
struct Triple {
    subject: String,
    predicate: String,
    object: String,
}

#[wasm_bindgen]
pub struct RDFEngine {
    triples: Vec<Triple>,
}

#[wasm_bindgen]
impl RDFEngine {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        RDFEngine {
            triples: Vec::new(),
        }
    }

    pub fn execute_query(&self, query: &str) -> Result<JsValue, JsError> {
        let results = self.triples.iter()
            .filter(|t| t.predicate == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            .map(|t| {
                let mut map = HashMap::new();
                map.insert("subject".to_string(), t.subject.clone());
                map.insert("object".to_string(), t.object.clone());
                map
            })
            .collect::<Vec<_>>();
        
        Ok(serde_wasm_bindgen::to_value(&results)?)
    }

    pub fn execute_update(&mut self, ttl: &str) -> Result<bool, JsError> {
        // Simple parser for N-Triples format
        for line in ttl.lines() {
            let line = line.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 3 {
                self.triples.push(Triple {
                    subject: parts[0].to_string(),
                    predicate: parts[1].to_string(),
                    object: parts[2].to_string(),
                });
            }
        }
        Ok(true)
    }

    pub fn execute_validation(&self, ttl: &str) -> Result<JsValue, JsError> {
        let mut validation_results = Vec::new();
        
        // Check for class definitions
        let has_classes = self.triples.iter().any(|t| {
            t.predicate == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" &&
            t.object == "http://www.w3.org/2002/07/owl#Class"
        });
        
        if !has_classes {
            validation_results.push("No owl:Class definitions found");
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