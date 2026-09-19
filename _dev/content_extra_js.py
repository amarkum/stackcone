"""Extra teaching material for the JavaScript lessons (outputs come from real Node runs)."""
from extra_util import js

EXTRA = {}

EXTRA["js-hello-world"] = {
    "intro": [
        ("h2", "What JavaScript is for"),
        ("p", "Every web page has three layers. <strong>HTML</strong> is the structure (headings, paragraphs, buttons). <strong>CSS</strong> is the look (colours, spacing, layout). <strong>JavaScript</strong> is the behaviour: what happens when you click, type, scroll or wait. Without it a page is a poster; with it a page is an application. Since Node.js arrived, the same language also runs servers, scripts and command-line tools."),
        ("p", "That makes JavaScript unusual: learn it once and you can build the front end, the back end and everything in between."),
    ],
    "more": [
        ("h2", "Try it right now in your browser"),
        ("p", "You already have a JavaScript playground installed. In any browser, press <strong>F12</strong> (or <strong>Cmd+Option+J</strong> on a Mac), open the <em>Console</em> tab, type a line and press Enter. It runs immediately, and you can experiment without saving anything."),
        *js('console.log("Hello from the console");\nconsole.log(2 + 3 * 4);\nconsole.log("5" + 1, "5" - 1);'),
        ("p", "Look at the last line: the same <code>5</code> behaves differently with <code>+</code> and <code>-</code>. JavaScript quietly converts between types, which is powerful and occasionally surprising. The next lesson explains the rules so they stop being surprising."),
        ("h2", "console.log is your best friend"),
        ("p", "When you want to know what a value is, print it. <code>console.log</code> accepts several values and understands objects and arrays, so it is the fastest debugging tool you have."),
        *js('const user = { name: "Ada", langs: ["JS", "Python"] };\nconsole.log(user);\nconsole.log("Name:", user.name, "| count:", user.langs.length);\nconsole.table([{ id: 1, ok: true }, { id: 2, ok: false }]);'),
        ("h2", "Your first HTML page with JavaScript"),
        ("p", "Save this as <code>index.html</code> and double-click it. The <code>&lt;script&gt;</code> tag holds your code, and <code>document.title</code> is a value the browser gives you for free."),
        ("code", "html", '<!DOCTYPE html>\n<html>\n  <body>\n    <h1 id="title">Hello</h1>\n    <script>\n      const heading = document.getElementById("title");\n      heading.textContent = "Hello, JavaScript!";\n      console.log("page title is", document.title);\n    </script>\n  </body>\n</html>'),
        ("p", "Refresh the page and the heading changes: your code reached into the page and rewrote it. You will do exactly this in the DOM lesson."),
    ],
    "recap": [
        "JavaScript adds behaviour to HTML and CSS, and also runs on servers through Node.js.",
        "The browser console and <code>node file.js</code> are the two quickest places to run code.",
        "<code>console.log</code> prints values and objects; use it constantly while learning.",
        "JavaScript converts types automatically, so learn the rules in the next lesson.",
    ],
}

EXTRA["js-variables-types"] = {
    "intro": [
        ("h2", "Storing information"),
        ("p", "Programs are mostly about moving information around: a name typed in a form, a price from a server, a score in a game. A <strong>variable</strong> is a named place to keep that information so you can use it later. In modern JavaScript you create one with <code>const</code> (a value you will not reassign) or <code>let</code> (a value that may change)."),
        *js('const siteName = "stackcone";\nlet visitors = 10;\nvisitors = visitors + 1;\nconsole.log(siteName, visitors);'),
        ("p", "Try to reassign a <code>const</code> and JavaScript refuses with a <code>TypeError</code>. That is a feature: it protects you from accidentally overwriting something. A good habit is to write <code>const</code> by default and switch to <code>let</code> only when you truly need to change the value."),
    ],
    "more": [
        ("h2", "The typeof operator"),
        ("p", "When unsure what you are holding, ask. <code>typeof</code> returns the type as text. There is one famous quirk: <code>typeof null</code> says <code>\"object\"</code>, a bug from 1995 that can never be fixed."),
        *js('console.log(typeof 42, typeof 3.14);\nconsole.log(typeof "hi", typeof true);\nconsole.log(typeof undefined, typeof null);\nconsole.log(typeof [1, 2], Array.isArray([1, 2]));'),
        ("h2", "undefined versus null"),
        ("p", "<code>undefined</code> means \"no value has been given yet\": a variable you declared but never set, or a property that does not exist. <code>null</code> means \"I deliberately have nothing here.\" You will mostly meet <code>undefined</code> as JavaScript's way of saying you asked for something that was not there."),
        *js('let notSet;\nconst user = { name: "Ada" };\nconsole.log(notSet);\nconsole.log(user.email);\nconsole.log(user.email ?? "no email on file");'),
        ("h2", "Numbers: what to watch for"),
        *js('console.log(0.1 + 0.2);\nconsole.log((0.1 + 0.2).toFixed(2));\nconsole.log(10 / 3, 10 % 3);\nconsole.log(Number("42"), Number("abc"));\nconsole.log(Number.isNaN(Number("abc")));'),
        ("p", "Like most languages, JavaScript stores decimals in binary, so <code>0.1 + 0.2</code> is not exactly <code>0.3</code>. For money, count whole cents as integers or round with <code>toFixed</code>. <code>NaN</code> (\"not a number\") is what you get when a conversion fails; it is the only value not equal to itself, so test it with <code>Number.isNaN</code>."),
        ("h2", "Converting between types on purpose"),
        *js('console.log(String(123) + "!");\nconsole.log(Number("7") + 1);\nconsole.log(parseInt("42px"), parseFloat("3.5kg"));\nconsole.log(Boolean(""), Boolean("text"), Boolean(0), Boolean([]));'),
    ],
    "recap": [
        "Use <code>const</code> by default and <code>let</code> when a value must change; avoid <code>var</code>.",
        "Primitive types: string, number, boolean, <code>undefined</code>, <code>null</code>, bigint, symbol.",
        "<code>typeof</code> reveals a type; <code>Number.isNaN</code> checks failed conversions.",
        "Always compare with <code>===</code>, and know which values are falsy.",
    ],
}

EXTRA["js-functions"] = {
    "intro": [
        ("h2", "Functions are the building blocks"),
        ("p", "A function packages a task so you can run it whenever you like, with different inputs each time. Instead of repeating the same lines in five places, you write them once, name them, and call the name. In JavaScript functions are also <em>values</em>: you can store them in variables, pass them to other functions and return them, which is why so much JavaScript code is built from small functions handed to other functions."),
        *js('function greet(name) {\n  return "Hello, " + name + "!";\n}\n\nconsole.log(greet("Ada"));\nconsole.log(greet("Linus"));'),
    ],
    "more": [
        ("h2", "Parameters, arguments and return values"),
        ("p", "The names in the definition are <em>parameters</em>; the actual values you pass are <em>arguments</em>. A function without a <code>return</code> gives back <code>undefined</code>. A function stops running the moment it returns."),
        *js('function area(w, h) {\n  if (w <= 0 || h <= 0) return 0;   // early return\n  return w * h;\n}\n\nconsole.log(area(3, 4), area(-1, 5));\n\nfunction noReturn() { const x = 1; }\nconsole.log(noReturn());'),
        ("h2", "Arrow functions in plain words"),
        ("p", "An arrow function is a shorter way to write a small function. Read <code>(x) =&gt; x * 2</code> as \"given x, produce x times 2.\" When the body is one expression, the <code>return</code> is implied."),
        *js('const double = (x) => x * 2;\nconst add = (a, b) => a + b;\nconst logAndAdd = (a, b) => {\n  console.log("adding", a, b);\n  return a + b;\n};\n\nconsole.log(double(21), add(2, 3), logAndAdd(4, 5));'),
        ("h2", "Closures: a function that remembers"),
        ("p", "A function remembers the variables that existed where it was created, even after that outer code has finished. This lets you build functions that keep private state, like a counter that nobody else can tamper with."),
        *js('function makeCounter() {\n  let count = 0;\n  return () => {\n    count += 1;\n    return count;\n  };\n}\n\nconst a = makeCounter();\nconst b = makeCounter();\nconsole.log(a(), a(), a());\nconsole.log(b());'),
        ("h2", "Callbacks: passing a function to a function"),
        *js('function repeat(times, action) {\n  for (let i = 1; i <= times; i++) action(i);\n}\n\nrepeat(3, (n) => console.log("round", n));\n\n[10, 20, 30].forEach((v, i) => console.log(i, v));'),
    ],
    "recap": [
        "A function names reusable work: parameters in, <code>return</code> out.",
        "Arrow functions <code>(a, b) =&gt; a + b</code> are concise; use them for short callbacks.",
        "Closures let a function remember the variables from where it was created.",
        "Functions are values: store them, pass them, and return them.",
    ],
}

EXTRA["js-arrays-objects"] = {
    "intro": [
        ("h2", "The two shapes of data"),
        ("p", "Almost all data in JavaScript is one of two shapes, or a mix of both. An <strong>array</strong> is an ordered list: <code>[\"red\", \"green\", \"blue\"]</code>. An <strong>object</strong> is a set of named properties: <code>{ name: \"Ada\", age: 36 }</code>. A list of users is an array of objects. JSON, the format almost every web API speaks, is exactly these two shapes written as text."),
        *js('const colors = ["red", "green", "blue"];\nconst user = { name: "Ada", age: 36 };\nconst users = [user, { name: "Linus", age: 54 }];\n\nconsole.log(colors[1], user.name, users[1].age);\nconsole.log(users.length);'),
    ],
    "more": [
        ("h2", "Changing arrays"),
        *js('const nums = [3, 1, 2];\nnums.push(4);          // add to the end\nnums.unshift(0);       // add to the start\nconst last = nums.pop();\nnums.sort((a, b) => a - b);\n\nconsole.log(nums, last);\nconsole.log(nums.includes(2), nums.indexOf(3));'),
        ("note", "sort needs a comparator for numbers", "Without <code>(a, b) =&gt; a - b</code>, <code>sort()</code> compares items as text, so <code>[10, 9, 1]</code> sorts to <code>[1, 10, 9]</code>."),
        ("h2", "Thinking in map, filter and reduce"),
        ("p", "Instead of writing a loop that builds a new array by hand, describe the transformation. <code>map</code> changes every item, <code>filter</code> keeps some items, and <code>reduce</code> folds all items into one value. They chain together like a pipeline."),
        *js('const orders = [\n  { item: "book", price: 12, qty: 2 },\n  { item: "pen", price: 2, qty: 10 },\n  { item: "bag", price: 40, qty: 1 },\n];\n\nconst totals = orders.map(o => o.price * o.qty);\nconst big = orders.filter(o => o.price * o.qty >= 24);\nconst grand = totals.reduce((sum, t) => sum + t, 0);\n\nconsole.log(totals);\nconsole.log(big.map(o => o.item));\nconsole.log(grand);'),
        ("h2", "Finding one item"),
        *js('const users = [{ id: 1, name: "Ada" }, { id: 2, name: "Linus" }];\nconsole.log(users.find(u => u.id === 2));\nconsole.log(users.find(u => u.id === 9));\nconsole.log(users.some(u => u.name === "Ada"), users.every(u => u.id > 1));'),
        ("h2", "Working with object properties"),
        *js('const car = { make: "Toyota", year: 2020 };\ncar.color = "blue";        // add\ncar.year = 2021;           // change\ndelete car.make;           // remove\n\nconsole.log(car);\nconsole.log(Object.keys(car), Object.values(car));\nconsole.log("color" in car, car.wheels);'),
        ("h2", "Optional chaining for safe access"),
        *js('const data = { user: { profile: null } };\n\nconsole.log(data.user.profile?.email);          // undefined, no crash\nconsole.log(data.settings?.theme ?? "light");'),
    ],
    "recap": [
        "Arrays are ordered lists; objects are named properties; real data is a mix.",
        "<code>map</code> transforms, <code>filter</code> selects, <code>reduce</code> combines; chain them.",
        "<code>find</code>, <code>some</code> and <code>every</code> answer questions about an array.",
        "Use <code>?.</code> and <code>??</code> to read data that might be missing.",
    ],
}

EXTRA["js-async"] = {
    "intro": [
        ("h2", "Why waiting is hard"),
        ("p", "Some work is slow: loading data from a server, reading a file, waiting for a timer. JavaScript has a single main thread, so if it simply stood still until each slow task finished, the whole page would freeze. Instead it starts the slow job, carries on with other work, and comes back when the result is ready. Think of ordering coffee: you give your order, take a buzzer, sit down, and collect the drink when the buzzer goes off. The buzzer is a <strong>Promise</strong>."),
        *js('console.log("1: order coffee");\nsetTimeout(() => console.log("3: coffee is ready"), 100);\nconsole.log("2: check phone while waiting");'),
        ("p", "Notice the order. The timer's message prints <em>last</em>, even though it was written second. The code did not wait; it scheduled the callback and moved on."),
    ],
    "more": [
        ("h2", "A promise has three states"),
        ("ul", [
            "<strong>pending</strong>: the work has started and is not finished.",
            "<strong>fulfilled</strong>: it finished and produced a value.",
            "<strong>rejected</strong>: it failed and produced an error.",
        ]),
        *js('const wait = (ms, value) => new Promise(resolve => setTimeout(() => resolve(value), ms));\n\nwait(50, "done").then(v => console.log("resolved with", v));\nconsole.log("this prints first");'),
        ("h2", "Same thing, easier to read: async and await"),
        ("p", "<code>await</code> pauses <em>that function</em> until the promise settles, then gives you the value as if the code were ordinary top-to-bottom. It can only be used inside an <code>async</code> function. Other code keeps running while you wait."),
        *js('const wait = (ms, value) => new Promise(r => setTimeout(() => r(value), ms));\n\nasync function main() {\n  console.log("start");\n  const a = await wait(50, "first");\n  const b = await wait(50, "second");\n  console.log(a, b);\n  console.log("end");\n}\nmain();'),
        ("h2", "Handling failure"),
        *js('const failing = () => new Promise((_, reject) => setTimeout(() => reject(new Error("server down")), 20));\n\nasync function load() {\n  try {\n    await failing();\n  } catch (err) {\n    console.log("caught:", err.message);\n  } finally {\n    console.log("cleanup");\n  }\n}\nload();'),
        ("h2", "Sequential versus parallel"),
        ("p", "Two <code>await</code>s in a row run one after the other, which is slow if the tasks are independent. Start them together and wait for both with <code>Promise.all</code>."),
        *js('const wait = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));\n\nasync function main() {\n  let t = Date.now();\n  await wait(100); await wait(100);\n  console.log("one by one:", Math.round((Date.now() - t) / 100) * 100, "ms");\n\n  t = Date.now();\n  const [a, b] = await Promise.all([wait(100, "x"), wait(100, "y")]);\n  console.log("together:", Math.round((Date.now() - t) / 100) * 100, "ms", a, b);\n}\nmain();'),
        ("h2", "A realistic fetch example"),
        ("code", "javascript", 'async function getUser(id) {\n  const response = await fetch(`https://api.example.com/users/${id}`);\n  if (!response.ok) {\n    throw new Error(`Request failed: ${response.status}`);\n  }\n  return response.json();   // also returns a promise\n}\n\ngetUser(1)\n  .then(user => console.log(user.name))\n  .catch(err => console.error(err.message));'),
    ],
    "recap": [
        "Slow work returns a Promise (pending, fulfilled or rejected) so the page never freezes.",
        "<code>async</code>/<code>await</code> lets you read asynchronous code top to bottom.",
        "Wrap awaits in <code>try/catch</code>; check <code>response.ok</code> when using <code>fetch</code>.",
        "Use <code>Promise.all</code> for independent tasks that can run together.",
    ],
}

EXTRA["js-dom"] = {
    "intro": [
        ("h2", "What the DOM is"),
        ("p", "When a browser loads HTML it builds a live tree of objects in memory, one for every element. That tree is the <strong>DOM</strong> (Document Object Model). JavaScript can find any node in the tree, read it, change it, add new ones, and react when the user interacts with them. Everything dynamic on a web page, from a dropdown menu to a live search, is JavaScript editing the DOM."),
        ("p", "Picture the HTML as a family tree: <code>&lt;html&gt;</code> is the ancestor, <code>&lt;body&gt;</code> a child, and each paragraph or button a leaf further down. To change the page you locate the right relative, then change it."),
        ("code", "html", '<body>\n  <h1 id="title">Todo</h1>\n  <ul id="list">\n    <li>Learn JS</li>\n  </ul>\n</body>'),
    ],
    "more": [
        ("h2", "A complete example: a working to-do list"),
        ("p", "This page combines everything from the lesson: find elements, listen for a click, read an input, create an element and add it to the page. Save it as <code>todo.html</code> and open it in your browser."),
        ("code", "html", '<!DOCTYPE html>\n<html>\n<body>\n  <h1>My tasks</h1>\n  <input id="task" placeholder="New task">\n  <button id="add">Add</button>\n  <ul id="list"></ul>\n\n  <script>\n    const input = document.querySelector("#task");\n    const list = document.querySelector("#list");\n\n    document.querySelector("#add").addEventListener("click", () => {\n      const text = input.value.trim();\n      if (!text) return;               // ignore empty input\n\n      const li = document.createElement("li");\n      li.textContent = text;           // textContent is safe from HTML injection\n      list.append(li);\n\n      input.value = "";\n      input.focus();\n    });\n  </script>\n</body>\n</html>'),
        ("h2", "How to read that code"),
        ("ul", [
            "<code>querySelector</code> finds the first element matching a CSS selector.",
            "<code>addEventListener(\"click\", fn)</code> registers <code>fn</code> to run each time the button is clicked.",
            "Inside the handler we read the input's <code>value</code>, create an <code>&lt;li&gt;</code>, set its text and <code>append</code> it to the list.",
            "Finally we clear the field and put the cursor back so the user can type the next task.",
        ]),
        ("h2", "Toggling classes instead of styles"),
        ("p", "Rather than setting colours from JavaScript, add or remove a CSS class and let the stylesheet decide how it looks. This keeps design in CSS and behaviour in JavaScript."),
        ("code", "html", '<style>\n  .done { text-decoration: line-through; color: gray; }\n</style>\n<ul id="list"><li>Buy milk</li><li>Write code</li></ul>\n<script>\n  document.querySelector("#list").addEventListener("click", (event) => {\n    if (event.target.matches("li")) {\n      event.target.classList.toggle("done");\n    }\n  });\n</script>'),
        ("note", "Never use innerHTML with user input", "Setting <code>innerHTML</code> from text a user typed lets them inject scripts (an XSS attack). Use <code>textContent</code> for plain text, or create elements with <code>createElement</code>."),
        ("h2", "Debugging DOM code"),
        ("ul", [
            "<code>null</code> errors usually mean your selector found nothing. Check the spelling and that the script runs after the element exists.",
            "Open DevTools, choose the <em>Elements</em> tab and confirm what the page really contains.",
            "Log the event: <code>console.log(event.target)</code> shows exactly what was clicked.",
        ]),
    ],
    "recap": [
        "The DOM is a live tree of objects the browser builds from your HTML.",
        "Find with <code>querySelector</code>, change with <code>textContent</code> and <code>classList</code>, add with <code>createElement</code> and <code>append</code>.",
        "React to users with <code>addEventListener</code>; use one listener on a parent for many children.",
        "Prefer <code>textContent</code> over <code>innerHTML</code> for user text.",
    ],
}
