"""LangChain lessons 6-15."""
from content_js_sql import M

META = [
    M("langchain-memory", "langchain", "Chat Memory", 15, "Beginner", "Thread a conversation through message history without stuffing the entire past into every call.", ["Keep a message list", "Trim old turns", "Store history outside the process"]),
    M("langchain-document-loaders", "langchain", "Loaders and Splitters", 16, "Intermediate", "Load PDFs and web pages, then split them so retrieval stays accurate.", ["Load a document", "Choose a splitter", "Inspect chunk overlap"]),
    M("langchain-vector-stores", "langchain", "Vector Stores", 16, "Intermediate", "FAISS, Chroma and hosted indexes: persist embeddings and query them.", ["Index chunks", "Similarity search", "Add metadata filters"]),
    M("langchain-lcel", "langchain", "LCEL in Depth", 16, "Intermediate", "Runnables, parallel branches, retries and how the pipe operator actually works.", ["Pipe runnables", "Use RunnableParallel", "Add a retry"]),
    M("langchain-streaming", "langchain", "Streaming and Callbacks", 14, "Intermediate", "Stream tokens to a client and hook callbacks for logging and tokens used.", ["Stream a chain", "Count tokens", "Log each step"]),
    M("langchain-structured-output", "langchain", "Structured Output and Tool Calling", 16, "Intermediate", "Force JSON that matches a Pydantic model and bind tools the model can call.", ["with_structured_output", "Bind a tool", "Parse a tool call"]),
    M("langchain-langgraph", "langchain", "LangGraph Basics", 18, "Advanced", "State graphs, cycles, conditional edges and checkpointing a long-running agent.", ["Define state", "Add a cycle", "Checkpoint a thread"]),
    M("langchain-multi-agent", "langchain", "Multi-Agent Patterns", 16, "Advanced", "Supervisor, handoff and router patterns — and when one agent is enough.", ["Route to a specialist", "Handoff state", "Bound the loop"]),
    M("langchain-langsmith", "langchain", "LangSmith Tracing and Evals", 16, "Advanced", "Trace every run, build a dataset and score answers with evaluators.", ["Enable tracing", "Log a dataset", "Run an evaluator"]),
    M("langchain-production-rag", "langchain", "A Production RAG Service", 18, "Advanced", "Put retrieval behind an API with citations, limits, caching and a fallback.", ["Cite sources", "Cap tokens", "Fail closed on empty retrieval"]),
]

CONTENT = {}

CONTENT["langchain-memory"] = [
    ("p", "A chat model is stateless. If you want a conversation, <em>you</em> send the previous messages each turn. Memory is just that list, stored somewhere durable, then trimmed so it fits the context window."),
    ("h2", "The message list"),
    ("code", "python", 'from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages\n\nhistory = [\n    SystemMessage("You are a concise assistant."),\n    HumanMessage("My name is Ada"),\n    AIMessage("Hi Ada."),\n]\n\ndef reply(user: str) -> str:\n    history.append(HumanMessage(user))\n    window = trim_messages(history, max_tokens=2000, strategy="last", token_counter=len)\n    ai = model.invoke(window)\n    history.append(ai)\n    return ai.content'),
    ("h2", "Store it outside RAM"),
    ("p", "A Python list dies with the process. Write messages to Redis, Postgres or LangGraph's checkpointer, keyed by a <code>thread_id</code> you put on the session cookie or API header."),
    ("code", "python", '# sketch: load, append, save\nrows = db.load_messages(thread_id)\nrows.append({"role": "user", "content": text})\nanswer = model.invoke(to_messages(rows))\nrows.append({"role": "assistant", "content": answer.content})\ndb.save_messages(thread_id, rows)'),
    ("note", "Summarise, do not drop everything", "When the window is full, summarise older turns into one system note instead of deleting them. The user said their name on turn 1 for a reason."),
    ("exercise", "Keep an in-memory list for a two-turn chat and trim it to the last four messages before each call."),
]

CONTENT["langchain-document-loaders"] = [
    ("p", "RAG quality is usually won or lost before the model: what you load, and how you cut it into chunks."),
    ("h2", "Loaders"),
    ("code", "python", 'from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, TextLoader\n\npages = PyPDFLoader("handbook.pdf").load()          # one Document per page\nweb = WebBaseLoader("https://example.com/docs").load()\nnotes = TextLoader("notes.md", encoding="utf-8").load()'),
    ("p", "Each <code>Document</code> has <code>page_content</code> and <code>metadata</code> (source path, page number). Keep that metadata: you will cite it later."),
    ("h2", "Splitting"),
    ("code", "python", 'from langchain_text_splitters import RecursiveCharacterTextSplitter\n\nsplitter = RecursiveCharacterTextSplitter(\n    chunk_size=800,\n    chunk_overlap=120,\n    separators=["\\n## ", "\\n\\n", "\\n", " ", ""],\n)\nchunks = splitter.split_documents(pages)\nprint(len(chunks), chunks[0].metadata)'),
    ("ul", [
        "Too large: retrieval returns a blob the model skims badly.",
        "Too small: a sentence without its heading is meaningless.",
        "Overlap keeps a sentence that straddles a cut in both chunks.",
    ]),
    ("note", "Code and tables", "Recursive splitters are for prose. For code, split on functions; for tables, keep a row together or you invent numbers."),
    ("exercise", "Load a short markdown file, split with overlap 50, and print each chunk's first 80 characters plus its metadata source."),
]

CONTENT["langchain-vector-stores"] = [
    ("p", "A vector store saves embeddings and returns the nearest neighbours of a query vector. FAISS is local and fast; Chroma adds persistence; Pinecone and pgvector are hosted / SQL."),
    ("h2", "Index and query"),
    ("code", "python", 'from langchain_community.vectorstores import FAISS\nfrom langchain_openai import OpenAIEmbeddings\n\nemb = OpenAIEmbeddings(model="text-embedding-3-small")\nstore = FAISS.from_documents(chunks, emb)\nstore.save_local("index")\n\nlater = FAISS.load_local("index", emb, allow_dangerous_deserialization=True)\nhits = later.similarity_search("How do refunds work?", k=4)\nfor h in hits:\n    print(h.metadata.get("source"), h.page_content[:120])'),
    ("h2", "Metadata filters"),
    ("code", "python", 'hits = store.similarity_search("refunds", k=4, filter={"lang": "en"})'),
    ("p", "Filters only work if you set metadata when you index. Add <code>source</code>, <code>product</code>, <code>as_of</code> so you can restrict results."),
    ("h2", "When to use what"),
    ("ul", [
        "<strong>FAISS</strong>: prototypes, single-node, you manage the files.",
        "<strong>Chroma / pgvector</strong>: persistence and filters without a new vendor.",
        "<strong>Hosted</strong>: many writers, huge corpora, SLA.",
    ]),
    ("note", "allow_dangerous_deserialization", "FAISS pickle-loads Python objects. Only load indexes you created."),
    ("exercise", "Index three short documents with a <code>topic</code> in metadata and search with <code>k=2</code>, printing the topic of each hit."),
]

CONTENT["langchain-lcel"] = [
    ("p", "LCEL (LangChain Expression Language) treats every step as a <strong>Runnable</strong>. The <code>|</code> operator builds a graph you can <code>invoke</code>, <code>batch</code> or <code>stream</code>."),
    ("h2", "The pipe"),
    ("code", "python", 'from langchain_core.prompts import ChatPromptTemplate\nfrom langchain_core.output_parsers import StrOutputParser\n\nprompt = ChatPromptTemplate.from_messages([\n    ("system", "Answer in one sentence."),\n    ("human", "{question}"),\n])\nchain = prompt | model | StrOutputParser()\nprint(chain.invoke({"question": "What is RAG?"}))'),
    ("h2", "Parallel branches"),
    ("code", "python", 'from langchain_core.runnables import RunnableParallel, RunnablePassthrough\n\ncombo = RunnableParallel(\n    question=RunnablePassthrough(),\n    context=lambda q: retriever.invoke(q),\n)\nrag = combo | prompt | model | StrOutputParser()'),
    ("h2", "Retries and fallbacks"),
    ("code", "python", 'reliable = chain.with_retry(stop_after_attempt=3).with_fallbacks([backup_chain])'),
    ("p", "Each runnable has the same interface, so you can swap a model or a parser without rewriting callers."),
    ("exercise", "Build <code>prompt | model | StrOutputParser</code> and invoke it with a dict that has <code>question</code>."),
]

CONTENT["langchain-streaming"] = [
    ("p", "Waiting for a full completion feels slow. Stream tokens, and use callbacks to record what happened without wrapping every call."),
    ("h2", "Streaming tokens"),
    ("code", "python", 'for chunk in chain.stream({"question": "Explain embeddings"}):\n    print(chunk, end="", flush=True)'),
    ("p", "In an API, write each chunk to an SSE response (see the AI course on streaming) and end with a <code>done</code> event."),
    ("h2", "Callbacks"),
    ("code", "python", 'from langchain_core.callbacks import BaseCallbackHandler\n\nclass TokenCounter(BaseCallbackHandler):\n    def __init__(self):\n        self.tokens = 0\n    def on_llm_end(self, response, **kwargs):\n        usage = response.llm_output.get("token_usage") or {}\n        self.tokens += usage.get("total_tokens", 0)\n\ncounter = TokenCounter()\nchain.invoke({"question": "Hi"}, config={"callbacks": [counter]})\nprint(counter.tokens)'),
    ("note", "LangSmith", "If <code>LANGCHAIN_TRACING_V2=true</code>, every runnable is traced automatically. Custom callbacks are for in-process metrics."),
    ("exercise", "Stream a short answer to stdout and add a callback that prints <code>on_llm_start</code>."),
]

CONTENT["langchain-structured-output"] = [
    ("p", "Free-form text is a bad API. Ask the model to fill a schema, or to call a tool whose arguments are that schema."),
    ("h2", "Pydantic first"),
    ("code", "python", 'from pydantic import BaseModel, Field\n\nclass Ticket(BaseModel):\n    title: str = Field(description="Short summary")\n    priority: str = Field(description="low, medium, or high")\n    steps: list[str]\n\nextractor = model.with_structured_output(Ticket)\nticket = extractor.invoke("The checkout 500s on Safari when the cart has a coupon.")\nprint(ticket.priority, ticket.steps)'),
    ("h2", "Tools"),
    ("code", "python", 'from langchain_core.tools import tool\n\n@tool\ndef get_weather(city: str) -> str:\n    """Return a one-line forecast for a city."""\n    return f"Sunny, 24C in {city}"\n\nllm = model.bind_tools([get_weather])\nmsg = llm.invoke("Weather in Lisbon?")\nprint(msg.tool_calls)'),
    ("p", "If <code>tool_calls</code> is set, run the function, append a tool result message, and call the model again. That loop is an agent; bound it with a max-steps counter."),
    ("note", "JSON mode vs schema", "\"JSON mode\" only guarantees JSON. <code>with_structured_output</code> guarantees the fields. Prefer the schema."),
    ("exercise", "Define a <code>Contact</code> model with <code>name</code> and <code>email</code> and extract it from a messy sentence."),
]

CONTENT["langchain-langgraph"] = [
    ("p", "<strong>LangGraph</strong> models an agent as a state machine: nodes are functions, edges decide the next node, and a checkpointer stores state per thread so a run can pause."),
    ("h2", "State and a cycle"),
    ("code", "python", 'from typing import Annotated, TypedDict\nfrom langgraph.graph import StateGraph, END\nfrom langgraph.graph.message import add_messages\n\nclass State(TypedDict):\n    messages: Annotated[list, add_messages]\n    steps: int\n\ndef agent(state: State):\n    reply = model.bind_tools([search]).invoke(state["messages"])\n    return {"messages": [reply], "steps": state.get("steps", 0) + 1}\n\ndef more(state: State):\n    last = state["messages"][-1]\n    if state["steps"] >= 4:\n        return END\n    return "tools" if getattr(last, "tool_calls", None) else END\n\ng = StateGraph(State)\ng.add_node("agent", agent)\ng.add_node("tools", tool_node)\ng.set_entry_point("agent")\ng.add_conditional_edges("agent", more)\ng.add_edge("tools", "agent")\napp = g.compile()'),
    ("h2", "Checkpoints"),
    ("code", "python", 'from langgraph.checkpoint.memory import MemorySaver\napp = g.compile(checkpointer=MemorySaver())\napp.invoke({"messages": [("user", "Find the refund policy")]}, {"configurable": {"thread_id": "u-1"}})'),
    ("p", "The same <code>thread_id</code> resumes. Swap MemorySaver for a Postgres checkpointer in production."),
    ("exercise", "Draw (or code) a two-node graph: <code>plan</code> then <code>answer</code>, with a conditional edge that skips <code>plan</code> when the question is a greeting."),
]

CONTENT["langchain-multi-agent"] = [
    ("p", "Several agents in a loop look impressive and fail in surprising ways. Start with one agent and tools. Split only when you have specialists with different prompts, tools or models."),
    ("h2", "A router"),
    ("code", "python", 'from typing import Literal\n\nclass Route(BaseModel):\n    expert: Literal["billing", "tech", "smalltalk"]\n\nrouter = model.with_structured_output(Route)\n\ndef handle(question: str) -> str:\n    choice = router.invoke(question).expert\n    return experts[choice].invoke(question)'),
    ("h2", "Supervisor vs handoff"),
    ("ul", [
        "<strong>Supervisor</strong>: one node decides which worker to call, sees every result, and stops the loop.",
        "<strong>Handoff</strong>: a worker transfers the whole state to another worker (support → billing). Easy to lose the original question.",
    ]),
    ("h2", "Bounds"),
    ("p", "Cap steps, cap tokens, and never let a worker call the supervisor forever. Log which expert ran; that is how you debug a wrong answer."),
    ("note", "Cost", "Each specialist is another model call. A single well-tooled agent is cheaper until you can measure a quality gain."),
    ("exercise", "Route questions matching \"invoice\" or \"refund\" to a billing prompt and everything else to a general prompt."),
]

CONTENT["langchain-langsmith"] = [
    ("p", "<strong>LangSmith</strong> records inputs, outputs, latency and token counts for every runnable. You cannot improve what you cannot see."),
    ("h2", "Tracing"),
    ("code", "bash", "export LANGCHAIN_TRACING_V2=true\nexport LANGCHAIN_API_KEY=lsv2_...\nexport LANGCHAIN_PROJECT=support-bot"),
    ("p", "Runs appear in the project. Click a trace to see the prompt after variables were filled, the retrieved chunks, and the model output."),
    ("h2", "Datasets and evaluators"),
    ("code", "python", 'from langsmith import Client\nclient = Client()\nds = client.create_dataset("refund-questions")\nclient.create_examples(\n    dataset_id=ds.id,\n    inputs=[{"question": "How long do refunds take?"}],\n    outputs=[{"answer": "Within 5 business days."}],\n)'),
    ("p", "An evaluator can be a string check, embedding similarity, or another model judging faithfulness to retrieved context. Run it in CI on a small golden set so a prompt change cannot silently regress."),
    ("note", "PII", "Traces contain user text. Redact emails and ids, or turn tracing off for that route."),
    ("exercise", "Enable tracing for one chain, send three questions, and write down which step used the most tokens."),
]

CONTENT["langchain-production-rag"] = [
    ("p", "A demo RAG notebook is not a service. Production adds an API, citations, empty-retrieval behaviour, caching and a budget."),
    ("h2", "The request path"),
    ("code", "python", 'class Ask(BaseModel):\n    question: str\n    k: int = 4\n\n@app.post("/ask")\ndef ask(body: Ask):\n    hits = store.similarity_search(body.question, k=body.k)\n    if not hits:\n        return {"answer": "I do not have that in the docs.", "sources": []}\n    context = "\\n\\n".join(h.page_content for h in hits)\n    answer = rag.invoke({"question": body.question, "context": context})\n    sources = list({h.metadata.get("source") for h in hits})\n    return {"answer": answer, "sources": sources}'),
    ("h2", "Guardrails"),
    ("ul", [
        "Refuse to answer when retrieval is empty or scores are below a threshold.",
        "Instruct the model: use only the context; say you do not know otherwise.",
        "Cap <code>max_tokens</code> and timeout the model call.",
        "Cache embeddings of identical questions (Redis) to cut cost.",
        "Log thread id, latency, token use, and whether retrieval was empty.",
    ]),
    ("h2", "Citations"),
    ("p", "Show the source path or URL next to the answer. People trust RAG when they can click through; they stop trusting it the first time it invents a policy."),
    ("note", "Refresh the index", "Docs change. Rebuild or upsert on a schedule, and store <code>as_of</code> in metadata so you can debug which version was retrieved."),
    ("exercise", "Write an <code>/ask</code> handler that returns <code>sources: []</code> and a fixed refusal when the retriever returns no hits."),
]
