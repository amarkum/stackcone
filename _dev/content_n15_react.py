"""React lessons 8-15."""
from content_js_sql import M

META = [
    M("react-usereducer", "react", "useReducer and Complex State", 16, "Intermediate", "Model state as events and a reducer when useState starts to sprawl.", ["Write a reducer", "Dispatch actions", "Choose useReducer vs useState"]),
    M("react-performance", "react", "Performance: memo, useMemo and useCallback", 16, "Intermediate", "Skip wasted renders and expensive work without premature optimisation.", ["Memoize a component", "Use useMemo and useCallback", "Profile before you cache"]),
    M("react-concurrent", "react", "Transitions, Deferred Values and useId", 15, "Intermediate", "Keep the UI responsive with concurrent features and stable ids.", ["Mark an update as a transition", "Defer a heavy value", "Generate stable ids"]),
    M("react-suspense-errors", "react", "Suspense and Error Boundaries", 16, "Intermediate", "Show fallbacks while data loads and recover when a subtree throws.", ["Wrap a tree in Suspense", "Write an error boundary", "Reset after a failure"]),
    M("react-testing", "react", "Testing Components", 17, "Intermediate", "Test behaviour with Vitest and Testing Library, not implementation details.", ["Render and query the DOM", "Fire user events", "Mock a fetch"]),
    M("react-state-libraries", "react", "App-wide State with Zustand", 16, "Intermediate", "Share global state without wrapping the tree in providers.", ["Create a store", "Select slices", "Know when Context is enough"]),
    M("react-patterns", "react", "Component Patterns", 16, "Advanced", "Compound components, portals, forwarding refs and composition that scales.", ["Build a compound component", "Use a portal", "Forward a ref"]),
    M("react-build-deploy", "react", "Accessibility, Build and Deploy", 15, "Advanced", "Ship an accessible production build with env vars and a static host.", ["Fix common a11y issues", "Build with Vite", "Set env vars for production"]),
]

CONTENT = {}

CONTENT["react-usereducer"] = [
    ("p", "When a component has several related pieces of state that update together, a pile of <code>useState</code> calls becomes hard to follow. <strong>useReducer</strong> puts the next-state logic in one function: you dispatch an event, the reducer returns the new state."),
    ("h2", "A reducer is a pure function"),
    ("p", "It takes the current state and an action, and returns the next state. It must not mutate the previous object."),
    ("code", "javascript", 'function cartReducer(state, action) {\n  switch (action.type) {\n    case "add":\n      return { ...state, items: [...state.items, action.item] };\n    case "remove":\n      return { ...state, items: state.items.filter((i) => i.id !== action.id) };\n    case "clear":\n      return { ...state, items: [] };\n    default:\n      throw new Error(`Unknown action ${action.type}`);\n  }\n}'),
    ("h2", "Wiring it up"),
    ("code", "javascript", 'import { useReducer } from "react";\n\nconst initial = { items: [] };\n\nfunction Cart() {\n  const [state, dispatch] = useReducer(cartReducer, initial);\n  const total = state.items.reduce((sum, i) => sum + i.price, 0);\n  return (\n    <>\n      <button onClick={() => dispatch({ type: "add", item: { id: 1, price: 9 } })}>\n        Add\n      </button>\n      <button onClick={() => dispatch({ type: "clear" })}>Clear</button>\n      <p>{state.items.length} items · ${total}</p>\n    </>\n  );\n}'),
    ("p", "<code>dispatch</code> is stable across renders, so you can pass it down without wrapping it in <code>useCallback</code>."),
    ("h2", "When to prefer it"),
    ("ul", [
        "Several fields change together (a form wizard, a cart, a game board).",
        "The next state depends on the previous one in a non-trivial way.",
        "You want the update rules in one testable function, outside the component.",
    ]),
    ("note", "useState is still the default", "A boolean, a string or a single number does not need a reducer. Reach for <code>useReducer</code> when the setter soup is harder to read than a switch."),
    ("exercise", "Write a <code>counterReducer</code> that handles <code>inc</code>, <code>dec</code> and <code>set</code> (with a number payload), then render buttons that dispatch each."),
    ("solution", "javascript", 'function counterReducer(n, action) {\n  switch (action.type) {\n    case "inc": return n + 1;\n    case "dec": return n - 1;\n    case "set": return action.value;\n    default: throw new Error(action.type);\n  }\n}\nfunction Counter() {\n  const [n, dispatch] = useReducer(counterReducer, 0);\n  return (\n    <>\n      <button onClick={() => dispatch({ type: "dec" })}>-</button>\n      <span>{n}</span>\n      <button onClick={() => dispatch({ type: "inc" })}>+</button>\n      <button onClick={() => dispatch({ type: "set", value: 0 })}>Reset</button>\n    </>\n  );\n}'),
]

CONTENT["react-performance"] = [
    ("p", "React is fast enough for most UIs. Performance work starts when a profiler shows a real problem: a slow list, a laggy input, a child that re-renders for no reason. The tools are <code>memo</code>, <code>useMemo</code> and <code>useCallback</code>."),
    ("h2", "Skip a render with memo"),
    ("p", "A child re-renders whenever its parent does, even if its props did not change. Wrap it in <code>memo</code> so React compares props and skips the work when they are equal."),
    ("code", "javascript", 'import { memo } from "react";\n\nconst UserRow = memo(function UserRow({ user }) {\n  return <li>{user.name}</li>;\n});'),
    ("p", "This only helps if the <code>user</code> reference is stable. Passing a new object or inline function every render defeats <code>memo</code>."),
    ("h2", "useMemo and useCallback"),
    ("p", "<code>useMemo</code> caches an expensive calculation. <code>useCallback</code> caches a function so children wrapped in <code>memo</code> see the same prop."),
    ("code", "javascript", 'function Directory({ users, query }) {\n  const visible = useMemo(\n    () => users.filter((u) => u.name.toLowerCase().includes(query.toLowerCase())),\n    [users, query],\n  );\n  const onSelect = useCallback((id) => console.log(id), []);\n  return visible.map((u) => <UserRow key={u.id} user={u} onSelect={onSelect} />);\n}'),
    ("h2", "Lists first"),
    ("ul", [
        "Give list items a stable <code>key</code> (the id, never the index if items can move).",
        "Window long lists (react-window) instead of rendering 10,000 rows.",
        "Do not put a new <code>style={{}}</code> or <code>onClick={() => ...}</code> on every row if you then wrap the row in <code>memo</code>.",
    ]),
    ("note", "Measure first", "Wrap everything in <code>memo</code> by default and you add complexity for no gain. Use React DevTools Profiler, then cache the hot path."),
    ("exercise", "A parent holds a counter and a list. Memoize the list item so clicking the counter does not re-render every row. Prove it with a <code>console.log</code> inside the row."),
]

CONTENT["react-concurrent"] = [
    ("p", "Some updates must feel instant (typing in a box). Others can wait (filtering a big list). Concurrent React lets you mark the slow work as a <strong>transition</strong> so the input stays snappy."),
    ("h2", "useTransition"),
    ("code", "javascript", 'import { useState, useTransition } from "react";\n\nfunction Search({ items }) {\n  const [query, setQuery] = useState("");\n  const [pending, startTransition] = useTransition();\n  const [list, setList] = useState(items);\n\n  function onChange(e) {\n    const q = e.target.value;\n    setQuery(q);                              // urgent: the input\n    startTransition(() => {\n      setList(items.filter((i) => i.includes(q)));   // can wait\n    });\n  }\n\n  return (\n    <>\n      <input value={query} onChange={onChange} />\n      {pending && <p>Updating…</p>}\n      <ul>{list.map((i) => <li key={i}>{i}</li>)}</ul>\n    </>\n  );\n}'),
    ("h2", "useDeferredValue"),
    ("p", "When you cannot wrap the setter (a library owns it), defer the <em>value</em> instead. React keeps showing the previous value until the new one is ready."),
    ("code", "javascript", 'const deferredQuery = useDeferredValue(query);\nconst visible = items.filter((i) => i.includes(deferredQuery));'),
    ("h2", "useId for labels"),
    ("p", "Server and client must generate the same id, or hydration mismatches. <code>useId</code> is built for that."),
    ("code", "javascript", 'function Field({ label }) {\n  const id = useId();\n  return (\n    <>\n      <label htmlFor={id}>{label}</label>\n      <input id={id} />\n    </>\n  );\n}'),
    ("note", "Not a debounce", "Transitions do not wait a fixed time. They let React paint urgent updates first. If you need to wait for the user to stop typing, debounce as well."),
    ("exercise", "Split a text box and a filtered list so the box always updates immediately and the list is wrapped in <code>startTransition</code>."),
]

CONTENT["react-suspense-errors"] = [
    ("p", "Two wrappers keep a crashed or loading subtree from taking down the page: <strong>Suspense</strong> for waiting, and an <strong>error boundary</strong> for thrown errors."),
    ("h2", "Suspense"),
    ("p", "A child that <em>suspends</em> (a data library using a Promise, or a lazy component) bubbles up to the nearest Suspense, which shows its fallback."),
    ("code", "javascript", 'import { Suspense, lazy } from "react";\n\nconst Chart = lazy(() => import("./Chart"));\n\nfunction Dashboard() {\n  return (\n    <Suspense fallback={<p>Loading chart…</p>}>\n      <Chart />\n    </Suspense>\n  );\n}'),
    ("p", "You can nest Suspense to stream parts of the page independently. Pair it with a data library that supports it (React Query, Relay, Next.js) rather than throwing Promises by hand."),
    ("h2", "Error boundaries"),
    ("p", "A class component with <code>getDerivedStateFromError</code> catches render errors in its children. Function components cannot do this yet."),
    ("code", "javascript", 'import { Component } from "react";\n\nclass ErrorBoundary extends Component {\n  state = { error: null };\n  static getDerivedStateFromError(error) {\n    return { error };\n  }\n  render() {\n    if (this.state.error) {\n      return (\n        <p role="alert">\n          Something broke.{" "}\n          <button onClick={() => this.setState({ error: null })}>Retry</button>\n        </p>\n      );\n    }\n    return this.props.children;\n  }\n}'),
    ("p", "Boundaries catch errors in render, lifecycle and constructors of children. They do <em>not</em> catch errors in event handlers or async code: use <code>try/catch</code> there."),
    ("note", "Libraries", "<code>react-error-boundary</code> wraps the class in a hook-friendly API with <code>resetKeys</code> so changing a prop retries automatically."),
    ("exercise", "Wrap a component that throws when a prop is missing in an error boundary that shows the error message and a retry button."),
]

CONTENT["react-testing"] = [
    ("p", "Test what the user sees and does, not the internals of a hook. <strong>Vitest</strong> (or Jest) runs the tests; <strong>Testing Library</strong> renders components into a fake DOM and queries them the way a person would."),
    ("h2", "Setup"),
    ("code", "bash", "npm install -D vitest jsdom @testing-library/react @testing-library/user-event @testing-library/jest-dom"),
    ("code", "javascript", '// vitest.config.js\nimport { defineConfig } from "vitest/config";\nimport react from "@vitejs/plugin-react";\nexport default defineConfig({\n  plugins: [react()],\n  test: { environment: "jsdom", setupFiles: "./src/setupTests.js" },\n});'),
    ("code", "javascript", '// src/setupTests.js\nimport "@testing-library/jest-dom/vitest";'),
    ("h2", "Render, query, click"),
    ("code", "javascript", 'import { render, screen } from "@testing-library/react";\nimport userEvent from "@testing-library/user-event";\nimport { Counter } from "./Counter";\n\ntest("increments on click", async () => {\n  const user = userEvent.setup();\n  render(<Counter />);\n  await user.click(screen.getByRole("button", { name: /add/i }));\n  expect(screen.getByText("1")).toBeInTheDocument();\n});'),
    ("p", "Prefer <code>getByRole</code>, <code>getByLabelText</code> and <code>getByText</code> over <code>getByTestId</code>. If a test cannot find a button by its name, neither can a screen reader."),
    ("h2", "Mocking the network"),
    ("code", "javascript", 'test("shows users", async () => {\n  global.fetch = vi.fn().mockResolvedValue({\n    ok: true,\n    json: async () => [{ id: 1, name: "Ada" }],\n  });\n  render(<Users />);\n  expect(await screen.findByText("Ada")).toBeInTheDocument();\n});'),
    ("note", "findBy vs getBy", "<code>getBy*</code> throws immediately if missing. <code>findBy*</code> waits for async UI. Use <code>queryBy*</code> when you assert that something is <em>not</em> there."),
    ("exercise", "Write a test for a login form: type an email, click Submit, and assert that a success message appears. Mock the POST."),
]

CONTENT["react-state-libraries"] = [
    ("p", "Context is enough for a theme or the current user. For frequent updates (a cart, a filter panel, a long form) it re-renders every consumer. A small store library such as <strong>Zustand</strong> lets components subscribe to just the slice they need."),
    ("h2", "A store"),
    ("code", "bash", "npm install zustand"),
    ("code", "javascript", '// store/cart.js\nimport { create } from "zustand";\n\nexport const useCart = create((set, get) => ({\n  items: [],\n  add: (item) => set((s) => ({ items: [...s.items, item] })),\n  remove: (id) => set((s) => ({ items: s.items.filter((i) => i.id !== id) })),\n  total: () => get().items.reduce((n, i) => n + i.price, 0),\n}));'),
    ("h2", "Select a slice"),
    ("code", "javascript", 'function CartCount() {\n  const count = useCart((s) => s.items.length);   // re-renders only when length changes\n  return <span>{count}</span>;\n}\n\nfunction AddButton({ product }) {\n  const add = useCart((s) => s.add);\n  return <button onClick={() => add(product)}>Add</button>;\n}'),
    ("p", "Selecting the whole store (<code>useCart()</code> with no argument) re-renders on every change. Always pick a field or a stable action."),
    ("h2", "When not to add a library"),
    ("ul", [
        "State used by one component or a parent and its children: <code>useState</code>.",
        "Rarely changing values (locale, auth user): Context is simpler.",
        "Server data (lists from an API): TanStack Query, not a client store.",
    ]),
    ("note", "Redux Toolkit", "Redux still fits large teams that want a strict action log and DevTools. For most apps Zustand or Jotai is less ceremony."),
    ("exercise", "Create a <code>useTheme</code> store with <code>mode</code> (<code>\"light\"</code> | <code>\"dark\"</code>) and <code>toggle</code>, then a button that switches it."),
    ("solution", "javascript", 'import { create } from "zustand";\nexport const useTheme = create((set) => ({\n  mode: "light",\n  toggle: () => set((s) => ({ mode: s.mode === "light" ? "dark" : "light" })),\n}));\nfunction Toggle() {\n  const { mode, toggle } = useTheme();\n  return <button onClick={toggle}>{mode}</button>;\n}'),
]

CONTENT["react-patterns"] = [
    ("p", "As a UI kit grows, a few composition patterns keep components flexible without a props explosion."),
    ("h2", "Compound components"),
    ("p", "Related pieces share state through context, and the parent decides the markup."),
    ("code", "javascript", 'import { createContext, useContext, useState } from "react";\n\nconst TabsCtx = createContext(null);\n\nexport function Tabs({ children, defaultValue }) {\n  const [value, setValue] = useState(defaultValue);\n  return <TabsCtx.Provider value={{ value, setValue }}>{children}</TabsCtx.Provider>;\n}\nTabs.List = function List({ children }) { return <div role="tablist">{children}</div>; };\nTabs.Tab = function Tab({ id, children }) {\n  const { value, setValue } = useContext(TabsCtx);\n  return (\n    <button role="tab" aria-selected={value === id} onClick={() => setValue(id)}>\n      {children}\n    </button>\n  );\n};\nTabs.Panel = function Panel({ id, children }) {\n  const { value } = useContext(TabsCtx);\n  if (value !== id) return null;\n  return <div role="tabpanel">{children}</div>;\n};'),
    ("h2", "Portals"),
    ("p", "Modals and toasts should escape overflow and stacking-context traps. <code>createPortal</code> renders children into a different DOM node."),
    ("code", "javascript", 'import { createPortal } from "react-dom";\n\nfunction Modal({ children, onClose }) {\n  return createPortal(\n    <div className="overlay" onClick={onClose}>\n      <div className="dialog" onClick={(e) => e.stopPropagation()}>{children}</div>\n    </div>,\n    document.body,\n  );\n}'),
    ("h2", "Forwarding refs"),
    ("p", "A custom input that wraps <code>&lt;input&gt;</code> must forward the ref so a parent can focus it."),
    ("code", "javascript", 'import { forwardRef } from "react";\n\nconst TextField = forwardRef(function TextField({ label, ...props }, ref) {\n  return (\n    <label>\n      {label}\n      <input ref={ref} {...props} />\n    </label>\n  );\n});'),
    ("note", "Children over render props", "Passing <code>children</code> (or a compound API) is usually clearer than a <code>render=</code> callback. Use a render prop when the parent needs data the child owns."),
    ("exercise", "Build a <code>Toggle</code> compound component with <code>Toggle.Button</code> and <code>Toggle.On</code> / <code>Toggle.Off</code> that share open state."),
]

CONTENT["react-build-deploy"] = [
    ("p", "Shipping a React app is a static build plus a host, plus the accessibility and environment work people skip until production hurts."),
    ("h2", "Accessibility checklist"),
    ("ul", [
        "Every interactive control is a <code>button</code> or a link, not a <code>div</code> with an onClick.",
        "Form fields have a <code>&lt;label htmlFor&gt;</code> (or wrap the input).",
        "Images have meaningful <code>alt</code>, or <code>alt=\"\"</code> if decorative.",
        "Do not rely on colour alone; keep contrast at 4.5:1 for body text.",
        "Manage focus when a modal opens and restore it when it closes.",
    ]),
    ("code", "javascript", 'function IconButton({ label, children, onClick }) {\n  return (\n    <button type="button" aria-label={label} onClick={onClick}>\n      {children}\n    </button>\n  );\n}'),
    ("h2", "Production build"),
    ("code", "bash", "npm run build\nnpm run preview          # serve the dist/ folder locally"),
    ("p", "Vite emits hashed assets in <code>dist/</code>. Any static host (Netlify, Cloudflare Pages, GitHub Pages, S3 + CloudFront) can serve it. For client-side routing, configure the host to fall back to <code>index.html</code>."),
    ("h2", "Environment variables"),
    ("p", "Vite only exposes variables prefixed with <code>VITE_</code>, and they are inlined at build time. Never put a secret in the frontend bundle."),
    ("code", "bash", "# .env.production\nVITE_API_URL=https://api.example.com"),
    ("code", "javascript", 'const api = import.meta.env.VITE_API_URL;\nfetch(`${api}/health`);'),
    ("note", "Code splitting", "<code>lazy(() => import(\"./Heavy\"))</code> plus <code>Suspense</code> keeps the first paint small. Split by route."),
    ("exercise", "Add an <code>aria-label</code> to an icon-only delete button, then set <code>VITE_API_URL</code> and read it in a fetch helper."),
]
