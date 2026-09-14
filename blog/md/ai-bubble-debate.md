# The AI Bubble Debate

**September 2026 · Published by Amar Kumar**

Every dinner party with people who work in tech now has a version of this fight. Someone says the whole thing is a bubble. Someone else says look at the HBM quotes, look at the interconnect queues, look at the fact that you cannot buy a fat DIMM without filling out a form that feels like a mortgage. They talk past each other for forty minutes. Both of them can be right.

Capex is enormous. Memory is tight. Power interconnects slip. Model labs still raise. Those facts support a boom *and* a bubble at the same time, which is annoying if you wanted a clean narrative and useful if you actually have to ship software.

The unhelpful question is “is AI a bubble?” You cannot answer it from a blog, and you should not try to underwrite NVIDIA’s multiple from a RAG demo. The useful question is: **which cash flows survive if the slides are wrong?** Which products still work if the next GPU ships with less HBM, tokens cost twice as much, or the cluster you were promised shows up two quarters late?

This is a builder’s cut of that debate — not financial advice, not a short thesis, not a pep talk. What the skeptics get right, what the buildout still is, a little shock tester, and the boring stack that stays useful either way.

## Table of contents

1. [Both stories can be true](#both-stories-can-be-true)
2. [What skeptics get right](#what-skeptics-get-right)
3. [What the buildout still is](#what-the-buildout-still-is)
4. [A product test](#a-product-test)
5. [What to build anyway](#what-to-build-anyway)
6. [FAQ](#faq)

## Both stories can be true

Search interest in “AI bubble” rose next to NVIDIA and DRAM for a reason. People are stress-testing a story that ate most of the last two years of tech capex. That is healthy. Markets that cannot joke about themselves tend to be the ones that later get a documentary with a sad piano.

The trick is that infrastructure shortages and speculative excess are not opposites. Housing bubbles happen in cities with real housing shortages. Fiber got overbuilt in places that later needed every strand. You can over-order GPUs for a workload that is genuinely growing. The hangover is about *how much* and *at what cost*, not about whether anyone uses a chatbot.

| Bull case | Bear case |
| --- | --- |
| Inference demand is still growing — agents eat tokens like teenagers eat cereal | Training clusters were front-loaded. The easy training spend already happened |
| HBM and power are scarce because use is real | Scarcity can be synchronized over-ordering with a procurement lag |
| Agents need more tokens per task, so the factory stays busy | Tokens per dollar may not cover depreciation on a rack that ages in dog years |
| Software is early; the apps have not caught up to the silicon | Software may never need this much silicon if smaller models keep getting good enough |

If you find yourself nodding at both columns, congratulations: you are paying attention. The rest of this post is about not having to pick a team.

## What skeptics get right

The bear case is not “AI is fake.” The bear case is “a lot of metal was bought on a story about utilization that has not shown up in the P&L yet.” That is a grown-up objection.
- **Depreciation clocks.** A GPU that ships with less HBM than last year’s slide still has to earn back the rack. Silicon does not care that the keynote was beautiful. See the [memory wall](/blog/posts/nvidia-ai-memory-wall/) — FLOPS without residency is a very expensive space heater with excellent PR.
- **Utilization.** Peak reserved capacity is not tokens sold. A reserved H100 that spends Tuesday waiting for a batch job is a stuffed animal you finance at datacenter rates.
- **Power and interconnect** slip dates even when the chip exists. You cannot decode your way around a missing substation. The cluster that “ships in Q2” and lands in Q4 is the most common science-fiction in this industry.
- **Application revenue** still lags infrastructure spend at most companies. Lots of pilots. Lots of “the CEO wants a demo.” Fewer products where the unit economics would survive a CFO who can do division.

A thinner Rubin Ultra HBM SKU is not proof demand vanished. It is proof the **bill of materials** is the scarce resource. That is the memory wall and the [DRAM supercycle](/blog/posts/dram-supercycle/) in one sentence: the boom is real enough to starve other products of wafers, and still not a guarantee that *your* feature pays for the card.

Skeptics also get this right, and it stings: a lot of “AI strategy” is a wrapping paper around a GPT wrapper. Wrappers are fine. Wrappers that require a dedicated cluster are a lifestyle.

## What the buildout still is

Hyperscalers are still buying. Server DRAM long-term agreements run for years. That is not a meme-stock chart. It is a procurement process that is painful to unwind, which is why “just wait for the crash and buy cheap GPUs” is a strategy for people who do not have customers this quarter.

The risk is not “nobody uses models.” People use models. Your support team uses models. Your least technical coworker uses models to write emails that used to take twelve minutes and now take twelve minutes plus a rewrite. The risk is “too much of the same model, at the wrong memory and power point, for workloads that fit a smaller card.”

That is a product-architecture problem wearing a macro costume. You do not need to win a debate on CNBC. You need a serving path that still works if the next SKU is 192 GB and the DIMM is priced like a weekend in Tokyo.

Indicative split of attention: infra spend is loud. Application gross margin is quieter. That gap is the debate.

## A product test

Forget the keynote. Run the product through a cheap, mean thought experiment: would this still be a product if the factory got worse? Toggle the shocks. If quality or unit economics collapse, you were not building a product. You were renting a boom.

### Would this product survive a 40% GPU price shock?

Pick a constraint. If the thing you shipped only works on cheap, abundant HBM, you are underwriting someone else’s cluster.

Cut context, rerank, and route to a resident model. If quality collapses, the product was a capacity trade dressed up as a roadmap.

## What to build anyway

There is a blessed category of work that is useful if the boom continues *and* if it compresses. It is not glamorous. It will not get you a keynote. It will keep you employed when the unused rack becomes a punchline.
- **Eval harnesses and golden sets** — so you know whether the smaller model is actually worse, or just less theatrical. See [agent testing](/blog/posts/ai-agent-testing-evaluation-strategies/).
- **Routing and cheaper models** — a 32B that stays resident beats a frontier model that pages. Start with [economical RAG models](/blog/posts/best-economical-llm-models-rag-openai-gemini-anthropic/).
- **Retrieval that earns its tokens** — every extra chunk is DRAM and HBM you paid for. [RAG evaluation](/blog/posts/how-to-evaluate-rag-retrieval/) is how you stop donating margin to memory vendors.

A bubble-proof stack is just a cost-aware stack with better manners. Cache the prefixes. Cap the context. Measure decode. Do not pin a 70B “for quality” you have not A/B tested against an 8B plus a reranker.

If the boom continues, those layers make you faster and cheaper than the team that bought prestige. If it compresses, those layers are why you still have a product when the CFO asks what the GPUs are for.

Either way you will sleep better than the person whose roadmap is a purchase order.

## FAQ

### Is this financial advice?

No. It is a product-architecture read of a public argument. If you want a price target, there are people with Bloomberg terminals who will be wrong more expensively than I will.

### Does a memory shortage prove there is no bubble?

No. Shortages can be real demand or synchronized over-ordering with a six-month lag. They do prove FLOPS are not free, and that the bill of materials can veto a slide. See the [DRAM supercycle](/blog/posts/dram-supercycle/).

### What should a startup do?

Design for 192 GB SKUs, expensive DIMMs, and higher token prices. If the product still works, you are not betting the company on a keynote. If it only works on infinite cheap HBM, you do not have a product — you have a weather derivative.

### Isn’t “just use a smaller model” giving up?

Only if quality actually falls, which you will not know unless you measure. A lot of “we need the frontier model” is taste, fear, and a demo that was run once on a fat context window. Taste is allowed. Fear is expensive.

### What if the boom is real and I under-build?

Then you scale the serving path that already works. That is a nicer problem than explaining a dark row of GPUs to a board. Capacity can be added. A product that only exists at last quarter’s prices cannot.

Believe the workload. Distrust the unused rack. And if someone at dinner asks whether it is a bubble, tell them the only honest answer for a builder: it does not matter if your serving path still works when the slides are wrong.
