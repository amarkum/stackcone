"""Extra teaching material for the HTML & CSS lessons."""

EXTRA = {}

EXTRA["html-introduction"] = {
    "intro": [
        ("h2", "What is HTML?"),
        ("p", "Every web page you have ever seen, from a simple blog to a huge web app, is built from <strong>HTML</strong>: HyperText Markup Language. HTML does not make things pretty or interactive; it describes what things <em>are</em>. This is a heading, this is a paragraph, this is a link, this is an image. The browser reads that description and draws the page. CSS then styles it and JavaScript makes it behave."),
        ("p", "The good news: HTML is not a programming language, so there are no variables or loops to learn. It is a set of labels you attach to content. You can be productive within an hour."),
        ("h2", "Your first page in two minutes"),
        ("p", "You need only a text editor (Notepad, TextEdit in plain-text mode, or VS Code) and a browser. Create a file called <code>index.html</code>, paste the code below, save it and double-click the file. The browser opens it."),
        ("code", "html", '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8">\n    <title>My first page</title>\n  </head>\n  <body>\n    <h1>Hello, web!</h1>\n    <p>This is my <strong>first</strong> page.</p>\n  </body>\n</html>'),
    ],
    "more": [
        ("h2", "Reading that page, line by line"),
        ("ul", [
            "<code>&lt;!DOCTYPE html&gt;</code> tells the browser to use modern HTML.",
            "<code>&lt;html lang=\"en\"&gt;</code> wraps everything and declares the language (helps screen readers and translation).",
            "<code>&lt;head&gt;</code> holds information <em>about</em> the page that is not shown in the window: the title in the browser tab, the character set, links to stylesheets.",
            "<code>&lt;body&gt;</code> holds everything visible.",
            "<code>&lt;h1&gt;</code> is the main heading, <code>&lt;p&gt;</code> a paragraph and <code>&lt;strong&gt;</code> marks important text (shown bold).",
        ]),
        ("h2", "Tags come in pairs"),
        ("p", "Most elements have an opening tag, some content and a closing tag with a slash: <code>&lt;p&gt;text&lt;/p&gt;</code>. A few elements have no content and no closing tag, such as <code>&lt;img&gt;</code> and <code>&lt;br&gt;</code>. Elements nest like boxes inside boxes, so always close the innermost one first."),
        ("code", "html", "<!-- correct nesting -->\n<p>This is <em>very <strong>important</strong></em> text.</p>\n\n<!-- wrong: tags overlap -->\n<p>This is <em>very <strong>important</em></strong> text.</p>"),
        ("h2", "Headings create an outline"),
        ("p", "Use <code>&lt;h1&gt;</code> once for the page title, then <code>&lt;h2&gt;</code> for main sections and <code>&lt;h3&gt;</code> for subsections beneath them. Do not pick a heading because of its size; pick it for its <em>meaning</em>. Search engines and screen-reader users navigate by this outline, and you can restyle sizes with CSS later."),
        ("h2", "Links and images, the two things that make it the Web"),
        ("code", "html", '<p>Read the <a href="https://developer.mozilla.org/">MDN docs</a>.</p>\n<p><a href="about.html">About us</a> (another page in the same folder)</p>\n<p><a href="#contact">Jump to the contact section</a></p>\n\n<img src="cat.jpg" alt="A grey cat asleep on a sofa" width="300">'),
        ("p", "The <code>href</code> attribute says where a link goes; <code>src</code> says where an image lives; <code>alt</code> describes the image for people who cannot see it and appears if it fails to load. Never leave <code>alt</code> out."),
        ("h2", "Lists: the workhorse of page structure"),
        ("code", "html", "<ul>          <!-- unordered: bullet points -->\n  <li>Milk</li>\n  <li>Eggs</li>\n</ul>\n\n<ol>          <!-- ordered: numbered steps -->\n  <li>Open the file</li>\n  <li>Edit it</li>\n  <li>Save it</li>\n</ol>"),
        ("h2", "Troubleshooting checklist"),
        ("ul", [
            "Nothing changes when you refresh? Make sure you saved the file, and that you edited the file the browser has open.",
            "Text looks wrong or shows odd symbols? Add <code>&lt;meta charset=\"UTF-8\"&gt;</code> in the <code>&lt;head&gt;</code>.",
            "Image is missing? Check the spelling and case of the file name and that the path matches where the file really is.",
            "Right-click the page and choose <em>Inspect</em> to see exactly how the browser understood your HTML.",
        ]),
    ],
    "recap": [
        "HTML labels what content <em>is</em>; CSS styles it; JavaScript adds behaviour.",
        "A page has a <code>&lt;head&gt;</code> (information about the page) and a <code>&lt;body&gt;</code> (what people see).",
        "Elements nest; attributes such as <code>href</code>, <code>src</code> and <code>alt</code> add details.",
        "Choose headings by meaning, and always write useful <code>alt</code> text.",
    ],
}

EXTRA["html-forms-semantics"] = {
    "intro": [
        ("h2", "Structure with meaning"),
        ("p", "You could build every page from generic boxes, but browsers, search engines and assistive technology cannot tell a navigation menu from a footer if everything is a box. <strong>Semantic</strong> elements such as <code>&lt;header&gt;</code>, <code>&lt;nav&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;article&gt;</code> and <code>&lt;footer&gt;</code> describe the role of each region. They cost nothing and make pages more accessible, easier to maintain and better for search."),
    ],
    "more": [
        ("h2", "A whole page laid out semantically"),
        ("code", "html", '<body>\n  <header>\n    <h1>Bean Counter Coffee</h1>\n    <nav>\n      <a href="/menu">Menu</a>\n      <a href="/about">About</a>\n      <a href="/contact">Contact</a>\n    </nav>\n  </header>\n\n  <main>\n    <article>\n      <h2>Our new espresso</h2>\n      <p>Rich, chocolatey and roasted this week.</p>\n    </article>\n    <aside>\n      <h2>Opening hours</h2>\n      <p>Mon-Fri 7am to 5pm</p>\n    </aside>\n  </main>\n\n  <footer><p>&copy; 2026 Bean Counter</p></footer>\n</body>'),
        ("h2", "How a form works"),
        ("p", "A form collects what a user types and sends it somewhere. Every field needs a <code>name</code> (the label the data is sent under) and a visible <code>&lt;label&gt;</code>. Clicking a label focuses its field, which also helps screen readers and makes small targets easier to hit on a phone."),
        ("code", "html", '<form action="/subscribe" method="post">\n  <label for="email">Email</label>\n  <input id="email" name="email" type="email" required>\n\n  <label for="plan">Plan</label>\n  <select id="plan" name="plan">\n    <option value="free">Free</option>\n    <option value="pro">Pro</option>\n  </select>\n\n  <label>\n    <input type="checkbox" name="terms" required>\n    I agree to the terms\n  </label>\n\n  <button type="submit">Subscribe</button>\n</form>'),
        ("ul", [
            "<code>for=\"email\"</code> on the label matches <code>id=\"email\"</code> on the input.",
            "<code>type=\"email\"</code> makes phones show an email keyboard and the browser check the format.",
            "<code>required</code> blocks submitting an empty field, with no JavaScript needed.",
            "<code>method=\"post\"</code> sends the data in the request body; <code>get</code> puts it in the URL (good for searches, wrong for passwords).",
        ]),
        ("note", "Client-side checks are not security", "HTML validation is only a convenience. Anyone can bypass it, so a real server must always validate the data again."),
        ("h2", "Choosing the right input type"),
        ("code", "html", '<input type="text">      <!-- free text -->\n<input type="number" min="1" max="10">\n<input type="date">\n<input type="password">\n<input type="tel">\n<input type="url">\n<input type="range" min="0" max="100">\n<textarea name="message" rows="4"></textarea>'),
    ],
    "recap": [
        "Use semantic elements (<code>header</code>, <code>nav</code>, <code>main</code>, <code>article</code>, <code>footer</code>) instead of anonymous boxes.",
        "Every form field needs a <code>name</code> and a properly linked <code>&lt;label&gt;</code>.",
        "Pick the input <code>type</code> that matches the data; the browser then helps for free.",
        "Always re-validate form data on the server.",
    ],
}

EXTRA["css-basics"] = {
    "intro": [
        ("h2", "What CSS does"),
        ("p", "HTML says <em>what</em> content is; <strong>CSS</strong> (Cascading Style Sheets) says <em>how it looks</em>: colours, fonts, spacing, layout. The same HTML can look like a plain document or a polished app depending on the stylesheet attached. Keeping them separate is the big idea: one CSS file can restyle a thousand pages."),
        ("p", "A CSS rule has two parts: a <strong>selector</strong> that says <em>which elements</em>, and a block of <strong>declarations</strong> that say <em>what to change</em>."),
        ("code", "css", "h1 {                  /* selector: every <h1> */\n  color: navy;         /* property: value; */\n  font-size: 2rem;\n}"),
    ],
    "more": [
        ("h2", "Connecting CSS to HTML"),
        ("code", "html", '<head>\n  <link rel="stylesheet" href="styles.css">\n</head>\n<body>\n  <h1 class="title">Hello</h1>\n  <p class="lead">Welcome to my page.</p>\n  <p>A normal paragraph.</p>\n</body>'),
        ("code", "css", "/* styles.css */\nbody {\n  font-family: system-ui, sans-serif;\n  line-height: 1.6;\n  color: #1f2937;\n}\n\n.title {              /* a class selector starts with a dot */\n  color: #0f766e;\n}\n\n.lead {\n  font-size: 1.25rem;\n  color: #475569;\n}"),
        ("h2", "The box model: everything is a box"),
        ("p", "Every element is a rectangle made of four layers. From the inside out: the <strong>content</strong>, <strong>padding</strong> (space inside the border), the <strong>border</strong> and <strong>margin</strong> (space outside, separating it from neighbours). Once you can see these boxes in your head, layout stops being mysterious."),
        ("code", "css", ".card {\n  width: 300px;\n  padding: 16px;          /* inside space */\n  border: 1px solid #cbd5e1;\n  margin: 24px auto;      /* outside space; auto centres horizontally */\n  border-radius: 12px;\n  box-sizing: border-box; /* width includes padding and border: much easier to reason about */\n}"),
        ("note", "Use DevTools", "Right-click any element and choose <em>Inspect</em>. The browser shows the box model diagram, every rule that applies, and lets you edit values live. It is the fastest way to learn and debug CSS."),
        ("h2", "Why is my rule not working?"),
        ("ul", [
            "<strong>Specificity</strong>: an ID selector beats a class, which beats an element selector. A more specific rule wins regardless of order.",
            "<strong>Order</strong>: when two rules are equally specific, the later one wins.",
            "<strong>Typos</strong>: an unknown property or a missing semicolon silently makes the browser skip the rule.",
            "<strong>Inspect</strong> the element: struck-through declarations show which rule lost.",
        ]),
    ],
    "recap": [
        "A rule is a selector plus declarations: <code>selector { property: value; }</code>.",
        "Select by element, <code>.class</code> or <code>#id</code>; prefer classes.",
        "Every element is a box: content, padding, border, margin; use <code>box-sizing: border-box</code>.",
        "Use DevTools to see which rules apply and to experiment live.",
    ],
}

EXTRA["css-flexbox"] = {
    "intro": [
        ("h2", "Layout used to be painful"),
        ("p", "For years developers used hacks to place things side by side or centre them. <strong>Flexbox</strong> solved the everyday cases: it lays children out in a row or column, spaces them, aligns them and lets them share space. You switch it on with one line on the <em>parent</em>, and the children obey."),
        ("code", "css", ".row {\n  display: flex;   /* children now sit in a row */\n  gap: 16px;\n}"),
    ],
    "more": [
        ("h2", "Two axes, two properties"),
        ("p", "Flexbox has a <strong>main axis</strong> (the direction items flow, a row by default) and a <strong>cross axis</strong> (the perpendicular direction). <code>justify-content</code> distributes items along the main axis; <code>align-items</code> aligns them on the cross axis. Memorise that pair and most layouts fall out."),
        ("code", "css", ".nav {\n  display: flex;\n  justify-content: space-between;  /* logo left, links right */\n  align-items: center;             /* vertically centred */\n  padding: 12px 24px;\n}"),
        ("h2", "The famous centring trick"),
        ("code", "css", ".hero {\n  display: flex;\n  justify-content: center;   /* horizontal */\n  align-items: center;       /* vertical */\n  min-height: 100vh;\n}"),
        ("h2", "A card row that wraps on small screens"),
        ("code", "html", '<div class="cards">\n  <div class="card">One</div>\n  <div class="card">Two</div>\n  <div class="card">Three</div>\n</div>'),
        ("code", "css", ".cards {\n  display: flex;\n  flex-wrap: wrap;   /* move to a new line when out of space */\n  gap: 16px;\n}\n.card {\n  flex: 1 1 240px;   /* grow, shrink, start at 240px wide */\n}"),
        ("p", "The <code>flex</code> shorthand means \"grow to share extra space, shrink if needed, start at this size.\" With wrapping, the cards form three columns on a laptop, two on a tablet and one on a phone, with no media query."),
        ("h2", "Common flexbox questions"),
        ("ul", [
            "<strong>Items will not wrap</strong>: add <code>flex-wrap: wrap</code>.",
            "<strong>Want a column instead of a row</strong>: <code>flex-direction: column</code>; the axes swap, so <code>justify-content</code> now works vertically.",
            "<strong>One item pushed to the far end</strong>: give it <code>margin-left: auto</code>.",
            "<strong>Does nothing</strong>: <code>display: flex</code> must be on the <em>parent</em>, not the items.",
        ]),
    ],
    "recap": [
        "Put <code>display: flex</code> on the parent to lay its children out in a row.",
        "<code>justify-content</code> works along the main axis; <code>align-items</code> works across it.",
        "<code>gap</code> spaces items; <code>flex-wrap</code> lets them flow onto new lines; <code>flex: 1</code> shares space.",
        "Flexbox is for one dimension (a row or a column); use Grid for two.",
    ],
}

EXTRA["css-grid-responsive"] = {
    "intro": [
        ("h2", "Rows and columns at once"),
        ("p", "Flexbox arranges items in one line. <strong>CSS Grid</strong> arranges them in a two-dimensional grid of rows <em>and</em> columns, which is what page layouts, galleries and dashboards need. You describe the columns on the parent and the browser places the children into the cells."),
        ("code", "css", ".gallery {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);   /* three equal columns */\n  gap: 16px;\n}"),
    ],
    "more": [
        ("h2", "What responsive means and why it matters"),
        ("p", "More than half of web traffic is on phones. A <strong>responsive</strong> page adapts to the screen: one column on a phone, more on a desktop. Start with the small-screen layout, then add rules for wider screens; this is called <em>mobile-first</em>. Always include this tag in your <code>&lt;head&gt;</code> or phones will zoom out to a fake desktop width:"),
        ("code", "html", '<meta name="viewport" content="width=device-width, initial-scale=1">'),
        ("h2", "A grid that adapts without media queries"),
        ("code", "css", ".gallery {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n  gap: 16px;\n}"),
        ("p", "Read it as: \"make as many columns as fit, each at least 220px wide, sharing leftover space equally.\" On a phone you get one column, on a laptop maybe four."),
        ("h2", "Media queries: change rules at a screen width"),
        ("code", "css", ".layout {\n  display: grid;\n  gap: 24px;\n  grid-template-columns: 1fr;          /* phone: stacked */\n}\n\n@media (min-width: 768px) {\n  .layout {\n    grid-template-columns: 240px 1fr;  /* tablet and up: sidebar + content */\n  }\n}"),
        ("h2", "A full page layout with named areas"),
        ("code", "css", ".page {\n  display: grid;\n  grid-template-areas:\n    \"header header\"\n    \"sidebar main\"\n    \"footer footer\";\n  grid-template-columns: 220px 1fr;\n  min-height: 100vh;\n}\nheader  { grid-area: header; }\naside   { grid-area: sidebar; }\nmain    { grid-area: main; }\nfooter  { grid-area: footer; }"),
        ("p", "The <code>grid-template-areas</code> block is literally a picture of the page. Rearranging the layout for a phone is just a matter of writing a different picture inside a media query."),
        ("h2", "Testing responsiveness"),
        ("ul", [
            "Open DevTools and toggle the <em>device toolbar</em> to preview phone and tablet sizes.",
            "Drag the window narrower and watch for text that overflows or buttons too small to tap.",
            "Aim for tap targets of at least 44 by 44 pixels and body text of at least 16px.",
        ]),
    ],
    "recap": [
        "Grid lays out rows and columns together; Flexbox handles a single row or column.",
        "<code>repeat(auto-fit, minmax(220px, 1fr))</code> gives a responsive gallery with no media queries.",
        "Design mobile-first and add <code>@media (min-width: ...)</code> rules for larger screens.",
        "Always include the viewport meta tag.",
    ],
}
