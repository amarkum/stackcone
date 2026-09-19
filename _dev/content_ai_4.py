"""AI (Artificial Intelligence), part 4 — interview preparation, scenarios, coding rounds, glossary and roadmap."""
from extra_util import py
from content_ai_1 import M

META = [
    M("ai-interview-basics", "Interview Special I: LLM, Embeddings, RAG and Search Questions", 40, "Intermediate",
      "Forty-plus real interview questions with model answers on LLMs, prompting, embeddings, vector search, BM25, hybrid search and RAG.",
      ["Answer fundamentals questions crisply", "Explain trade-offs, not just definitions", "Avoid the classic wrong answers"]),
    M("ai-interview-advanced", "Interview Special II: Agents, System Design and Live Scenarios", 45, "Advanced",
      "Agent and harness questions, five system design walkthroughs, live debugging scenarios and coding-round exercises.",
      ["Design a RAG chatbot and an agent on a whiteboard", "Debug production scenarios out loud", "Solve the common coding-round tasks"]),
    M("ai-glossary-roadmap", "Glossary, Cheat Sheet and Learning Roadmap", 20, "Beginner",
      "Every term from the course in one place, a one-page cheat sheet, and a roadmap for what to learn and build next.",
      ["Recall the key vocabulary", "Use the cheat sheet as a quick reference", "Plan your next projects"]),
]

CONTENT = {}


def qa(q, a):
    return [("p", f"<strong>{q}</strong>"), ("p", a)]


def section(title, pairs):
    out = [("h2", title)]
    for q, a in pairs:
        out += qa(q, a)
    return out


# ---------------------------------------------------------------------------
CONTENT["ai-interview-basics"] = [
    ("p", "Welcome to the interview special. Everything you learned in this course is now converted into the questions interviewers actually ask, with the answer <em>shape</em> that impresses them. A general rule before we start: <strong>interviewers rarely want definitions, they want judgement.</strong> \"What is RAG?\" is a warm-up; \"your RAG bot is wrong 8% of the time, what do you do?\" is the real interview. Answer every question in three moves: <strong>define it in one sentence, give a concrete example, then state the trade-off or when it fails.</strong>"),
    ("note", "How to use this lesson", "Cover the answer, say yours out loud for 60 seconds, then compare. Speaking aloud matters: interviews test whether you can <em>explain</em>, not whether you can recognise. Questions are grouped by topic, roughly easy to hard within each group."),
] + section("Part A: LLM fundamentals", [
    ("1. What is an LLM and how does it work?",
     "A large language model is a neural network (almost always a transformer) trained on huge amounts of text to predict the next token. At inference it repeatedly produces a probability distribution over the next token, samples one, appends it, and repeats. Fluency comes from scale and training data. <em>Trade-off to mention:</em> it optimises plausibility, not truth, which is the root of hallucination."),
    ("2. What is a token and why does it matter?",
     "A token is a sub-word chunk the tokenizer produces (about 4 English characters, or 0.75 of a word). Tokens matter because they set <em>cost</em> (APIs bill per token), <em>limits</em> (the context window is measured in tokens) and <em>quirks</em> (letter counting and arithmetic are unreliable because the model never sees individual characters). Non-English text and code usually cost more tokens per word."),
    ("3. What is a context window? Is it the same as memory?",
     "It is the maximum tokens the model can attend to in one request, covering instructions, history, documents <em>and</em> the reply. It is not long-term memory: the model is stateless, and 'remembering' is the application re-sending history or stored notes. Long contexts cost money on every call, and models often use the middle of a long prompt less well ('lost in the middle')."),
    ("4. Explain temperature, top-k and top-p.",
     "They control how the next token is sampled from the model's probabilities. Temperature rescales the distribution: near 0 it is nearly deterministic (good for extraction, code and factual answers), higher values flatten it for variety. Top-k restricts choices to the k likeliest tokens; top-p keeps the smallest set whose probabilities sum to p, adapting to the model's confidence. I use low temperature for accuracy and moderate temperature plus top-p for creative tasks. Temperature 0 reduces randomness but is still not a guarantee of identical outputs across runs."),
    ("5. Pre-training vs fine-tuning vs RLHF?",
     "Pre-training learns language and world knowledge by next-token prediction on trillions of tokens. Fine-tuning (instruction tuning) trains further on curated examples so the model follows instructions. RLHF and similar preference methods (DPO, RLAIF) push it toward answers humans or judges prefer: helpful, honest, safe. Together they turn a base autocomplete model into an assistant."),
    ("6. When would you fine-tune instead of using RAG?",
     "Fine-tune to change <em>behaviour</em>: consistent tone, strict output format, domain style, or making a small model cheap and fast at one task. Use RAG for <em>knowledge</em>, especially facts that change, are private or need citations. Fine-tuning teaches style much better than facts, and facts go stale. Often the answer is both: RAG for facts, light tuning or prompting for behaviour."),
    ("7. What is a hallucination and why does it happen?",
     "A fluent, confident output that is false or unsupported. It happens because the model is trained to produce plausible continuations, not verified truth; rare or missing facts get filled with plausible guesses; models are tuned to be helpful rather than to abstain; and there is a training cut-off. Mitigations: ground answers in retrieved documents, allow 'I do not know', require citations, lower temperature, use tools for maths and lookups, verify with a second pass, and keep humans in the loop for high stakes."),
    ("8. How would you measure hallucination?",
     "Split into <em>factual</em> and <em>faithfulness</em> errors. For RAG the practical metric is faithfulness: is every claim in the answer supported by the retrieved context? Measure with an LLM-as-judge or NLI model over a golden set, including questions that have no answer in the data to test refusal accuracy. Calibrate the judge against human labels."),
    ("9. What is the difference between a base model, an instruct model and a reasoning model?",
     "A base model only continues text. An instruct/chat model is tuned to follow instructions in a conversation. A reasoning model additionally spends extra tokens 'thinking' before answering, trading latency and cost for better multi-step accuracy. Choose by task: simple extraction wants a small instruct model; hard multi-step problems may justify a reasoning model."),
    ("10. What are the main levers for reducing LLM cost and latency?",
     "Shrink the prompt (fewer, better chunks), cap output tokens, use prompt caching for repeated prefixes, cache answers semantically, route easy requests to a small model, stream so perceived latency drops, batch non-urgent work, and set budgets and alerts. Measure time-to-first-token and tokens per second separately."),
]) + section("Part B: Prompting and outputs", [
    ("11. What makes a good prompt?",
     "Clear task, relevant context, the desired output format (ideally with an example), explicit handling of uncertainty ('if not in the text, say so'), and delimiters that separate instructions from data. Iterate against an eval set, not by feel."),
    ("12. Few-shot vs zero-shot vs chain-of-thought?",
     "Zero-shot just asks. Few-shot includes examples, which teach format and style quickly. Chain-of-thought asks for step-by-step reasoning, helping on multi-step problems. Reasoning models do this internally, so explicit CoT prompting matters less on them."),
    ("13. How do you get reliable JSON from a model?",
     "Use structured outputs or a tool schema so the API constrains generation to your JSON Schema, otherwise JSON mode with a schema described in the prompt. Always validate on your side (pydantic/jsonschema), and on failure send the error back to the model for a retry. Keep schemas small and use enums."),
    ("14. What is prompt injection and how do you defend against it?",
     "Untrusted text (a web page, email, document) containing instructions the model may obey. There is no prompt-only fix. Defend architecturally: least-privilege tools, no single agent holding private data plus untrusted input plus an outbound channel, human approval for consequential actions, output and argument validation, sandboxing, audit logging and red-team testing. Pattern filters are a weak extra layer only."),
    ("15. What is a system prompt and can users see or override it?",
     "It is the standing instruction message that sets role, rules and format. Users can often coax it out, so never put secrets in it, and never rely on it alone for security; enforce important rules in code."),
]) + section("Part C: Embeddings and vector search", [
    ("16. What is an embedding?",
     "A vector of numbers, produced by a model, that represents the meaning of a piece of text (or image, audio, code) so that semantically similar inputs land near each other. It converts a fuzzy question (are these related?) into geometry (how close are these points?)."),
    ("17. Cosine similarity vs dot product vs Euclidean distance?",
     "Cosine is the angle between vectors and ignores magnitude, the default for text. Dot product is cosine times the lengths; for normalised vectors they are identical and the dot product is cheaper. Euclidean is straight-line distance and is affected by magnitude. Use whatever metric the embedding model was trained with, and normalise if it recommends it."),
    ("18. Why can't you mix embeddings from two different models?",
     "Each model defines its own coordinate space, so vectors from different models are not comparable. If you change the model (or major version), you must re-embed the whole corpus and the queries with the same model."),
    ("19. How do you choose an embedding model?",
     "Test on your own retrieval eval set rather than trusting leaderboards. Consider quality on your domain and language, dimensions (storage and speed), context length per input, cost or self-hosting needs, and licence. Also consider whether a truncatable (Matryoshka) model can cut storage."),
    ("20. What is chunking and how do you pick chunk size?",
     "Splitting documents into pieces that are embedded and retrieved individually, because one vector per long document is blurry. Typical starting point is 200 to 800 tokens with 10 to 20 percent overlap, splitting on structure (headings, paragraphs) rather than raw character counts. Tune by measuring retrieval recall on a golden set. Smaller chunks are precise but lose context; larger chunks keep context but dilute the vector and waste prompt space."),
    ("21. What is ANN search and why not exact search?",
     "Approximate nearest neighbour search uses an index (HNSW, IVF, PQ) to find very likely nearest vectors while examining a small fraction of the data. Exact search is O(n) per query, too slow at millions of vectors. You trade a little recall for orders of magnitude of speed, tuned via parameters like efSearch."),
    ("22. Explain HNSW in a few sentences.",
     "A multi-layer proximity graph. Upper layers are sparse 'highways' that let the search jump quickly across the space; lower layers are dense. Search enters at the top, greedily moves to the closest neighbour, drops a layer, and repeats, ending in the densest layer with a local best-first search. It is fast and accurate but memory-hungry."),
    ("23. How do you handle metadata filtering and access control in vector search?",
     "Store metadata (tenant, permissions, date, type) with each chunk and apply it in the query, ideally as an in-index filter rather than post-filtering, which can leave too few results. Enforce permissions at retrieval time; never retrieve text a user may not see and hope the model hides it."),
    ("24. When would you pick pgvector over a dedicated vector database?",
     "When you already run PostgreSQL, the corpus is up to a few million vectors, and you value transactions, SQL joins and one less system to operate. Move to a dedicated engine for very large scale, heavy filtering, multi-tenant isolation at scale or specialised features."),
]) + section("Part D: Keyword search, hybrid search and reranking", [
    ("25. What is BM25?",
     "A probabilistic keyword ranking function. It scores a document by summing, over query terms, an IDF weight (rare terms count more) times a saturating term-frequency factor, normalised by document length. Two parameters: k1 controls frequency saturation and b controls length normalisation. It is fast, needs no model, and excels at exact terms, names and identifiers."),
    ("26. TF-IDF versus BM25?",
     "Both weight terms by frequency and rarity. TF-IDF uses raw or log term frequency which keeps growing, and has no length normalisation by default. BM25 saturates term frequency (repeating a word 40 times is not 40 times better) and penalises long documents. BM25 usually ranks better."),
    ("27. Why does keyword search still matter when we have embeddings?",
     "Embeddings blur exact tokens: error codes, SKUs, names, legal citations and rare jargon. BM25 finds them precisely. Embeddings handle paraphrase and synonyms that BM25 misses. They fail in opposite ways, so combining them is stronger than either."),
    ("28. What is hybrid search and how do you combine the scores?",
     "Running keyword and vector retrieval and merging the results. Scores are on different scales, so the common method is Reciprocal Rank Fusion (sum of 1/(k+rank) across lists, k around 60), which uses ranks only. Alternatively normalise scores and take a weighted sum, which needs tuning."),
    ("29. Bi-encoder vs cross-encoder?",
     "A bi-encoder embeds query and document separately, so document vectors are precomputed and search is fast, but the two never interact. A cross-encoder reads query and document together and outputs a relevance score, which is more accurate but needs one model pass per pair, so it is used only on a shortlist. Standard pipeline: bi-encoder/hybrid retrieval for recall, cross-encoder reranking for precision."),
    ("30. What is query rewriting / multi-query / HyDE?",
     "Techniques that improve the query before retrieval. Rewriting turns a follow-up into a standalone question using chat history. Multi-query generates paraphrases and merges results. HyDE has the model write a hypothetical answer and searches with that, because answers resemble documents more than questions do. They cost an extra LLM call and can drift, so measure the gain."),
]) + section("Part E: RAG", [
    ("31. Explain RAG end to end.",
     "Offline: parse documents, chunk, embed, store in a vector index (plus BM25) with metadata. Online: take the question, optionally rewrite it, retrieve candidates with hybrid search, rerank to a handful, build a prompt with instructions and the retrieved context, have the LLM answer with citations (streaming), and optionally check faithfulness. The model stays frozen; knowledge lives in the index, so updates are just re-indexing."),
    ("32. RAG vs fine-tuning vs long context?",
     "RAG for changing, private or citable knowledge. Fine-tuning for behaviour and format. Long context for one or few documents where simplicity wins, but it costs tokens on every call, degrades in the middle and does not scale to a whole corpus. Frequently combined."),
    ("33. A RAG bot gives a wrong answer. How do you debug it?",
     "Locate the failing stage with logged intermediate data: (1) was the answer in the index at all (ingestion or parsing bug)? (2) was it in the top-k retrieved (chunking, embedding, missing BM25, filters, vague query)? (3) did it survive reranking and fit in the prompt? (4) if it was in the prompt, did the model use it (prompt, conflicting chunks, temperature)? Most failures are retrieval, so I inspect the retrieved chunks first."),
    ("34. How do you evaluate a RAG system?",
     "Build a golden set of 50 to 200 real questions with reference answers and the chunks that contain them, including unanswerable ones. Evaluate retrieval separately (recall@k, MRR, nDCG) and generation (faithfulness, relevance, correctness, refusal accuracy), using LLM-as-judge calibrated on human labels. Run it in CI and turn every production failure into a new test case."),
    ("35. What are recall@k and MRR?",
     "Recall@k is the fraction of relevant chunks that appear in the top k results, the key retrieval metric because a missing chunk cannot be used. MRR is the mean of 1/rank of the first relevant result, rewarding putting the right chunk near the top."),
    ("36. How do you make RAG answer 'I don't know' instead of guessing?",
     "Prompt: answer only from the context, otherwise reply with a fixed refusal phrase. Add a retrieval-confidence threshold (if top scores are low, refuse before calling the model), require citations, evaluate refusal accuracy on unanswerable questions, and monitor for 'confident but unsupported' answers."),
    ("37. What are parent-child retrieval and contextual chunking?",
     "Parent-child indexes small chunks for precise matching but returns the larger parent section to the model for context. Contextual chunking prepends each chunk with a short generated description of where it sits in the document, improving both embedding and keyword matching."),
    ("38. What is GraphRAG and when is it useful?",
     "It builds a knowledge graph of entities and relations (and community summaries) from the corpus and retrieves over the graph. It helps with multi-hop, relationship and 'summarise the whole corpus' questions that flat chunk retrieval handles poorly, at higher ingestion cost and complexity."),
    ("39. How do you handle tables, PDFs and images in RAG?",
     "Parsing quality often decides success. Use layout-aware parsers to keep tables as structured text (Markdown/CSV) rather than scrambled lines, extract headings for metadata, OCR scans, and use vision models to describe charts and figures. Verify by reading the parsed output, not the PDF."),
    ("40. How do you keep a RAG index fresh?",
     "Incremental ingestion driven by change events or hashes, upserting new or changed chunks and deleting stale ones by document ID, with embedding-model version tracked so a model change triggers a full re-embed. Store timestamps so retrieval can prefer newer content."),
    ("41. How do you secure a multi-tenant RAG system?",
     "Filter by tenant and user permissions in the retrieval query, isolate indexes or namespaces for strict tenants, never rely on the prompt to hide data, sanitise logs, treat retrieved text as untrusted (indirect prompt injection), and test cross-tenant leakage explicitly."),
]) + [
    ("h2", "Warm-up coding question: cosine similarity"),
    ("p", "Interviewers love this one because it has edge cases. Write cosine similarity, handle the zero vector, and explain what the answer means."),
] + py('''import math

def cosine(a, b):
    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:          # the edge case interviewers look for
        return 0.0
    return dot / (na * nb)

print(cosine([1, 0], [1, 0]))    # same direction  -> 1.0
print(cosine([1, 0], [0, 1]))    # unrelated       -> 0.0
print(cosine([1, 0], [-1, 0]))   # opposite        -> -1.0
print(cosine([0, 0], [1, 1]))    # zero vector     -> 0.0 (not a crash)''') + [
    ("exercise", "Explain in 60 seconds, out loud, how you would decide between fixing retrieval and fixing the prompt for a RAG bot. Then implement <code>recall_at_k(retrieved, relevant, k)</code> without looking at the earlier lesson."),
    ("solution", "python", 'def recall_at_k(retrieved, relevant, k):\n    if not relevant:\n        return 0.0\n    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)\n\nprint(recall_at_k(["a", "b", "c"], ["b", "z"], 3))   # 0.5'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-interview-advanced"] = [
    ("p", "Part II is where offers are won. It covers agents and harnesses, five full <strong>system design</strong> walkthroughs, <strong>live debugging scenarios</strong> (the 'real-time questions' interviewers throw at you), and the <strong>coding tasks</strong> that come up most. For system design, use this skeleton every time: <strong>clarify requirements, sketch the pipeline, dive into the risky parts, then cover evaluation, cost, latency and security.</strong> Saying the structure out loud is itself a signal of seniority."),
] + section("Part A: Agents, tools and harnesses", [
    ("1. What is an agent? How is it different from a workflow?",
     "An agent is an LLM that decides its own next steps in a loop, using tools, until a goal is met. A workflow is LLM calls orchestrated by predefined code paths. Workflows are predictable and cheap; agents are flexible for open-ended tasks but slower, costlier and harder to control. I default to the simplest thing that works and add autonomy only where the steps genuinely cannot be listed in advance."),
    ("2. Describe the ReAct loop.",
     "Reason, act, observe. The model emits a short thought and a tool call, the harness executes it and appends the observation, and the model continues until it produces a final answer or hits a limit. The loop plus tool feedback is what lets an agent correct itself."),
    ("3. How does tool calling work, and who executes the tool?",
     "You describe tools with a name, description and JSON Schema. The model returns a structured request to call one. Your application executes it (never the model), appends the result as a tool message, and calls the model again. Because your code is in the middle, it is where you validate arguments, enforce permissions and log."),
    ("4. What is an agent harness?",
     "Everything around the model that makes it an agent: the loop, tool registry and execution, context management (trimming, compaction, retrieval), memory, permissions and approvals, budgets and limits, streaming, and tracing. The same model behaves very differently in different harnesses, so quality is largely harness design."),
    ("5. What is context engineering?",
     "Deciding exactly what the model sees each turn. Techniques: stable prefix for prompt caching, trimming and summarising tool outputs, compaction of old turns, just-in-time retrieval via search tools instead of preloading, scratchpad files, and delegating messy subtasks to sub-agents that return short results."),
    ("6. How do you stop an agent from looping or running away?",
     "Hard step limit, token and dollar budgets, wall-clock timeouts, loop detection on repeated identical calls, a cancellation path, and clear stop conditions. Also design tools to return actionable errors so the model can change strategy instead of repeating."),
    ("7. Why do multi-step agents fail so often?",
     "Errors compound: 95 percent per-step reliability is about 60 percent over ten steps and 36 percent over twenty. Plus context bloat, wrong tool choice, and prompt injection. Mitigate with short loops, verification steps, checkpoints, human approval on risky actions, and evals over full trajectories."),
    ("8. When would you use multiple agents?",
     "When subtasks are parallelisable or need different tools, models or contexts: orchestrator-worker for broad research or repo-wide coding, handoffs for routing between specialised agents. Not by default: it multiplies cost and coordination complexity."),
    ("9. What is MCP and why does it exist?",
     "The Model Context Protocol is an open JSON-RPC standard for connecting AI apps (clients) to tool and data servers, so an integration written once works in any MCP-capable app. Servers expose tools, resources and prompts. It solves the N-apps times M-integrations problem. Security still matters: a connected server is a capability and a trust boundary."),
    ("10. Explain the 'lethal trifecta'.",
     "An agent that combines access to private data, exposure to untrusted content and the ability to communicate externally can be tricked by prompt injection into exfiltrating that data. Removing any one of the three breaks the attack, so I split privileges across separate agents and never give one agent all three."),
    ("11. LangGraph vs a plain while-loop?",
     "A while-loop is fine for a simple agent. LangGraph models control flow as an explicit graph with shared state, conditional edges and checkpointing, which pays off with branching, retries, human approval pauses, resumable or long-running work, parallel branches and multi-agent composition, and it makes each step inspectable and testable."),
    ("12. LlamaIndex vs LangChain?",
     "LlamaIndex is data-first: loaders, parsing, chunking, indexes, retrievers and query engines for RAG over varied sources. LangChain is a broad toolkit of model, prompt, parser, retriever and tool abstractions, with LangGraph for agents. They overlap, and many teams use pieces of each or neither."),
    ("13. How would you evaluate an agent?",
     "Build tasks with verifiable outcomes and grade end state (did the tests pass, was the ticket resolved) plus trajectory quality (unnecessary steps, dangerous calls, cost, latency). Run each task multiple times because behaviour is stochastic, track pass rate and variance, and add every real failure as a new task."),
    ("14. How do you make an agent safe to deploy?",
     "Least-privilege scoped tools, sandboxed execution, human approval for irreversible or external actions, input and output validation, prompt-injection testing, full audit logs, budgets and rate limits, and a kill switch."),
]) + [
    ("h2", "Part B: System design walkthroughs"),
    ("p", "<strong>Design 1: A customer-support RAG chatbot for 10 million documents.</strong> Start with requirements: who are the users, latency target (say time-to-first-token under 1.5 seconds), accuracy and citation needs, multi-tenancy, languages, freshness. Then the pipeline:"),
    ("ul", [
        "<strong>Ingestion</strong>: connectors, layout-aware parsing, dedupe, structure-based chunking (300 to 500 tokens, overlap), metadata (tenant, ACL, doc type, timestamps), embeddings plus a BM25 index. Incremental updates by content hash; deletions propagate.",
        "<strong>Storage</strong>: vector DB with HNSW and in-index metadata filters (10M chunks at 1,024 dims is roughly 40 GB raw, so consider quantisation), plus the text store and keyword index.",
        "<strong>Query path</strong>: auth, rate limit, query rewrite with history, hybrid retrieval (top 50), cross-encoder rerank (top 5), prompt assembly with citations, streamed generation over SSE, semantic cache in front.",
        "<strong>Safety</strong>: ACL filtering at retrieval, retrieved text treated as untrusted, PII redaction in logs, refusal when retrieval confidence is low.",
        "<strong>Quality</strong>: golden set in CI, online feedback, faithfulness judge on a sample, weekly failure review.",
        "<strong>Cost and latency</strong>: prompt caching, small model for rewrite and routing, larger model for hard questions, budget alerts.",
    ]),
    ("p", "<strong>Design 2: A coding agent that fixes failing tests.</strong> Tools: read file, search, edit, run tests (sandboxed). Loop with a step and token budget. Success signal is the test suite, which is what makes this a good agent problem. Context engineering: repo map, just-in-time file reads, trimmed test output. Safety: container sandbox, no network, allow-listed commands, changes proposed as a diff for review. Evaluate on a held-out set of real failing-test tasks and measure pass rate, cost and steps."),
    ("p", "<strong>Design 3: Real-time voice assistant.</strong> Requirements: sub-second turn latency and interruptibility. Two-way audio needs WebRTC or WebSockets, not SSE. Pipeline: streaming speech-to-text, LLM streaming tokens, streaming text-to-speech, with voice-activity detection to allow barge-in (cancel generation when the user speaks). Discuss latency budget per stage, and what to do on dropped connections."),
    ("p", "<strong>Design 4: 'Chat with your documents' for one user, 200 pages.</strong> Do not over-engineer. For one document, long-context with prompt caching may beat RAG on simplicity and quality; use RAG when the corpus exceeds context, cost matters, or you need citations at scale. Showing you can choose the <em>simpler</em> design is a strong signal."),
    ("p", "<strong>Design 5: An AI support triage system (classification plus actions).</strong> This is a workflow, not an agent: classify (small model, structured output), route, look up order data via read-only tools, draft a reply, and require human approval before refunds above a threshold. Discuss evaluation with a labelled ticket set and monitoring for drift."),
    ("h2", "Part C: Live scenarios, the 'real-time questions'"),
    ("p", "Interviewers give you a situation and watch how you reason. Talk through: <strong>measure, hypothesise, isolate, fix, verify.</strong>"),
] + section("Scenarios", [
    ("Scenario 1. 'Our RAG bot is wrong on about 8% of questions.'",
     "First I would not touch the prompt. I would pull a sample of failing questions and, for each, read the retrieved chunks. That splits failures into: not indexed or badly parsed, not retrieved (chunking, no keyword matching for IDs, vague query), retrieved but ignored (prompt or conflicting context) or genuinely unanswerable (should have refused). I would compute recall@k on a labelled set to confirm retrieval is the main problem, then apply the fix for the biggest bucket, usually hybrid search, better chunking and a reranker, and re-measure."),
    ("Scenario 2. 'Responses take 12 seconds. Fix it.'",
     "Break latency into spans with tracing: retrieval, rerank, time to first token, generation. Then act on the largest: stream tokens so users see output in under a second; cache or shrink the prompt and use prompt caching to cut time-to-first-token; parallelise independent steps (retrieval and query rewriting where possible); use a smaller model for rewrite and routing; cap output length; run reranking on fewer candidates. Report time-to-first-token and total time separately."),
    ("Scenario 3. 'The bill is 10 times what we forecast.'",
     "Look at cost per request by feature and by prompt length. Common culprits: ever-growing conversation history re-sent each turn, too many retrieved chunks, an agent looping, retries without backoff, and everything going to the biggest model. Fixes: compaction and history summarisation, fewer chunks after reranking, step and budget limits, prompt and semantic caching, model routing, output caps, and per-user budgets with alerts."),
    ("Scenario 4. 'A user saw another customer's document in an answer.'",
     "Treat as a security incident. Contain (disable the path if needed), then find the root cause: almost certainly retrieval without a tenant or permission filter, a shared cache key ignoring the tenant, or logs and embeddings mixing tenants. Fix by enforcing filters inside the vector query, namespacing caches by tenant, adding automated cross-tenant leakage tests, and reviewing what else shares the same index."),
    ("Scenario 5. 'The agent keeps repeating the same failing tool call.'",
     "Add loop detection and a step limit, return richer tool errors that suggest alternatives, add a reflection step ('what have you tried, what will you change?') and escalate to a human after N failures. Examine the tool description: unclear tool docs are a frequent cause."),
    ("Scenario 6. 'Quality dropped after the model provider updated their model.'",
     "That is why we pin model versions and keep an eval suite. Run the eval on old versus new, find which categories regressed, adjust prompts, and roll forward only when scores are back. Alert on eval scores and on production quality proxies like thumbs-down rate."),
    ("Scenario 7. 'The model ignores an instruction in the middle of a long prompt.'",
     "Long context degrades in the middle. Shorten the context by retrieving fewer, better chunks, move critical instructions to the start and repeat key ones at the end, structure the prompt with clear sections, and test whether a smaller prompt reproduces the behaviour."),
    ("Scenario 8. 'Search cannot find product code XJ-4471 but finds everything else.'",
     "Embeddings blur exact identifiers. Add BM25 or keyword search and fuse with RRF (hybrid), keep the code as its own token (do not split on hyphens during tokenisation), and consider a metadata or exact-match lookup path for identifiers."),
]) + [
    ("h2", "Part D: The coding round"),
    ("p", "Typical tasks: implement cosine similarity and top-k retrieval, write RRF, chunk text with overlap, build BM25, implement a retry with backoff, parse an SSE stream, or write a tool-call loop. You have practised most of them in this course. Here are two more, with the traps interviewers look for."),
    ("p", "<strong>Task: chunk text with overlap.</strong> Edge cases: overlap greater than or equal to chunk size (infinite loop), empty text, last short chunk."),
] + py('''def chunk_words(text, size, overlap):
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and < size")   # else the window never advances
    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, max(len(words), 1), step):
        piece = words[start:start + size]
        if piece:
            chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks

text = "one two three four five six seven eight nine ten"
for c in chunk_words(text, size=4, overlap=1):
    print("|", c)
print(chunk_words("", 4, 1))''') + [
    ("p", "<strong>Task: efficient top-k.</strong> Do not sort everything when you only need the best k. A heap does it in O(n log k):"),
] + py('''import heapq

def top_k(scored_items, k):
    """scored_items: iterable of (score, item). Returns the k best, highest score first."""
    return heapq.nlargest(k, scored_items)

docs = [(0.31, "shipping"), (0.92, "refunds"), (0.55, "warranty"), (0.87, "returns"), (0.12, "careers")]
print(top_k(docs, 2))''') + [
    ("h2", "Behavioural questions specific to AI roles"),
    ("ul", [
        "<strong>\"Tell me about a time an AI system failed in production.\"</strong> Use the structure: what happened, how you detected it, root cause, fix, and the eval or guardrail you added so it cannot recur.",
        "<strong>\"How do you decide whether AI is the right solution?\"</strong> Clear success metric, tolerance for errors, a non-AI baseline to beat, and a human fallback. Sometimes a rule or a SQL query wins.",
        "<strong>\"How do you keep up with this field?\"</strong> Read primary sources (model cards, provider changelogs, key papers), rebuild things from scratch to understand them, and keep a personal eval set to test new models on your own tasks.",
        "<strong>\"How do you explain hallucinations to a non-technical stakeholder?\"</strong> It is a very well-read autocomplete that always answers confidently. We reduce it by giving it the documents to read and telling it to admit when the answer is not there, and we measure how often it still goes wrong.",
    ]),
    ("h2", "Red-flag answers to avoid"),
    ("ul", [
        "\"Just fine-tune it on our data\" as the answer to a knowledge problem.",
        "\"Set temperature to 0 and it will not hallucinate.\"",
        "\"Use the biggest model for everything.\"",
        "Proposing an autonomous agent for a task a fixed workflow handles.",
        "No mention of evaluation, cost, latency or security. Always bring these up unprompted.",
        "Trusting the model to enforce permissions or hide data.",
    ]),
    ("exercise", "Pick one of the five system designs and present it out loud in five minutes to a friend (or a mirror), using the skeleton: requirements, pipeline, risky parts, evaluation, cost, latency, security. Record yourself and count how many times you mention a <em>trade-off</em>. Aim for at least five."),
    ("solution", "python", 'def recall_at_k(retrieved, relevant, k):\n    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)\n\ndef rrf(rankings, k=60):\n    from collections import defaultdict\n    s = defaultdict(float)\n    for r in rankings:\n        for i, d in enumerate(r, 1):\n            s[d] += 1 / (k + i)\n    return [d for d, _ in sorted(s.items(), key=lambda kv: -kv[1])]\n\nprint(rrf([["a", "b", "c"], ["b", "c", "a"]]))\nprint(recall_at_k(["a", "b", "c"], ["c"], 2))'),
]

# ---------------------------------------------------------------------------
CONTENT["ai-glossary-roadmap"] = [
    ("p", "You made it to the last lesson. Here is everything in one place: a glossary you can search with Ctrl+F, a one-page cheat sheet of the numbers and rules of thumb worth memorising, and a practical roadmap for what to build next. Bookmark this page."),
    ("h2", "Glossary, A to Z"),
    ("ul", [
        "<strong>Agent</strong>: an LLM that chooses its own next steps in a loop, using tools, until a goal is met.",
        "<strong>Agentic RAG</strong>: retrieval driven by an agent that decides when and what to search and can search again.",
        "<strong>ANN (approximate nearest neighbour)</strong>: fast vector search that trades a little recall for big speedups (HNSW, IVF).",
        "<strong>API key</strong>: a secret credential identifying and billing you; keep it server-side.",
        "<strong>Attention</strong>: the transformer mechanism that lets each token weigh every other token in the context.",
        "<strong>Backoff</strong>: waiting longer between retries (usually exponentially, with jitter).",
        "<strong>Base model</strong>: a pre-trained model that only continues text and does not yet follow instructions.",
        "<strong>Bi-encoder</strong>: encodes query and document separately; fast, used for retrieval.",
        "<strong>BM25</strong>: a keyword ranking function using rarity (IDF), saturating term frequency and length normalisation.",
        "<strong>Chain of thought</strong>: prompting or training a model to reason step by step before answering.",
        "<strong>Checkpointing</strong>: saving agent state after each step so runs can pause, resume and replay.",
        "<strong>Chunking</strong>: splitting documents into pieces to embed and retrieve.",
        "<strong>Context engineering</strong>: deciding what the model sees on each turn.",
        "<strong>Context window</strong>: the maximum tokens a model can consider in one request.",
        "<strong>Cosine similarity</strong>: the cosine of the angle between two vectors; the standard text-similarity measure.",
        "<strong>Cross-encoder</strong>: reads query and document together to score relevance; slower and more accurate; used for reranking.",
        "<strong>Embedding</strong>: a vector representing the meaning of text (or other data).",
        "<strong>Eval</strong>: a repeatable test that scores AI outputs against expectations.",
        "<strong>Few-shot</strong>: putting examples of the task in the prompt.",
        "<strong>Fine-tuning</strong>: further training a model on curated examples to change its behaviour.",
        "<strong>Function calling / tool calling</strong>: the model requests that your code run a described function and gets the result back.",
        "<strong>Grounding</strong>: tying answers to supplied source documents.",
        "<strong>GraphRAG</strong>: RAG over a knowledge graph of entities and relations.",
        "<strong>Guardrails</strong>: checks and constraints on inputs, outputs and actions.",
        "<strong>Hallucination</strong>: a fluent but false or unsupported output.",
        "<strong>Harness</strong>: the code around a model (loop, tools, context, memory, permissions, limits) that makes it an agent.",
        "<strong>HNSW</strong>: a layered proximity-graph index for ANN search.",
        "<strong>HyDE</strong>: retrieving with a hypothetical answer generated by the LLM instead of the raw question.",
        "<strong>Hybrid search</strong>: combining keyword (BM25) and vector search.",
        "<strong>Inference</strong>: running a trained model to produce output.",
        "<strong>Inverted index</strong>: a map from each term to the documents containing it.",
        "<strong>JSON Schema</strong>: a standard way to describe the shape of JSON, used for tool parameters and structured output.",
        "<strong>KV cache</strong>: stored attention keys and values that make generation and prompt caching faster.",
        "<strong>Latency</strong>: delay; measured as time to first token and total time.",
        "<strong>LLM</strong>: large language model, a neural network trained to predict the next token.",
        "<strong>LLM-as-judge</strong>: using a model to grade another model's output.",
        "<strong>LoRA</strong>: a parameter-efficient fine-tuning method.",
        "<strong>MCP</strong>: Model Context Protocol, an open standard for connecting AI apps to tools and data.",
        "<strong>Memory</strong>: information stored outside the model and re-inserted into context.",
        "<strong>Metadata filtering</strong>: restricting search to chunks matching attributes such as tenant or date.",
        "<strong>MRR</strong>: mean reciprocal rank, a retrieval metric.",
        "<strong>Multimodal</strong>: handling more than one type of data (text, images, audio).",
        "<strong>nDCG</strong>: a retrieval metric that rewards relevant results ranked higher.",
        "<strong>Orchestrator-worker</strong>: a lead agent delegating subtasks to worker agents.",
        "<strong>Parameters</strong>: the learned numbers inside a model.",
        "<strong>Pre-training</strong>: the first, large-scale next-token training stage.",
        "<strong>Prompt</strong>: the input text (and messages) sent to a model.",
        "<strong>Prompt caching</strong>: discounted, faster processing of a repeated prompt prefix.",
        "<strong>Prompt injection</strong>: malicious instructions hidden in text the model reads.",
        "<strong>RAG</strong>: retrieval-augmented generation; fetch relevant documents, then generate from them.",
        "<strong>ReAct</strong>: reason, act, observe; the classic agent loop.",
        "<strong>Recall@k</strong>: the fraction of relevant items found in the top k results.",
        "<strong>Reranking</strong>: a second, more precise scoring pass over retrieval candidates.",
        "<strong>RLHF</strong>: reinforcement learning from human feedback; aligns model behaviour with preferences.",
        "<strong>RRF</strong>: reciprocal rank fusion; merges ranked lists using ranks only.",
        "<strong>Sampling</strong>: choosing the next token from the model's probabilities.",
        "<strong>Semantic cache</strong>: reusing answers for near-identical questions found by embedding similarity.",
        "<strong>SSE</strong>: server-sent events; one-way streaming from server to client over HTTP.",
        "<strong>Streaming</strong>: sending output as it is generated instead of all at once.",
        "<strong>Structured output</strong>: model output constrained to a schema.",
        "<strong>System prompt</strong>: standing instructions setting role and rules.",
        "<strong>Temperature</strong>: a knob controlling randomness in sampling.",
        "<strong>Token</strong>: the sub-word unit models read and write.",
        "<strong>Tool</strong>: a function the model can ask your code to run.",
        "<strong>Top-k / top-p</strong>: sampling filters that limit which tokens are considered.",
        "<strong>Transformer</strong>: the neural architecture behind modern LLMs.",
        "<strong>Vector</strong>: a list of numbers; a point in a high-dimensional space.",
        "<strong>Vector database</strong>: a store that indexes vectors for fast similarity search with metadata.",
        "<strong>WebSocket</strong>: a persistent two-way connection between client and server.",
        "<strong>Zero-shot</strong>: asking a model to do a task with no examples.",
    ]),
    ("h2", "The one-page cheat sheet"),
    ("p", "<strong>Numbers to remember</strong>"),
    ("ul", [
        "1 token is about 4 English characters, or 0.75 words. A page of text is roughly 500 to 700 tokens.",
        "Output tokens usually cost 3 to 5 times input tokens.",
        "Chunk size: start at 200 to 800 tokens with 10 to 20 percent overlap.",
        "Retrieve 30 to 100 candidates, rerank, keep 3 to 8 for the prompt.",
        "RRF constant k is about 60. BM25 defaults: k1 between 1.2 and 2.0, b about 0.75.",
        "Typical embedding sizes: 384, 768, 1024, 1536, 3072.",
        "Per-step reliability compounds: 0.95 over 10 steps is 0.60.",
        "Golden eval set: 50 to 200 real questions, including unanswerable ones.",
    ]),
    ("p", "<strong>Rules of thumb</strong>"),
    ("ul", [
        "Simplest thing that works: prompt, then workflow, then agent.",
        "Debug retrieval before the prompt; log the retrieved chunks with every answer.",
        "Hybrid search plus reranking beats either alone on messy data.",
        "RAG for knowledge, fine-tuning for behaviour.",
        "Temperature near 0 for facts, code and extraction.",
        "Validate every tool argument; enforce permissions in code, not in prompts.",
        "Stream tokens; use SSE for one-way, WebSockets or WebRTC for two-way and voice.",
        "Never give one agent private data, untrusted content and an outbound channel together.",
        "Measure first: evals, tracing, cost per request.",
    ]),
    ("p", "<strong>Which tool for which job?</strong>"),
    ("ul", [
        "Exact terms, IDs, error codes: BM25 / keyword.",
        "Paraphrase and meaning: embeddings.",
        "Both: hybrid with RRF, then a cross-encoder rerank.",
        "One-way token streaming: SSE. Interactive, two-way, binary: WebSocket / WebRTC.",
        "Knowledge that changes: RAG. Style and format: fine-tune or prompt.",
        "Fixed steps: workflow. Unknown steps with verifiable results: agent.",
        "Branching, approvals, resumable runs: LangGraph-style graph.",
        "Messy multi-source documents: LlamaIndex-style ingestion, plus good parsing.",
        "Plugging tools into many apps: MCP.",
    ]),
    ("h2", "A roadmap: what to build next"),
    ("p", "You learn this field by building, in order of increasing difficulty. Each project below reuses a chunk of this course:"),
    ("ul", [
        "<strong>Project 1: A prompt playground (1 weekend).</strong> A small web page that calls a model API with a system prompt, streams the reply over SSE, and lets you change temperature. Teaches APIs, streaming and sampling.",
        "<strong>Project 2: Chat with a PDF (1 to 2 weeks).</strong> Parse, chunk, embed, store, retrieve, answer with citations. Add a refusal path. Teaches embeddings, chunking and RAG.",
        "<strong>Project 3: Make Project 2 good (2 weeks).</strong> Build a 50-question golden set, measure recall@5, add BM25 and RRF, add a reranker, and watch the numbers move. This is the most valuable project on the list, because it teaches evaluation.",
        "<strong>Project 4: A tool-using assistant (1 to 2 weeks).</strong> Give it 3 tools (search, calculator, one real API), add step limits, validation and a human approval gate. Teaches tool calling and harness design.",
        "<strong>Project 5: A LangGraph workflow with human approval (2 weeks).</strong> Something like a support-triage flow with a pause before refunds. Teaches state, checkpoints and interrupts.",
        "<strong>Project 6: Production hardening (ongoing).</strong> Add tracing, an eval suite in CI, caching, budgets, prompt-injection tests and cost dashboards.",
    ]),
    ("h2", "How to keep learning"),
    ("ul", [
        "<strong>Read primary sources</strong>: provider docs and changelogs, model cards, and a few key papers (Attention Is All You Need, RAG, ReAct, BM25 background).",
        "<strong>Rebuild from scratch</strong> whatever you use through a framework, at least once. That is how the ideas stick.",
        "<strong>Keep a personal eval set</strong> of your own hard questions and re-run it whenever a new model ships.",
        "<strong>Ship small things and get feedback</strong>. Real users find failures no benchmark will.",
        "<strong>Be sceptical</strong>: benchmark claims and demos are marketing until you test them on your data.",
    ]),
    ("h2", "Where to go next on this site"),
    ("ul", [
        "<a href=\"/learn/frameworks/langchain/introduction/\">LangChain course</a> for hands-on chains, retrieval and agents in code.",
        "<a href=\"/learn/frameworks/fastapi/introduction/\">FastAPI course</a> to build the API and SSE layer behind an AI product.",
        "<a href=\"/learn/programming/python/hello-world/\">Python</a>, <a href=\"/learn/programming/sql/introduction/\">SQL</a> and <a href=\"/learn/ds-algo/sysdesign/fundamentals/\">System Design</a> to strengthen the fundamentals every AI engineer leans on.",
        "<a href=\"/blog/posts/how-to-build-a-production-rag-chatbot/\">Build a RAG Chatbot in Python</a> for a long-form, production-oriented walkthrough.",
    ]),
    ("note", "You now know the whole stack", "LLMs and tokens, prompts and sampling, hallucinations, APIs and streaming, embeddings and vectors, chunking and vector databases, BM25, hybrid search and reranking, RAG and its evaluation, tool calling, agents, harnesses, LangGraph and LlamaIndex, MCP, safety, and production. That is the complete map. The rest is practice."),
    ("exercise", "Write your own one-page cheat sheet from memory, without looking, for the five topics you feel least sure about. Then compare it to the one above and fill the gaps. The gaps show you what to revisit."),
    ("solution", "python", '# A tiny self-quiz you can extend: term -> one-line meaning\nglossary = {\n    "RAG": "retrieve documents, then generate an answer from them",\n    "BM25": "keyword ranking using rarity and saturating frequency",\n    "RRF": "merge ranked lists using ranks only",\n    "SSE": "one-way streaming over HTTP",\n}\nimport random\nrng = random.Random(1)\nterm = rng.choice(sorted(glossary))\nprint("Define:", term)\nprint("Answer:", glossary[term])'),
]
