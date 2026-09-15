#!/usr/bin/env python3
"""Generate learn/ catalog, lessons, and courses.json."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "learn"

TRACKS = {
    "python": {
        "label": "Python",
        "parent": "Coding",
        "color": "#3776ab",
        "description": "From your first print() to classes, files, and exceptions.",
    },
    "java": {
        "label": "Java",
        "parent": "Coding",
        "color": "#e76f00",
        "description": "Static typing, OOP, and the collections you use every day.",
    },
    "data-structures": {
        "label": "Data Structures",
        "parent": None,
        "color": "#7c3aed",
        "description": "Arrays, lists, trees, graphs, and why Big O matters.",
    },
}

LESSONS = [
    # Python
    {"slug": "python-hello-world", "track": "python", "title": "Hello, Python", "minutes": 8, "level": "Beginner",
     "summary": "Install Python, run your first script, and understand how the interpreter works.",
     "objectives": ["Run Python from the terminal", "Use print() and comments", "Understand .py files"],
     "sections": [
         ("p", "Python is an interpreted language — you write text, the interpreter runs it line by line. No compile step before you see output."),
         ("h2", "Your first program"),
         ("code", "python", 'print("Hello, stackcone!")\nprint(2 + 2)'),
         ("p", "Save as <code>hello.py</code> and run:"),
         ("code", "bash", "python3 hello.py"),
         ("exercise", "Change the program to print your name and today's year on two separate lines."),
     ]},
    {"slug": "python-variables-and-types", "track": "python", "title": "Variables and Types", "minutes": 12, "level": "Beginner",
     "summary": "Names, assignment, and the core built-in types: int, float, str, and bool.",
     "objectives": ["Assign and reassign variables", "Use type() to inspect values", "Cast between types"],
     "sections": [
         ("p", "A variable is a name bound to a value. Python figures out the type at runtime — you do not declare it."),
         ("h2", "Core types"),
         ("code", "python", 'age = 28\nprice = 19.99\nname = "Amar"\nactive = True\n\nprint(type(age), type(price), type(name), type(active))'),
         ("h2", "Type conversion"),
         ("code", "python", 'n = int("42")\ns = str(3.14)\nprint(n + 1, s)'),
         ("exercise", "Create variables for a product title, price, and in-stock flag. Print a one-line summary string."),
     ]},
    {"slug": "python-control-flow", "track": "python", "title": "Control Flow", "minutes": 15, "level": "Beginner",
     "summary": "if/elif/else, for loops, while loops, and when to use each.",
     "objectives": ["Branch with if/elif/else", "Iterate with for and range()", "Use while with a clear exit"],
     "sections": [
         ("h2", "Conditionals"),
         ("code", "python", 'score = 87\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelse:\n    grade = "C"\nprint(grade)'),
         ("h2", "Loops"),
         ("code", "python", 'for i in range(3):\n    print("tick", i)\n\ncount = 3\nwhile count > 0:\n    print(count)\n    count -= 1'),
         ("exercise", "Print even numbers from 2 to 20 using a for loop."),
     ]},
    {"slug": "python-functions", "track": "python", "title": "Functions", "minutes": 14, "level": "Beginner",
     "summary": "Define reusable blocks with parameters, return values, and default arguments.",
     "objectives": ["Define functions with def", "Return values", "Use default parameters"],
     "sections": [
         ("code", "python", 'def greet(name, excited=False):\n    msg = f"Hello, {name}"\n    return msg + "!" if excited else msg\n\nprint(greet("world"))\nprint(greet("world", excited=True))'),
         ("exercise", "Write a function <code>area_rect(w, h)</code> that returns width × height."),
     ]},
    {"slug": "python-lists-tuples", "track": "python", "title": "Lists and Tuples", "minutes": 16, "level": "Beginner",
     "summary": "Ordered sequences — mutable lists vs immutable tuples.",
     "objectives": ["Create and slice lists", "Use list methods append/pop", "Know when tuples beat lists"],
     "sections": [
         ("code", "python", 'nums = [10, 20, 30]\nnums.append(40)\nprint(nums[1:3])\n\npoint = (3, 4)\nprint(point[0])'),
         ("exercise", "Given <code>scores = [88, 92, 75, 95]</code>, print the highest score without using max()."),
     ]},
    {"slug": "python-dictionaries", "track": "python", "title": "Dictionaries and Sets", "minutes": 14, "level": "Beginner",
     "summary": "Key-value maps and unordered unique collections.",
     "objectives": ["Read and write dict keys", "Iterate .items()", "Use sets for uniqueness"],
     "sections": [
         ("code", "python", 'user = {"id": 1, "email": "dev@example.com"}\nuser["role"] = "admin"\n\nfor key, val in user.items():\n    print(key, val)\n\ntags = {"python", "api", "python"}\nprint(tags)'),
         ("exercise", "Build a word-frequency dict from a sentence string."),
     ]},
    {"slug": "python-oop-classes", "track": "python", "title": "Classes and Objects", "minutes": 18, "level": "Intermediate",
     "summary": "Model data with classes, __init__, methods, and self.",
     "objectives": ["Define a class with __init__", "Add instance methods", "Understand self"],
     "sections": [
         ("code", "python", 'class BankAccount:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self.balance = balance\n\n    def deposit(self, amount):\n        self.balance += amount\n\nacct = BankAccount("Amar", 100)\nacct.deposit(50)\nprint(acct.balance)'),
         ("exercise", "Add a <code>withdraw</code> method that refuses negative balances."),
     ]},
    {"slug": "python-file-handling", "track": "python", "title": "File Handling", "minutes": 12, "level": "Intermediate",
     "summary": "Read and write text files safely with context managers.",
     "objectives": ["Use with open()", "Read and write text", "Handle missing files"],
     "sections": [
         ("code", "python", 'with open("notes.txt", "w", encoding="utf-8") as f:\n    f.write("first line\\n")\n\nwith open("notes.txt", encoding="utf-8") as f:\n    print(f.read())'),
         ("exercise", "Write a function that counts lines in a file path."),
     ]},
    {"slug": "python-error-handling", "track": "python", "title": "Error Handling", "minutes": 13, "level": "Intermediate",
     "summary": "try/except/finally and raising your own exceptions.",
     "objectives": ["Catch specific exceptions", "Use finally for cleanup", "Raise ValueError with a message"],
     "sections": [
         ("code", "python", 'def parse_port(text):\n    try:\n        port = int(text)\n    except ValueError:\n        raise ValueError(f"invalid port: {text}") from None\n    if not 1 <= port <= 65535:\n        raise ValueError("port out of range")\n    return port'),
         ("exercise", "Wrap file reading in try/except and return None if the file is missing."),
     ]},
    # Java
    {"slug": "java-hello-world", "track": "java", "title": "Hello, Java", "minutes": 10, "level": "Beginner",
     "summary": "JDK setup, your first class, and the main method.",
     "objectives": ["Understand public class and main", "Compile with javac", "Run with java"],
     "sections": [
         ("code", "java", 'public class Hello {\n    public static void main(String[] args) {\n        System.out.println("Hello, stackcone!");\n    }\n}'),
         ("code", "bash", "javac Hello.java\njava Hello"),
         ("exercise", "Print two lines: your name and a favorite language."),
     ]},
    {"slug": "java-variables-types", "track": "java", "title": "Variables and Types", "minutes": 14, "level": "Beginner",
     "summary": "Primitives, Strings, final, and basic operators.",
     "objectives": ["Declare typed variables", "Use String concatenation", "Know int vs long vs double"],
     "sections": [
         ("code", "java", 'int count = 3;\ndouble price = 9.99;\nString title = "Widget";\nfinal int MAX = 100;\n\nSystem.out.println(title + " costs " + price);'),
         ("exercise", "Declare variables for a product SKU, quantity, and unit price; print total."),
     ]},
    {"slug": "java-control-flow", "track": "java", "title": "Control Flow", "minutes": 15, "level": "Beginner",
     "summary": "if/else, for, while, and enhanced for-each loops.",
     "objectives": ["Write if/else chains", "Use for and while", "Iterate arrays with for-each"],
     "sections": [
         ("code", "java", 'int[] scores = {88, 92, 75};\nfor (int s : scores) {\n    if (s >= 90) {\n        System.out.println("A");\n    } else {\n        System.out.println("pass");\n    }\n}'),
         ("exercise", "Print numbers 1–10, skipping 5."),
     ]},
    {"slug": "java-oop-classes", "track": "java", "title": "Classes and Objects", "minutes": 18, "level": "Intermediate",
     "summary": "Fields, constructors, methods, and encapsulation with private.",
     "objectives": ["Define a class with fields", "Write a constructor", "Add getters/setters"],
     "sections": [
         ("code", "java", 'public class User {\n    private final String email;\n    private int loginCount;\n\n    public User(String email) {\n        this.email = email;\n        this.loginCount = 0;\n    }\n\n    public void recordLogin() {\n        loginCount++;\n    }\n\n    public int getLoginCount() {\n        return loginCount;\n    }\n}'),
         ("exercise", "Add a <code>getEmail()</code> method and a <code>resetLogins()</code> method."),
     ]},
    {"slug": "java-collections", "track": "java", "title": "Collections Framework", "minutes": 17, "level": "Intermediate",
     "summary": "ArrayList, HashMap, and when to pick each.",
     "objectives": ["Use ArrayList add/get", "Store key-value in HashMap", "Iterate with for-each"],
     "sections": [
         ("code", "java", 'import java.util.*;\n\nList<String> tags = new ArrayList<>();\ntags.add("java");\ntags.add("api");\n\nMap<String, Integer> stock = new HashMap<>();\nstock.put("widget", 42);\n\nfor (String t : tags) {\n    System.out.println(t);\n}'),
         ("exercise", "Count word frequency in a sentence using a HashMap."),
     ]},
    {"slug": "java-exceptions", "track": "java", "title": "Exception Handling", "minutes": 13, "level": "Intermediate",
     "summary": "try/catch/finally and throwing checked exceptions.",
     "objectives": ["Catch NumberFormatException", "Use finally", "Throw IllegalArgumentException"],
     "sections": [
         ("code", "java", 'public static int parsePositive(String raw) {\n    try {\n        int n = Integer.parseInt(raw);\n        if (n <= 0) throw new IllegalArgumentException("must be positive");\n        return n;\n    } catch (NumberFormatException e) {\n        throw new IllegalArgumentException("not a number", e);\n    }\n}'),
         ("exercise", "Write a method that divides two ints and returns 0 on divide-by-zero."),
     ]},
    # Data structures
    {"slug": "ds-introduction", "track": "data-structures", "title": "What Are Data Structures?", "minutes": 10, "level": "Beginner",
     "summary": "Why structure matters, abstract data types, and how interviews use them.",
     "objectives": ["Define data structure vs algorithm", "Name common ADTs", "Connect to real code (lists, maps)"],
     "sections": [
         ("p", "A data structure is how you organize data in memory so operations are fast enough for your problem. Picking the wrong one is how a feature that should be instant becomes a timeout."),
         ("h2", "Common structures"),
         ("p", "Arrays, linked lists, stacks, queues, trees, hash tables, and graphs — each optimizes different operations (lookup, insert, order, relationships)."),
         ("exercise", "For a chat app's \"recent messages\" feature, would you prioritize fast append or fast lookup by ID?"),
     ]},
    {"slug": "ds-arrays", "track": "data-structures", "title": "Arrays", "minutes": 12, "level": "Beginner",
     "summary": "Contiguous memory, index access, and resize costs.",
     "objectives": ["O(1) index access", "Understand fixed vs dynamic arrays", "Know when cache locality helps"],
     "sections": [
         ("p", "An array stores elements in contiguous memory. Access by index is O(1). Inserting in the middle is O(n) because elements shift."),
         ("code", "python", 'nums = [10, 20, 30, 40]\nprint(nums[2])      # O(1) access\nnums.insert(1, 15)  # O(n) insert'),
         ("exercise", "Given an array, write a function to reverse it in-place."),
     ]},
    {"slug": "ds-linked-lists", "track": "data-structures", "title": "Linked Lists", "minutes": 14, "level": "Intermediate",
     "summary": "Nodes, pointers, singly vs doubly linked, and tradeoffs vs arrays.",
     "objectives": ["Describe a node structure", "Insert at head in O(1)", "Compare to arrays"],
     "sections": [
         ("code", "python", 'class Node:\n    def __init__(self, val, nxt=None):\n        self.val = val\n        self.next = nxt\n\nhead = Node(1, Node(2, Node(3)))\ncur = head\nwhile cur:\n    print(cur.val)\n    cur = cur.next'),
         ("exercise", "Implement a function to count nodes in a singly linked list."),
     ]},
    {"slug": "ds-stacks-queues", "track": "data-structures", "title": "Stacks and Queues", "minutes": 13, "level": "Intermediate",
     "summary": "LIFO stacks, FIFO queues, and everyday uses (undo, BFS).",
     "objectives": ["Implement stack with list append/pop", "Use collections.deque for queue", "Name real-world uses"],
     "sections": [
         ("code", "python", 'from collections import deque\n\nstack = []\nstack.append("a")\nstack.append("b")\nprint(stack.pop())\n\nqueue = deque()\nqueue.append("first")\nqueue.append("second")\nprint(queue.popleft())'),
         ("exercise", "Use a stack to check if a string of parentheses is balanced."),
     ]},
    {"slug": "ds-trees", "track": "data-structures", "title": "Trees", "minutes": 16, "level": "Intermediate",
     "summary": "Binary trees, traversals, and binary search trees.",
     "objectives": ["Define root, child, leaf", "Walk in-order traversal", "Understand BST ordering"],
     "sections": [
         ("code", "python", 'class TreeNode:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef inorder(node):\n    if not node:\n        return\n    inorder(node.left)\n    print(node.val)\n    inorder(node.right)'),
         ("exercise", "Write a function that returns the height of a binary tree."),
     ]},
    {"slug": "ds-hash-tables", "track": "data-structures", "title": "Hash Tables", "minutes": 14, "level": "Intermediate",
     "summary": "Hash functions, collisions, and average O(1) lookup.",
     "objectives": ["Explain hash → bucket", "Use dict/HashMap", "Know collision strategies exist"],
     "sections": [
         ("p", "A hash table maps keys to buckets via a hash function. Average lookup is O(1); worst case O(n) when many keys collide."),
         ("code", "python", 'cache = {}\ncache["user:42"] = {"name": "Amar"}\nprint(cache.get("user:42"))'),
         ("exercise", "Implement a function that returns the first duplicate character in a string using a set."),
     ]},
    {"slug": "ds-graphs", "track": "data-structures", "title": "Graphs", "minutes": 16, "level": "Advanced",
     "summary": "Vertices, edges, adjacency lists, BFS and DFS intuition.",
     "objectives": ["Represent a graph as adjacency list", "Run BFS for shortest unweighted path", "Know when graphs model real systems"],
     "sections": [
         ("code", "python", 'from collections import deque\n\ngraph = {\n    "A": ["B", "C"],\n    "B": ["D"],\n    "C": [],\n    "D": [],\n}\n\ndef bfs(start):\n    seen = {start}\n    q = deque([start])\n    while q:\n        node = q.popleft()\n        print(node)\n        for nxt in graph[node]:\n            if nxt not in seen:\n                seen.add(nxt)\n                q.append(nxt)'),
         ("exercise", "Add a target to BFS and return the path when found."),
     ]},
    {"slug": "ds-big-o", "track": "data-structures", "title": "Big O Notation", "minutes": 15, "level": "Intermediate",
     "summary": "Worst-case growth rates and comparing algorithms.",
     "objectives": ["Read O(1), O(n), O(log n), O(n²)", "Drop constants in big-O", "Pick structure by operation cost"],
     "sections": [
         ("p", "Big O describes how runtime or memory grows as input size n grows. We care about the dominant term, not whether you save 2× with a faster CPU."),
         ("h2", "Common complexities"),
         ("p", "O(1) — hash lookup. O(log n) — binary search. O(n) — scan an array. O(n log n) — good sorts. O(n²) — nested loops over n."),
         ("exercise", "What is the complexity of finding duplicates with nested loops vs a hash set?"),
     ]},
]

# wire prev/next per track
by_track: dict[str, list] = {}
for les in LESSONS:
    by_track.setdefault(les["track"], []).append(les)
for track_lessons in by_track.values():
    for i, les in enumerate(track_lessons):
        les["lesson_num"] = i + 1
        les["lesson_total"] = len(track_lessons)
        les["prev"] = track_lessons[i - 1]["slug"] if i > 0 else None
        les["next"] = track_lessons[i + 1]["slug"] if i < len(track_lessons) - 1 else None


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_section(item: tuple) -> str:
    kind, *rest = item
    if kind == "p":
        return f"      <p>{rest[0]}</p>"
    if kind == "h2":
        return f"      <h2>{esc(rest[0])}</h2>"
    if kind == "code":
        lang, code = rest
        return f"      <div class=\"learn-code-wrap\"><span class=\"learn-code-lang\">{esc(lang)}</span><pre><code>{esc(code)}</code></pre></div>"
    if kind == "exercise":
        return f"      <div class=\"learn-exercise\"><h3>Try it yourself</h3><p>{rest[0]}</p></div>"
    return ""


def lesson_html(les: dict) -> str:
    track = TRACKS[les["track"]]
    track_slug = les["track"]
    sidebar_items = []
    for t in by_track[track_slug]:
        active = " is-active" if t["slug"] == les["slug"] else ""
        done = " is-done" if t["lesson_num"] < les["lesson_num"] else ""
        sidebar_items.append(
            f'          <a class="learn-sidebar-link{active}{done}" href="/learn/courses/{t["slug"]}/">'
            f'<span class="learn-sidebar-num">{t["lesson_num"]}</span>{esc(t["title"])}</a>'
        )
    sidebar = "\n".join(sidebar_items)
    objectives = "".join(f"<li>{esc(o)}</li>" for o in les["objectives"])
    sections = "\n".join(render_section(s) for s in les["sections"])
    prev_link = (
        f'<a class="learn-nav-btn" href="/learn/courses/{les["prev"]}/">← Previous</a>'
        if les["prev"] else '<span class="learn-nav-btn is-disabled">← Previous</span>'
    )
    next_link = (
        f'<a class="learn-nav-btn learn-nav-btn--primary" href="/learn/courses/{les["next"]}/">Next lesson →</a>'
        if les["next"] else '<span class="learn-nav-btn is-disabled">Next lesson →</span>'
    )
    parent = track["parent"]
    breadcrumb_parent = f' / <a href="/learn/#track-{track_slug}">{esc(track["label"])}</a>' if parent else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="index, follow">
  <title>{esc(les["title"])} | {esc(track["label"])} | stackcone Learn</title>
  <meta name="description" content="{esc(les["summary"])}">
  <link rel="canonical" href="https://stackcone.com/learn/courses/{les["slug"]}/">
  <link rel="icon" type="image/png" href="/favicon/dark-favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/blog/blog.css?v=4">
  <link rel="stylesheet" href="/learn/learn.css?v=1">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B29M3GX6QM"></script>
  <script src="/assets/analytics.js" defer></script>
</head>
<body class="learn-page">
  <header class="header">
    <div class="nav-overlay" id="nav-overlay" aria-hidden="true"></div>
    <div class="header-inner">
      <a href="/" class="logo-link"><img src="/logo/stackcone.png" alt="stackcone" class="logo" width="280" height="60"></a>
      <button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav">
        <span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span>
      </button>
      <nav class="nav" id="main-nav" aria-label="Main navigation"></nav>
    </div>
  </header>

  <main class="learn-main">
    <div class="learn-main-inner">
      <p class="learn-breadcrumb"><a href="/learn/">Learn</a>{breadcrumb_parent} / {esc(les["title"])}</p>
      <div class="learn-layout">
        <aside class="learn-sidebar" aria-label="Course lessons">
          <div class="learn-sidebar-head">
            <p class="learn-sidebar-track">{esc(track["label"])}</p>
            <p class="learn-sidebar-progress">Lesson {les["lesson_num"]} of {les["lesson_total"]}</p>
          </div>
          <nav class="learn-sidebar-lessons">
{sidebar}
          </nav>
        </aside>
        <article class="blog-article learn-lesson">
          <div class="learn-lesson-meta">
            <span class="learn-badge">{esc(les["level"])}</span>
            <span class="learn-duration">{les["minutes"]} min</span>
          </div>
          <h1>{esc(les["title"])}</h1>
          <p class="learn-summary">{esc(les["summary"])}</p>
          <div class="learn-objectives">
            <h2>What you will learn</h2>
            <ul>{objectives}</ul>
          </div>
{sections}
          <nav class="learn-lesson-nav" aria-label="Lesson navigation">
            {prev_link}
            {next_link}
          </nav>
          <aside class="blog-cta">
            <h2>Want a custom curriculum for your team?</h2>
            <p>stackcone builds internal training, workshops, and production engineering courses tailored to your stack.</p>
            <div class="blog-cta-links">
              <a href="https://www.upwork.com/agencies/2022687811186513260/" class="cta cta--primary" rel="noopener noreferrer">Hire us on Upwork</a>
              <a href="/contact/" class="cta cta--secondary">Contact us</a>
            </div>
          </aside>
        </article>
      </div>
    </div>
  </main>

  <footer class="footer">
    <div class="footer-inner">
      <a href="/"><img src="/logo/stackcone.png" alt="stackcone" class="footer-logo" width="220" height="48"></a>
      <nav class="footer-nav" aria-label="Site links">
        <a href="/work/">Portfolio</a><a href="/solutions/">Solutions</a><a href="/learn/">Learn</a><a href="/blog/">Blog</a><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a>
      </nav>
      <p class="footer-copy">© stackcone 2026</p>
    </div>
  </footer>
  <script src="/site-nav.js" defer></script>
  <script src="/script.js" defer></script>
</body>
</html>
"""


def catalog_html() -> str:
    track_cards = []
    for track_id, track in TRACKS.items():
        lessons = by_track[track_id]
        lesson_links = "\n".join(
            f'            <a class="learn-course-link" href="/learn/courses/{l["slug"]}/"><span class="learn-course-num">{l["lesson_num"]}</span><span><strong>{esc(l["title"])}</strong><small>{l["minutes"]} min · {esc(l["level"])}</small></span></a>'
            for l in lessons
        )
        parent_label = f'<span class="learn-track-parent">{esc(track["parent"])}</span>' if track["parent"] else ""
        track_cards.append(f"""
      <section class="learn-track-card" id="track-{track_id}" style="--track-color:{track["color"]}">
        <div class="learn-track-card-head">
          {parent_label}
          <h2>{esc(track["label"])}</h2>
          <p>{esc(track["description"])}</p>
          <p class="learn-track-count">{len(lessons)} lessons</p>
        </div>
        <div class="learn-course-list">
{lesson_links}
        </div>
      </section>""")
    tracks_block = "\n".join(track_cards)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Learn Coding &amp; Data Structures | stackcone</title>
  <meta name="description" content="Free coding courses — Python basics, Java fundamentals, and data structures. Interactive lessons with exercises.">
  <link rel="canonical" href="https://stackcone.com/learn/">
  <link rel="icon" type="image/png" href="/favicon/dark-favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/learn/learn.css?v=1">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B29M3GX6QM"></script>
  <script src="/assets/analytics.js" defer></script>
</head>
<body class="learn-page">
  <header class="header">
    <div class="nav-overlay" id="nav-overlay" aria-hidden="true"></div>
    <div class="header-inner">
      <a href="/" class="logo-link"><img src="/logo/stackcone.png" alt="stackcone" class="logo" width="280" height="60"></a>
      <button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav">
        <span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span><span class="nav-toggle-bar"></span>
      </button>
      <nav class="nav" id="main-nav" aria-label="Main navigation"></nav>
    </div>
  </header>
  <main class="learn-main">
    <div class="learn-main-inner learn-catalog">
      <div class="learn-hero">
        <h1>Learn</h1>
        <p class="learn-hero-desc">Hands-on coding courses — Python, Java, and data structures. Short lessons, runnable examples, and exercises after every topic.</p>
      </div>
      <div class="learn-tracks">
{tracks_block}
      </div>
    </div>
  </main>
  <footer class="footer">
    <div class="footer-inner">
      <a href="/"><img src="/logo/stackcone.png" alt="stackcone" class="footer-logo" width="220" height="48"></a>
      <nav class="footer-nav" aria-label="Site links">
        <a href="/work/">Portfolio</a><a href="/solutions/">Solutions</a><a href="/learn/">Learn</a><a href="/blog/">Blog</a><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy/">Privacy</a>
      </nav>
      <p class="footer-copy">© stackcone 2026</p>
    </div>
  </footer>
  <script src="/site-nav.js" defer></script>
  <script src="/script.js" defer></script>
</body>
</html>
"""


def courses_json() -> dict:
    courses = []
    for les in LESSONS:
        track = TRACKS[les["track"]]
        courses.append({
            "id": les["slug"],
            "title": les["title"],
            "description": les["summary"],
            "href": f"./courses/{les['slug']}/",
            "track": les["track"],
            "trackLabel": track["label"],
            "parent": track.get("parent"),
            "lessonNum": les["lesson_num"],
            "lessonTotal": les["lesson_total"],
            "minutes": les["minutes"],
            "level": les["level"],
        })
    return {"courses": courses}


def main() -> None:
    LEARN.mkdir(exist_ok=True)
    (LEARN / "courses").mkdir(exist_ok=True)
    (LEARN / "index.html").write_text(catalog_html(), encoding="utf-8")
    (LEARN / "courses.json").write_text(json.dumps(courses_json(), indent=2) + "\n", encoding="utf-8")
    for les in LESSONS:
        out = LEARN / "courses" / les["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(lesson_html(les), encoding="utf-8")
    print(f"Generated {len(LESSONS)} lessons + catalog")


if __name__ == "__main__":
    main()
