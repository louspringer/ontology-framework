# Guidance Ontology Test Report
Generated: 2025-04-12T09:13:53.701929
Runtime: 9.28 seconds

## Summary
- Tests Run: 11
- Failures: 0
- Errors: 2
- Skipped: 0

## Details

### Errors

#### test_guidance.TestGuidanceOntology.test_test_coverage
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_guidance.py", line 253, in test_test_coverage
    results = list(self.g.query(query))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1621, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))  # type: ignore[arg-type]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 145, in query
    strOrQuery = translateQuery(parseQuery(strOrQuery), base, initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/parser.py", line 1553, in parseQuery
    return Query.parseString(q, parseAll=True)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/util.py", line 377, in _inner
    return fn(self, *args, **kwargs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/pyparsing/core.py", line 1212, in parse_string
    raise exc.with_traceback(None)
pyparsing.exceptions.ParseException: Expected SelectQuery, found 'BIND'  (at char 286), (line:10, col:13)

```

#### test_guidance.TestGuidanceOntology.test_validation_patterns_completeness
```
Traceback (most recent call last):
  File "/Users/lou/Documents/ontology-framework/tests/test_guidance.py", line 206, in test_validation_patterns_completeness
    results = list(self.g.query(query))
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/graph.py", line 1621, in query
    return result(processor.query(query_object, initBindings, initNs, **kwargs))  # type: ignore[arg-type]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/processor.py", line 145, in query
    strOrQuery = translateQuery(parseQuery(strOrQuery), base, initNs)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 933, in translateQuery
    q[1] = traverse(
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 468, in traverse
    r = _traverse(tree, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 427, in _traverse
    e[k] = _traverse(val, visitPre, visitPost)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in _traverse
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 421, in <listcomp>
    return [_traverse(x, visitPre, visitPost) for x in e]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 429, in _traverse
    _e = visitPost(e)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/algebra.py", line 193, in translatePName
    return prologue.absolutize(p)  # type: ignore[return-value]
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 468, in absolutize
    return self.resolvePName(iri.prefix, iri.localname)
  File "/Users/lou/miniconda3/envs/ontology-framework/lib/python3.10/site-packages/rdflib/plugins/sparql/sparql.py", line 450, in resolvePName
    raise Exception("Unknown namespace prefix : %s" % prefix)
Exception: Unknown namespace prefix : validation

```
