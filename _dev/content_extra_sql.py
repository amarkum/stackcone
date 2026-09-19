"""Extra teaching material for the SQL lessons (results come from a real SQLite run)."""
from extra_util import sql as _sql

SETUP = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT, age INTEGER);
INSERT INTO customers VALUES (1,'Ada','UK',36),(2,'Linus','FI',28),(3,'Grace','US',45);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL, status TEXT);
INSERT INTO orders VALUES (10,1,120.0,'paid'),(11,1,35.5,'paid'),(12,3,80.0,'refunded');
"""


def q(query, setup=SETUP):
    return _sql(setup, query)


EXTRA = {}

EXTRA["sql-introduction"] = {
    "intro": [
        ("h2", "Why databases exist"),
        ("p", "A spreadsheet works for a small list, but imagine an online shop with millions of customers, orders and products being read and changed by thousands of people at the same moment. You need something faster, safer and more organised. That is a <strong>database</strong>, and <strong>SQL</strong> (Structured Query Language) is the language you use to talk to it. It is over 40 years old and still the most important data skill in software, used by analysts, backend developers, data scientists and product managers alike."),
        ("p", "SQL is <em>declarative</em>: you describe <strong>what</strong> you want (\"the names of customers over 30\") and the database works out <strong>how</strong> to find it. That makes simple questions very short to write."),
    ],
    "more": [
        ("h2", "The vocabulary, with a picture"),
        ("p", "Think of a table as a spreadsheet tab with strict rules. Every <strong>column</strong> has a name and a type (text, number, date), and every <strong>row</strong> is one record. A <strong>database</strong> is a collection of related tables. A <strong>query</strong> is a question you ask about them."),
        ("ul", [
            "<strong>Table</strong>: a set of rows about one kind of thing, such as <code>customers</code>.",
            "<strong>Row</strong> (record): one customer.",
            "<strong>Column</strong> (field): one attribute, such as <code>country</code>.",
            "<strong>Primary key</strong>: a column that uniquely identifies each row, like <code>id</code>.",
            "<strong>Foreign key</strong>: a column that points at a row in another table, like <code>orders.customer_id</code>.",
        ]),
        ("h2", "Ask your first three questions"),
        ("p", "Every example on this page runs against the same two small tables, so you can follow along. Here is everything in <code>customers</code>:"),
        *q("SELECT * FROM customers"),
        ("p", "Now only two columns. The database returns exactly the columns you list, in the order you list them:"),
        *q("SELECT name, country FROM customers"),
        ("p", "And a question that needs a decision: which customers are older than 30?"),
        *q("SELECT name, age FROM customers WHERE age > 30"),
        ("h2", "Reading a query in plain English"),
        ("p", "Read <code>SELECT name, age FROM customers WHERE age &gt; 30</code> aloud in a different order and it becomes a sentence: \"<strong>From</strong> the customers table, <strong>keep</strong> the rows where age is over 30, and <strong>show me</strong> the name and age.\" SQL is written in a slightly unusual order but read it as that sentence and it always makes sense."),
        ("h2", "Two tables, one relationship"),
        ("p", "Orders live in their own table and refer to customers by id instead of repeating the customer's details. This is the core idea of relational databases: store each fact once, and link rows together. A quick look at <code>orders</code>:"),
        *q("SELECT * FROM orders"),
        ("p", "Customer 1 (Ada) appears twice because she placed two orders, and there is nothing for Linus (id 2) at all. The joins lesson shows how to combine the two tables into one answer."),
    ],
    "recap": [
        "A database holds tables; a table holds rows; each row has the same columns.",
        "A primary key uniquely identifies a row; a foreign key points at a row in another table.",
        "<code>SELECT columns FROM table WHERE condition</code> is the shape of most questions.",
        "SQL is declarative: say what you want, not how to get it.",
    ],
}

EXTRA["sql-select-where"] = {
    "intro": [
        ("h2", "The two most-used clauses"),
        ("p", "If you learn only two things in SQL, learn these. <strong>SELECT</strong> chooses which <em>columns</em> you see. <strong>WHERE</strong> chooses which <em>rows</em> you see. Almost every real query, from a small report to a complex dashboard, is built by adding to this pair."),
    ],
    "more": [
        ("h2", "Comparison operators"),
        *q("SELECT name, age FROM customers WHERE age >= 30 AND country <> 'FI'"),
        ("p", "The operators are <code>=</code>, <code>&lt;&gt;</code> (or <code>!=</code>), <code>&lt;</code>, <code>&gt;</code>, <code>&lt;=</code>, <code>&gt;=</code>. Note that SQL uses a single <code>=</code> to compare, unlike most programming languages. Text values go in single quotes; numbers do not."),
        ("h2", "AND, OR and parentheses"),
        ("p", "<code>AND</code> needs both sides true, <code>OR</code> needs one. When you mix them, use parentheses. Without them <code>AND</code> is evaluated first, which often is not what you meant."),
        *q("SELECT name, country, age FROM customers WHERE (country = 'UK' OR country = 'US') AND age > 40"),
        ("h2", "Patterns with LIKE"),
        ("p", "<code>LIKE</code> searches text. <code>%</code> matches any number of characters, and <code>_</code> matches exactly one. Use it for \"starts with\", \"ends with\" and \"contains\" searches."),
        *q("SELECT name FROM customers WHERE name LIKE 'G%'"),
        *q("SELECT name FROM customers WHERE name LIKE '%n%'"),
        ("h2", "Lists and ranges: IN and BETWEEN"),
        *q("SELECT name, country FROM customers WHERE country IN ('UK', 'FI')"),
        *q("SELECT name, age FROM customers WHERE age BETWEEN 30 AND 40"),
        ("p", "<code>BETWEEN</code> includes both ends. <code>IN</code> is a tidy way to write several <code>OR</code>s on the same column."),
        ("h2", "Missing values: IS NULL"),
        ("p", "<code>NULL</code> means \"unknown\", not zero and not empty text. You cannot test it with <code>=</code>; you must ask <code>IS NULL</code>. Here we add a customer with no age to see the difference."),
        *q("SELECT name FROM people WHERE age IS NULL", setup="CREATE TABLE people (name TEXT, age INTEGER); INSERT INTO people VALUES ('Ada',36),('Zed',NULL),('Kim',29);"),
        *q("SELECT name FROM people WHERE age = NULL", setup="CREATE TABLE people (name TEXT, age INTEGER); INSERT INTO people VALUES ('Ada',36),('Zed',NULL),('Kim',29);"),
        ("p", "The second query returns nothing at all: <code>age = NULL</code> is never true, because \"unknown equals unknown\" is itself unknown. This is one of the most common SQL bugs."),
    ],
    "recap": [
        "<code>SELECT</code> picks columns; <code>WHERE</code> picks rows.",
        "Combine conditions with <code>AND</code>/<code>OR</code> and use parentheses when mixing them.",
        "<code>LIKE</code> with <code>%</code> and <code>_</code> searches text; <code>IN</code> and <code>BETWEEN</code> shorten lists and ranges.",
        "Test for missing values with <code>IS NULL</code>, never <code>= NULL</code>.",
    ],
}

EXTRA["sql-sorting-aggregates"] = {
    "intro": [
        ("h2", "From rows to answers"),
        ("p", "Reading raw rows is useful, but the questions people actually ask are summaries: \"How many orders did we get?\", \"What is the average order value?\", \"Which country spends the most?\". SQL answers these with <strong>aggregate functions</strong>. First, though, you often want the rows in a sensible order, which is what <code>ORDER BY</code> does."),
    ],
    "more": [
        ("h2", "Sorting and limiting"),
        *q("SELECT name, age FROM customers ORDER BY age DESC"),
        *q("SELECT id, total FROM orders ORDER BY total DESC LIMIT 2"),
        ("p", "<code>ASC</code> (ascending) is the default. <code>LIMIT</code> keeps only the first rows after sorting, which is how you build \"top 10\" lists and pages of results."),
        ("h2", "Summarising with aggregate functions"),
        ("p", "An aggregate takes many rows and returns one value: <code>COUNT</code>, <code>SUM</code>, <code>AVG</code>, <code>MIN</code>, <code>MAX</code>."),
        *q("SELECT COUNT(*) AS orders, SUM(total) AS revenue, AVG(total) AS average, MAX(total) AS biggest FROM orders"),
        ("h2", "GROUP BY: one summary per group"),
        ("p", "Without <code>GROUP BY</code> an aggregate collapses everything into a single row. Add <code>GROUP BY column</code> and you get one result row per distinct value, which is how you answer \"per country\", \"per month\" or \"per customer\" questions."),
        *q("SELECT status, COUNT(*) AS n, SUM(total) AS money FROM orders GROUP BY status"),
        *q("SELECT customer_id, COUNT(*) AS orders, SUM(total) AS spent FROM orders GROUP BY customer_id ORDER BY spent DESC"),
        ("h2", "The order SQL actually runs things"),
        ("p", "You write <code>SELECT</code> first, but the database processes clauses in a different order. Knowing it explains most error messages."),
        ("ul", [
            "<code>FROM</code>: pick the table.",
            "<code>WHERE</code>: throw away rows that do not match.",
            "<code>GROUP BY</code>: bundle the remaining rows into groups.",
            "<code>HAVING</code>: throw away whole groups that do not match.",
            "<code>SELECT</code>: compute the columns to show.",
            "<code>ORDER BY</code> then <code>LIMIT</code>: sort and trim the final result.",
        ]),
        ("h2", "WHERE versus HAVING, with a real example"),
        *q("SELECT customer_id, SUM(total) AS spent FROM orders WHERE status = 'paid' GROUP BY customer_id HAVING SUM(total) > 100"),
        ("p", "<code>WHERE status = 'paid'</code> removes the refunded order <em>before</em> grouping. <code>HAVING SUM(total) &gt; 100</code> then removes customers whose paid total is too small <em>after</em> grouping. You cannot put an aggregate inside <code>WHERE</code>."),
    ],
    "recap": [
        "<code>ORDER BY</code> sorts (<code>DESC</code> for descending); <code>LIMIT</code> keeps the top rows.",
        "Aggregates (<code>COUNT</code>, <code>SUM</code>, <code>AVG</code>, <code>MIN</code>, <code>MAX</code>) turn many rows into one value.",
        "<code>GROUP BY</code> gives one result row per group.",
        "<code>WHERE</code> filters rows before grouping; <code>HAVING</code> filters groups after.",
    ],
}

EXTRA["sql-joins"] = {
    "intro": [
        ("h2", "Why data is split across tables"),
        ("p", "Imagine storing the customer's name, country and age on every one of their orders. If Ada moves country you would have to fix hundreds of rows, and miss one. Good design keeps each fact in exactly one place: customers in one table, orders in another, linked by an id. A <strong>join</strong> temporarily stitches those tables back together when you need an answer that spans both."),
        ("p", "Picture two lists on a table. A join lays a line from each order to its customer wherever the ids match, then reads across."),
    ],
    "more": [
        ("h2", "INNER JOIN: only rows that match on both sides"),
        *q("SELECT c.name, o.id AS order_id, o.total FROM customers c INNER JOIN orders o ON o.customer_id = c.id"),
        ("p", "Linus placed no orders, so he does not appear. An inner join keeps only the pairs that have a match. The <code>ON</code> clause is the matching rule, and <code>c</code> and <code>o</code> are short aliases so we can write <code>c.name</code> and <code>o.total</code> without ambiguity."),
        ("h2", "LEFT JOIN: keep everyone from the left table"),
        *q("SELECT c.name, o.id AS order_id, o.total FROM customers c LEFT JOIN orders o ON o.customer_id = c.id"),
        ("p", "Now Linus appears, with <code>NULL</code> where the order columns would be. Use a left join when you want \"all customers, and their orders if they have any\"."),
        ("h2", "The classic use: find what is missing"),
        *q("SELECT c.name FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.id IS NULL"),
        ("p", "\"Customers who never ordered\" is a left join plus a check for <code>NULL</code> on the right side. Learn this pattern; you will use it constantly."),
        ("h2", "Joining and summarising together"),
        *q("SELECT c.name, COUNT(o.id) AS orders, COALESCE(SUM(o.total), 0) AS spent FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name ORDER BY spent DESC"),
        ("p", "<code>COUNT(o.id)</code> counts only real orders (it ignores <code>NULL</code>), and <code>COALESCE</code> replaces a missing sum with 0. This single query is a real customer report."),
        ("h2", "Debugging a join that returns too many rows"),
        ("ul", [
            "<strong>Forgot the ON clause</strong>: every row pairs with every row (a cartesian product).",
            "<strong>Joining on the wrong column</strong>: check that you match a foreign key to the primary key it points at.",
            "<strong>Duplicate matches</strong>: if the right table has several matching rows, the left row repeats. That is correct, but it inflates sums, so aggregate carefully.",
        ]),
    ],
    "recap": [
        "Join tables on a foreign key = primary key match using <code>ON</code>.",
        "<code>INNER JOIN</code> keeps matches only; <code>LEFT JOIN</code> keeps every left row, using <code>NULL</code> when nothing matches.",
        "Left join plus <code>IS NULL</code> finds rows with no partner.",
        "Aliases (<code>c</code>, <code>o</code>) keep multi-table queries readable.",
    ],
}

EXTRA["sql-modifying-data"] = {
    "intro": [
        ("h2", "From reading to changing"),
        ("p", "Until now every query only <em>read</em> data. Real applications also create, edit and remove it: signing up adds a row, changing your email edits one, closing an account deletes one. Those three actions are <code>INSERT</code>, <code>UPDATE</code> and <code>DELETE</code>. Because they change data permanently, they deserve extra care, which is why this lesson also covers transactions."),
    ],
    "more": [
        ("h2", "Seeing a change happen"),
        *q("INSERT INTO customers (id, name, country, age) VALUES (4, 'Kim', 'KR', 29); SELECT id, name FROM customers"),
        ("h2", "UPDATE: always check your WHERE first"),
        ("p", "An <code>UPDATE</code> without <code>WHERE</code> changes <strong>every row</strong>. A safe habit is to write the same <code>WHERE</code> in a <code>SELECT</code> first, confirm it returns the rows you expect, and only then turn it into an <code>UPDATE</code>."),
        *q("UPDATE orders SET status = 'paid' WHERE id = 12; SELECT id, status FROM orders ORDER BY id"),
        ("h2", "DELETE works the same way"),
        *q("DELETE FROM orders WHERE status = 'refunded'; SELECT id, status FROM orders"),
        ("h2", "Why transactions matter"),
        ("p", "Moving money between accounts takes two steps: subtract from one, add to the other. If the program crashes between them, money vanishes. A <strong>transaction</strong> groups steps so either all succeed or none do. Put <code>BEGIN</code> first, <code>COMMIT</code> to keep the changes, or <code>ROLLBACK</code> to undo them."),
        *q("BEGIN; UPDATE accounts SET balance = balance - 50 WHERE id = 1; UPDATE accounts SET balance = balance + 50 WHERE id = 2; COMMIT; SELECT id, balance FROM accounts ORDER BY id", setup="CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER); INSERT INTO accounts VALUES (1,100),(2,20);"),
        ("note", "Back up before you experiment", "On a production database, run risky changes inside a transaction first and check the result before committing. Most teams also restrict who may run <code>DELETE</code> and <code>UPDATE</code> at all."),
    ],
    "recap": [
        "<code>INSERT</code> adds rows, <code>UPDATE</code> edits them, <code>DELETE</code> removes them.",
        "Always include a <code>WHERE</code> on <code>UPDATE</code> and <code>DELETE</code>; test it with <code>SELECT</code> first.",
        "Transactions make multi-step changes all-or-nothing (<code>BEGIN</code>, <code>COMMIT</code>, <code>ROLLBACK</code>).",
    ],
}

EXTRA["sql-schema-design"] = {
    "intro": [
        ("h2", "Design before you build"),
        ("p", "The tables you create decide how easy every future query will be. A good schema stops bad data from ever entering the database (an order for a customer who does not exist, two accounts with the same email) and avoids storing the same fact in many places. Spending ten minutes on design saves months of clean-up."),
        ("p", "A simple method: list the <em>things</em> your application knows about (customers, orders, products). Each becomes a table. Then ask how they relate: one customer has many orders, so each order stores its customer's id."),
    ],
    "more": [
        ("h2", "A schema that protects itself"),
        ("p", "Constraints are rules the database enforces for you, so bugs in your application cannot corrupt the data. Here the database itself rejects an order that points at a customer who does not exist."),
        ("code", "sql", "CREATE TABLE customers (\n  id      INTEGER PRIMARY KEY,\n  email   TEXT NOT NULL UNIQUE,\n  name    TEXT NOT NULL\n);\n\nCREATE TABLE orders (\n  id           INTEGER PRIMARY KEY,\n  customer_id  INTEGER NOT NULL REFERENCES customers(id),\n  total        REAL NOT NULL CHECK (total >= 0),\n  created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP\n);"),
        ("ul", [
            "<code>PRIMARY KEY</code>: unique, never null; identifies the row.",
            "<code>NOT NULL</code>: the value is required.",
            "<code>UNIQUE</code>: no two rows may share this value (two users cannot register the same email).",
            "<code>REFERENCES</code>: a foreign key; the value must exist in the other table.",
            "<code>CHECK</code>: a custom rule, such as a total that cannot be negative.",
            "<code>DEFAULT</code>: what to store when no value is given.",
        ]),
        ("h2", "Seeing constraints in action"),
        ("p", "Trying to break a rule produces an error instead of bad data. This is exactly what you want."),
        ("code", "sql", "INSERT INTO orders (customer_id, total) VALUES (999, 10);"),
        ("output", "Error: FOREIGN KEY constraint failed"),
        ("code", "sql", "INSERT INTO customers (email, name) VALUES ('ada@example.com', 'Ada');\nINSERT INTO customers (email, name) VALUES ('ada@example.com', 'Ada Two');"),
        ("output", "Error: UNIQUE constraint failed: customers.email"),
        ("h2", "Many-to-many needs a bridge table"),
        ("p", "A student can join many courses and a course has many students. You cannot store that in either table alone, so you add a third table holding one row per pairing."),
        ("code", "sql", "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL);\nCREATE TABLE courses  (id INTEGER PRIMARY KEY, title TEXT NOT NULL);\n\nCREATE TABLE enrollments (\n  student_id INTEGER NOT NULL REFERENCES students(id),\n  course_id  INTEGER NOT NULL REFERENCES courses(id),\n  PRIMARY KEY (student_id, course_id)   -- a student can enrol only once per course\n);"),
    ],
    "recap": [
        "Each kind of thing gets its own table; relationships use foreign keys.",
        "Constraints (<code>NOT NULL</code>, <code>UNIQUE</code>, <code>REFERENCES</code>, <code>CHECK</code>) reject bad data automatically.",
        "Many-to-many relationships need a bridge table.",
        "Store each fact once; that is the heart of normalization.",
    ],
}

EXTRA["sql-indexes-performance"] = {
    "intro": [
        ("h2", "Why queries get slow"),
        ("p", "With 100 rows every query feels instant, whatever you write. With 100 million rows, the way the database finds data matters enormously. Without help it must read <em>every row</em> to find matches, a <strong>full table scan</strong>, like finding a name by reading a phone book from page one. An <strong>index</strong> is the alphabetical order that lets it jump straight to the right page."),
    ],
    "more": [
        ("h2", "See the difference with EXPLAIN"),
        ("p", "Databases can describe their plan for a query. Below, the same search is run before and after adding an index. The plan changes from a scan of the whole table to a direct search through the index."),
        *_sql("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, city TEXT);", "EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'ada@example.com'")[:1],
        ("output", "SCAN users"),
        ("code", "sql", "CREATE INDEX idx_users_email ON users(email);\nEXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'ada@example.com';"),
        ("output", "SEARCH users USING INDEX idx_users_email (email=?)"),
        ("p", "<code>SCAN</code> means \"read everything\"; <code>SEARCH ... USING INDEX</code> means \"jump to the match.\" The words differ between databases (PostgreSQL says <em>Seq Scan</em> and <em>Index Scan</em>) but the idea is identical."),
        ("h2", "What to index"),
        ("ul", [
            "Columns you filter on often in <code>WHERE</code> (email, status, created_at).",
            "Foreign-key columns used in joins (<code>orders.customer_id</code>).",
            "Columns you sort by frequently.",
        ]),
        ("h2", "Indexes are not free"),
        ("p", "Every index takes disk space and must be updated on each <code>INSERT</code>, <code>UPDATE</code> and <code>DELETE</code>. Too many indexes make writes slow. Add them for real, measured slow queries, not on every column just in case."),
        ("h2", "A tuning routine that works"),
        ("ul", [
            "<strong>Measure first</strong>: find which query is actually slow (most databases have a slow-query log).",
            "<strong>Explain it</strong>: does the plan show a full scan on a big table?",
            "<strong>Fix the cause</strong>: add an index, select fewer columns, or rewrite the filter so the index can be used.",
            "<strong>Measure again</strong>: confirm the plan and the time both improved.",
        ]),
    ],
    "recap": [
        "Without an index the database scans every row; an index lets it jump to matches.",
        "Use <code>EXPLAIN</code> to see whether a query scans or searches an index.",
        "Index columns you filter, join and sort on; avoid indexing everything.",
        "Measure before and after; guessing is not tuning.",
    ],
}
