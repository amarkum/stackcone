"""AI: One Course, part 2 — embeddings, vector search, BM25, hybrid search, RAG and evaluation."""
from extra_util import py
from content_ai_1 import M

META = [
    M("ai-embeddings", "Vectors and Embeddings", 26, "Intermediate",
      "What a vector is, how text becomes numbers that capture meaning, and how cosine similarity finds related text.",
      ["Explain what an embedding is", "Compute cosine similarity by hand", "Know when embeddings help and when they fail"]),
    M("ai-vector-search", "Chunking, Vector Databases and ANN Search", 26, "Intermediate",
      "How to split documents, store vectors, and search millions of them fast with approximate nearest neighbour indexes.",
      ["Choose a chunking strategy", "Explain brute-force vs ANN search", "Pick a vector database"]),
    M("ai-bm25", "Keyword Search and BM25", 24, "Intermediate",
      "Inverted indexes, TF-IDF and BM25 built from scratch, and why keyword search still beats embeddings for some queries.",
      ["Explain TF-IDF and BM25", "Build an inverted index", "Know when keyword search wins"]),
    M("ai-hybrid-rerank", "Hybrid Search and Reranking", 24, "Intermediate",
      "Combine keyword and vector search with reciprocal rank fusion, then rerank with a cross-encoder for precision.",
      ["Fuse rankings with RRF", "Explain bi-encoder vs cross-encoder", "Use query rewriting and multi-query"]),
    M("ai-rag", "RAG: Retrieval-Augmented Generation", 30, "Intermediate",
      "The full RAG pipeline end to end, with a working mini-RAG you can run, plus prompt design and common failure modes.",
      ["Explain the RAG pipeline", "Build a mini RAG", "Debug retrieval vs generation failures"]),
    M("ai-rag-evaluation", "Evaluating and Improving RAG", 26, "Advanced",
      "recall@k, MRR and nDCG computed by hand, faithfulness, chunk-size experiments, and advanced RAG patterns.",
      ["Compute retrieval metrics", "Diagnose a bad RAG answer", "Apply advanced patterns like parent-child and GraphRAG"]),
]

CONTENT = {}

# ---------------------------------------------------------------------------
CONTENT["ai-embeddings"] = [
    ("p", "How does a computer know that \"puppy\" and \"dog\" are related, while \"puppy\" and \"invoice\" are not? Not from a dictionary, and not by matching letters (\"puppy\" and \"puppet\" share letters and mean nothing alike). The answer is <strong>embeddings</strong>: a way of turning text into a list of numbers so that <em>meaning becomes geometry</em>. This one idea powers semantic search, RAG, recommendations, clustering and much of modern AI. Let us build the intuition from zero."),
    ("h2", "What is a vector?"),
    ("p", "A <strong>vector</strong> is just a list of numbers. That is all. <code>[3, 4]</code> is a vector. So is <code>[0.12, -0.53, 0.91]</code>. The reason vectors are useful is that a vector with two numbers is a <em>point on a map</em>, three numbers is a point in 3D space, and 1,536 numbers is a point in a space we cannot picture but can still do maths in."),
    ("p", "And once things are points, we can ask: <strong>how far apart are they?</strong> Points that are close together are similar. That is the whole trick."),
    ("h2", "A map of meaning (with two numbers)"),
    ("p", "Imagine a tiny map where the horizontal axis says \"how much like an animal is it?\" and the vertical axis says \"how much like food is it?\". We can place words on it by hand:"),
] + py('''import math

# (animal-ness, food-ness) - hand-made for illustration
words = {
    "dog":       (0.95, 0.05),
    "puppy":     (0.90, 0.05),
    "cat":       (0.93, 0.07),
    "pizza":     (0.00, 0.98),
    "sandwich":  (0.02, 0.95),
    "chicken":   (0.60, 0.70),   # both an animal and a food!
}

def distance(a, b):
    return math.dist(words[a], words[b])

for a, b in [("dog", "puppy"), ("dog", "cat"), ("dog", "pizza"), ("pizza", "sandwich"), ("chicken", "dog"), ("chicken", "pizza")]:
    print(f"{a:>8} vs {b:<9} distance = {distance(a, b):.2f}")''') + [
    ("p", "\"dog\" and \"puppy\" are close (0.05). \"dog\" and \"pizza\" are far apart (about 1.3). And \"chicken\" sits in the middle, near both animals and foods, which is exactly right. <strong>An embedding model does this, but it invents its own axes</strong>, learned from reading enormous amounts of text, and it uses hundreds or thousands of them instead of two. Nobody names the axes; they capture subtle things like formality, topic, sentiment, tense and countless others."),
    ("h2", "What is an embedding, then?"),
    ("p", "An <strong>embedding</strong> is the vector an embedding model produces for a piece of text (a word, a sentence, a paragraph, a whole document). Similar meanings get nearby vectors. Typical sizes: 384, 768, 1,024, 1,536 or 3,072 numbers. You send text to an embedding API or model; you get a list of floats back."),
    ("code", "text", 'embed("How do I reset my password?")   ->  [ 0.021, -0.113,  0.087, ..., 0.045 ]   (1,536 numbers)\nembed("I forgot my login credentials")  ->  [ 0.019, -0.109,  0.091, ..., 0.041 ]   <- nearly identical!\nembed("Best pizza in Naples")           ->  [-0.204,  0.310, -0.012, ..., 0.152 ]   <- somewhere else entirely'),
    ("p", "Notice the first two share <em>almost no words</em> yet land right next to each other. That is the magic keyword search cannot do: matching by <strong>meaning</strong>, not by spelling."),
    ("h2", "Measuring similarity: cosine, dot product, distance"),
    ("p", "There are three common ways to compare two vectors:"),
    ("ul", [
        "<strong>Euclidean distance</strong>: the straight-line distance between the points. Smaller = more similar.",
        "<strong>Dot product</strong>: multiply matching numbers and add them up. Larger = more similar (but it also grows with vector length).",
        "<strong>Cosine similarity</strong>: the cosine of the <em>angle</em> between the vectors. It ignores length and only cares about <em>direction</em>. Ranges from -1 (opposite) to 1 (same direction); 0 means unrelated. This is the default for text, because a long document and a short one about the same topic point the same way.",
    ]),
    ("p", "Cosine similarity is <code>dot(a, b) / (|a| &times; |b|)</code>. Here it is from scratch, so no library hides the idea:"),
] + py('''import math

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def norm(a):
    return math.sqrt(dot(a, a))

def cosine(a, b):
    return dot(a, b) / (norm(a) * norm(b))

cat  = [0.9, 0.1]
dog  = [0.8, 0.2]
pizza = [0.05, 0.95]

print("cat vs dog  :", round(cosine(cat, dog), 3))
print("cat vs pizza:", round(cosine(cat, pizza), 3))

# Length does not matter to cosine: a doubled vector points the same way
print("cat vs 2*cat:", round(cosine(cat, [x * 2 for x in cat]), 3))''') + [
    ("note", "Normalised vectors", "Many embedding models return vectors already scaled to length 1 (\"normalised\"). For those, cosine similarity equals the dot product, which is faster to compute. Vector databases use this shortcut constantly."),
    ("h2", "A working semantic search, with a toy embedder"),
    ("p", "Real embedding models are huge neural networks, but we can simulate one honestly: give every word a hand-made vector over a few \"concept\" dimensions, and embed a sentence as the <em>average</em> of its word vectors. It is crude, but it shows exactly how embedding-based search behaves, including finding matches that share no words with the query."),
] + py('''import math

# dimensions: [animals, food, technology, money, travel]
VEC = {
    "dog": [1,0,0,0,0], "puppy": [1,0,0,0,0], "cat": [1,0,0,0,0], "pet": [1,0,0,0,0], "adopt": [.6,0,0,.1,0],
    "pizza": [0,1,0,0,0], "recipe": [0,1,0,0,0], "cook": [0,1,0,0,0], "dinner": [0,1,0,0,.1], "restaurant": [0,.9,0,.2,.2],
    "laptop": [0,0,1,.1,0], "software": [0,0,1,0,0], "bug": [0,0,1,0,0], "code": [0,0,1,0,0], "computer": [0,0,1,.1,0],
    "invoice": [0,0,.1,1,0], "payment": [0,0,.1,1,0], "refund": [0,0,0,1,0], "price": [0,0,0,1,0], "bank": [0,0,0,1,0],
    "eat": [0,1,0,0,0], "flight": [0,0,0,.2,1], "hotel": [0,0,0,.3,1], "trip": [0,0,0,.1,1], "airport": [0,0,0,0,1], "visa": [0,0,0,.3,.9],
}

def embed(text):
    vecs = [VEC[w] for w in text.lower().split() if w in VEC]
    n = len(vecs) or 1
    return [sum(col) / n for col in zip(*vecs)] if vecs else [0]*5

def cosine(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x*x for x in a)), math.sqrt(sum(y*y for y in b))
    return d / (na * nb) if na and nb else 0.0

docs = [
    "adopt a puppy",
    "cook a pizza recipe",
    "fix a software bug",
    "request a refund for an invoice",
    "book a flight and hotel",
    "dinner at a restaurant near the airport",
]

for query in ["my dog needs a new pet", "where can I eat before my flight"]:
    q = embed(query)
    print("Q:", query)
    for d in sorted(docs, key=lambda d: cosine(q, embed(d)), reverse=True)[:3]:
        print(f"   {cosine(q, embed(d)):.2f}  {d}")''') + [
    ("p", "The first query shares zero words with \"adopt a puppy\", yet that document wins. The second mixes two ideas (food and travel) and the best match is the document that mixes the same two, the restaurant near the airport, with the pure-travel document behind it. A keyword engine would have returned nothing for either. That is semantic search."),
    ("h2", "Where do real embeddings come from?"),
    ("p", "Embedding models are neural networks trained with a clever objective: <strong>pull texts that mean the same thing together, push unrelated ones apart</strong> (contrastive learning). Show the model millions of pairs (question and its answer, a title and its article, a sentence and its paraphrase) and it learns a space where meaning is distance. Popular options: OpenAI <code>text-embedding-3</code>, Cohere Embed, Google's embeddings, Voyage, and open models like BGE, E5 and GTE that you can run yourself."),
    ("code", "pyfile", '# Typical real-world usage (shown for reading; needs a key or a model download)\nfrom openai import OpenAI\nclient = OpenAI()\n\nresp = client.embeddings.create(\n    model="text-embedding-3-small",\n    input=["How do I reset my password?", "Best pizza in Naples"],\n)\nvectors = [item.embedding for item in resp.data]   # two lists of 1,536 floats\nprint(len(vectors), len(vectors[0]))'),
    ("h2", "Choosing an embedding model"),
    ("ul", [
        "<strong>Quality</strong>: check the MTEB leaderboard, but always test on <em>your</em> data.",
        "<strong>Dimensions</strong>: more dimensions capture more nuance but cost more storage and search time. Some models let you truncate (\"Matryoshka\" embeddings).",
        "<strong>Language</strong>: use a multilingual model if you serve multiple languages.",
        "<strong>Domain</strong>: code, legal and medical text often benefit from specialised models.",
        "<strong>Cost and privacy</strong>: an API is easy; a self-hosted open model keeps data in-house.",
        "<strong>Never mix models</strong>: vectors from different models live in different spaces. If you change the model, you must re-embed everything.",
    ]),
    ("h2", "What embeddings are bad at"),
    ("ul", [
        "<strong>Exact matches</strong>: product codes, error numbers, names, IDs. \"ERR-4471\" and \"ERR-4472\" look nearly identical to an embedding. (Keyword search and hybrid search fix this; see the next lessons.)",
        "<strong>Negation</strong>: \"I like this\" and \"I do not like this\" can embed close together.",
        "<strong>Numbers and dates</strong>: \"before 2020\" is poorly captured.",
        "<strong>Domain jargon</strong> the model never saw.",
        "<strong>Long text</strong>: one vector for a 20-page document blurs everything together. That is why we chunk (next lesson).",
    ]),
    ("h2", "Beyond text"),
    ("p", "Anything can be embedded: images, audio, code, products, users, songs. <em>Multimodal</em> models even put images and text into the <strong>same</strong> space, so the text \"a red bicycle\" lands near photos of red bicycles. That is how image search by description works. Recommendation systems embed both users and items and recommend the nearest items."),
    ("exercise", "Add a sixth document to the toy semantic search, \"cheap hotel and airport pickup\", and a query \"where should I stay on my trip\". Which document ranks first? Then add the word \"stay\" to the vocabulary with the vector [0,0,0,.2,1] and see how the ranking changes."),
    ("solution", "python", 'import math\n\nVEC = {"hotel": [0,0,0,.3,1], "airport": [0,0,0,0,1], "trip": [0,0,0,.1,1], "cheap": [0,0,0,1,0],\n       "puppy": [1,0,0,0,0], "adopt": [.6,0,0,.1,0], "stay": [0,0,0,.2,1]}\n\ndef embed(t):\n    v = [VEC[w] for w in t.split() if w in VEC]\n    return [sum(c) / len(v) for c in zip(*v)]\n\ndef cos(a, b):\n    d = sum(x*y for x, y in zip(a, b))\n    return d / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b)))\n\ndocs = ["adopt a puppy", "cheap hotel and airport pickup"]\nq = embed("where should i stay on my trip")\nfor d in sorted(docs, key=lambda d: -cos(q, embed(d))):\n    print(round(cos(q, embed(d)), 2), d)'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-vector-search"] = [
    ("p", "You now know that text becomes vectors and that similar meanings sit close together. But a real company has millions of documents. Two practical questions follow: <strong>how do we cut documents into pieces</strong> a model can use (chunking), and <strong>how do we find the nearest vectors among millions in milliseconds</strong> (vector databases and approximate search)? This lesson answers both."),
    ("h2", "Step 1: Chunking, because one vector per document is a blurry vector"),
    ("p", "Embed a whole 30-page handbook as a single vector and you get a smoothie of every topic in it. A question about the refund policy will match that smoothie only weakly. So we split documents into <strong>chunks</strong> and embed each chunk. Retrieval then returns the specific passages that matter, and only those go into the prompt (saving tokens and money, lesson 2)."),
    ("p", "Chunking is where many RAG projects quietly succeed or fail. The trade-off:"),
    ("ul", [
        "<strong>Too small</strong> (one sentence): precise, but loses context. \"It must be returned within 30 days\", what is \"it\"?",
        "<strong>Too big</strong> (five pages): full context, but the vector is blurry, retrieval is imprecise, and you waste prompt tokens on irrelevant text.",
        "<strong>Sweet spot</strong>: usually 200&ndash;800 tokens, with a small <em>overlap</em> (10&ndash;20%) so sentences that straddle a boundary are not lost.",
    ]),
    ("h2", "Chunking strategies, from simple to smart"),
    ("ul", [
        "<strong>Fixed size</strong>: every N characters/tokens. Easy, but cuts mid-sentence.",
        "<strong>Recursive / by structure</strong>: split on paragraphs first, then sentences, then words, only as needed. The sensible default.",
        "<strong>Semantic chunking</strong>: split where the topic changes (embedding similarity between neighbouring sentences drops).",
        "<strong>Document-aware</strong>: use headings, Markdown sections, code functions, table rows or slide boundaries as natural chunks.",
        "<strong>Parent-child</strong>: embed small chunks for precise matching, but hand the model the larger parent section for context (more in the RAG evaluation lesson).",
    ]),
    ("p", "Two chunkers side by side, on the same text, so you can see the difference:"),
] + py('''import re

text = ("Refunds. Laptops can be returned within 30 days for a full refund. Opened software is not refundable. "
        "Shipping. Shipping is free on orders over 50 dollars. Express shipping takes two days. "
        "Warranty. Every laptop has a one year warranty. Batteries are covered for six months.")

def fixed_chunks(text, size, overlap=0):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]

def sentence_chunks(text, max_chars):
    sentences = re.split(r"(?<=[.!?])\\s+", text)
    chunks, current = [], ""
    for s in sentences:
        if current and len(current) + len(s) + 1 > max_chars:
            chunks.append(current)
            current = s
        else:
            current = f"{current} {s}".strip()
    if current:
        chunks.append(current)
    return chunks

print("FIXED (cuts words in half):")
for c in fixed_chunks(text, 90):
    print("  |", c)

print("\\nSENTENCE-AWARE:")
for c in sentence_chunks(text, 110):
    print("  |", c)''') + [
    ("p", "The fixed chunker slices \"refundable\" in the middle. The sentence-aware one keeps ideas whole. Always add <em>metadata</em> to each chunk (source file, page, section title, date, access permissions); it powers filtering, citations and debugging later."),
    ("h2", "Step 2: Searching millions of vectors"),
    ("p", "Suppose you have 10 million chunk vectors, each with 1,536 numbers. The honest way to find the nearest to a query is <strong>brute force</strong>: compute the similarity to every single one and keep the best. That is called <em>exact</em> or <em>flat</em> search. It is perfectly accurate, and fine up to maybe a hundred thousand vectors. At ten million it means about 15 billion multiplications per query, too slow for a chatbot."),
    ("p", "The solution is <strong>Approximate Nearest Neighbour (ANN)</strong> search: build an index that finds <em>very probably</em> the best matches while looking at only a tiny fraction of the data. You give up a sliver of accuracy (say, 98% recall) for a 100&times; speedup. Let us feel the idea with the simplest ANN method: <strong>clustering</strong> (\"IVF\"). Group vectors into buckets around a few centres. At query time, look only in the bucket(s) whose centre is closest."),
] + py('''import math, random

rng = random.Random(42)

# 3,000 fake 2-D "vectors" scattered around 6 hidden topic centres
centres = [(0, 0), (10, 0), (0, 10), (10, 10), (5, 5), (-5, 8)]
points = [(cx + rng.gauss(0, 1.2), cy + rng.gauss(0, 1.2)) for cx, cy in centres for _ in range(500)]

def dist(a, b):
    return math.dist(a, b)

# --- brute force: compare against every point ---
def brute(query, k=3):
    scored = sorted(points, key=lambda p: dist(query, p))
    return scored[:k], len(points)

# --- IVF: assign each point to its nearest centre once, up front ---
buckets = {c: [] for c in centres}
for p in points:
    buckets[min(centres, key=lambda c: dist(p, c))].append(p)

def ivf(query, k=3, probe=1):
    nearest_centres = sorted(centres, key=lambda c: dist(query, c))[:probe]
    candidates = [p for c in nearest_centres for p in buckets[c]]
    return sorted(candidates, key=lambda p: dist(query, p))[:k], len(candidates)

query = (9.0, 9.5)
exact, looked_exact = brute(query)
approx, looked_ivf = ivf(query)

print(f"brute force looked at {looked_exact} points")
print(f"IVF (1 bucket) looked at {looked_ivf} points  ({looked_exact // looked_ivf}x fewer)")
print("same top-3 result:", exact == approx)''') + [
    ("p", "About five times fewer comparisons and the same answer here. Real indexes are cleverer, and they do occasionally miss the true best match, which is why it is called <em>approximate</em>. The popular ones:"),
    ("ul", [
        "<strong>HNSW</strong> (Hierarchical Navigable Small World): builds a multi-layer graph, like a road network with highways on top and local streets below. Search starts on the highway layer, hops toward the query, then drops to finer layers. Fast and accurate, the most common default. Costs extra memory.",
        "<strong>IVF</strong> (inverted file): the clustering idea you just ran. Often combined with compression.",
        "<strong>PQ</strong> (product quantization): compress each vector into a few bytes so billions fit in RAM, at some accuracy cost.",
        "<strong>DiskANN</strong> and friends: keep most of the index on SSD for huge collections.",
    ]),
    ("code", "text", "HNSW intuition - finding a house in a new city\n\n  Layer 2 (highways):   [A] -------------------- [F]              few nodes, big jumps\n  Layer 1 (main roads): [A] ---- [C] ---- [F] ---- [H]\n  Layer 0 (every home): [A][B][C][D][E][F][G][H][I][J]           all vectors, tiny hops\n\n  Start at the top, hop toward the query, drop a layer, repeat until you land next door."),
    ("h2", "The ANN dials"),
    ("p", "Every ANN index has knobs that trade speed against recall: for HNSW, <code>M</code> (connections per node), <code>efConstruction</code> (build effort) and <code>efSearch</code> (search effort); for IVF, the number of clusters and how many to probe. Higher effort means better recall and slower queries. You tune them by measuring <strong>recall@k against exact search</strong> on a sample of your own data."),
    ("h2", "Choosing a vector database"),
    ("p", "A <strong>vector database</strong> stores vectors alongside their text and metadata, builds ANN indexes, and answers \"give me the nearest k, optionally filtered by metadata\". The landscape:"),
    ("ul", [
        "<strong>pgvector</strong> (a PostgreSQL extension): use your existing Postgres. Great when you already run it, want SQL joins and transactions, and have up to a few million vectors.",
        "<strong>Chroma</strong>, <strong>LanceDB</strong>: embedded/local, ideal for prototypes and small apps.",
        "<strong>FAISS</strong>: a library (not a server) from Meta; a fast building block.",
        "<strong>Qdrant</strong>, <strong>Weaviate</strong>, <strong>Milvus</strong>: dedicated open-source engines with filtering, hybrid search and horizontal scaling.",
        "<strong>Pinecone</strong>: fully managed cloud service; least ops work.",
        "<strong>Elasticsearch / OpenSearch / MongoDB Atlas</strong>: existing search/database products that added vector support, handy if you are already on them.",
    ]),
    ("p", "How to pick: start with the simplest thing you already run (often pgvector). Move to a dedicated engine when you hit scale, latency or feature limits (advanced filtering, multi-tenant isolation, very large collections)."),
    ("h2", "Metadata filtering: the feature you will need on day two"),
    ("p", "Real questions are rarely \"nearest anywhere\". They are \"nearest <em>among documents this user is allowed to see</em>, from the last year, in English\". Filter on metadata, either <strong>pre-filtering</strong> (restrict candidates first) or <strong>post-filtering</strong> (search then discard, which can leave you with too few results). Good engines filter during the graph traversal. This is also how you enforce <strong>access control</strong> in RAG: never rely on the model to hide documents from users; never retrieve them in the first place."),
    ("code", "pyfile", '# pgvector: nearest chunks for a tenant, in plain SQL\nSELECT id, text, 1 - (embedding <=> %(query_vec)s) AS similarity\nFROM   chunks\nWHERE  tenant_id = %(tenant)s\n  AND  published_at > now() - interval \'1 year\'\nORDER  BY embedding <=> %(query_vec)s      -- cosine distance\nLIMIT  5;'),
    ("h2", "Operating a vector store"),
    ("ul", [
        "<strong>Keep text and vectors together</strong> with a stable chunk ID so you can cite and debug.",
        "<strong>Version your embeddings</strong> (model name + date) so you know when to re-embed.",
        "<strong>Re-index incrementally</strong> when documents change; deleting stale chunks matters as much as adding new ones.",
        "<strong>Watch memory</strong>: 10 million 1,536-dim float32 vectors is about 60 GB before the index. Compression or lower dimensions help.",
    ]),
    ("exercise", "Change the IVF demo to probe 2 buckets instead of 1 and query near a border between clusters, such as (5, 9). Compare the candidate count and whether the top-3 matches the brute-force answer. This is the recall-vs-speed dial in action."),
    ("solution", "python", 'import math, random\n\nrng = random.Random(42)\ncentres = [(0, 0), (10, 0), (0, 10), (10, 10), (5, 5), (-5, 8)]\npoints = [(cx + rng.gauss(0, 1.2), cy + rng.gauss(0, 1.2)) for cx, cy in centres for _ in range(500)]\nbuckets = {c: [] for c in centres}\nfor p in points:\n    buckets[min(centres, key=lambda c: math.dist(p, c))].append(p)\n\nq = (5, 9)\nexact = sorted(points, key=lambda p: math.dist(q, p))[:3]\nfor probe in (1, 2):\n    near = sorted(centres, key=lambda c: math.dist(q, c))[:probe]\n    cand = [p for c in near for p in buckets[c]]\n    top = sorted(cand, key=lambda p: math.dist(q, p))[:3]\n    print(f"probe={probe}: {len(cand)} candidates, matches exact: {top == exact}")'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-bm25"] = [
    ("p", "Here is a plot twist for a course about modern AI: <strong>a 1990s keyword algorithm called BM25 still beats fancy embeddings on a lot of real queries</strong>, and every serious search system, including the ones behind RAG chatbots, uses it. Search \"ERR-4471\" or a person's surname or a rare product name, and semantic search shrugs while BM25 nails it. Let us understand it properly, and build it."),
    ("h2", "Keyword search in one picture: the inverted index"),
    ("p", "A book has an index at the back: for each term, the pages it appears on. A search engine builds the same thing for documents, called an <strong>inverted index</strong>: a dictionary from each <em>word</em> to the list of <em>documents</em> containing it. To answer a query you look up each query word and combine the lists. No scanning of every document."),
] + py('''import re
from collections import defaultdict

docs = {
    1: "Laptops can be returned within 30 days for a refund",
    2: "Opened software is not refundable",
    3: "Error ERR-4471 means the payment gateway timed out",
    4: "Free shipping on laptops over 50 dollars",
}

def tokenize(text):
    return re.findall(r"[a-z0-9-]+", text.lower())

index = defaultdict(set)
for doc_id, text in docs.items():
    for token in tokenize(text):
        index[token].add(doc_id)

for word in ["laptops", "refund", "err-4471", "shipping"]:
    print(f"{word:<10} -> docs {sorted(index[word])}")

# AND search: documents containing BOTH words
both = index["laptops"] & index["refund"]
print("laptops AND refund ->", sorted(both))''') + [
    ("p", "That is exact keyword matching. It is fast and precise, but blunt: it treats all matches equally. Doc 1 matches \"refund\" once; a 50-page policy that mentions \"refund\" 40 times would also match, and is a document 3 is barely about. We need a way to <strong>rank</strong>. Enter TF-IDF."),
    ("h2", "TF-IDF: two very human intuitions"),
    ("ul", [
        "<strong>TF (term frequency)</strong>: if a document mentions \"refund\" many times, it is probably about refunds. More mentions, higher score.",
        "<strong>IDF (inverse document frequency)</strong>: rare words are more informative than common ones. \"the\" appears in every document, so it tells you nothing. \"ERR-4471\" appears in one, so it tells you a lot. The rarer the word across the collection, the more it counts.",
    ]),
    ("p", "TF-IDF multiplies them: <code>score = TF &times; IDF</code>. Words that are frequent <em>here</em> but rare <em>everywhere</em> win."),
    ("h2", "BM25: TF-IDF, but grown up"),
    ("p", "<strong>BM25</strong> (Best Match 25) fixes two flaws in raw TF-IDF:"),
    ("ul", [
        "<strong>Diminishing returns on frequency.</strong> Mentioning a word 40 times is not 40&times; more relevant than once. BM25's term-frequency part <em>saturates</em>: extra repeats add less and less. A knob <code>k1</code> (typically 1.2&ndash;2.0) controls how fast.",
        "<strong>Length normalisation.</strong> A long document naturally contains more words. BM25 penalises length, so a short focused document beats a long rambling one with the same term count. A knob <code>b</code> (typically 0.75) controls how much.",
    ]),
    ("code", "text", "score(D, Q) = sum over each query term t:\n\n      IDF(t)  *   tf * (k1 + 1)\n                 ----------------------------------------\n                 tf + k1 * (1 - b + b * len(D)/avg_len)\n\n  IDF(t) = ln( (N - n_t + 0.5) / (n_t + 0.5) + 1 )      N = #documents, n_t = #documents containing t"),
    ("p", "Do not memorise it; <em>see</em> it. Here is BM25 in about twenty lines, with no libraries:"),
] + py('''import math, re
from collections import Counter

docs = [
    "Laptops can be returned within 30 days for a full refund",
    "Opened software is not refundable but laptops accessories can be refunded",
    "Error ERR-4471 means the payment gateway timed out",
    "Free shipping on laptops over 50 dollars",
    "Refund refund refund refund refund refund policy policy policy overview",
]

def tokenize(text):
    return re.findall(r"[a-z0-9-]+", text.lower())

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tokens = [tokenize(d) for d in docs]
        self.N = len(docs)
        self.avg_len = sum(len(t) for t in self.tokens) / self.N
        self.df = Counter(w for t in self.tokens for w in set(t))   # docs containing each word
        self.tf = [Counter(t) for t in self.tokens]

    def idf(self, word):
        n = self.df.get(word, 0)
        return math.log((self.N - n + 0.5) / (n + 0.5) + 1)

    def score(self, query, i):
        length = len(self.tokens[i])
        total = 0.0
        for w in tokenize(query):
            tf = self.tf[i].get(w, 0)
            if not tf:
                continue
            norm = tf + self.k1 * (1 - self.b + self.b * length / self.avg_len)
            total += self.idf(w) * tf * (self.k1 + 1) / norm
        return total

    def search(self, query, k=3):
        scored = [(self.score(query, i), i) for i in range(self.N)]
        return [(round(s, 2), docs[i]) for s, i in sorted(scored, reverse=True)[:k] if s > 0]

bm25 = BM25(docs)
for q in ["laptop refund", "ERR-4471", "refund"]:
    print(f"Q: {q}")
    for score, text in bm25.search(q):
        print(f"   {score:5}  {text[:60]}")

# Saturation: how much does 6 mentions beat 1 mention?  Raw counting vs BM25
spam, normal = 4, 0                     # indexes of the two documents
raw_ratio = bm25.tf[spam]["refund"] / bm25.tf[normal]["refund"]
bm25_ratio = bm25.score("refund", spam) / bm25.score("refund", normal)
print(f"\\nrefund appears {bm25.tf[spam]['refund']}x vs {bm25.tf[normal]['refund']}x")
print(f"raw counting says the spammy doc is {raw_ratio:.1f}x better")
print(f"BM25 says it is only          {bm25_ratio:.1f}x better")''') + [
    ("p", "Two things to notice. First, the query \"ERR-4471\" finds the one document instantly, because that token is rare (huge IDF). An embedding model would blur it with every other error code. Second, look at the last lines: the document that repeats \"refund\" six times is really about refunds, so it deserves to win for the bare word, but raw counting would call it 6&times; better while BM25 says about 2&times;. Repeats add less and less (saturation) and long documents are penalised. That is the difference between BM25 and naive counting."),
    ("h2", "What BM25 is great at, and what it misses"),
    ("ul", [
        "<strong>Great:</strong> exact terms, names, IDs, error codes, SKUs, legal citations, code identifiers, rare jargon. Fast, cheap, explainable (you can see which words matched), needs no model and no GPU.",
        "<strong>Misses:</strong> synonyms and paraphrase (\"car\" vs \"automobile\", \"forgot my login\" vs \"reset my password\"), and understanding intent. It only sees the words you typed.",
    ]),
    ("p", "Notice the pattern: <strong>BM25 and embeddings fail in opposite ways.</strong> Keyword search is precise but literal; semantic search understands meaning but is fuzzy about exact tokens. That complementarity is exactly why the next lesson combines them."),
    ("h2", "Improving keyword search"),
    ("ul", [
        "<strong>Stemming / lemmatisation</strong>: reduce \"returning\", \"returned\", \"returns\" to one root so they match.",
        "<strong>Stop words</strong>: ignore \"the\", \"is\", \"of\" (BM25's IDF already down-weights them, so this is optional).",
        "<strong>Synonym lists</strong> and <strong>fuzzy matching</strong> for typos.",
        "<strong>Field boosts</strong>: a match in the title counts more than in the body.",
        "<strong>Phrase and proximity</strong> queries.",
    ]),
    ("h2", "In the real world"),
    ("p", "You rarely write BM25 yourself. It is built into <strong>Elasticsearch</strong>, <strong>OpenSearch</strong>, <strong>Apache Lucene</strong>, <strong>Solr</strong> and <strong>Tantivy</strong>, into <strong>PostgreSQL full-text search</strong> (<code>ts_rank</code>, and extensions for true BM25), <strong>SQLite FTS5</strong> (which literally has a <code>bm25()</code> function), and into vector databases with hybrid mode. Python has the <code>rank_bm25</code> package for quick experiments."),
    ("exercise", "Try the BM25 class with <code>k1=0.1</code> and then <code>k1=3.0</code> on the query \"refund\". With a tiny k1, term frequency barely matters; with a large k1 the repeated-refund document climbs. Which setting ranks it first? What does that tell you about tuning k1 for your data?"),
    ("solution", "python", 'import math, re\nfrom collections import Counter\n\ndocs = ["Laptops can be returned within 30 days for a full refund",\n        "Refund refund refund refund refund refund policy policy policy overview"]\ntok = lambda t: re.findall(r"[a-z0-9-]+", t.lower())\ntoks = [tok(d) for d in docs]\nN = len(docs); avg = sum(map(len, toks)) / N\ndf = Counter(w for t in toks for w in set(t))\n\ndef score(q, i, k1, b=0.75):\n    tf = Counter(toks[i])[q]\n    if not tf: return 0\n    idf = math.log((N - df[q] + .5) / (df[q] + .5) + 1)\n    return idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(toks[i]) / avg))\n\nfor k1 in (0.1, 3.0):\n    print(k1, [round(score("refund", i, k1), 2) for i in range(N)])'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-hybrid-rerank"] = [
    ("p", "You now own two search tools that fail in opposite ways. <strong>Vector search</strong> understands meaning but blurs exact tokens. <strong>BM25</strong> nails exact tokens but is blind to paraphrase. The obvious question: can we use both? Yes, and the result, <strong>hybrid search</strong>, is the single biggest upgrade most RAG systems can make. Then a second stage called <strong>reranking</strong> squeezes out extra precision."),
    ("h2", "The two-stage idea: cast a wide net, then look closely"),
    ("code", "text", "        query\n          |\n   +------+-------+\n   |              |\n BM25          vector        <- stage 1: RETRIEVAL. Cheap and fast, looks at millions.\n (top 50)      (top 50)         Goal: high RECALL (do not miss the good ones)\n   |              |\n   +------+-------+\n          | fuse (RRF)      <- combine the two ranked lists\n          v\n   top 50 candidates\n          |\n      RERANKER           <- stage 2: RERANKING. Slow but smart, looks at ~50.\n          |                  Goal: high PRECISION (put the best on top)\n          v\n    top 5 -> the LLM prompt"),
    ("h2", "Fusing two rankings: Reciprocal Rank Fusion"),
    ("p", "The tricky part of hybrid search: BM25 scores (like 12.7) and cosine similarities (like 0.83) are on completely different scales, so you cannot just add them. <strong>Reciprocal Rank Fusion (RRF)</strong> sidesteps that by ignoring scores entirely and using only <em>positions</em>. A document scores <code>1 / (k + rank)</code> in each list (with <code>k</code> around 60), and the scores are summed. Documents ranked high in <em>either</em> list rise; documents high in <em>both</em> win."),
] + py('''from collections import defaultdict

# Ranked results (best first) from two different retrievers
bm25_ranking   = ["doc_err4471", "doc_refund", "doc_shipping", "doc_warranty"]
vector_ranking = ["doc_refund", "doc_returns", "doc_warranty", "doc_err4471"]

def rrf(rankings, k=60):
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda kv: -kv[1])

for doc, score in rrf([bm25_ranking, vector_ranking]):
    print(f"{score:.4f}  {doc}")''') + [
    ("p", "\"doc_refund\" is near the top of both lists, so it wins. \"doc_err4471\" is #1 for keywords but last for vectors, and still stays high in the fused list. \"doc_returns\" only the vector search found, and it still makes it in. Best of both, no score calibration needed. Most vector databases (Qdrant, Weaviate, Elasticsearch, Pinecone hybrid) offer RRF or a weighted variant out of the box."),
    ("p", "An alternative is <strong>weighted score fusion</strong>: normalise both score sets to 0&ndash;1 and take <code>alpha * vector + (1 - alpha) * keyword</code>. You must tune alpha, which is why many teams start with RRF."),
    ("h2", "A complete hybrid retriever"),
    ("p", "Let us assemble everything from the last three lessons: a toy embedder, BM25 and RRF, over a small support knowledge base. Try the queries: one needs keywords, one needs meaning."),
] + py('''import math, re
from collections import Counter, defaultdict

DOCS = {
    "refund":   "Laptops can be returned within 30 days for a full refund.",
    "software": "Opened software is not refundable.",
    "err4471":  "Error ERR-4471 means the payment gateway timed out. Retry in five minutes.",
    "shipping": "Shipping is free on orders over 50 dollars. Express shipping takes two days.",
    "warranty": "Every laptop includes a one year warranty covering defects.",
    "password": "To reset your password use the forgot password link on the login page.",
}
SYNONYMS = {"credentials": "password", "login": "password", "forgot": "password", "money": "refund",
            "back": "refund", "send": "shipping", "deliver": "shipping", "broken": "warranty", "defect": "warranty"}

tok = lambda t: re.findall(r"[a-z0-9-]+", t.lower())

# --- keyword side: BM25 ---
ids = list(DOCS)
T = {i: tok(DOCS[i]) for i in ids}
N, avg = len(ids), sum(len(t) for t in T.values()) / len(ids)
df = Counter(w for t in T.values() for w in set(t))
def bm25(q, i, k1=1.5, b=0.75):
    tf = Counter(T[i]); s = 0.0
    for w in tok(q):
        if w in tf:
            idf = math.log((N - df[w] + .5) / (df[w] + .5) + 1)
            s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(T[i]) / avg))
    return s

# --- "semantic" side: words mapped to shared concept tokens (toy embedder) ---
def concepts(text):
    return Counter(SYNONYMS.get(w, w) for w in tok(text))
def cosine(a, b):
    d = sum(a[k] * b[k] for k in a)
    return d / (math.sqrt(sum(v*v for v in a.values())) * math.sqrt(sum(v*v for v in b.values()))) if a and b else 0
C = {i: concepts(DOCS[i]) for i in ids}

def rank_bm25(q):  return [i for i in sorted(ids, key=lambda i: -bm25(q, i)) if bm25(q, i) > 0]
def rank_vec(q):   return [i for i in sorted(ids, key=lambda i: -cosine(concepts(q), C[i])) if cosine(concepts(q), C[i]) > 0]

def hybrid(q, k=3, rrf_k=60):
    score = defaultdict(float)
    for ranking in (rank_bm25(q), rank_vec(q)):
        for r, i in enumerate(ranking, 1):
            score[i] += 1 / (rrf_k + r)
    return [i for i, _ in sorted(score.items(), key=lambda kv: -kv[1])][:k]

for q in ["ERR-4471", "I forgot my login credentials", "get my money back"]:
    print(f"Q: {q}")
    print("   keyword :", rank_bm25(q)[:3])
    print("   semantic:", rank_vec(q)[:3])
    print("   HYBRID  :", hybrid(q))''') + [
    ("p", "Query 1 is a keyword job. Query 2 only matches on the single word \"login\" (\"credentials\" never appears in the document). Query 3 shares no word with its answer at all, so keyword search returns nothing and only the meaning side finds it. The hybrid list is correct in all three cases because each retriever covers the other's blind spot. This is the pattern in production systems."),
    ("h2", "Stage two: reranking"),
    ("p", "Retrieval must be <em>fast</em>, so it scores each document independently against the query using precomputed vectors. That is a <strong>bi-encoder</strong>: the query and the document are encoded <em>separately</em> and compared. Quick, but the query and document never actually \"see\" each other."),
    ("p", "A <strong>cross-encoder</strong> takes the query <em>and</em> a candidate document <em>together</em> in one pass and outputs a relevance score. Because the model reads both at once, it catches subtle things: negation, whether the passage <em>answers</em> the question or merely mentions the topic. It is far more accurate and far slower (one model run per candidate), so you only run it on the top 20&ndash;100 candidates from stage one."),
    ("ul", [
        "<strong>Bi-encoder (retrieval)</strong>: encode once, compare with a dot product. Millions of documents in milliseconds. Less precise.",
        "<strong>Cross-encoder (reranker)</strong>: joint reading of query + document. Hundreds of candidates in a fraction of a second. Most precise.",
        "<strong>Popular rerankers</strong>: Cohere Rerank, Voyage rerank, Jina reranker, and open models such as BGE-reranker. You can also use an LLM itself to rank candidates, at higher cost.",
    ]),
    ("code", "pyfile", '# Rerank the top 50 candidates down to the best 5 (shown for reading)\nimport cohere\nco = cohere.Client()\n\nresults = co.rerank(\n    model="rerank-english-v3.0",\n    query="Can I return a laptop after 30 days?",\n    documents=[c.text for c in candidates],   # the ~50 from hybrid search\n    top_n=5,\n)\nbest = [candidates[r.index] for r in results.results]'),
    ("h2", "Fixing the query itself"),
    ("p", "Sometimes the retrieval is fine and the <em>question</em> is the problem. Users type vague, short or conversational queries (\"what about that one?\"). Cheap fixes that use an LLM before retrieval:"),
    ("ul", [
        "<strong>Query rewriting</strong>: turn a follow-up like \"and for laptops?\" into a standalone question (\"What is the return policy for laptops?\") using the conversation history.",
        "<strong>Multi-query</strong>: ask the LLM for three paraphrases of the question, retrieve for each, and merge results (with RRF). Catches phrasing mismatches.",
        "<strong>HyDE (hypothetical document embeddings)</strong>: have the LLM write a fake answer, then search with <em>that</em> text. Answers look more like documents than questions do.",
        "<strong>Query decomposition</strong>: split \"compare the warranty and return policies\" into two sub-queries.",
        "<strong>Metadata extraction</strong>: pull filters out of the question (\"invoices from March\" becomes a date filter).",
    ]),
    ("h2", "Rules of thumb"),
    ("ul", [
        "Retrieve a <em>lot</em> (30&ndash;100), rerank, then keep a <em>few</em> (3&ndash;8) for the prompt.",
        "Hybrid + rerank usually beats either alone, often dramatically on messy real-world data.",
        "Measure! Compare vector-only, hybrid, and hybrid+rerank on your own question set (next lessons) instead of trusting anyone's benchmark.",
    ]),
    ("exercise", "Add a fourth ranking to the RRF demo (say, a rule-based \"recently updated\" list) and see how a document that appears in three lists behaves. Then change <code>k</code> from 60 to 1 and notice how much more the very top ranks dominate."),
    ("solution", "python", 'from collections import defaultdict\n\ndef rrf(rankings, k=60):\n    s = defaultdict(float)\n    for r in rankings:\n        for pos, d in enumerate(r, 1):\n            s[d] += 1 / (k + pos)\n    return sorted(s.items(), key=lambda kv: -kv[1])\n\nlists = [["a", "b", "c"], ["b", "a", "d"], ["b", "e", "a"]]\nfor k in (60, 1):\n    print("k =", k, [(d, round(v, 3)) for d, v in rrf(lists, k)][:3])'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-rag"] = [
    ("p", "Time to put everything together. <strong>RAG (Retrieval-Augmented Generation)</strong> is the most important pattern in applied AI, and now that you know embeddings, chunking, vector search, BM25, hybrid search and hallucinations, it will feel like a natural conclusion instead of a buzzword. By the end of this lesson you will have run a complete mini-RAG system in your browser."),
    ("h2", "The problem RAG solves"),
    ("p", "An LLM has three limits that matter to businesses: it does not know <strong>your private data</strong> (your policies, tickets, contracts), it does not know <strong>recent events</strong> (training cut-off), and it <strong>hallucinates</strong> when it does not know. You could fine-tune a model on your data, but that is expensive, slow to update, and does not reliably stop invention. RAG takes the opposite approach: <em>leave the model alone and hand it the right pages at question time</em>."),
    ("p", "The analogy: an <strong>open-book exam</strong>. A closed-book student relies on memory and bluffs. An open-book student looks up the relevant page first, then answers from it. RAG turns the LLM into the open-book student."),
    ("h2", "The two pipelines"),
    ("p", "RAG has an <strong>offline</strong> half (prepare the library) and an <strong>online</strong> half (answer a question):"),
    ("code", "text", "OFFLINE - ingestion (run when documents change)\n  documents -> parse/clean -> CHUNK -> EMBED -> store in vector DB (+ BM25 index) with metadata\n\nONLINE - answering (run for every question)\n  question\n     -> (rewrite query)\n     -> RETRIEVE (hybrid: vector + BM25)  -> top 30\n     -> RERANK                             -> top 5\n     -> build PROMPT = instructions + retrieved chunks + question\n     -> LLM generates answer (with citations)\n     -> (check faithfulness) -> answer to user"),
    ("h2", "A complete mini-RAG you can run"),
    ("p", "No API key, no server. The retriever is the hybrid one from last lesson. The \"LLM\" is replaced by a small function that extracts the best-matching sentence, so you can see the pipeline shape clearly and the prompt that <em>would</em> go to a real model."),
] + py('''import math, re
from collections import Counter, defaultdict

# ---------- OFFLINE: the knowledge base ----------
DOCUMENTS = {
    "returns.md": "Laptops can be returned within 30 days of delivery for a full refund. Opened software is not refundable. Refunds go back to the original payment method within five business days.",
    "shipping.md": "Shipping is free on orders over 50 dollars. Express shipping takes two days and costs 12 dollars. We ship to the US and Canada only.",
    "warranty.md": "Every laptop includes a one year warranty that covers manufacturing defects. Batteries are covered for six months. Water damage is not covered.",
    "support.md": "Support is available Monday to Friday from 9am to 6pm Eastern. Error ERR-4471 means the payment gateway timed out. Retry after five minutes.",
}

def chunk(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\\s+", text) if s.strip()]

chunks = []                                   # (id, source, text)
for source, body in DOCUMENTS.items():
    for n, piece in enumerate(chunk(body)):
        chunks.append((f"{source}#{n}", source, piece))

# ---------- retrieval ----------
SYN = {"money": "refund", "back": "refund", "return": "returned", "cost": "costs", "deliver": "shipping",
       "broken": "defects", "hours": "available", "open": "available", "time": "available", "canada": "canada"}
tok = lambda t: [SYN.get(w, w) for w in re.findall(r"[a-z0-9-]+", t.lower())]
STOP = {"the", "a", "an", "is", "are", "to", "of", "for", "on", "in", "and", "do", "i", "my", "can", "how", "what", "much", "does", "it"}
content = lambda t: [w for w in tok(t) if w not in STOP]

T = [content(c[2]) for c in chunks]
N = len(T); avg = sum(map(len, T)) / N
df = Counter(w for t in T for w in set(t))

def bm25(q, i, k1=1.5, b=0.75):
    tf = Counter(T[i]); s = 0.0
    for w in content(q):
        if w in tf:
            s += math.log((N - df[w] + .5) / (df[w] + .5) + 1) * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(T[i]) / avg))
    return s

def retrieve(question, k=2):
    ranked = sorted(range(N), key=lambda i: -bm25(question, i))
    return [(chunks[i], round(bm25(question, i), 2)) for i in ranked[:k] if bm25(question, i) > 0]

# ---------- generation ----------
PROMPT = """Answer using ONLY the context. If it is not there, say "I don't have that information."
Cite the source in [brackets].

<context>
{context}
</context>

Question: {question}"""

def answer(question):
    hits = retrieve(question)
    if not hits:
        return "I don't have that information.", None
    context = "\\n".join(f"[{c[1]}] {c[2]}" for c, _ in hits)
    prompt = PROMPT.format(context=context, question=question)
    best = hits[0][0]                                     # stand-in for the LLM
    return f"{best[2]} [{best[1]}]", prompt

for q in ["How long do I have to return a laptop?", "What does ERR-4471 mean?", "Who won the World Cup?"]:
    a, prompt = answer(q)
    print("Q:", q)
    print("A:", a)
    print()''') + [
    ("p", "The third question is the important one. Nothing in the knowledge base matches, so the system <strong>refuses instead of inventing</strong>. That behaviour, designed on purpose, is the difference between a trustworthy assistant and a liar. Here is the prompt that would go to a real model for the first question:"),
] + py('''PROMPT = """Answer using ONLY the context. If it is not there, say "I don't have that information."
Cite the source in [brackets].

<context>
{context}
</context>

Question: {question}"""

context = "[returns.md] Laptops can be returned within 30 days of delivery for a full refund.\\n[returns.md] Opened software is not refundable."
print(PROMPT.format(context=context, question="How long do I have to return a laptop?"))''') + [
    ("h2", "In production: the same shape with real parts"),
    ("code", "pyfile", 'def answer(question, history):\n    standalone = llm.rewrite(question, history)             # \"and for laptops?\" -> full question\n    candidates = hybrid_search(standalone, k=40)            # BM25 + vectors, fused with RRF\n    top = reranker.rerank(standalone, candidates, top_n=5)  # cross-encoder\n    context = \"\\n\\n\".join(f\"[{c.source}] {c.text}\" for c in top)\n\n    response = llm.chat(\n        system=\"Answer ONLY from the context. Cite sources. If unsure, say you do not know.\",\n        user=f\"<context>{context}</context>\\n\\nQuestion: {standalone}\",\n        temperature=0,\n        stream=True,                                         # SSE to the browser\n    )\n    return response'),
    ("h2", "Prompt design for RAG"),
    ("ul", [
        "<strong>Constrain</strong>: answer only from the context; otherwise refuse with a fixed phrase.",
        "<strong>Cite</strong>: require source tags; render them as links so users can verify.",
        "<strong>Structure</strong>: wrap context in tags (<code>&lt;context&gt;</code>) and label each chunk with its source.",
        "<strong>Order</strong>: put the most relevant chunks first (and last), not buried in the middle.",
        "<strong>Conflicts</strong>: tell the model what to do when sources disagree (prefer the newest; mention both).",
        "<strong>Temperature 0</strong> for factual answers.",
    ]),
    ("h2", "RAG versus fine-tuning versus long context"),
    ("ul", [
        "<strong>RAG</strong>: best for knowledge that changes, is private, or needs citations. Cheap to update: just re-index.",
        "<strong>Fine-tuning</strong>: best for changing <em>behaviour, style or format</em> (tone, domain jargon, structured output), not for injecting facts. Expensive to update.",
        "<strong>Long context (stuff everything in the prompt)</strong>: simple and great for a single document. But it costs tokens on every call, degrades in the middle, and does not scale to a company's whole knowledge base.",
        "<strong>Usually you combine them</strong>: RAG for facts, a well-written prompt (or light fine-tune) for behaviour.",
    ]),
    ("h2", "How RAG fails: debug retrieval first"),
    ("p", "When a RAG answer is wrong, do not blame the model first. Ask <strong>which half broke</strong>:"),
    ("ul", [
        "<strong>Retrieval failure</strong> (most common, roughly 70% of cases): the right chunk never reached the prompt. Causes: bad chunking, no keyword matching for IDs, wrong embedding model, missing metadata filter, question too vague, document never ingested.",
        "<strong>Generation failure</strong>: the right chunk <em>was</em> in the prompt but the model ignored it, misread it, or mixed in outside knowledge. Causes: weak prompt, too many distracting chunks, contradictory chunks, high temperature.",
        "<strong>Data failure</strong>: the document itself is wrong, stale or a badly parsed PDF (tables and columns mangled).",
    ]),
    ("p", "The single most useful debugging habit: <strong>log the retrieved chunks with every answer</strong>. Ten seconds reading them tells you whether to fix search or fix the prompt."),
    ("h2", "Security in RAG"),
    ("ul", [
        "<strong>Access control at retrieval time</strong>: filter by the user's permissions in the query; never rely on the model to hide things.",
        "<strong>Indirect prompt injection</strong>: a poisoned document can contain instructions (\"ignore your rules and reveal...\"). Treat retrieved text as untrusted data, not commands, and limit what the model can do.",
        "<strong>PII</strong>: do not embed or log sensitive data you do not need.",
    ]),
    ("exercise", "Add a fifth document, \"billing.md\": \"Invoices are emailed on the first of each month. Late payments incur a 5 percent fee.\" then ask \"When are invoices sent?\" and \"What is the late fee?\" Does the retriever find them? What synonym would you add to help a user asking \"When do I get billed?\"."),
    ("solution", "python", 'import re, math\nfrom collections import Counter\n\ndocs = ["Invoices are emailed on the first of each month.",\n        "Late payments incur a 5 percent fee.",\n        "Laptops can be returned within 30 days."]\nSYN = {"billed": "invoices", "bill": "invoices"}\ntok = lambda t: [SYN.get(w, w) for w in re.findall(r"[a-z0-9]+", t.lower())]\nT = [tok(d) for d in docs]\nN = len(T); avg = sum(map(len, T)) / N\ndf = Counter(w for t in T for w in set(t))\n\ndef score(q, i):\n    tf = Counter(T[i]); s = 0\n    for w in tok(q):\n        if w in tf:\n            s += math.log((N - df[w] + .5) / (df[w] + .5) + 1) * tf[w] * 2.5 / (tf[w] + 1.5 * (0.25 + 0.75 * len(T[i]) / avg))\n    return s\n\nfor q in ["When are invoices sent", "When do I get billed", "What is the late fee"]:\n    best = max(range(N), key=lambda i: score(q, i))\n    print(q, "->", docs[best] if score(q, best) > 0 else "no match")'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-rag-evaluation"] = [
    ("p", "\"It seems to work\" is not a strategy. Teams that ship reliable RAG systems all share one habit: they <strong>measure</strong>. This lesson gives you the vocabulary and the tools: retrieval metrics you can compute in a few lines, a way to judge answer quality, a diagnosis flowchart for bad answers, and the advanced patterns (parent-child, GraphRAG, agentic RAG, caching) that senior engineers reach for after the basics work."),
    ("h2", "Step zero: build a golden dataset"),
    ("p", "Collect 50&ndash;200 realistic questions. For each, record the <em>correct answer</em> and <em>which document chunk(s) contain it</em>. Include tricky cases: paraphrased questions, multi-hop questions (needing two documents), questions with <strong>no</strong> answer in your data, and adversarial ones. Source them from real users, logs and support tickets, not just from your imagination. Every evaluation below runs against this set."),
    ("h2", "Retrieval metrics: did we fetch the right chunks?"),
    ("p", "Evaluate retrieval <em>separately</em> from generation. For each question you have a ranked list of retrieved chunk IDs and a set of truly relevant IDs:"),
    ("ul", [
        "<strong>Hit rate / Recall@k</strong>: what fraction of the relevant chunks appear in the top k? The most important metric for RAG: if the answer is not retrieved, the model cannot use it.",
        "<strong>Precision@k</strong>: what fraction of the top k are relevant? Low precision means noise in the prompt.",
        "<strong>MRR (Mean Reciprocal Rank)</strong>: average of <code>1 / rank of the first relevant result</code>. Rewards putting the right answer near the top.",
        "<strong>nDCG</strong>: rewards relevant results ranked high, with a smooth discount for lower positions; handles graded relevance.",
    ]),
] + py('''import math

def recall_at_k(retrieved, relevant, k):
    return len(set(retrieved[:k]) & relevant) / len(relevant)

def precision_at_k(retrieved, relevant, k):
    return len(set(retrieved[:k]) & relevant) / k

def reciprocal_rank(retrieved, relevant):
    for rank, doc in enumerate(retrieved, 1):
        if doc in relevant:
            return 1 / rank
    return 0.0

def ndcg_at_k(retrieved, relevant, k):
    dcg = sum(1 / math.log2(i + 2) for i, d in enumerate(retrieved[:k]) if d in relevant)
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / ideal

# Three test questions: what we retrieved (best first) vs what was truly relevant
tests = [
    (["c1", "c7", "c3", "c9", "c2"], {"c1"}),              # perfect: hit at rank 1
    (["c4", "c8", "c2", "c5", "c6"], {"c2"}),              # found, but at rank 3
    (["c9", "c8", "c7", "c6", "c5"], {"c1", "c2"}),        # missed completely
]

for name, fn in [("recall@3", lambda r, rel: recall_at_k(r, rel, 3)),
                 ("precision@3", lambda r, rel: precision_at_k(r, rel, 3)),
                 ("MRR", reciprocal_rank),
                 ("nDCG@5", lambda r, rel: ndcg_at_k(r, rel, 5))]:
    scores = [fn(r, rel) for r, rel in tests]
    print(f"{name:<12} per question {[round(s, 2) for s in scores]}   mean = {sum(scores)/len(scores):.2f}")''') + [
    ("p", "Read the output like a doctor: recall@3 of 0.5 means half the time the good chunk is not even in the top three. That tells you to fix <em>retrieval</em> (chunking, hybrid search, reranking), and no amount of prompt tuning will help."),
    ("h2", "Comparing retrieval strategies, the honest way"),
    ("p", "The whole point of these metrics is <em>A/B comparison</em>. Run the same golden set through vector-only, BM25-only, hybrid, and hybrid+rerank, and compare recall@5 and MRR. Change one thing at a time (chunk size, k, embedding model, reranker) and keep a results table. Here is the shape of a chunk-size experiment on a toy problem:"),
] + py('''import math, re
from collections import Counter

DOC = ("Refunds. Laptops can be returned within 30 days for a full refund. Opened software is not refundable. "
       "Shipping. Shipping is free on orders over 50 dollars. Express shipping takes two days. "
       "Warranty. Every laptop has a one year warranty. Batteries are covered for six months. "
       "Support. Support is open Monday to Friday. Error ERR-4471 means the payment gateway timed out.")

QUESTIONS = [   # (question, phrase that must appear in a retrieved chunk to count as a hit)
    ("how many days to return a laptop", "30 days"),
    ("is shipping free", "free on orders"),
    ("battery warranty length", "six months"),
    ("what is ERR-4471", "ERR-4471"),
]

tok = lambda t: re.findall(r"[a-z0-9-]+", t.lower())

def make_chunks(size):
    words = DOC.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]

def score(q, chunk, chunks):
    N = len(chunks); df = Counter(w for c in chunks for w in set(tok(c)))
    tf = Counter(tok(chunk)); s = 0
    for w in tok(q):
        if w in tf:
            s += math.log((N - df[w] + .5) / (df[w] + .5) + 1) * tf[w]
    return s

for size in (6, 12, 24, 48):
    chunks = make_chunks(size)
    hits = 0
    for q, needle in QUESTIONS:
        best = max(chunks, key=lambda c: score(q, c, chunks))
        hits += needle in best
    avg_words = sum(len(c.split()) for c in chunks) / len(chunks)
    print(f"chunk size {size:>2} words -> {len(chunks):>2} chunks, hit rate {hits}/{len(QUESTIONS)}")''') + [
    ("p", "On this toy text the 6- and 12-word chunks slice answers away from their keywords, while 24 words and up worked. On real documents the curve usually rises and then falls again as chunks grow, because huge chunks dilute the signal. The exact best size is a property of <em>your</em> documents and questions, which is why you measure instead of copying someone's default."),
    ("h2", "Generation metrics: is the answer good?"),
    ("ul", [
        "<strong>Faithfulness / groundedness</strong>: is every claim in the answer supported by the retrieved context? (Lesson 4.) The core anti-hallucination metric.",
        "<strong>Answer relevance</strong>: does it actually address the question?",
        "<strong>Correctness</strong>: does it match the reference answer?",
        "<strong>Context precision / recall</strong>: how much of the retrieved context was needed, and did it contain everything needed?",
        "<strong>Refusal accuracy</strong>: does it decline when the answer is not in the data, and only then?",
    ]),
    ("p", "Scoring these by hand does not scale, so teams use <strong>LLM-as-a-judge</strong>: a strong model reads (question, context, answer, reference) and returns scores against a rubric. It is imperfect (judges have biases: they favour longer answers and their own outputs), so <em>calibrate it against human labels</em> on a sample, and use pairwise comparison (\"which answer is better?\") where you can. Popular tooling: Ragas, DeepEval, TruLens, LangSmith, Braintrust and Arize Phoenix."),
    ("h2", "A diagnosis flowchart for a bad answer"),
    ("code", "text", "Bad answer\n  |\n  +-- Was the right chunk in the index at all?\n  |      NO  -> ingestion bug: parsing, missing file, stale data\n  |\n  +-- Was it in the top-k retrieved?\n  |      NO  -> retrieval problem: chunking, hybrid/BM25, embedding model, filters, query rewriting\n  |\n  +-- Was it in the prompt (after reranking / trimming)?\n  |      NO  -> reranking or context-budget problem\n  |\n  +-- Did the model use it correctly?\n         NO  -> generation problem: prompt, temperature, conflicting chunks, model too weak"),
    ("h2", "Advanced RAG patterns"),
    ("ul", [
        "<strong>Parent-child (small-to-big) retrieval</strong>: search over small chunks for precision, but return the surrounding parent section for context.",
        "<strong>Contextual chunks</strong>: prepend each chunk with a short LLM-written summary of where it sits in the document (\"This is from the 2024 refund policy, section 3\"), which improves both embedding and BM25 matching.",
        "<strong>Metadata and self-querying</strong>: let the LLM turn \"invoices from March over 500 dollars\" into filters.",
        "<strong>GraphRAG</strong>: extract entities and relationships into a knowledge graph, then answer \"how is X connected to Y?\" or summarise whole corpora, which flat chunk retrieval handles poorly.",
        "<strong>Agentic RAG</strong>: instead of one retrieval, an agent decides <em>whether</em> to search, <em>what</em> to search, inspects results, and searches again if unsatisfied. Great for multi-hop questions; costs more calls (see the agents lessons).",
        "<strong>Corrective / self-reflective RAG</strong>: grade the retrieved chunks; if poor, rewrite the query or fall back to web search; check the final answer against the sources.",
        "<strong>Semantic caching</strong>: if a new question is nearly identical (by embedding) to a previous one, return the cached answer, saving cost and latency.",
        "<strong>Multimodal RAG</strong>: index images, charts and tables (parse tables into structured text; use vision models for figures).",
    ]),
    ("h2", "A practical improvement order"),
    ("ul", [
        "<strong>1.</strong> Build the golden set and a baseline number before touching anything.",
        "<strong>2.</strong> Fix ingestion and parsing (garbage in, garbage out; check tables and PDFs).",
        "<strong>3.</strong> Add hybrid search (BM25 + vectors).",
        "<strong>4.</strong> Tune chunking, add overlap and metadata.",
        "<strong>5.</strong> Add a reranker.",
        "<strong>6.</strong> Improve the prompt and refusal behaviour.",
        "<strong>7.</strong> Only then consider fine-tuning an embedding model, agentic loops or GraphRAG, since each adds cost and complexity.",
    ]),
    ("exercise", "In the metrics demo, add a fourth test where two chunks are relevant and retrieval returns one of them at rank 2 and the other at rank 5. Compute recall@3 and recall@5 by hand first, then check with the code. Why can recall@5 be higher while MRR stays the same?"),
    ("solution", "python", 'def recall_at_k(r, rel, k):\n    return len(set(r[:k]) & rel) / len(rel)\n\ndef rr(r, rel):\n    for i, d in enumerate(r, 1):\n        if d in rel:\n            return 1 / i\n    return 0\n\nretrieved = ["c9", "c1", "c8", "c7", "c2"]\nrelevant = {"c1", "c2"}\nprint("recall@3 =", recall_at_k(retrieved, relevant, 3))\nprint("recall@5 =", recall_at_k(retrieved, relevant, 5))\nprint("MRR      =", rr(retrieved, relevant))   # only the FIRST hit (rank 2) counts'),
]
