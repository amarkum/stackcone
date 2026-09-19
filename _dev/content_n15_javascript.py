"""JavaScript lessons 7-15."""
from content_js_sql import M

META = [
    M("js-control-flow", "javascript", "Conditionals and Loops", 12, "Beginner", "if/else, switch, for, while, for...of and truthy/falsy values.", ["Branch with if and switch", "Loop with for and for...of", "Explain truthy and falsy"]),
    M("js-strings-numbers", "javascript", "Strings, Numbers and Math", 12, "Beginner", "String methods, number quirks, parsing and the Math object.", ["Use common string methods", "Parse and format numbers", "Handle floating-point surprises"]),
    M("js-objects-this", "javascript", "Objects, this and Prototypes", 15, "Intermediate", "Object literals, methods, this binding and how prototypes share behaviour.", ["Write objects with methods", "Explain this", "Describe the prototype chain"]),
    M("js-classes", "javascript", "Classes and Inheritance", 14, "Intermediate", "class syntax, constructors, static members, getters and extends.", ["Write a class", "Use extends and super", "Add private fields"]),
    M("js-modules", "javascript", "Modules: import and export", 12, "Intermediate", "Split code into files with ES modules and use npm packages.", ["Use named and default exports", "Import modules", "Install an npm package"]),
    M("js-error-handling", "javascript", "Errors and Debugging", 13, "Intermediate", "try/catch/finally, throwing errors, custom errors and debugging tools.", ["Catch and throw errors", "Create custom errors", "Debug with the console and devtools"]),
    M("js-json-fetch", "javascript", "JSON and the Fetch API", 14, "Intermediate", "Talk to web APIs: fetch, JSON parsing, headers, POST and error handling.", ["Fetch JSON from an API", "Send a POST request", "Handle HTTP errors"]),
    M("js-iterators-generators", "javascript", "Iterators, Generators, Map and Set", 15, "Advanced", "Map, Set, symbols, iterators and generator functions.", ["Use Map and Set", "Write a generator", "Make an object iterable"]),
    M("js-testing", "javascript", "Testing JavaScript", 13, "Advanced", "Unit tests with Node's built-in runner or Jest, assertions and mocking.", ["Write unit tests", "Run tests from npm", "Mock a dependency"]),
]

CONTENT = {}

CONTENT["js-control-flow"] = [
    ("p", "Control flow decides which code runs and how many times. JavaScript has the usual tools plus a few quirks around what counts as true."),
    ("h2", "if / else and switch"),
    ("code", "javascript", 'const score = 72;\nif (score >= 90) console.log("A");\nelse if (score >= 70) console.log("B");\nelse console.log("C");\n\nconst day = "sat";\nswitch (day) {\n  case "sat":\n  case "sun":\n    console.log("weekend");\n    break;\n  default:\n    console.log("weekday");\n}'),
    ("output", "B\nweekend"),
    ("note", "break", "Without <code>break</code> a switch case <em>falls through</em> to the next one. Above, \"sat\" deliberately falls into the \"sun\" branch."),
    ("h2", "Truthy and falsy"),
    ("p", "Conditions do not need a boolean. These are <strong>falsy</strong>: <code>false</code>, <code>0</code>, <code>\"\"</code>, <code>null</code>, <code>undefined</code>, <code>NaN</code>. Everything else is truthy, including <code>\"0\"</code>, <code>[]</code> and <code>{}</code>."),
    ("code", "javascript", 'const name = "";\nconsole.log(name || "anonymous");     // || picks the first truthy\nconsole.log(0 ?? 10);                  // ?? only skips null/undefined\nconsole.log(Boolean([]));'),
    ("output", "anonymous\n0\ntrue"),
    ("h2", "Loops"),
    ("code", "javascript", 'for (let i = 0; i < 3; i++) console.log("i =", i);\n\nconst fruits = ["apple", "pear"];\nfor (const f of fruits) console.log(f);      // values of an iterable\n\nconst user = { id: 1, name: "Ada" };\nfor (const key in user) console.log(key);    // keys of an object\n\nlet n = 3;\nwhile (n > 0) n--;\nconsole.log(n);'),
    ("output", "i = 0\ni = 1\ni = 2\napple\npear\nid\nname\n0"),
    ("p", "Use <code>break</code> to leave a loop early and <code>continue</code> to skip to the next iteration."),
    ("exercise", "Print the numbers 1 to 20, but \"Fizz\" for multiples of 3, \"Buzz\" for multiples of 5 and \"FizzBuzz\" for both."),
]

CONTENT["js-strings-numbers"] = [
    ("p", "Strings and numbers look simple, but a handful of methods and one famous floating-point quirk cover most day-to-day surprises."),
    ("h2", "String methods"),
    ("code", "javascript", 'const s = "  Hello, World  ";\nconsole.log(s.trim());\nconsole.log(s.trim().toUpperCase());\nconsole.log(s.includes("World"));\nconsole.log(s.trim().slice(0, 5));\nconsole.log("a-b-c".split("-"));\nconsole.log("ha".repeat(3));\nconsole.log("7".padStart(3, "0"));\nconsole.log("abc".replaceAll("b", "X"));'),
    ("output", "Hello, World\nHELLO, WORLD\ntrue\nHello\n[ 'a', 'b', 'c' ]\nhahaha\n007\naXc"),
    ("p", "Strings are immutable: these methods return new strings and leave the original alone."),
    ("h2", "Numbers"),
    ("p", "JavaScript has one number type (a 64-bit float) plus <code>BigInt</code> for huge integers. That means decimals are approximate."),
    ("code", "javascript", 'console.log(0.1 + 0.2);\nconsole.log((0.1 + 0.2).toFixed(2));\nconsole.log(Math.abs(0.3 - (0.1 + 0.2)) < Number.EPSILON);\nconsole.log(parseInt("42px"), Number("42px"));\nconsole.log(Number.isInteger(5.0));'),
    ("output", "0.30000000000000004\n0.30\ntrue\n42 NaN\ntrue"),
    ("note", "Money", "Never store currency as floats. Keep integer cents (<code>1999</code>) and format at the edge."),
    ("h2", "The Math object"),
    ("code", "javascript", 'console.log(Math.round(2.5), Math.floor(2.9), Math.ceil(2.1));\nconsole.log(Math.max(3, 9, 4), Math.min(3, 9, 4));\nconsole.log(Math.max(...[5, 1, 8]));\nconst dice = Math.floor(Math.random() * 6) + 1;\nconsole.log(dice >= 1 && dice <= 6);'),
    ("output", "3 2 3\n9 3\n8\ntrue"),
    ("h2", "Formatting for people"),
    ("code", "javascript", 'console.log((1234567.891).toLocaleString("en-US"));\nconsole.log(new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(19.5));'),
    ("output", "1,234,567.891\n$19.50"),
    ("exercise", "Write a function that turns \"hello world\" into \"Hello World\" (capitalise each word)."),
]

CONTENT["js-objects-this"] = [
    ("p", "Objects are bags of properties. When a function lives on an object it is a <em>method</em>, and inside it the keyword <code>this</code> refers to the object it was called on."),
    ("h2", "Methods and this"),
    ("code", "javascript", '"use strict";\nconst user = {\n  name: "Ada",\n  greet() {\n    return `Hi, I am ${this.name}`;\n  },\n};\nconsole.log(user.greet());\n\nconst loose = user.greet;\ntry { console.log(loose()); } catch (e) { console.log("lost this"); }'),
    ("output", "Hi, I am Ada\nlost this"),
    ("p", "<code>this</code> is decided by <em>how a function is called</em>, not where it was written. Detached from its object it loses its owner. Fix it with <code>bind</code>, or use an arrow function, which takes <code>this</code> from the surrounding code."),
    ("code", "javascript", 'const user = { name: "Ada", greet() { return this.name; } };\nconst bound = user.greet.bind(user);\nconsole.log(bound());\n\nconst timer = {\n  n: 0,\n  start() { [1, 2, 3].forEach(() => this.n++); },   // arrow keeps this\n};\ntimer.start();\nconsole.log(timer.n);'),
    ("output", "Ada\n3"),
    ("h2", "Prototypes"),
    ("p", "Every object has a hidden link to a <strong>prototype</strong>. When you read a property JavaScript looks on the object, then its prototype, then that object's prototype, up the <em>prototype chain</em> until it finds it or reaches <code>null</code>."),
    ("code", "javascript", 'const animal = { eats: true, speak() { return "..."; } };\nconst dog = Object.create(animal);\ndog.bark = () => "Woof";\nconsole.log(dog.eats, dog.bark());\nconsole.log(Object.getPrototypeOf(dog) === animal);\nconsole.log(Object.hasOwn(dog, "eats"));'),
    ("output", "true Woof\ntrue\nfalse"),
    ("h2", "Handy object tools"),
    ("code", "javascript", 'const o = { a: 1, b: 2 };\nconsole.log(Object.keys(o), Object.values(o));\nconsole.log(Object.entries(o));\nconsole.log({ ...o, c: 3 });\nconsole.log(Object.fromEntries([["x", 1]]));\nconst frozen = Object.freeze({ id: 1 });\ntry { frozen.id = 2; } catch { console.log("frozen!"); }\nconsole.log(frozen.id);'),
    ("output", "[ 'a', 'b' ] [ 1, 2 ]\n[ [ 'a', 1 ], [ 'b', 2 ] ]\n{ a: 1, b: 2, c: 3 }\n{ x: 1 }\nfrozen!\n1"),
    ("exercise", "Create a counter object with <code>count</code>, <code>increment()</code> and <code>reset()</code> methods, then call increment through a detached reference and fix it."),
]

CONTENT["js-classes"] = [
    ("p", "The <code>class</code> keyword is friendlier syntax over the prototype system. It bundles data and the functions that work on it."),
    ("h2", "A class"),
    ("code", "javascript", 'class Account {\n  #balance = 0;                 // private field\n  static count = 0;\n\n  constructor(owner) {\n    this.owner = owner;\n    Account.count++;\n  }\n  deposit(n) {\n    if (n <= 0) throw new Error("positive only");\n    this.#balance += n;\n    return this;                // allows chaining\n  }\n  get balance() { return this.#balance; }\n}\n\nconst a = new Account("Ada");\na.deposit(50).deposit(25);\nconsole.log(a.balance, Account.count);\nconsole.log(a.owner);'),
    ("output", "75 1\nAda"),
    ("ul", [
        "<code>#name</code> fields are truly private; code outside the class cannot read them.",
        "<code>static</code> members belong to the class, not to instances.",
        "A <code>get</code> accessor reads like a property but runs code.",
    ]),
    ("h2", "Inheritance"),
    ("code", "javascript", 'class Shape {\n  area() { return 0; }\n  describe() { return `${this.constructor.name} with area ${this.area()}`; }\n}\nclass Square extends Shape {\n  constructor(side) { super(); this.side = side; }\n  area() { return this.side ** 2; }\n}\nconsole.log(new Square(4).describe());\nconsole.log(new Square(2) instanceof Shape);'),
    ("output", "Square with area 16\ntrue"),
    ("note", "super() first", "In a subclass constructor you must call <code>super()</code> before using <code>this</code>."),
    ("h2", "Classes are not always the answer"),
    ("p", "Plain objects and functions are often simpler. Reach for a class when you have many instances that share behaviour and need to keep private state."),
    ("exercise", "Write a Stack class (push, pop, peek, size) that keeps its array in a private field."),
]

CONTENT["js-modules"] = [
    ("p", "A module is a file with its own scope. You choose what to <strong>export</strong> and other files <strong>import</strong> it, so code stays organised and names do not collide."),
    ("h2", "Named and default exports"),
    ("code", "javascript", '// math.js\nexport const PI = 3.14159;\nexport function add(a, b) { return a + b; }\nexport default function multiply(a, b) { return a * b; }\n\n// main.js\nimport multiply, { PI, add } from "./math.js";\nimport * as math from "./math.js";\n\nconsole.log(add(2, 3), multiply(2, 3), PI);\nconsole.log(math.add(1, 1));'),
    ("ul", [
        "A file may have many <strong>named</strong> exports but only one <strong>default</strong>.",
        "Named imports use braces and exact names; a default import can be named freely.",
        "<code>import * as x</code> gathers every export under one object.",
    ]),
    ("h2", "Using modules"),
    ("p", "In the browser add <code>type=\"module\"</code>. In Node, use the <code>.mjs</code> extension or set <code>\"type\": \"module\"</code> in <code>package.json</code>."),
    ("code", "javascript", '<script type="module" src="main.js"></script>'),
    ("h2", "npm packages"),
    ("code", "bash", "npm init -y\nnpm install dayjs\n# now: import dayjs from \"dayjs\";"),
    ("p", "<code>package.json</code> records your dependencies; <code>node_modules</code> holds the downloaded code (do not commit it) and <code>package-lock.json</code> pins exact versions."),
    ("h2", "Dynamic import"),
    ("code", "javascript", 'const button = document.querySelector("#chart");\nbutton.addEventListener("click", async () => {\n  const { drawChart } = await import("./chart.js");   // loaded only when needed\n  drawChart();\n});'),
    ("note", "CommonJS", "Older Node code uses <code>require()</code> and <code>module.exports</code>. You will meet it in existing projects, but new code should use ES modules."),
    ("exercise", "Split a small program into <code>utils.js</code> (two helpers) and <code>main.js</code> that imports and uses them."),
]

CONTENT["js-error-handling"] = [
    ("p", "When something goes wrong JavaScript <em>throws</em> an error. If nothing catches it, the program stops. <code>try/catch</code> lets you respond instead."),
    ("h2", "try, catch, finally"),
    ("code", "javascript", 'function parse(json) {\n  try {\n    return JSON.parse(json);\n  } catch (err) {\n    console.log("bad json:", err.name);\n    return null;\n  } finally {\n    console.log("done");\n  }\n}\nconsole.log(parse(\'{"a":1}\'));\nconsole.log(parse("{oops"));'),
    ("output", "done\n{ a: 1 }\nbad json: SyntaxError\ndone\nnull"),
    ("p", "<code>finally</code> always runs, which makes it the place for cleanup."),
    ("h2", "Throwing and custom errors"),
    ("code", "javascript", 'class ValidationError extends Error {\n  constructor(field, message) {\n    super(message);\n    this.name = "ValidationError";\n    this.field = field;\n  }\n}\n\nfunction setAge(age) {\n  if (age < 0) throw new ValidationError("age", "age cannot be negative");\n  return age;\n}\n\ntry {\n  setAge(-1);\n} catch (e) {\n  if (e instanceof ValidationError) console.log(e.field, "-", e.message);\n  else throw e;                 // do not swallow unknown errors\n}'),
    ("output", "age - age cannot be negative"),
    ("h2", "Async errors"),
    ("code", "javascript", 'async function load() {\n  try {\n    const res = await fetch("https://example.invalid/data");\n    return await res.json();\n  } catch (e) {\n    console.log("request failed");\n  }\n}\nload();\n\nPromise.reject(new Error("x")).catch(e => console.log(e.message));'),
    ("h2", "Debugging tools"),
    ("ul", [
        "<code>console.log</code>, <code>console.table(array)</code>, <code>console.error</code> and <code>console.time</code> / <code>timeEnd</code>.",
        "The <code>debugger;</code> statement pauses execution when devtools are open.",
        "Devtools <strong>Sources</strong> tab: set breakpoints, step through code, watch variables. Read the <strong>stack trace</strong> from the top: the first line of your own code is usually the culprit.",
    ]),
    ("exercise", "Write <code>safeDivide(a, b)</code> that throws a custom error when b is 0, and call it inside try/catch."),
]

CONTENT["js-json-fetch"] = [
    ("p", "Web apps constantly exchange data with servers as <strong>JSON</strong>. <code>fetch</code> makes the request and returns a promise."),
    ("h2", "JSON basics"),
    ("code", "javascript", 'const user = { id: 1, name: "Ada", tags: ["math"] };\nconst text = JSON.stringify(user);\nconsole.log(text);\nconsole.log(JSON.parse(text).name);\nconsole.log(JSON.stringify(user, null, 2));'),
    ("output", '{"id":1,"name":"Ada","tags":["math"]}\nAda\n{\n  "id": 1,\n  "name": "Ada",\n  "tags": [\n    "math"\n  ]\n}'),
    ("p", "JSON keeps only data: functions and <code>undefined</code> are dropped, and dates become strings."),
    ("h2", "GET request"),
    ("code", "javascript", 'async function getPost(id) {\n  const res = await fetch(`https://jsonplaceholder.typicode.com/posts/${id}`);\n  if (!res.ok) throw new Error(`HTTP ${res.status}`);   // fetch does NOT reject on 404/500\n  return res.json();\n}\n\ngetPost(1).then(p => console.log(p.title)).catch(console.error);'),
    ("note", "Check res.ok", "<code>fetch</code> only rejects on network failure. A 404 or 500 still resolves, so always check <code>res.ok</code>."),
    ("h2", "POST with JSON"),
    ("code", "javascript", 'const res = await fetch("https://jsonplaceholder.typicode.com/posts", {\n  method: "POST",\n  headers: { "Content-Type": "application/json" },\n  body: JSON.stringify({ title: "Hello", userId: 1 }),\n});\nconsole.log(res.status, await res.json());'),
    ("h2", "Several requests, timeouts"),
    ("code", "javascript", 'const [a, b] = await Promise.all([getPost(1), getPost(2)]);   // in parallel\n\nconst controller = new AbortController();\nsetTimeout(() => controller.abort(), 5000);\nawait fetch(url, { signal: controller.signal });           // cancel after 5s'),
    ("exercise", "Fetch a list of users from jsonplaceholder and render each name into a &lt;ul&gt; on the page, with a loading and an error message."),
]

CONTENT["js-iterators-generators"] = [
    ("p", "Beyond arrays and plain objects, JavaScript has <code>Map</code> and <code>Set</code> collections and a protocol for custom iteration."),
    ("h2", "Map and Set"),
    ("code", "javascript", 'const seen = new Set([1, 2, 2, 3]);\nseen.add(3);\nconsole.log(seen.size, seen.has(2));\nconsole.log([...new Set("mississippi")].join(""));\n\nconst ages = new Map();\nages.set("Ada", 36).set("Linus", 28);\nconsole.log(ages.get("Ada"), ages.size);\nfor (const [name, age] of ages) console.log(name, age);'),
    ("output", "3 true\nmisp\n36 2\nAda 36\nLinus 28"),
    ("p", "Use <code>Map</code> when keys are not strings or you add and remove often; a <code>Set</code> is the easy way to remove duplicates."),
    ("h2", "Generators"),
    ("p", "A generator function (<code>function*</code>) can <strong>pause</strong> at <code>yield</code> and resume later, producing values one at a time."),
    ("code", "javascript", 'function* count(limit) {\n  for (let i = 1; i <= limit; i++) yield i;\n}\nconsole.log([...count(4)]);\n\nfunction* naturals() {\n  let n = 1;\n  while (true) yield n++;     // infinite, but lazy\n}\nconst it = naturals();\nconsole.log(it.next().value, it.next().value, it.next().value);'),
    ("output", "[ 1, 2, 3, 4 ]\n1 2 3"),
    ("h2", "Making your own iterable"),
    ("code", "javascript", 'class Range {\n  constructor(a, b) { this.a = a; this.b = b; }\n  *[Symbol.iterator]() {\n    for (let i = this.a; i <= this.b; i++) yield i;\n  }\n}\nfor (const n of new Range(1, 3)) console.log(n);\nconsole.log(Math.max(...new Range(1, 5)));'),
    ("output", "1\n2\n3\n5"),
    ("note", "Async generators", "<code>async function*</code> with <code>for await ... of</code> lets you consume data that arrives over time, such as paged API results."),
    ("exercise", "Write a generator <code>fibonacci()</code> and print the first ten values."),
]

CONTENT["js-testing"] = [
    ("p", "Tests are code that checks your code. They catch regressions when you change things later and document how functions should behave."),
    ("h2", "The built-in Node test runner"),
    ("code", "javascript", '// sum.js\nexport function sum(a, b) { return a + b; }\n\n// sum.test.js\nimport { test } from "node:test";\nimport assert from "node:assert/strict";\nimport { sum } from "./sum.js";\n\ntest("adds numbers", () => {\n  assert.equal(sum(2, 3), 5);\n});\n\ntest("adds negatives", () => {\n  assert.equal(sum(-2, -3), -5);\n});'),
    ("code", "bash", "node --test"),
    ("h2", "Jest / Vitest style"),
    ("p", "Most projects use Jest or Vitest. Their API is nearly identical: <code>describe</code> groups tests, <code>test</code> defines one, and <code>expect</code> checks a value."),
    ("code", "javascript", 'import { describe, test, expect } from "vitest";\nimport { sum } from "./sum.js";\n\ndescribe("sum", () => {\n  test("adds", () => {\n    expect(sum(1, 2)).toBe(3);\n  });\n  test("arrays compare by value with toEqual", () => {\n    expect([1, 2]).toEqual([1, 2]);\n  });\n  test("throws", () => {\n    expect(() => JSON.parse("{")).toThrow();\n  });\n});'),
    ("h2", "Async tests and mocks"),
    ("code", "javascript", 'import { test, expect, vi } from "vitest";\n\ntest("loads a user", async () => {\n  const fetchUser = vi.fn().mockResolvedValue({ name: "Ada" });   // fake dependency\n  const user = await fetchUser(1);\n  expect(user.name).toBe("Ada");\n  expect(fetchUser).toHaveBeenCalledWith(1);\n});'),
    ("h2", "Add it to npm"),
    ("code", "bash", 'npm pkg set scripts.test="vitest run"\nnpm test'),
    ("note", "What to test", "Test behaviour, not implementation. Cover the normal case, edge cases (empty, zero, huge) and expected failures."),
    ("exercise", "Write three tests for a <code>capitalize(word)</code> function including the empty string."),
]
