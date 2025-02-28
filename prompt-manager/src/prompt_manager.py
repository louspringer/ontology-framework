import time

import psycopg2


class PromptManager:
    def __init__(self):
        self._connect_with_retry()
        self.setup_db()

    def _connect_with_retry(self, max_retries=5):
        for attempt in range(max_retries):
            try:
                self.conn = psycopg2.connect(
                    "dbname=prompts user=promptuser password=promptpass host=localhost",
                )
                return
            except psycopg2.OperationalError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)

    def setup_db(self):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE,
                    content TEXT,
                    category VARCHAR(100),
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            )
        self.conn.commit()

    def add_prompt(self, name, content, category="general", tags=None):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO prompts (name, content, category, tags) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO UPDATE 
                SET content = EXCLUDED.content,
                    category = EXCLUDED.category,
                    tags = EXCLUDED.tags
                """,
                (name, content, category, tags or []),
            )
        self.conn.commit()

    def search_prompts(self, query):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, content, category, tags 
                FROM prompts 
                WHERE content ILIKE %s 
                OR name ILIKE %s 
                OR category ILIKE %s
                """,
                (f"%{query}%", f"%{query}%", f"%{query}%"),
            )
            return cur.fetchall()

    def list_prompts(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT name, category, tags FROM prompts ORDER BY name")
            return cur.fetchall()

    def list_with_ids(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, category, tags FROM prompts ORDER BY id")
            return cur.fetchall()

    def get_by_id(self, id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT content FROM prompts WHERE id = %s", (id,))
            result = cur.fetchone()
            return result[0] if result else None
