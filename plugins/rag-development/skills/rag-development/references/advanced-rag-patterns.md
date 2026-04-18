# Advanced RAG Patterns

## Agentic RAG

Agent orchestrates retrieval dynamically -- decides when to retrieve, which indexes to query, whether to refine the query, and when to stop.

**Architecture**:
```
User Query -> Agent (LLM)
  -> Decide: retrieve? which index? transform query?
  -> Execute retrieval
  -> Evaluate: sufficient? accurate?
  -> If not: re-query, use different tool, decompose
  -> Generate final answer
```

Frameworks: LangGraph agents, LlamaIndex `AgentRunner`, CrewAI with RAG tools.

- Survey: https://github.com/asinghcsu/AgenticRAG-Survey

## Graph RAG (Microsoft) and LazyGraphRAG

Builds a knowledge graph from documents, detects community structures, generates hierarchical summaries, then uses these for retrieval.

**Process**:
1. LLM extracts entities (nodes) and relationships (edges) from text chunks
2. Community detection partitions the graph hierarchically (Leiden algorithm)
3. LLM generates summaries for each community at each level
4. At query time, searches both graph structure and community summaries

**Best for**: themes, narratives, cross-document reasoning, "what are the main themes across these documents?"

**LazyGraphRAG** (Microsoft, 2024) -- same idea, deferred indexing. Entity extraction + community summarization happens on-demand per query rather than upfront, cutting indexing cost by orders of magnitude. Preferred starting point over full GraphRAG unless you run many queries over the same corpus.

**Important caveat:** 2025 benchmarks ([arxiv:2502.11371](https://arxiv.org/html/2502.11371v2), [arxiv:2506.05690](https://arxiv.org/html/2506.05690v3)) show GraphRAG variants frequently **underperform** a well-tuned hybrid + reranking pipeline on real-world tasks. Default to hybrid + rerank first; escalate to Graph RAG only for cross-document theme questions.

- Code: https://github.com/microsoft/graphrag
- Docs: https://microsoft.github.io/graphrag/
- Paper: https://arxiv.org/html/2404.16130v1

## HippoRAG and HippoRAG 2

Hippocampus-inspired memory layer on top of RAG.

**Process** (HippoRAG v1, NeurIPS 2024):
1. Extract entities from documents, build a knowledge graph
2. Embed entities; at query time, identify query entities via dense retrieval
3. Run Personalized PageRank on the KG starting from query entities to spread activation
4. Retrieve passages linked to the highest-activation entities

**HippoRAG 2** (ICML 2025) refines v1: uses the KG to guide retrieval rather than expand the corpus, improves associative memory benchmarks 7% over SOTA embeddings, and adds continual learning support.

**Best for**: multi-hop Q&A and continual knowledge integration where new docs arrive over time.

- Paper (v1): https://arxiv.org/abs/2405.14831
- Paper (v2): https://arxiv.org/html/2502.14802v1
- Code: https://github.com/OSU-NLP-Group/HippoRAG

## LightRAG

HKU/BUPT 2024 -- dual-level retrieval (low-level entity/relationship + high-level concept) combined with graph-enhanced indexing, with incremental updates without reprocessing the corpus.

**Best for**: evolving corpora that need graph reasoning but should stay lighter than Microsoft GraphRAG.

- Paper: https://arxiv.org/abs/2410.05779
- Code (mirror): https://github.com/LarFii/LightRAG-hku

## LongRAG

2024 -- pair a "long retriever" with a "long reader." Group related documents into ~4K-token units, retrieve fewer but longer compressed chunks, then let a long-context LLM do the reading.

Reported: 62.7% EM on NQ, 64.3% on HotpotQA without retriever fine-tuning.

**Best for**: when you already have a long-context LLM (Claude 1M, Gemini 2M, GPT-4o-long) and want minimal retriever complexity. Cost scales with long-context LLM usage.

- Paper: https://arxiv.org/abs/2406.15319

## RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval)

Hierarchical tree of summaries from leaf chunks up to root summaries.

**Process**:
1. Embed and cluster leaf chunks by semantic similarity
2. Summarize each cluster
3. Embed summaries, cluster again, summarize again
4. Repeat until single root summary
5. At query time, traverse tree from root to leaves

**Best for**: long-context Q&A where answers span multiple parts of a document.

- Code: https://github.com/parthsarthi03/raptor

## Corrective RAG (CRAG)

Adds a retrieval evaluator that grades retrieved documents before passing to LLM.

**Flow**:
1. Retrieve documents
2. Evaluator grades each: "Correct", "Ambiguous", or "Incorrect"
3. Correct -> use for generation
4. Ambiguous -> refine query, re-retrieve
5. Incorrect -> fall back to web search or alternative sources

## Self-RAG

Model decides when to retrieve and self-critiques outputs for factuality.

**Special tokens**:
- `[Retrieve]` -- should I retrieve? (yes/no)
- `[IsRel]` -- is retrieved passage relevant?
- `[IsSup]` -- is response supported by passage?
- `[IsUse]` -- is response useful?

## Modular RAG

RAG as interchangeable modules:
- **Router** -- directs queries to appropriate retrieval pipeline
- **Retriever** -- multiple types (dense, sparse, graph)
- **Evaluator** -- scores retrieved context quality
- **Generator** -- LLM for answer synthesis
- **Refiner** -- post-processes and validates outputs

## Multi-Modal RAG

### Tables
- Extract as HTML (preserves structure best)
- Embed with text models or summarize with LLM
- Store both raw table and LLM summary

### Images
- Multimodal embeddings (CLIP, SigLIP) for image-text matching
- Vision LLMs to generate text descriptions for indexing
- ColPali/ColQwen: late-interaction models for document page images (no OCR needed)

### PDFs
- Unstructured.io for element-level extraction
- LlamaParse for LlamaIndex integration
- Consider page-level indexing with vision models for complex layouts

## Pattern Selection Guide

| Pattern | Complexity | Best For | When to Use |
|---------|-----------|---------|------------|
| Naive RAG | Low | Simple Q&A, clean docs | Start here |
| Hybrid + Reranking | Medium | Most production use cases | Default modern baseline; keyword misses or irrelevant results |
| Contextual Retrieval | Medium | Ambiguous chunks | 49-67% fewer retrieval failures |
| Agentic RAG | High | Complex multi-hop queries | Simple retrieval insufficient; diverse query types |
| LongRAG | Low-Medium | Long-context LLM available | Let the LLM read fewer, longer chunks |
| HippoRAG / HippoRAG 2 | High | Multi-hop + continual learning | KG + Personalized PageRank over evolving corpora |
| LightRAG | Medium-High | Evolving corpora | Cheaper graph RAG than Microsoft GraphRAG |
| Graph RAG (incl. LazyGraphRAG) | High | Cross-document themes | Global queries; benchmark against hybrid+rerank first |
| RAPTOR | High | Long documents | Answers span multiple doc sections |
| CRAG | Medium | Unreliable corpus | Retrieved docs often irrelevant |
| Self-RAG | High | Variable query types | Some queries don't need retrieval |

## Evaluation Frameworks (2026 stack)

| Framework | Role | Best for |
|-----------|------|----------|
| RAGAS | Reference-free metrics (Context Precision/Recall, Faithfulness, Answer Relevance) | Metric exploration during system design |
| DeepEval | Pytest-style assertions | CI/CD quality gates |
| TruLens | Live production monitoring | Production observability dashboards |
| Langfuse | Traces + evals combined | End-to-end LLM observability |
| ARES | Academic benchmarking | Comparative research (less adopted in 2025-2026 production) |

Recommended pipeline: RAGAS during design -> DeepEval gates in CI -> TruLens or Langfuse in prod.

- RAGAS paper: https://arxiv.org/abs/2309.15217
- DeepEval docs: https://deepeval.com/docs/metrics-ragas

## Legacy patterns (historical)

FiD (Fusion-in-Decoder), RA-DIT, and REPLUG are still referenced academically but rarely appear in 2025-2026 production stacks. Modern agentic + hybrid-rerank + long-context-LLM pipelines subsume their capabilities. Document them if you encounter legacy systems; prefer the patterns above for new work.

## References
- [Microsoft GraphRAG](https://arxiv.org/html/2404.16130v1)
- [HippoRAG](https://arxiv.org/abs/2405.14831)
- [HippoRAG 2](https://arxiv.org/html/2502.14802v1)
- [LightRAG](https://arxiv.org/abs/2410.05779)
- [LongRAG](https://arxiv.org/abs/2406.15319)
- [Agentic RAG with LangGraph](https://blog.langchain.com/agentic-rag-with-langgraph/)
- [Contextual AI on GraphRAG alternatives](https://contextual.ai/blog/an-agentic-alternative-to-graphrag)
- [Agentic RAG Survey](https://github.com/asinghcsu/AgenticRAG-Survey)
- [HybridRAG benchmark (2025)](https://arxiv.org/html/2502.11371v2)
