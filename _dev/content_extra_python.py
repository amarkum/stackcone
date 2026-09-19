"""Extra teaching material for the original Python lessons."""
from extra_util import py

EXTRA = {}

EXTRA["python-hello-world"] = {
    "intro": [
        ("h2", "What is programming, really?"),
        ("p", "A program is a list of instructions written so precisely that a computer can follow them without ever guessing. Think of a recipe: \"boil two cups of water, add the pasta, wait eight minutes.\" A human cook can cope with vague steps, but a computer cannot, so every step has to be exact. <strong>Python</strong> is a language designed so those exact steps read almost like plain English."),
        ("p", "You do not need any prior experience. By the end of this lesson you will have installed Python, written a program, run it, and read your first error message, which is the most important beginner skill of all."),
        ("h2", "Where do I write Python?"),
        ("ul", [
            "<strong>A text editor plus a terminal</strong>: write a file ending in <code>.py</code> and run it with <code>python3 file.py</code>. This is what the rest of the course assumes.",
            "<strong>VS Code</strong> (free): a friendly editor with a built-in terminal and a Run button. A great first choice.",
            "<strong>The REPL</strong>: type <code>python3</code> in a terminal and you get a prompt where every line runs instantly. Perfect for experiments.",
            "<strong>Right here</strong>: every editor on this site with a Run button executes real Python in your browser, so you can try things without installing anything first.",
        ]),
    ],
    "more": [
        ("h2", "How a program actually runs"),
        ("p", "When you run <code>python3 hello.py</code>, Python reads the file from the first line to the last, one statement at a time, and does what each says. It never skips ahead unless you tell it to (you will learn how in the control-flow lesson). Output from <code>print()</code> appears in the order the lines run."),
        *py('print("step 1")\nprint("step 2")\nprint("step 3")'),
        ("p", "Order matters. If you swap two lines, the output swaps too. Whenever a program surprises you, the first question to ask is: <em>which line is running right now, and what has already happened?</em>"),
        ("h2", "Printing several things at once"),
        ("p", "<code>print()</code> accepts many values separated by commas and puts a space between them. Use <code>sep=</code> to change that separator and <code>end=</code> to change what comes after (the default is a new line)."),
        *py('print("Python", "is", "fun")\nprint("a", "b", "c", sep="-")\nprint("loading", end="...")\nprint("done")'),
        ("h2", "Your first error, on purpose"),
        ("p", "Errors are not failure; they are the computer telling you exactly what it did not understand. Type the line below and you will see one. Read the last line first."),
        ("code", "python", 'print("Hello)'),
        ("output", "  File \"hello.py\", line 1\n    print(\"Hello)\n          ^\nSyntaxError: unterminated string literal (detected at line 1)"),
        ("p", "Python points at the exact spot (the <code>^</code>) and names the problem: the string that started with a quote never closed. Add the missing <code>\"</code> and the error disappears."),
    ],
    "recap": [
        "A program is precise, ordered instructions; Python runs them from top to bottom.",
        "<code>print()</code> shows values; commas add spaces, <code>sep=</code> and <code>end=</code> change the layout.",
        "Run a file with <code>python3 file.py</code>, or experiment instantly in the REPL.",
        "Read errors from the last line upward; the message tells you what went wrong.",
    ],
}

EXTRA["python-variables-and-types"] = {
    "intro": [
        ("h2", "Variables are labels, not boxes"),
        ("p", "Many tutorials say a variable is a box that holds a value. A better picture is a <strong>sticky label</strong> attached to a value. The value lives somewhere in memory; the label lets you find it again. Writing <code>age = 28</code> creates the number 28 and sticks the label <code>age</code> on it. Later, <code>age = 29</code> simply moves the label to a different value."),
        *py('age = 28\nprint(age)\nage = 29          # move the label to a new value\nprint(age)\n\nother = age       # two labels on the same value\nprint(other)'),
    ],
    "more": [
        ("h2", "Walkthrough: a tiny shopping cart"),
        ("p", "Let us combine everything: several variables, arithmetic, and formatted output. Read the code line by line and predict the output before you look at it."),
        *py('item = "notebook"\nunit_price = 3.50\nquantity = 4\n\nsubtotal = unit_price * quantity\ntax = subtotal * 0.08\ntotal = subtotal + tax\n\nprint(f"Item: {item}")\nprint(f"Subtotal: ${subtotal:.2f}")\nprint(f"Tax: ${tax:.2f}")\nprint(f"Total: ${total:.2f}")'),
        ("p", "Notice how each line uses names defined above it. A variable must exist <em>before</em> you use it; asking for one that does not exist raises a <code>NameError</code>. Also notice the <code>:.2f</code> inside the braces: it means \"show two decimal places\", which is how you print money."),
        ("h2", "Checking a value's type"),
        ("p", "When something behaves strangely, ask Python what type it is. <code>type()</code> tells you, and <code>isinstance()</code> answers yes or no. This is the fastest way to spot a number that is secretly text."),
        *py('value = "42"\nprint(type(value), value + value)\n\nnumber = int(value)\nprint(type(number), number + number)\nprint(isinstance(number, int))'),
        ("h2", "Integer division and remainders, visually"),
        ("p", "<code>//</code> answers \"how many whole times does it fit?\" and <code>%</code> answers \"what is left over?\". Together they solve everyday problems such as converting minutes to hours and minutes."),
        *py('total_minutes = 135\nhours = total_minutes // 60\nminutes = total_minutes % 60\nprint(f"{total_minutes} minutes = {hours}h {minutes}m")'),
    ],
    "recap": [
        "A variable is a label attached to a value; assignment moves the label.",
        "The core types are <code>int</code>, <code>float</code>, <code>str</code>, <code>bool</code> and <code>None</code>.",
        "Use <code>type()</code> to inspect a value and <code>int()</code>/<code>float()</code>/<code>str()</code> to convert.",
        "<code>//</code> gives the whole-number quotient, <code>%</code> the remainder; f-strings format output.",
    ],
}

EXTRA["python-control-flow"] = {
    "intro": [
        ("h2", "Think in decisions and repetition"),
        ("p", "Every program you use is built from just two ideas beyond simple steps. <strong>Decisions</strong>: \"if the password is wrong, show an error; otherwise let the user in.\" <strong>Repetition</strong>: \"for every item in the cart, add up the price.\" Control flow is how you express those two ideas in code."),
        ("p", "Before writing any code, get used to describing the logic in words. If you can say it as \"if this, do that, otherwise do something else\", the code is only a translation."),
    ],
    "more": [
        ("h2", "Combining conditions"),
        ("p", "Join tests with <code>and</code> (both must be true), <code>or</code> (at least one) and <code>not</code> (flip the answer). Python also lets you chain comparisons the way you would in maths: <code>18 &lt;= age &lt; 65</code>."),
        *py('age = 30\nhas_ticket = True\n\nif age >= 18 and has_ticket:\n    print("Welcome in")\n\nif not has_ticket or age < 18:\n    print("Sorry, no entry")\n\nprint(18 <= age < 65)'),
        ("h2", "Controlling a loop: break, continue and else"),
        ("p", "<code>break</code> leaves the loop immediately. <code>continue</code> skips the rest of this round and jumps to the next one. Use them to stop as soon as you find what you want, or to ignore items you do not care about."),
        *py('for n in range(1, 10):\n    if n == 3:\n        continue      # skip 3\n    if n == 6:\n        break         # stop completely\n    print(n)'),
        ("h2", "Nested loops: a multiplication table"),
        ("p", "A loop inside another loop runs the inner one completely for each turn of the outer one. Think of a clock: the minute hand does a full circle for every single step of the hour hand."),
        *py('for row in range(1, 4):\n    for col in range(1, 4):\n        print(row * col, end="\\t")\n    print()'),
        ("h2", "Worked example: guess the number (logic only)"),
        ("p", "Here is a complete mini-program that combines a loop, a decision and a counter. Trace it by hand with the values shown, writing down the value of each variable after every line. Tracing on paper is the single best way to understand loops."),
        *py('secret = 7\nguesses = [3, 9, 7, 2]\nattempts = 0\n\nfor guess in guesses:\n    attempts += 1\n    if guess < secret:\n        print(guess, "is too low")\n    elif guess > secret:\n        print(guess, "is too high")\n    else:\n        print(guess, "is correct after", attempts, "attempts")\n        break'),
    ],
    "recap": [
        "<code>if</code>/<code>elif</code>/<code>else</code> choose one branch; combine tests with <code>and</code>, <code>or</code>, <code>not</code>.",
        "<code>for</code> walks a known sequence; <code>while</code> repeats until a condition changes.",
        "<code>break</code> exits a loop, <code>continue</code> skips to the next round.",
        "Indentation is syntax: it defines what belongs inside each block.",
    ],
}

EXTRA["python-functions"] = {
    "intro": [
        ("h2", "Why functions exist"),
        ("p", "Imagine writing the same five lines of code in ten places. When you find a bug you must fix it ten times, and you will miss one. A function lets you write those five lines <em>once</em>, give them a name, and use that name wherever you need them. Functions are also how big programs stay understandable: each one does one clear job."),
        ("p", "A useful mental model is a vending machine. You put something in (the <strong>arguments</strong>), the machine does its work without you watching, and something comes out (the <strong>return value</strong>). You do not need to know how it works inside to use it."),
    ],
    "more": [
        ("h2", "The anatomy of a function, step by step"),
        *py('def total_price(price, quantity, tax_rate=0.1):\n    """Return the price including tax."""\n    subtotal = price * quantity\n    return subtotal * (1 + tax_rate)\n\nprint(total_price(20, 3))\nprint(total_price(20, 3, tax_rate=0))'),
        ("ul", [
            "<code>def</code> starts the definition; <code>total_price</code> is the name.",
            "<code>price, quantity, tax_rate=0.1</code> are the <em>parameters</em>. <code>tax_rate</code> has a default, so callers may leave it out.",
            "The triple-quoted line is a <em>docstring</em>: a one-sentence description shown by <code>help()</code>.",
            "<code>return</code> sends the answer back and ends the function immediately.",
        ]),
        ("h2", "print versus return"),
        ("p", "Beginners often confuse these two. <code>print</code> only <em>shows</em> something on the screen; the value is then gone. <code>return</code> hands the value back to the caller so it can be stored, tested or used in more maths."),
        *py('def add_print(a, b):\n    print(a + b)\n\ndef add_return(a, b):\n    return a + b\n\nx = add_print(2, 3)\ny = add_return(2, 3)\nprint("x is", x)\nprint("y is", y * 10)'),
        ("h2", "Functions calling functions"),
        ("p", "Small functions are easy to test and combine. Build bigger behavior by letting one function call another."),
        *py('def clean(name):\n    return name.strip().title()\n\ndef greeting(name):\n    return f"Welcome, {clean(name)}!"\n\nprint(greeting("  aDA lovelace "))'),
        ("h2", "*args and **kwargs (flexible arguments)"),
        ("p", "When you do not know how many arguments a caller will pass, <code>*args</code> collects extras into a tuple and <code>**kwargs</code> collects named extras into a dict."),
        *py('def describe(*args, **kwargs):\n    print(args)\n    print(kwargs)\n\ndescribe(1, 2, 3, color="red", size="M")'),
    ],
    "recap": [
        "A function names a reusable job: parameters in, <code>return</code> value out.",
        "<code>print</code> displays; <code>return</code> gives a value back. Prefer returning.",
        "Defaults make arguments optional; keyword arguments make calls readable.",
        "Keep functions small and single-purpose, and let them call each other.",
    ],
}

EXTRA["python-lists-tuples"] = {
    "intro": [
        ("h2", "Why we need collections"),
        ("p", "So far each variable held one value. Real data comes in groups: a list of prices, the days of the week, the pixels of an image. A <strong>list</strong> is a numbered row of boxes you can look through, add to and rearrange. Picture a shopping list on paper: items in order, you can cross one out, add another at the bottom, or read the third item."),
    ],
    "more": [
        ("h2", "Looping over a list"),
        *py('fruits = ["apple", "banana", "cherry"]\n\nfor fruit in fruits:\n    print(fruit.upper())\n\nprint(len(fruits), "fruits")'),
        ("h2", "Adding, removing and searching"),
        *py('todo = ["email", "gym"]\ntodo.append("read")        # add at the end\ntodo.insert(1, "coffee")   # add at position 1\ntodo.remove("gym")         # remove by value\nprint(todo)\nprint("read" in todo)\nprint(todo.index("read"))\nprint(sorted(todo))'),
        ("h2", "Lists are shared, not copied"),
        ("p", "This trips up almost everyone. Assigning a list to another name does <em>not</em> copy it; both names label the same list. Change it through one name and the other sees the change. Use <code>.copy()</code> or a slice <code>[:]</code> for a real copy."),
        *py('a = [1, 2, 3]\nb = a            # same list!\nb.append(4)\nprint(a)\n\nc = a.copy()     # independent copy\nc.append(5)\nprint(a, c)'),
        ("h2", "Useful built-ins for numbers"),
        *py('scores = [72, 88, 95, 61]\nprint(sum(scores), min(scores), max(scores))\nprint(sum(scores) / len(scores))\nscores.sort(reverse=True)\nprint(scores)'),
        ("h2", "When to choose a tuple"),
        ("p", "A tuple is a list you promise not to change. Use it for things that belong together as one fixed record, like a coordinate <code>(x, y)</code> or an RGB colour <code>(255, 0, 0)</code>. Because it cannot change, it is safe to use as a dictionary key, which a list is not."),
        *py('point = (3, 4)\nx, y = point        # unpacking\nprint(x, y)\n\nvisited = {(0, 0): "start", (1, 2): "shop"}\nprint(visited[(1, 2)])'),
    ],
    "recap": [
        "A list is an ordered, changeable collection; a tuple is ordered and fixed.",
        "Indexes start at 0; negative indexes count from the end; slices take ranges.",
        "<code>append</code>, <code>insert</code>, <code>remove</code>, <code>pop</code>, <code>sort</code> change a list in place.",
        "Assignment shares a list; use <code>.copy()</code> when you need a separate one.",
    ],
}

EXTRA["python-dictionaries"] = {
    "intro": [
        ("h2", "Look things up by name, not position"),
        ("p", "A list finds items by position: \"give me item 3.\" But often you know a <em>name</em>, not a position: \"what is Ada's email?\" A <strong>dictionary</strong> works like a real dictionary or a phone contact list: you look up a <em>key</em> and get its <em>value</em>. It is one of the most useful tools in the language because so much real data is \"a set of named fields\": a user, a product, a settings file."),
    ],
    "more": [
        ("h2", "Reading, adding and safely looking up"),
        *py('user = {"name": "Ada", "role": "admin"}\n\nprint(user["name"])\nuser["email"] = "ada@example.com"   # add a new key\nuser["role"] = "owner"              # change a value\n\nprint(user.get("phone"))            # missing key -> None, no crash\nprint(user.get("phone", "n/a"))     # or supply a default\nprint("email" in user)'),
        ("note", "KeyError", "Reading a missing key with <code>user[\"phone\"]</code> raises <code>KeyError</code>. Use <code>.get()</code> when the key might not exist."),
        ("h2", "Looping over a dictionary"),
        *py('prices = {"tea": 2.5, "coffee": 3.0, "juice": 4.25}\n\nfor item, price in prices.items():\n    print(f"{item:<8} ${price:.2f}")\n\nprint(list(prices.keys()))\nprint(sum(prices.values()))'),
        ("h2", "Worked example: counting words"),
        ("p", "Counting how often things appear is the classic dictionary job. The key is the thing being counted; the value is the running total."),
        *py('text = "the cat and the hat and the bat"\ncounts = {}\n\nfor word in text.split():\n    counts[word] = counts.get(word, 0) + 1\n\nprint(counts)'),
        ("h2", "Nested data"),
        ("p", "Values can be lists or other dictionaries, which is how real data such as API responses is shaped. Read it one level at a time."),
        *py('order = {\n    "id": 1001,\n    "customer": {"name": "Ada", "city": "London"},\n    "items": [{"sku": "A1", "qty": 2}, {"sku": "B7", "qty": 1}],\n}\n\nprint(order["customer"]["city"])\nprint(order["items"][0]["qty"])\nprint(sum(i["qty"] for i in order["items"]))'),
        ("h2", "Sets: unique items and fast membership"),
        *py('a = {"python", "sql", "git"}\nb = {"git", "docker", "sql"}\n\nprint(a & b)      # in both\nprint(a | b)      # in either\nprint(a - b)      # only in a\nprint(len({1, 1, 2, 2, 3}))'),
    ],
    "recap": [
        "A dictionary maps unique keys to values; use it when data has names.",
        "Read with <code>d[key]</code> or the safe <code>d.get(key, default)</code>.",
        "Loop with <code>.items()</code>; counting is the classic pattern.",
        "Sets store unique items and support union, intersection and difference.",
    ],
}

EXTRA["python-oop-classes"] = {
    "intro": [
        ("h2", "The idea behind classes"),
        ("p", "So far you have stored data in variables and behavior in functions, kept separately. When a program models real things such as a bank account, a player, an order, you find yourself passing the same group of values around. A <strong>class</strong> bundles the data and the functions that work on it into one unit. Picture a cookie cutter: the <em>class</em> is the cutter (the blueprint); each <em>object</em> is a cookie made from it. Every cookie has the same shape but its own icing."),
    ],
    "more": [
        ("h2", "Anatomy of a class, line by line"),
        *py('class Counter:\n    def __init__(self, start=0):\n        self.value = start        # data stored on this object\n\n    def increment(self):          # behavior\n        self.value += 1\n        return self.value\n\n\na = Counter()\nb = Counter(10)\na.increment()\na.increment()\nb.increment()\nprint(a.value, b.value)'),
        ("ul", [
            "<code>class Counter:</code> defines the blueprint.",
            "<code>__init__</code> runs automatically when you create an object. It sets up the starting data.",
            "<code>self</code> means \"this particular object\". Every method receives it first; you do not pass it yourself.",
            "<code>a</code> and <code>b</code> are separate objects, so their <code>value</code>s do not affect each other.",
        ]),
        ("h2", "Keeping data valid"),
        ("p", "A class is a good place to protect rules. Here a bank account refuses to go below zero, and every caller gets the same protection automatically."),
        *py('class Account:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self.balance = balance\n\n    def withdraw(self, amount):\n        if amount > self.balance:\n            raise ValueError("insufficient funds")\n        self.balance -= amount\n\nacct = Account("Ada", 100)\nacct.withdraw(30)\nprint(acct.balance)\ntry:\n    acct.withdraw(500)\nexcept ValueError as err:\n    print("Error:", err)'),
        ("h2", "Making objects print nicely"),
        *py('class Book:\n    def __init__(self, title, pages):\n        self.title = title\n        self.pages = pages\n\n    def __str__(self):\n        return f"{self.title} ({self.pages} pages)"\n\nprint(Book("Dune", 412))'),
        ("h2", "Class attributes and methods that do not need an object"),
        *py('class Circle:\n    PI = 3.14159            # shared by all circles\n\n    def __init__(self, r):\n        self.r = r\n\n    def area(self):\n        return Circle.PI * self.r ** 2\n\n    @staticmethod\n    def diameter(r):\n        return 2 * r\n\nprint(Circle(2).area())\nprint(Circle.diameter(5))'),
    ],
    "recap": [
        "A class is a blueprint; an object is one thing built from it.",
        "<code>__init__</code> sets up each object; <code>self</code> refers to the current object.",
        "Methods are functions that belong to the class and work on <code>self</code>.",
        "Use classes to keep related data and behavior, and its rules, in one place.",
    ],
}

EXTRA["python-file-handling"] = {
    "intro": [
        ("h2", "Why programs need files"),
        ("p", "Variables disappear the moment your program ends. A file is how information survives: settings, saved games, reports, logs. Reading and writing files lets your program remember things between runs, and lets it work with data created by other people and tools."),
        ("p", "Think of a file as a notebook. To use it you <strong>open</strong> it, then <strong>read</strong> or <strong>write</strong>, then <strong>close</strong> it. Python's <code>with</code> statement does the closing for you, even when something goes wrong."),
    ],
    "more": [
        ("h2", "The three modes you need"),
        ("ul", [
            "<code>\"r\"</code> read (the default): fails if the file does not exist.",
            "<code>\"w\"</code> write: creates the file, <strong>erasing</strong> anything already there.",
            "<code>\"a\"</code> append: adds to the end without erasing.",
        ]),
        ("h2", "Write, then read back"),
        *py('with open("notes.txt", "w") as f:\n    f.write("first line\\n")\n    f.write("second line\\n")\n\nwith open("notes.txt", "a") as f:\n    f.write("third line\\n")\n\nwith open("notes.txt") as f:\n    print(f.read())'),
        ("h2", "Reading line by line"),
        ("p", "For big files do not load everything at once. Looping over the file gives you one line at a time using very little memory. Each line ends with <code>\\n</code>, so call <code>.strip()</code> to remove it."),
        *py('with open("notes.txt") as f:\n    for number, line in enumerate(f, start=1):\n        print(number, line.strip())', setup='open("notes.txt", "w").write("first line\\nsecond line\\nthird line\\n")'),
        ("h2", "Worked example: total a CSV of expenses"),
        *py('with open("expenses.csv", "w") as f:\n    f.write("item,amount\\ncoffee,3.5\\nbooks,20\\ntrain,12.25\\n")\n\ntotal = 0\nwith open("expenses.csv") as f:\n    next(f)                      # skip the header row\n    for line in f:\n        item, amount = line.strip().split(",")\n        total += float(amount)\n\nprint(f"Total: {total:.2f}")'),
        ("h2", "Handling a missing file"),
        *py('try:\n    with open("does-not-exist.txt") as f:\n        data = f.read()\nexcept FileNotFoundError:\n    data = ""\n    print("No file yet, starting empty")\nprint(repr(data))'),
    ],
    "recap": [
        "Open files with <code>with open(path, mode) as f</code> so they always close.",
        "<code>r</code> reads, <code>w</code> overwrites, <code>a</code> appends.",
        "Loop over a file to read it line by line; <code>.strip()</code> removes the newline.",
        "Catch <code>FileNotFoundError</code> when a file might not exist yet.",
    ],
}

EXTRA["python-error-handling"] = {
    "intro": [
        ("h2", "Errors will happen, so plan for them"),
        ("p", "Users type letters where numbers are expected. Files go missing. Networks drop. A program that assumes everything goes right will crash the first time reality disagrees. <strong>Exception handling</strong> lets you say: \"try this, and if a specific thing goes wrong, do this instead of crashing.\" It is the difference between a program that dies with a scary traceback and one that politely tells the user what to fix."),
    ],
    "more": [
        ("h2", "try, except, else, finally: what each part is for"),
        *py('def parse_age(text):\n    try:\n        age = int(text)\n    except ValueError:\n        print("not a number:", repr(text))\n        return None\n    else:\n        print("parsed fine")\n        return age\n    finally:\n        print("(always runs)")\n\nprint(parse_age("42"))\nprint(parse_age("forty"))'),
        ("ul", [
            "<code>try</code>: the risky code.",
            "<code>except ValueError</code>: runs only if <em>that</em> error happens. Be specific.",
            "<code>else</code>: runs only when nothing went wrong.",
            "<code>finally</code>: always runs, good for cleanup such as closing connections.",
        ]),
        ("h2", "Catch specific errors, not everything"),
        ("p", "Writing a bare <code>except:</code> hides real bugs, including typos. Catch the exact exception you expect, and let unexpected ones crash loudly so you notice them."),
        *py('data = {"price": "12.5"}\n\ntry:\n    value = float(data["price"]) / int(data.get("qty", 0))\nexcept (KeyError, ValueError):\n    print("bad input")\nexcept ZeroDivisionError:\n    print("quantity was zero")'),
        ("h2", "Writing helpful error messages"),
        ("p", "Use <code>raise</code> when a caller gives you something invalid. A clear message saves the next developer (often you) hours of guessing."),
        *py('def set_age(age):\n    if not 0 <= age <= 130:\n        raise ValueError(f"age out of range: {age}")\n    return age\n\ntry:\n    set_age(200)\nexcept ValueError as err:\n    print("Rejected:", err)'),
        ("h2", "Worked example: ask until valid"),
        ("p", "A very common pattern: keep asking until the input is acceptable. Here the inputs are simulated with a list so you can run it."),
        *py('answers = iter(["abc", "-5", "27"])\n\nwhile True:\n    text = next(answers)\n    try:\n        age = int(text)\n        if age < 0:\n            raise ValueError("negative")\n    except ValueError:\n        print(f"{text!r} is not valid, try again")\n        continue\n    print("Accepted", age)\n    break'),
    ],
    "recap": [
        "Wrap risky code in <code>try</code>; handle expected problems in <code>except</code>.",
        "Catch specific exceptions; never hide bugs with a bare <code>except:</code>.",
        "<code>else</code> runs on success, <code>finally</code> always runs.",
        "<code>raise</code> your own errors with clear messages.",
    ],
}
