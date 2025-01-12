# Streamlit Caching Discussion

## Initial Question
**Q:** Oh I see what you are doing. If someone selects the same row twice, it returns the cached result?

**A:** Yes, exactly! Based on the Streamlit documentation and search results, here's what's happening:

1. load_document_list() is correctly cached with @st.cache_data
2. When a user selects a file and extract_document_content() runs, that result is also cached

## Memory Management
**Q:** This *could* use gobs of memory. Is the cache smart enough to dump cache entries when under memory pressure?

**A:** Based on the documentation, Streamlit's caching system does not automatically dump cache entries under memory pressure. We need to explicitly configure:

- TTL (Time To Live) for cache expiration
- max_entries to limit cache size
- Manual cache clearing if needed

## Solution Evolution

### Initial Implementation
Added basic caching to document list query

```python
@st.cache_data(max_entries=100)
def load_document_list():
    docs_list = session.sql("SELECT DISTINCT METADATA$FILENAME as FILENAME FROM @INPUT_STAGE").to_pandas()
    return docs_list['FILENAME'].tolist()
```

### Final Implementation
Optimized implementation with proper session handling and cache limits

```python
@st.cache_resource
def get_snowflake_session():
    return session

@st.cache_data(ttl="1h", max_entries=20)
def extract_document_content(filename):
    snowflake_session = get_snowflake_session()
    escaped_filename = filename.replace("'", "''")
    doc_extract = snowflake_session.sql(f"SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@INPUT_STAGE','{escaped_filename}')")
    content_list = doc_extract.select(doc_extract["EXTRACTED_DATA"]).collect()
    return " ".join(str(row["EXTRACTED_DATA"]) for row in content_list)
```

## Key Learnings

### Cache Types

- Use @st.cache_data for data transformations and queries that return serializable objects (e.g., DataFrames, lists, dictionaries)
- Use @st.cache_resource for non-serializable objects and stateful connections (e.g., database connections, ML models, API clients)

### Memory Management

- Added max_entries=20 for document cache to prevent unbounded growth
- Added ttl="1h" for time-based cache invalidation
- Focus caching limits on heavy operations (document extraction)

### Best Practices

- Cache expensive operations
- Use appropriate cache decorators
- Set reasonable limits on cache size
- Consider TTL for data freshness
- Handle database connections properly with cache_resource
