# Following policies with RAG (15 minutes)

## What RAG means
RAG stands for Retrieval-Augmented Generation.

In plain language:
- retrieve relevant documents or passages
- give that retrieved context to the model
- generate an answer grounded in that context

## Why this matters for policy work
If the track asks the agent to follow policy documents, the safest approach is not to rely on memory alone. The agent should pull relevant policy text and answer using that source material.

## What RAG helps with
- grounding answers in actual documents
- reducing made-up policy statements
- showing why the answer was given

## What RAG does not guarantee
- perfect retrieval
- perfect interpretation
- permission to ignore the original document

## Beginner debugging tip
If the answer sounds wrong:
- check whether the right policy document was indexed or retrieved
- check whether the query wording was specific enough
- check whether the answer cited the retrieved material

## Optional video
Watch: **How to use Retrieval Augmented Generation (RAG)**
https://www.youtube.com/watch?v=oVtlp72f9NQ
