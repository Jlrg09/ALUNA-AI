# Data Directory

This directory contains runtime data files for the IguiChat chatbot.

## Files

- `embeddings.pkl`: Vector embeddings for document search (RAG system)
- `semantic_memory.pkl`: Semantic memory cache for improved response times

## Important

These files are automatically generated and should not be committed to version control. They are excluded in `.gitignore`.

## Regeneration

If these files are missing or corrupted, you can regenerate them by running:

```bash
python scripts/generate_embeddings.py
```

For more information, see the main project documentation.
