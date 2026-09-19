"""Next.js lessons 6-15."""
from content_js_sql import M

META = [
    M("nextjs-data-caching", "nextjs", "Data Fetching and Caching", 16, "Intermediate", "Control freshness with cache, revalidate, tags and unstable_cache.", ["Choose static vs dynamic", "Revalidate by time or tag", "Cache a database call"]),
    M("nextjs-streaming", "nextjs", "Streaming and Loading UI", 15, "Intermediate", "Show shells instantly and stream the rest with Suspense.", ["Add loading.tsx", "Split slow parts into Suspense", "Avoid blocking the whole page"]),
    M("nextjs-middleware-auth", "nextjs", "Middleware, Cookies and Sessions", 17, "Intermediate", "Run code at the edge for auth redirects and read cookies on the server.", ["Write middleware", "Set httpOnly cookies", "Protect a route group"]),
    M("nextjs-database", "nextjs", "Databases with Prisma", 17, "Intermediate", "Query Postgres from Server Components and mutate with server actions.", ["Define a Prisma schema", "Query in a page", "Mutate and revalidate"]),
    M("nextjs-errors-parallel", "nextjs", "Errors, Parallel and Intercepting Routes", 16, "Intermediate", "error.tsx, slots for parallel UI and intercepting routes for modals.", ["Recover with error.tsx", "Compose parallel slots", "Open a modal over a page"]),
    M("nextjs-authjs", "nextjs", "Authentication with Auth.js", 17, "Intermediate", "Sign in with OAuth or credentials and read the session on server and client.", ["Configure Auth.js", "Protect a page", "Read the session"]),
    M("nextjs-env-config", "nextjs", "Config, Env and Route Segment Options", 14, "Intermediate", "next.config, public vs secret env, and per-route runtime settings.", ["Split public and secret env", "Set headers and redirects", "Pick a runtime"]),
    M("nextjs-testing", "nextjs", "Testing Next.js Apps", 16, "Advanced", "Unit-test server actions and cover critical flows with Playwright.", ["Test a server action", "Write a Playwright spec", "Mock fetch in tests"]),
    M("nextjs-performance", "nextjs", "Images, Fonts and Performance", 15, "Advanced", "next/image, next/font, bundle analysis and Core Web Vitals.", ["Optimize images", "Self-host fonts", "Find a heavy import"]),
    M("nextjs-fullstack", "nextjs", "Full-stack Project Structure", 16, "Advanced", "Lay out a production App Router project and keep server code off the client.", ["Split app, components, lib", "Mark server-only modules", "Compose a feature folder"]),
]

CONTENT = {}

CONTENT["nextjs-data-caching"] = [
    ("p", "Next.js can cache both HTTP <code>fetch</code> calls and the HTML of a page. Getting this right is the difference between a snappy static site and a dashboard that always shows fresh data."),
    ("h2", "Three freshness knobs"),
    ("code", "javascript", '// Cached until you rebuild (or until a tag is invalidated)\nawait fetch(url);\n\n// Recheck at most every 60 seconds (ISR-style)\nawait fetch(url, { next: { revalidate: 60 } });\n\n// Never cache: user-specific or always-changing data\nawait fetch(url, { cache: "no-store" });'),
    ("h2", "Tag and on-demand revalidation"),
    ("p", "When a mutation happens, you do not want to wait for a timer. Tag the fetch, then invalidate that tag from a server action."),
    ("code", "javascript", 'await fetch(url, { next: { tags: ["products"] } });\n\n// in a server action\nimport { revalidateTag, revalidatePath } from "next/cache";\nrevalidateTag("products");\nrevalidatePath("/products");'),
    ("h2", "Caching non-fetch work"),
    ("p", "Database queries are not <code>fetch</code>. Wrap them in <code>unstable_cache</code> (the name is historical; it is the supported helper)."),
    ("code", "javascript", 'import { unstable_cache } from "next/cache";\n\nexport const getPublishedPosts = unstable_cache(\n  async () => db.post.findMany({ where: { published: true } }),\n  ["published-posts"],\n  { revalidate: 60, tags: ["posts"] },\n);'),
    ("h2", "What makes a page dynamic"),
    ("p", "Reading <code>cookies()</code>, <code>headers()</code>, or using <code>no-store</code> opts the route into per-request rendering. Keep that at the edge of the tree: a product page can stay static while the cart badge is dynamic."),
    ("note", "Version note", "Default cache behaviour has shifted between Next.js 14 and 15. Always set <code>revalidate</code> or <code>cache</code> explicitly on fetches you care about."),
    ("exercise", "Fetch a list with <code>tags: [\"todos\"]</code>, then write a server action that creates a todo and calls <code>revalidateTag(\"todos\")</code>."),
]

CONTENT["nextjs-streaming"] = [
    ("p", "A slow database call should not blank the whole page. Stream a shell immediately, then fill in the slow parts as they finish."),
    ("h2", "loading.tsx is a boundary"),
    ("p", "A <code>loading.tsx</code> next to a <code>page.tsx</code> wraps that page in Suspense. Navigation shows the fallback instantly while the page awaits data."),
    ("code", "javascript", '// app/dashboard/loading.tsx\nexport default function Loading() {\n  return <p>Loading dashboard…</p>;\n}'),
    ("h2", "Split the slow bits"),
    ("p", "If only one widget is slow, do not put the await in the page. Extract it and wrap that component in <code>Suspense</code> so the rest of the page paints first."),
    ("code", "javascript", '// app/dashboard/page.tsx\nimport { Suspense } from "react";\nimport { Revenue } from "./revenue";\nimport { RecentOrders } from "./orders";\n\nexport default function Dashboard() {\n  return (\n    <>\n      <h1>Dashboard</h1>\n      <Suspense fallback={<p>Loading revenue…</p>}>\n        <Revenue />\n      </Suspense>\n      <Suspense fallback={<p>Loading orders…</p>}>\n        <RecentOrders />\n      </Suspense>\n    </>\n  );\n}\n\n// revenue.tsx — a server component\nexport async function Revenue() {\n  const data = await getRevenue();   // slow\n  return <p>This month: {data.total}</p>;\n}'),
    ("h2", "Skeletons beat spinners"),
    ("p", "Match the fallback layout to the final UI (grey boxes of the same size). The page feels faster because nothing jumps."),
    ("note", "Blocking metadata", "<code>generateMetadata</code> that awaits slow data delays the document. Keep metadata cheap, or stream the body independently."),
    ("exercise", "Build a page with a heading that renders immediately and a slow server component (simulate with a delay) wrapped in Suspense with a skeleton fallback."),
]

CONTENT["nextjs-middleware-auth"] = [
    ("p", "Middleware runs on the Edge before a request hits a page or route handler. Use it for redirects and header tweaks, not for database work."),
    ("h2", "A matcher and a redirect"),
    ("code", "javascript", '// middleware.ts at the project root\nimport { NextResponse } from "next/server";\nimport type { NextRequest } from "next/server";\n\nexport function middleware(req: NextRequest) {\n  const session = req.cookies.get("session")?.value;\n  if (!session) {\n    const url = req.nextUrl.clone();\n    url.pathname = "/login";\n    url.searchParams.set("from", req.nextUrl.pathname);\n    return NextResponse.redirect(url);\n  }\n  return NextResponse.next();\n}\n\nexport const config = { matcher: ["/dashboard/:path*", "/settings/:path*"] };'),
    ("h2", "httpOnly cookies"),
    ("p", "Store session tokens in cookies the JavaScript on the page cannot read. Set them from a Route Handler or server action."),
    ("code", "javascript", 'import { cookies } from "next/headers";\n\nexport async function POST() {\n  const token = await createSession();          // your auth code\n  const jar = await cookies();\n  jar.set("session", token, {\n    httpOnly: true,\n    secure: true,\n    sameSite: "lax",\n    path: "/",\n    maxAge: 60 * 60 * 24 * 7,\n  });\n  return Response.json({ ok: true });\n}'),
    ("h2", "Reading the user in a Server Component"),
    ("code", "javascript", 'import { cookies } from "next/headers";\nimport { redirect } from "next/navigation";\n\nexport default async function Page() {\n  const token = (await cookies()).get("session")?.value;\n  const user = token ? await getUser(token) : null;\n  if (!user) redirect("/login");\n  return <h1>Hello {user.name}</h1>;\n}'),
    ("note", "Middleware is a gate, not the source of truth", "Anyone can call a Route Handler directly. Always re-check the session in the server code that mutates data."),
    ("exercise", "Redirect unauthenticated users away from <code>/account</code>, and after login send them back to the <code>from</code> query param."),
]

CONTENT["nextjs-database"] = [
    ("p", "<strong>Prisma</strong> is a typed ORM that fits the App Router: generate a client, query from Server Components, mutate from server actions."),
    ("h2", "Schema and client"),
    ("code", "bash", "npm install prisma @prisma/client\nnpx prisma init --datasource-provider postgresql"),
    ("code", "text", '// prisma/schema.prisma\nmodel Post {\n  id        Int      @id @default(autoincrement())\n  title     String\n  body      String\n  published Boolean  @default(false)\n  createdAt DateTime @default(now())\n}'),
    ("code", "javascript", '// lib/db.ts\nimport { PrismaClient } from "@prisma/client";\n\nconst globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };\nexport const db = globalForPrisma.prisma ?? new PrismaClient();\nif (process.env.NODE_ENV !== "production") globalForPrisma.prisma = db;'),
    ("p", "The global cache stops Next.js hot reload from opening a new connection on every save."),
    ("h2", "Read on the server"),
    ("code", "javascript", '// app/posts/page.tsx\nimport { db } from "@/lib/db";\n\nexport default async function Posts() {\n  const posts = await db.post.findMany({ where: { published: true }, orderBy: { createdAt: "desc" } });\n  return <ul>{posts.map((p) => <li key={p.id}>{p.title}</li>)}</ul>;\n}'),
    ("h2", "Write with a server action"),
    ("code", "javascript", '"use server";\nimport { db } from "@/lib/db";\nimport { revalidatePath } from "next/cache";\nimport { z } from "zod";\n\nconst Input = z.object({ title: z.string().min(1).max(120) });\n\nexport async function createPost(formData: FormData) {\n  const parsed = Input.safeParse({ title: formData.get("title") });\n  if (!parsed.success) return { error: "Title required" };\n  await db.post.create({ data: { title: parsed.data.title, body: "" } });\n  revalidatePath("/posts");\n}'),
    ("note", "Never import db in a client component", "Put the client in <code>lib/db.ts</code> and import it only from server files. A leak would ship your database URL to the browser."),
    ("exercise", "Add a <code>published</code> toggle server action that flips the flag and revalidates <code>/posts</code>."),
]

CONTENT["nextjs-errors-parallel"] = [
    ("p", "The App Router has a file for failures and two advanced routing tools: <strong>parallel routes</strong> (several pages in one layout) and <strong>intercepting routes</strong> (a modal that still has a real URL)."),
    ("h2", "error.tsx"),
    ("p", "It must be a Client Component. It catches errors in the segment and below, and receives a <code>reset</code> function."),
    ("code", "javascript", '// app/dashboard/error.tsx\n"use client";\nexport default function Error({ error, reset }: { error: Error; reset: () => void }) {\n  return (\n    <p role="alert">\n      {error.message}{" "}\n      <button onClick={reset}>Try again</button>\n    </p>\n  );\n}'),
    ("p", "<code>global-error.tsx</code> wraps the root layout (it must include <code>&lt;html&gt;</code> and <code>&lt;body&gt;</code>). Use <code>not-found.tsx</code> for expected missing data."),
    ("h2", "Parallel routes"),
    ("p", "A folder named <code>@slot</code> becomes a prop on the parent layout. A dashboard can render <code>@analytics</code> and <code>@team</code> side by side, each with its own loading and error UI."),
    ("code", "javascript", '// app/dashboard/layout.tsx\nexport default function Layout({\n  children, analytics, team,\n}: { children: React.ReactNode; analytics: React.ReactNode; team: React.ReactNode }) {\n  return (\n    <div>\n      {children}\n      <aside>{analytics}</aside>\n      <section>{team}</section>\n    </div>\n  );\n}'),
    ("h2", "Intercepting routes for modals"),
    ("p", "<code>(.)photo</code> intercepts <code>/photo/[id]</code> when you navigate from the same segment, so a grid can open a modal without leaving the page. Refreshing the URL still shows the full photo page."),
    ("note", "Default files", "Each slot needs a <code>default.tsx</code> for when Next.js cannot match that slot on hard navigation."),
    ("exercise", "Add an <code>error.tsx</code> to a blog segment that shows the message and a reset button, then sketch folders for a <code>@modal</code> slot."),
]

CONTENT["nextjs-authjs"] = [
    ("p", "<strong>Auth.js</strong> (next-auth v5) handles OAuth, magic links and credentials, and exposes the session on the server and in Client Components."),
    ("h2", "Config"),
    ("code", "javascript", '// auth.ts\nimport NextAuth from "next-auth";\nimport GitHub from "next-auth/providers/github";\n\nexport const { handlers, auth, signIn, signOut } = NextAuth({\n  providers: [GitHub],\n});\n\n// app/api/auth/[...nextauth]/route.ts\nimport { handlers } from "@/auth";\nexport const { GET, POST } = handlers;'),
    ("h2", "Protect a page"),
    ("code", "javascript", 'import { auth } from "@/auth";\nimport { redirect } from "next/navigation";\n\nexport default async function Account() {\n  const session = await auth();\n  if (!session?.user) redirect("/api/auth/signin");\n  return <p>Signed in as {session.user.email}</p>;\n}'),
    ("h2", "Buttons"),
    ("code", "javascript", 'import { signIn, signOut } from "@/auth";\n\nexport function SignIn() {\n  return (\n    <form action={async () => { "use server"; await signIn("github"); }}>\n      <button type="submit">Sign in</button>\n    </form>\n  );\n}'),
    ("p", "On the client, wrap the tree with <code>SessionProvider</code> and call <code>useSession()</code> only where you need interactivity (an avatar menu). Prefer <code>auth()</code> in Server Components so the session is not a client waterfall."),
    ("note", "Credentials", "Email/password works, but you must hash passwords and rate-limit yourself. OAuth is less for you to get wrong."),
    ("exercise", "Add a GitHub provider, a server page that redirects if there is no session, and sign-in / sign-out forms."),
]

CONTENT["nextjs-env-config"] = [
    ("p", "Configuration belongs in <code>next.config.ts</code> and environment files, not scattered through components."),
    ("h2", "Public vs secret"),
    ("ul", [
        "<code>NEXT_PUBLIC_*</code> is inlined into the browser bundle. Use it for a public API URL or an analytics id.",
        "Everything else (<code>DATABASE_URL</code>, <code>AUTH_SECRET</code>) is server-only. Read it in Server Components, actions and route handlers.",
    ]),
    ("code", "javascript", 'const api = process.env.NEXT_PUBLIC_API_URL;\nconst db = process.env.DATABASE_URL;   // never in a "use client" file'),
    ("h2", "next.config.ts"),
    ("code", "javascript", 'import type { NextConfig } from "next";\n\nconst config: NextConfig = {\n  images: { remotePatterns: [{ hostname: "images.example.com" }] },\n  async redirects() {\n    return [{ source: "/old", destination: "/new", permanent: true }];\n  },\n  async headers() {\n    return [{\n      source: "/(.*)",\n      headers: [{ key: "X-Frame-Options", value: "DENY" }],\n    }];\n  },\n};\nexport default config;'),
    ("h2", "Segment config"),
    ("code", "javascript", 'export const dynamic = "force-static";     // or force-dynamic\nexport const revalidate = 60;\nexport const runtime = "nodejs";           // or "edge" for middleware-like routes\nexport const maxDuration = 30;             // seconds, on hosts that allow it'),
    ("note", "Edge limits", "The Edge runtime has no Node APIs (no <code>fs</code>, limited crypto). Keep Prisma and heavy SDKs on <code>nodejs</code>."),
    ("exercise", "Add a redirect from <code>/docs</code> to <code>/learn</code> and a content-security-friendly <code>X-Frame-Options</code> header."),
]

CONTENT["nextjs-testing"] = [
    ("p", "Test server code with Vitest and user flows with Playwright. Mock the network; do not hit a real database in unit tests."),
    ("h2", "Unit-test a server action"),
    ("code", "javascript", 'import { describe, expect, it, vi } from "vitest";\nimport { createPost } from "./actions";\n\nvi.mock("@/lib/db", () => ({ db: { post: { create: vi.fn() } } }));\n\nit("rejects an empty title", async () => {\n  const fd = new FormData();\n  fd.set("title", "  ");\n  const result = await createPost(fd);\n  expect(result).toEqual({ error: "Title required" });\n});'),
    ("h2", "Playwright for a critical path"),
    ("code", "bash", "npm init playwright@latest"),
    ("code", "javascript", '// e2e/home.spec.ts\nimport { test, expect } from "@playwright/test";\n\ntest("home has a heading", async ({ page }) => {\n  await page.goto("/");\n  await expect(page.getByRole("heading", { name: /welcome/i })).toBeVisible();\n});'),
    ("p", "Run the app with a test database or MSW. Point Playwright at <code>npm run dev</code> locally and a preview URL in CI."),
    ("h2", "Mocking fetch in component tests"),
    ("code", "javascript", 'global.fetch = vi.fn().mockResolvedValue({\n  ok: true,\n  json: async () => [{ id: 1, title: "Hello" }],\n});'),
    ("note", "What not to test", "Do not assert on class names or the contents of <code>next/image</code> markup. Assert on roles, text and navigation."),
    ("exercise", "Write a Playwright test that opens <code>/contact</code>, fills an email field and clicks Send, then expects a thank-you message."),
]

CONTENT["nextjs-performance"] = [
    ("p", "Core Web Vitals (LCP, INP, CLS) are mostly won with images, fonts and how much JavaScript you send."),
    ("h2", "next/image"),
    ("code", "javascript", 'import Image from "next/image";\n\n<Image\n  src="/hero.jpg"\n  alt="Team at a whiteboard"\n  width={1200}\n  height={800}\n  priority          // LCP image on the first screen\n/>'),
    ("p", "The component serves modern formats, srcset, and lazy-loads everything without <code>priority</code>. Remote hosts must be listed in <code>images.remotePatterns</code>."),
    ("h2", "next/font"),
    ("p", "Self-hosting Google fonts avoids a render-blocking request to another origin."),
    ("code", "javascript", 'import { Inter } from "next/font/google";\nconst inter = Inter({ subsets: ["latin"], display: "swap" });\n\nexport default function RootLayout({ children }) {\n  return <html lang="en" className={inter.className}><body>{children}</body></html>;\n}'),
    ("h2", "Find the heavy import"),
    ("code", "bash", "npm i -D @next/bundle-analyzer\nANALYZE=true npm run build"),
    ("p", "A charting library or a markdown renderer should be <code>dynamic(() => import(...))</code> so it is not in the first bundle."),
    ("note", "CLS", "Always set width and height (or <code>fill</code> plus a sized parent) on images, or the layout jumps when they load."),
    ("exercise", "Replace an <code>&lt;img&gt;</code> hero with <code>next/image</code> and <code>priority</code>, and load Inter with <code>next/font</code>."),
]

CONTENT["nextjs-fullstack"] = [
    ("p", "A durable App Router project keeps routing in <code>app/</code>, reusable UI in <code>components/</code>, and server-only code in <code>lib/</code> or colocation folders that never get imported from the client."),
    ("h2", "A layout that scales"),
    ("code", "text", 'app/\n  (marketing)/          # public layout\n  (app)/                # signed-in layout\n    dashboard/\ncomponents/             # presentational, safe for client or server\nfeatures/\n  posts/\n    actions.ts          # "use server"\n    queries.ts          # db reads\n    ui/                 # feature-specific components\nlib/\n  db.ts\n  auth.ts\n  server-only.ts'),
    ("h2", "Mark server-only modules"),
    ("code", "javascript", '// lib/db.ts\nimport "server-only";\nimport { PrismaClient } from "@prisma/client";\nexport const db = new PrismaClient();'),
    ("p", "If a Client Component imports this file, the build fails instead of leaking secrets."),
    ("h2", "Colocate a feature"),
    ("p", "A posts feature can own its actions, queries and UI. Pages in <code>app/</code> stay thin: fetch, pass props, render."),
    ("code", "javascript", '// app/posts/page.tsx\nimport { getPublishedPosts } from "@/features/posts/queries";\nimport { PostList } from "@/features/posts/ui/post-list";\n\nexport default async function Page() {\n  const posts = await getPublishedPosts();\n  return <PostList posts={posts} />;\n}'),
    ("note", "Barrel files", "Avoid <code>index.ts</code> that re-export both client and server modules. A client import of the barrel pulls the server code in."),
    ("exercise", 'Sketch folders for an <code>invoices</code> feature with a list page, a create action and a server-only <code>queries.ts</code>, and add <code>import "server-only"</code> to the database module.'),
]
