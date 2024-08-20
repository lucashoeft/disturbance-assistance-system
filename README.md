# Incident Assistance System

<p align="center">
<img width="891" alt="Screenshot 2021-05-27 at 16 10 26" src="/assets/images/assistance_system.png">
</p>

### Requirements

For using the OpenAI-API add the `.env`-file to the root directory (or just rename `.env.example` to `.env`) containing:

```
OPENAI_API_KEY="sk.."
LANGFUSE_PUBLIC_KEY="pk.."
LANGFUSE_SECRET_KEY="sk.."
```

When working with langfuse, it is also neccessary to add `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` to the `.env`-file. These keys can be obtained after setting up the project in langfuse (access via http://localhost:3000).

To get the chat history working, you need to create the required tables (`chat_history`) in the Postgres database. You can use `PostgresChatMessageHistory.create_tables(sync_connection, table_name)` from `langchain_postgres` and add it to the `demo.py` file.

To get the vector database properly working, you need to add documents. You can add the documents provided in `/data` or create your own documents. You can add documents to the database with `ingest.py` in the data folder.

### Working with Docker

To start the containers run `docker compose up`. To incorporate changes automatically start the containers with `docker compose watch` or `docker compose up -watch`.

After starting the containers access the assistance system via http://localhost:8000.

To stop the containers run `docker compose down`.

To rebuild the containers run `docker compose build --no-cache`.

## Stack

* Docker (with Docker Engine 27.0)
* Postgres 16 (with PGVector 0.7)
* Python 3.9 (Slim)
* Chainlit 1.1
* Langchain 0.2
* Langfuse 2
