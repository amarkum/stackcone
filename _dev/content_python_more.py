"""Extra Python lessons (strings, comprehensions, inheritance, modules, JSON/dates, testing).

Every runnable example is executed at import time and its real stdout is used as the
lesson output, so the published output can never drift from what Python prints.
"""
import contextlib
import io


def M(slug, title, minutes, level, summary, objectives):
    return {"slug": slug, "track": "python", "title": title, "minutes": minutes,
            "level": level, "summary": summary, "objectives": objectives}


def ex(src):
    """A code block followed by the exact output Python produces for it."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, "<lesson>", "exec"), {"__name__": "__lesson__"})
    return [("code", "python", src), ("output", buf.getvalue().rstrip("\n"))]


META = [
    M("python-strings", "Working with Strings", 14, "Beginner",
      "Indexing, slicing, the everyday string methods and clean formatting with f-strings.",
      ["Slice and index text", "Use split, join, strip and replace", "Format numbers with f-strings"]),
    M("python-comprehensions", "Comprehensions and Iteration", 15, "Intermediate",
      "Build lists, dicts and sets in one line, and loop smarter with enumerate, zip and sorted.",
      ["Write list, dict and set comprehensions", "Loop with enumerate and zip", "Sort with a key function"]),
    M("python-inheritance", "Inheritance and Special Methods", 16, "Intermediate",
      "Reuse behavior with subclasses, override methods, and make objects print and compare nicely.",
      ["Create a subclass with super()", "Override methods", "Add __repr__ and __eq__"]),
    M("python-modules-packages", "Modules, Packages and pip", 13, "Intermediate",
      "Split code across files, import the standard library, and install packages in a virtual environment.",
      ["Import from your own modules", "Use the standard library", "Create a venv and install packages"]),
    M("python-json-datetime", "JSON, Dates and the Standard Library", 14, "Intermediate",
      "Read and write JSON, work with dates and durations, and reach for collections and pathlib.",
      ["Convert data to and from JSON", "Do date arithmetic", "Count and group with collections"]),
    M("python-testing-debugging", "Testing and Debugging", 15, "Intermediate",
      "Write tests with pytest, read tracebacks, and track down bugs with print and the debugger.",
      ["Write and run pytest tests", "Test error cases", "Debug with breakpoint()"]),
]

CONTENT = {}

# ---------------------------------------------------------------------------
CONTENT["python-strings"] = [
    ("p", "Text is everywhere in real programs: names, emails, log lines, file paths, API responses. A Python <code>str</code> is an <strong>immutable sequence of characters</strong>. Sequence means you can index and slice it like a list. Immutable means no operation changes a string in place; every method returns a <em>new</em> string and leaves the original alone."),
    ("h2", "Creating strings"),
    ("p", "Use single or double quotes, whichever avoids escaping. Triple quotes span several lines. A backslash starts an <em>escape sequence</em> such as <code>\\n</code> (new line) or <code>\\t</code> (tab). Prefix a string with <code>r</code> to keep backslashes literal, which is handy for Windows paths and regular expressions."),
] + ex('''single = 'It is fine'
double = "She said \\"hi\\""
poem = """Roses are red,
Violets are blue"""
path = r"C:\\new\\table"

print(single)
print(double)
print(poem)
print(path)''') + [
    ("h2", "Indexing and slicing"),
    ("p", "Each character has a position starting at <code>0</code>. Negative positions count from the end, so <code>-1</code> is the last character. A slice <code>text[start:stop]</code> takes characters from <code>start</code> up to but <em>not including</em> <code>stop</code>. Leave either side empty to go to that end, and add a third number as the step."),
] + ex('''word = "stackcone"
print(word[0], word[-1])
print(word[0:5])
print(word[5:])
print(word[::-1])
print(word[::2])
print(len(word))''') + [
    ("note", "Slices never crash", "Indexing outside the string, like <code>word[99]</code>, raises an <code>IndexError</code>. A slice like <code>word[99:]</code> quietly returns an empty string instead."),
    ("h2", "Everyday string methods"),
    ("p", "Methods are functions attached to a value, called with a dot. The ones you will use constantly clean up text (<code>strip</code>, <code>lower</code>), search it (<code>startswith</code>, <code>find</code>, <code>in</code>) and rewrite it (<code>replace</code>)."),
] + ex('''raw = "   Hello, World!  "
clean = raw.strip()

print(clean)
print(clean.lower(), clean.upper())
print(clean.replace("World", "Python"))
print(clean.startswith("Hello"), clean.endswith("?"))
print("World" in clean)
print(clean.find("o"), clean.count("l"))
print(raw)''') + [
    ("p", "Notice the last line: <code>raw</code> is unchanged, because <code>strip()</code> returned a new string."),
    ("h2", "Splitting and joining"),
    ("p", "<code>split()</code> turns a string into a list of pieces, and <code>join()</code> glues a list back into one string. Together they handle most text-processing chores, such as reading comma-separated values or building a sentence. Note the odd-looking order of <code>join</code>: you call it on the <em>separator</em>."),
] + ex('''line = "ada,grace,linus"
names = line.split(",")
print(names)

print(" & ".join(names))
print("one two  three".split())
print("-".join(["2026", "01", "15"]))''') + [
    ("h2", "Formatting with f-strings"),
    ("p", "An f-string embeds expressions inside braces. After a colon you can control the format: number of decimals, thousands separators, alignment and padding. This is the modern, readable replacement for <code>+</code> concatenation and <code>%</code> formatting."),
] + ex('''name = "Ada"
score = 93.456
big = 1234567

print(f"{name} scored {score:.1f}")
print(f"Population: {big:,}")
print(f"{name:>8}|{name:<8}|{name:^8}|")
print(f"{7:03d}")
print(f"{0.256:.0%}")
print(f"{name!r}")''') + [
    ("h2", "Checking what a string contains"),
    ("p", "Methods such as <code>isdigit()</code>, <code>isalpha()</code> and <code>isspace()</code> answer yes/no questions about the characters, which is a cheap way to validate input before converting it."),
] + ex('''for text in ["2026", "abc", "12a", ""]:
    print(repr(text), text.isdigit(), text.isalpha())''') + [
    ("h2", "Common mistakes"),
    ("ul", [
        "<strong>Expecting in-place changes</strong>: <code>s.upper()</code> on its own does nothing useful. Assign the result: <code>s = s.upper()</code>.",
        "<strong>Assigning to an index</strong>: <code>s[0] = \"X\"</code> raises <code>TypeError</code> because strings are immutable. Build a new string with slicing or <code>replace</code>.",
        "<strong>Joining non-strings</strong>: <code>\",\".join([1, 2])</code> fails. Convert first: <code>\",\".join(str(n) for n in nums)</code>.",
        "<strong>Off-by-one slices</strong>: the stop index is excluded, so <code>s[0:3]</code> has three characters, not four.",
    ]),
    ("exercise", "Given <code>email = \"  Ada.Lovelace@Example.com \"</code>, print the cleaned lowercase address, then print just the part before the <code>@</code> with the dot replaced by a space and each word capitalized (use <code>.title()</code>)."),
    ("solution", "python", 'email = "  Ada.Lovelace@Example.com "\nclean = email.strip().lower()\nprint(clean)\n\nuser = clean.split("@")[0]\nprint(user.replace(".", " ").title())'),
]

# ---------------------------------------------------------------------------
CONTENT["python-comprehensions"] = [
    ("p", "Much of everyday Python is <em>take a collection, change or filter it, and get a new collection</em>. Comprehensions express that in a single readable line. Alongside them, a few built-in helpers such as <code>enumerate</code>, <code>zip</code> and <code>sorted</code> remove most of the index bookkeeping you would otherwise write by hand."),
    ("h2", "From loop to list comprehension"),
    ("p", "Here is the loop you already know: build an empty list, loop, append. A list comprehension packs the same idea into brackets, in the shape <code>[expression for item in iterable]</code>."),
] + ex('''nums = [1, 2, 3, 4, 5]

squares = []
for n in nums:
    squares.append(n * n)
print(squares)

squares2 = [n * n for n in nums]
print(squares2 == squares)''') + [
    ("h2", "Filtering with a condition"),
    ("p", "Add <code>if</code> at the end to keep only some items. To <em>transform</em> items differently depending on a condition, put a conditional expression at the front instead: <code>[a if test else b for ...]</code>."),
] + ex('''nums = range(1, 11)

evens = [n for n in nums if n % 2 == 0]
labels = ["even" if n % 2 == 0 else "odd" for n in nums]

print(evens)
print(labels[:4])''') + [
    ("h2", "Dictionary and set comprehensions"),
    ("p", "The same syntax works with braces. Use <code>{key: value for ...}</code> for a dict and <code>{item for ...}</code> for a set (which also removes duplicates)."),
] + ex('''words = ["apple", "kiwi", "banana", "kiwi"]

lengths = {w: len(w) for w in words}
first_letters = {w[0] for w in words}

print(lengths)
print(sorted(first_letters))''') + [
    ("note", "When not to use one", "If a comprehension needs two conditions, nested loops and a long expression, it stops being readable. Use a normal <code>for</code> loop. Clarity beats cleverness."),
    ("h2", "enumerate: the index without the bookkeeping"),
    ("p", "When you need both the position and the value, do not track a counter yourself. <code>enumerate</code> hands you both, and <code>start=</code> sets the first number."),
] + ex('''tasks = ["write", "test", "ship"]
for number, task in enumerate(tasks, start=1):
    print(f"{number}. {task}")''') + [
    ("h2", "zip: walking several lists together"),
    ("p", "<code>zip</code> pairs up items from two or more sequences and stops at the shortest one. Wrapping the result in <code>dict()</code> is a neat way to build a lookup table from two lists."),
] + ex('''names = ["Ada", "Grace", "Linus"]
scores = [95, 88, 91]

for name, score in zip(names, scores):
    print(name, score)

print(dict(zip(names, scores)))''') + [
    ("h2", "Sorting with a key"),
    ("p", "<code>sorted()</code> returns a new sorted list and accepts a <code>key=</code> function that says <em>what to sort by</em>. Use <code>reverse=True</code> for descending order. Python's sort is stable, so equal items keep their original order. Related helpers <code>any()</code> and <code>all()</code> answer \"is at least one / is every\" questions."),
] + ex('''people = [("Ann", 31), ("Bob", 25), ("Cy", 31)]

print(sorted(people, key=lambda p: p[1]))
print(sorted(people, key=lambda p: (-p[1], p[0])))

scores = [72, 88, 95]
print(any(s >= 90 for s in scores), all(s >= 70 for s in scores))''') + [
    ("h2", "Generator expressions"),
    ("p", "Swap the brackets for parentheses and you get a <strong>generator expression</strong>: it produces values one at a time instead of building the whole list in memory. It is ideal when you only need to feed the result into <code>sum()</code>, <code>max()</code> or <code>any()</code>."),
] + ex('''total = sum(n * n for n in range(1, 1001))
print(total)''') + [
    ("h2", "Common mistakes"),
    ("ul", [
        "Using a comprehension only for its side effects, like <code>[print(x) for x in items]</code>. Use a plain loop.",
        "Forgetting that <code>zip</code> silently drops extra items when the lists differ in length.",
        "Reusing a generator: once exhausted it yields nothing more. Recreate it or use a list.",
    ]),
    ("exercise", "From <code>words = [\"python\", \"is\", \"very\", \"readable\"]</code>, build a dict mapping each word longer than 2 letters to its length using a dict comprehension, then print the words sorted by length, longest first."),
    ("solution", "python", 'words = ["python", "is", "very", "readable"]\nlengths = {w: len(w) for w in words if len(w) > 2}\nprint(lengths)\nprint(sorted(lengths, key=lengths.get, reverse=True))'),
]

# ---------------------------------------------------------------------------
CONTENT["python-inheritance"] = [
    ("p", "In the previous OOP lesson you built a class from scratch. <strong>Inheritance</strong> lets a new class start from an existing one, reusing its attributes and methods and adding or changing only what is different. The existing class is the <em>parent</em> (base class); the new one is the <em>child</em> (subclass). Use it for a real \"is a\" relationship: a <code>Dog</code> <em>is an</em> <code>Animal</code>."),
    ("h2", "Your first subclass"),
    ("p", "Put the parent's name in parentheses. The child gets everything the parent has. Inside the child's <code>__init__</code>, call <code>super().__init__(...)</code> so the parent still sets up its part."),
] + ex('''class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed


rex = Dog("Rex", "Beagle")
print(rex.name, rex.breed)
print(rex.speak())''') + [
    ("h2", "Overriding methods"),
    ("p", "A subclass can define a method with the same name to replace the parent's version. This is <strong>polymorphism</strong>: code that calls <code>speak()</code> works on any animal, and each one answers in its own way, without an <code>if</code> chain checking the type."),
] + ex('''class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"


class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof"


class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow"


for pet in [Dog("Rex"), Cat("Tom"), Animal("Generic")]:
    print(pet.speak())''') + [
    ("h2", "Extending instead of replacing"),
    ("p", "Often you want to <em>add</em> to the parent's behavior. Call <code>super().method()</code> inside the override to run the parent's version first and then continue."),
] + ex('''class Account:
    def __init__(self, balance=0):
        self.balance = balance

    def describe(self):
        return f"balance={self.balance}"


class Savings(Account):
    def __init__(self, balance=0, rate=0.02):
        super().__init__(balance)
        self.rate = rate

    def describe(self):
        return super().describe() + f", rate={self.rate:.0%}"


print(Savings(500).describe())''') + [
    ("h2", "isinstance and issubclass"),
    ("p", "<code>isinstance(obj, Class)</code> is true if the object was created from that class <em>or any subclass</em>. Prefer it over comparing <code>type(obj)</code> directly."),
] + ex('''class Animal: ...
class Dog(Animal): ...

d = Dog()
print(isinstance(d, Dog), isinstance(d, Animal), isinstance(d, str))
print(issubclass(Dog, Animal))''') + [
    ("h2", "Special (dunder) methods"),
    ("p", "Methods with double underscores let your objects behave like built-in ones. <code>__repr__</code> controls how an object prints in a debugger or the REPL, <code>__str__</code> what <code>print()</code> shows, and <code>__eq__</code> what <code>==</code> means. Without them, two objects with identical data are considered different and print as an unhelpful memory address."),
] + ex('''class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


a, b = Point(1, 2), Point(1, 2)
print(a)
print(a == b, a is b)
print(a + Point(10, 10))''') + [
    ("note", "Composition over inheritance", "If the relationship is \"has a\" rather than \"is a\", store one object inside another instead of inheriting. A <code>Car</code> <em>has an</em> <code>Engine</code>; it is not a kind of engine. Deep inheritance chains are hard to follow, so keep hierarchies shallow."),
    ("h2", "Common mistakes"),
    ("ul", [
        "Forgetting <code>super().__init__()</code>, so the parent's attributes are never set and you get <code>AttributeError</code> later.",
        "Overriding a method with a different signature, which breaks code that expects the parent's contract.",
        "Using inheritance just to share a few lines of code when a plain function would do.",
    ]),
    ("exercise", "Create a <code>Shape</code> class with an <code>area()</code> method that returns <code>0</code>. Add subclasses <code>Rectangle(w, h)</code> and <code>Circle(r)</code> that override it (use 3.14 for pi). Loop over one of each and print the areas."),
    ("solution", "python", 'class Shape:\n    def area(self):\n        return 0\n\n\nclass Rectangle(Shape):\n    def __init__(self, w, h):\n        self.w, self.h = w, h\n\n    def area(self):\n        return self.w * self.h\n\n\nclass Circle(Shape):\n    def __init__(self, r):\n        self.r = r\n\n    def area(self):\n        return 3.14 * self.r ** 2\n\n\nfor s in [Rectangle(3, 4), Circle(2)]:\n    print(s.area())'),
]

# ---------------------------------------------------------------------------
CONTENT["python-modules-packages"] = [
    ("p", "Once a program grows past one file you need a way to split it up and to reuse code written by others. A <strong>module</strong> is simply a <code>.py</code> file. A <strong>package</strong> is a folder of modules. Python ships with a large <strong>standard library</strong>, and the community publishes hundreds of thousands more packages you can install with <code>pip</code>."),
    ("h2", "Importing from the standard library"),
    ("p", "The <code>import</code> statement loads a module. Access its contents with a dot, or pull out specific names with <code>from ... import</code>. Add <code>as</code> to give something a shorter name."),
] + ex('''import math
from random import Random
from collections import Counter as C

print(math.sqrt(49), math.pi)
print(math.ceil(4.1), math.floor(4.9))

rng = Random(7)          # seeded so the result is repeatable
print(rng.randint(1, 100))

print(C("banana").most_common(2))''') + [
    ("h2", "Writing your own module"),
    ("p", "Any file you create can be imported by the others in the same folder. Suppose you save helper functions in <code>shapes.py</code>:"),
    ("code", "pyfile", '# shapes.py\nPI = 3.14159\n\ndef circle_area(r):\n    return PI * r ** 2\n\ndef rect_area(w, h):\n    return w * h'),
    ("p", "Now another file in the same folder can use them:"),
    ("code", "pyfile", '# main.py\nimport shapes\nfrom shapes import rect_area\n\nprint(shapes.circle_area(2))\nprint(rect_area(3, 4))'),
    ("h2", "The __name__ guard"),
    ("p", "When you run a file directly, Python sets its <code>__name__</code> to <code>\"__main__\"</code>. When the file is <em>imported</em>, <code>__name__</code> is the module name instead. Wrapping your script in <code>if __name__ == \"__main__\":</code> means the code runs when you execute the file but not when another file imports it."),
    ("code", "python", 'def main():\n    print("running as a script")\n\nif __name__ == "__main__":\n    main()'),
    ("h2", "Packages: folders of modules"),
    ("p", "Put modules in a folder to make a package. An <code>__init__.py</code> file (often empty) marks the folder as a package, and you import with dots."),
    ("code", "bash", "myapp/\n  __init__.py\n  main.py\n  utils/\n    __init__.py\n    text.py      # from myapp.utils.text import slugify"),
    ("h2", "Virtual environments and pip"),
    ("p", "A <strong>virtual environment</strong> is a private folder of installed packages for one project, so different projects can use different versions without clashing. Create one, activate it, then install with <code>pip</code>. Record the exact versions in <code>requirements.txt</code> so anyone can recreate the setup."),
    ("code", "bash", "python3 -m venv .venv\nsource .venv/bin/activate        # Windows: .venv\\Scripts\\activate\n\npip install requests\npip freeze > requirements.txt\npip install -r requirements.txt   # on another machine"),
    ("code", "pyfile", 'import requests\n\nresponse = requests.get("https://api.github.com")\nprint(response.status_code)'),
    ("note", "Always activate first", "If <code>pip install</code> seems to work but <code>import</code> then fails, you probably installed into a different Python. Check that your prompt shows <code>(.venv)</code> and that <code>which python</code> points inside the project."),
    ("h2", "Common mistakes"),
    ("ul", [
        "<strong>Naming your file like a library</strong>: a file called <code>random.py</code> or <code>math.py</code> shadows the real module and breaks imports.",
        "<strong>Circular imports</strong>: module A imports B while B imports A. Move the shared code into a third module.",
        "<strong>Wildcard imports</strong>: <code>from x import *</code> hides where names come from. Import what you need by name.",
        "<strong>Committing the venv</strong>: add <code>.venv/</code> to <code>.gitignore</code> and share <code>requirements.txt</code> instead.",
    ]),
    ("exercise", "Use the standard library only: import <code>math</code> and print the hypotenuse of a right triangle with sides 3 and 4 using <code>math.hypot</code>, and use <code>collections.Counter</code> to print the most common letter in <code>\"mississippi\"</code>."),
    ("solution", "python", 'import math\nfrom collections import Counter\n\nprint(math.hypot(3, 4))\nprint(Counter("mississippi").most_common(1))'),
]

# ---------------------------------------------------------------------------
CONTENT["python-json-datetime"] = [
    ("p", "Two things show up in almost every real project: exchanging data with other systems, and dealing with time. JSON is the near-universal data format of web APIs, and the <code>datetime</code> module handles dates without you counting days by hand. Both come with Python, so there is nothing to install."),
    ("h2", "What JSON looks like"),
    ("p", "JSON is text that describes data using objects (like Python dicts), arrays (lists), strings, numbers, booleans and <code>null</code> (Python's <code>None</code>). The <code>json</code> module converts between that text and Python objects. <code>dumps</code> turns a Python object into a JSON <em>string</em>; <code>loads</code> parses a JSON string back."),
] + ex('''import json

user = {"id": 1, "name": "Ada", "admin": True, "tags": ["math", "code"], "manager": None}

text = json.dumps(user)
print(text)

back = json.loads(text)
print(back["tags"][0], back["manager"])''') + [
    ("h2", "Pretty printing and reading and writing files"),
    ("p", "Pass <code>indent</code> to make the output readable and <code>sort_keys</code> for a stable order. The file versions are <code>json.dump</code> and <code>json.load</code> (no trailing <em>s</em>), which take an open file."),
] + ex('''import json

config = {"debug": False, "port": 8000, "hosts": ["a.example", "b.example"]}
print(json.dumps(config, indent=2, sort_keys=True))''') + [
    ("code", "python", 'import json\n\nwith open("config.json", "w") as f:\n    json.dump(config, f, indent=2)\n\nwith open("config.json") as f:\n    loaded = json.load(f)\nprint(loaded["port"])'),
    ("note", "Not everything is JSON-friendly", "JSON has no dates, sets or custom classes. <code>json.dumps({1, 2})</code> raises a <code>TypeError</code>. Convert first: a set to a list, a date to an ISO string with <code>.isoformat()</code>."),
    ("h2", "Dates and times"),
    ("p", "<code>date</code> holds a day, <code>datetime</code> a day and a time, and <code>timedelta</code> a <em>length</em> of time. Subtracting two dates gives a <code>timedelta</code>, and adding one to a date moves it forward."),
] + ex('''from datetime import date, datetime, timedelta

launch = date(2026, 3, 1)
today = date(2026, 1, 15)

print(launch - today)
print((launch - today).days)
print(today + timedelta(days=30))
print(today.weekday(), today.strftime("%A, %d %B %Y"))

meeting = datetime(2026, 1, 15, 9, 30)
print(meeting + timedelta(hours=2, minutes=15))''') + [
    ("h2", "Parsing and formatting"),
    ("p", "<code>strftime</code> formats a date as text using codes like <code>%Y</code> (year), <code>%m</code> (month) and <code>%d</code> (day). <code>strptime</code> does the reverse. For the standard ISO format use <code>isoformat()</code> and <code>fromisoformat()</code>, which is the safest thing to store or send."),
] + ex('''from datetime import datetime

parsed = datetime.strptime("15/01/2026 18:45", "%d/%m/%Y %H:%M")
print(parsed)
print(parsed.isoformat())
print(parsed.strftime("%b %d, %Y at %I:%M %p"))
print(datetime.fromisoformat("2026-01-15T18:45:00").year)''') + [
    ("note", "Time zones", "A plain <code>datetime.now()</code> has no time zone attached, which causes bugs when servers and users are in different places. Store and compare times in UTC using <code>datetime.now(timezone.utc)</code>, and convert to a local zone only when displaying."),
    ("h2", "More standard-library helpers"),
    ("p", "<code>collections.Counter</code> counts things, <code>defaultdict</code> removes the \"does this key exist yet?\" check when grouping, and <code>pathlib.Path</code> is the modern way to build file paths without string gluing."),
] + ex('''from collections import Counter, defaultdict
from pathlib import Path

votes = ["red", "blue", "red", "green", "red", "blue"]
print(Counter(votes).most_common())

by_length = defaultdict(list)
for word in ["kiwi", "fig", "plum", "pear", "lime"]:
    by_length[len(word)].append(word)
print(dict(by_length))

p = Path("data") / "reports" / "2026.csv"
print(p.name, p.suffix, p.parent)''') + [
    ("h2", "Common mistakes"),
    ("ul", [
        "Mixing up <code>dump</code>/<code>load</code> (files) with <code>dumps</code>/<code>loads</code> (strings).",
        "Forgetting that JSON object keys are always strings, so <code>{1: \"a\"}</code> comes back as <code>{\"1\": \"a\"}</code>.",
        "Comparing naive and time-zone-aware datetimes, which raises <code>TypeError</code>.",
        "Formatting dates by hand with string slicing instead of <code>strftime</code>.",
    ]),
    ("exercise", "Build a dict with your name and a list of two hobbies, convert it to a JSON string with 2-space indent and print it. Then compute how many days are between <code>date(2026, 1, 1)</code> and <code>date(2026, 12, 25)</code>."),
    ("solution", "python", 'import json\nfrom datetime import date\n\nme = {"name": "Amar", "hobbies": ["chess", "running"]}\nprint(json.dumps(me, indent=2))\n\nprint((date(2026, 12, 25) - date(2026, 1, 1)).days)'),
]

# ---------------------------------------------------------------------------
CONTENT["python-testing-debugging"] = [
    ("p", "Every program has bugs; the skill is finding them quickly and making sure they stay fixed. <strong>Tests</strong> are small programs that check your code still does what you think. <strong>Debugging</strong> is the detective work when it does not. Learning both early will save you far more time than they cost."),
    ("h2", "Reading a traceback"),
    ("p", "When an exception is not handled, Python prints a <em>traceback</em>: the chain of calls that led to the error. Read it from the <strong>bottom up</strong>. The last line is the error type and message; the line above it is where it happened; the lines above that show how you got there."),
    ("code", "python", 'def average(nums):\n    return sum(nums) / len(nums)\n\nprint(average([]))'),
    ("output", "Traceback (most recent call last):\n  File \"app.py\", line 4, in <module>\n    print(average([]))\n  File \"app.py\", line 2, in average\n    return sum(nums) / len(nums)\nZeroDivisionError: division by zero"),
    ("p", "The message tells you exactly what went wrong: <code>len(nums)</code> was zero because the list was empty. The fix is a decision for you: return <code>0</code>, raise a clearer error, or make callers check first."),
    ("h2", "Your first test with assert"),
    ("p", "An <code>assert</code> statement checks a claim and raises <code>AssertionError</code> if it is false. It is the simplest possible test: call your function with known input and assert the answer you expect."),
] + ex('''def is_palindrome(text):
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]


assert is_palindrome("Racecar")
assert is_palindrome("A man, a plan, a canal: Panama")
assert not is_palindrome("python")
print("all checks passed")''') + [
    ("h2", "Real tests with pytest"),
    ("p", "<strong>pytest</strong> is the most popular test runner. Install it with <code>pip install pytest</code>, put tests in files named <code>test_*.py</code>, and name each test function <code>test_*</code>. Run <code>pytest</code> and it finds and runs them all, showing exactly which assertion failed and with what values."),
    ("code", "pyfile", '# test_text.py\nfrom text import is_palindrome\n\ndef test_simple_palindrome():\n    assert is_palindrome("level")\n\ndef test_ignores_case_and_punctuation():\n    assert is_palindrome("A man, a plan, a canal: Panama")\n\ndef test_not_a_palindrome():\n    assert not is_palindrome("python")'),
    ("code", "bash", "pip install pytest\npytest -v"),
    ("output", "test_text.py::test_simple_palindrome PASSED\ntest_text.py::test_ignores_case_and_punctuation PASSED\ntest_text.py::test_not_a_palindrome PASSED\n\n3 passed in 0.02s"),
    ("h2", "Testing the error cases"),
    ("p", "Good tests cover the awkward inputs too: empty values, zero, negatives, missing data. When a function is <em>supposed</em> to raise, use <code>pytest.raises</code> to assert that it does. Use <code>parametrize</code> to run the same test over many inputs without copy and paste."),
    ("code", "pyfile", 'import pytest\n\ndef safe_divide(a, b):\n    if b == 0:\n        raise ValueError("b must not be zero")\n    return a / b\n\ndef test_divides():\n    assert safe_divide(10, 4) == 2.5\n\ndef test_zero_raises():\n    with pytest.raises(ValueError):\n        safe_divide(1, 0)\n\n@pytest.mark.parametrize("a, b, expected", [(6, 3, 2), (9, 3, 3), (1, 4, 0.25)])\ndef test_many(a, b, expected):\n    assert safe_divide(a, b) == expected'),
    ("h2", "Debugging: print first, then the debugger"),
    ("p", "The fastest first move is a well-placed <code>print</code> showing the values you assumed. Use <code>repr()</code> or the f-string <code>=</code> shortcut so you can see quotes and types. When that is not enough, drop in <code>breakpoint()</code>: execution pauses there and opens an interactive debugger (<code>pdb</code>)."),
] + ex('''items = [3, 8, 2]
total = 0
for n in items:
    total += n
    print(f"{n=} {total=}")''') + [
    ("code", "bash", "n  next line           c  continue to next breakpoint\ns  step into a call    p x  print the value of x\nl  list source code    q  quit the debugger"),
    ("h2", "A simple debugging routine"),
    ("ul", [
        "<strong>Reproduce it</strong>: find the smallest input that triggers the bug and write it down, ideally as a failing test.",
        "<strong>Read the traceback</strong> bottom-up before touching any code.",
        "<strong>Check your assumptions</strong> with a print or breakpoint: is this variable really what you think it is?",
        "<strong>Change one thing at a time</strong>, and re-run after each change.",
        "<strong>Keep the test</strong> once fixed so the bug cannot quietly come back.",
    ]),
    ("note", "Rubber-duck debugging", "Explaining the problem out loud, line by line, to a rubber duck (or a patient friend) solves a surprising number of bugs. Putting your assumptions into words exposes the one that is wrong."),
    ("exercise", "Write <code>fizz(n)</code> that returns <code>\"Fizz\"</code> for multiples of 3, <code>\"Buzz\"</code> for multiples of 5, <code>\"FizzBuzz\"</code> for both and the number as a string otherwise. Add four <code>assert</code> statements that check 3, 5, 15 and 7."),
    ("solution", "python", 'def fizz(n):\n    if n % 15 == 0:\n        return "FizzBuzz"\n    if n % 3 == 0:\n        return "Fizz"\n    if n % 5 == 0:\n        return "Buzz"\n    return str(n)\n\n\nassert fizz(3) == "Fizz"\nassert fizz(5) == "Buzz"\nassert fizz(15) == "FizzBuzz"\nassert fizz(7) == "7"\nprint("ok")'),
]
