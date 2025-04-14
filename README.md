# Zluri Chatbot

Welcome to the Zluri Chatbot – your friendly assistant for any customer support inquiries regarding our Next-Gen Identity Governance & Administration platform for IT & Security teams. Here’s an overview of the key features and technology behind our solution:

## Get Started

Before using the chatbot, ensure that all required dependencies are installed. Run the following command in your terminal:

```shell
pip install -r requirements.txt
```

This command installs all the Python packages necessary for the chatbot to run smoothly.

## Knowledge Base
The chatbot utilizes a structured knowledge base to provide accurate and prompt responses. The following files are essential:

`knowledge_base.json`: Contains the extracted documentation data from the Zluri website.

`section_index.index` and `chunk_index.index`: These files store the indexes for topic headings (sections) and content chunks, enabling efficient retrieval during a query.

### Generate Groq API Key
Generate Groq API key to use LLMs hosted by Groq. We are particularly using llama4 models but these can be changes to better and suitable models

> edit `config.py` to add the GROQ_API_KEY

## How to Run

You can run the Zluri Chatbot in two different environments:

### Command Line Interface (CLI)
For a text-based interaction, execute:

```shell
python main.py
```

### Web Application via Streamlit
For an interactive web-based experience, run:

```
streamlit run streamlit_app.py
```

This command launches the chatbot in your default web browser using Streamlit's streamlined UI.


## 🚀 Key Features

### 🧠 RAG with Hybrid Search
- **Dual FAISS Indexing:**
  - **Chunk Embedding:** Uses the full content of each section to capture detailed context.
  - **Section Embedding:** Leverages the semantic meaning of section headings for more precise matching.
- **Hybrid Retrieval Logic:**
  1. Prioritizes matching semantically with section headings.
  2. Falls back to full content similarity when a strong section match isn’t found.

### 💬 LLM-Backed Answers
- **Intelligent Query Understanding:** Our system uses the Groq API paired with LLaMA-4 for comprehensive query interpretation.
- **Customized, Friendly Responses:** Answers are generated using a custom prompt template that ensures responses are both accurate and helpful.
- **Context-Driven Assistance:** The chatbot relies strictly on provided context to resolve customer support queries effectively.

---

## 🧱 Tech Stack

- [Streamlit](https://streamlit.io/) for an intuitive, interactive user interface.
- [Sentence Transformers](https://www.sbert.net/) to generate high-quality text embeddings.
- [FAISS](https://github.com/facebookresearch/faiss) for rapid vector search and retrieval.
- [Groq API](https://console.groq.com/) with LLaMA-3 to power our intelligent answer generation.

## Future Improvements:
- Add Contextual Summary in each topic node to provide relevant information context with each chunk to LLM - [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- Use BM25 Retriever for section/topic name retrieval from LLamaIndex
- Fix token length based Chunking of each topics but connecting them with same topic
- Preprocessing and Crawling of Text into Rich .md file using FireCrawl and other API based WebCralwer service
---

Got questions? Feel free to [submit a ticket](https://support.zluri.com/support/tickets/new) or contact us directly at support@zluri.com.
