INSERT INTO users (username, email) VALUES
  ('alice', 'alice@example.com'),
  ('bob',   'bob@example.com'),
  ('charlie', 'charlie@example.com');

INSERT INTO posts (user_id, title, body, published) VALUES
  (1, 'First Post', 'Hello from Alice', TRUE),
  (1, 'Draft Post', 'Not published yet', FALSE),
  (2, 'Bob Post', 'Hello from Bob', TRUE);
