# Disturbance Assistance System

<p align="center">
<img width="891" alt="Screenshot 2021-05-27 at 16 10 26" src="/assets/images/assistance_system.png">
</p>

## Setting up the environment

For the OpenAI models and the Langfuse integration, you need to create an `.env` file for the API keys in the root directory as shown below. For convenience, you can also rename the `.env.example` file and add the API keys to the file. The API key for the OpenAI models can be obtained from the [OpenAI platform](platform.openai.com). The keys for Langfuse can be obtained after setting up a project in Langfuse after the first start of the container. After adding the keys, the containers must to be restarted to access to the API keys.

```
OPENAI_API_KEY="sk.."
LANGFUSE_PUBLIC_KEY="pk.."
LANGFUSE_SECRET_KEY="sk.."
```

To store the chat histories in the Postgres database, you need to create the `chat_history` table. You can use the `create_tables` method from Langchain to automatically create the table schema.

The last step is to add documents to the vector database. You can do this with the `ingest.py` file in the `/data` folder. An example document is also provided, feel free to add your own documents and adjust the parameters.

## Working with Docker

To start the Docker containers simultaneously, run the `docker compose up` command in your terminal. This will build the containers the start them. For development, use the `docker compose watch` command. This will automatically synchronize the file changes from the directory to the Docker containers. Once the containers have started successfully, you can access the assistance system via localhost 8000 in your web browser.

To stop the containers run the `docker compose down` command. To rebuild the containers without using the cache run the `docker compose build --no-cache` command.

## Stack

* Docker (using Docker Engine 27.0)
* Postgres 16 (using PGVector 0.7)
* Python 3.9 (slim)
* Chainlit 1.1
* Langchain 0.2
* Langfuse 2
