CREATE TABLE base_model (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT
);

CREATE TABLE transformation (
    id VARCHAR PRIMARY KEY,
    source_id VARCHAR REFERENCES base_model(id),
    target_id VARCHAR REFERENCES base_model(id),
    FOREIGN KEY (id) REFERENCES base_model(id)
);

CREATE TABLE transformation_rule (
    id VARCHAR PRIMARY KEY,
    transformation_id VARCHAR REFERENCES transformation(id),
    FOREIGN KEY (id) REFERENCES base_model(id)
); 