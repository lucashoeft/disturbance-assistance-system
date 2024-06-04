# Incident Assistance System

### Requirements

For using the OpenAI-API add the `.env`-file to the root directory containing:

```
OPENAI_API_KEY=""
```

When working with langfuse, it is also neccessary to add `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` to the `.env`-file. These keys can be obtained after setting up the project in langfuse (localhost:3000).

### Working with Docker

To start the containers run `docker compose up`. To incorporate changes automatically start the containers with `docker compose watch` or `docker compose up -watch`.

To stop the containers run `docker compose down`.