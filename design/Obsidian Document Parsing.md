# Obsidian Document Parsing

As part of this project, I would like to be able to create vector embeddings of my Obsidian Notebook.  An AI Assistant who has access to my knowledge and experience can more effectively work along side me without the need for me to provide large volumes of context as I work AND the LLM can then connect itself to my knowledge through the creation of it's own edges in the database to reinforce or grow it's capabilities.

## Document Structure

Parsing Documents from Obsidian involves understanding the document layout.  That layout includes specific types of information:

1. Frontmatter - At the top of a document there is a space to add YAML details to the document.  Obsidian will render these in a special way and when used with other extensions and tools within the application to help organize documents.
2. Outlinks - Text notes inside of Obsidian are Markdown which provides a specification for adding clickable links to the document.  Additionally Obsidian provides a [WikiLinks](https://help.obsidian.md/Linking+notes+and+files/Internal+links) syntax, which allows users to reference other notes.  The WikiLinks are also used to generate the relationship graph.
3. Images - We can embed images into the document using the [Markdown Image Syntax](https://spec.commonmark.org/0.31.2/#images).  These are non-text based details which provide context about a document.
4. Code Blocks - Code blocks are a content segmentation tool which also gives us syntax highlighting for blocks of code.  Obsidian also uses these (specifically with the **Dataview** plugin) for dynamic content.  We need to treat these specially because they may not always make sense for the LLM.
5. Text Content - Finally we have the actual text that the user inputs.  This can be both information pulled in from other sources AND information the user has generated themselves.

It is important to identify this information as it outlines what steps we need to take on each document in order to successfully extract the information that is useful for searching for the document.

## Document Search

Previously I have spent my time looking at the problem from the front.  It is easy to read a Markdown document because it is plain text.  Writing a _regular expression_ to grab the links and image links has well defined solutions OR tools to make it trivial.  The challenge with this process seems to be how to store the information in an optimal way so that when we collect documents that will be used as context for an LLM, the context will be relevant to the input (such as a user asking a specific question that can be answered by the document).

For my project, I am using **Neo4j** as my database for both Graph and Vector data.  LangChain does have a [Neo4j Vector Index](https://python.langchain.com/v0.2/docs/integrations/vectorstores/neo4jvector/) integration.  Importantly this database is one of the integrated databases that supports "Hybrid Search".  Specifically for **Neo4J** we have either Euclidean Similarity or Cosine Similarity search alongside _Keyword Search_ within the integration itself.  Though **Neo4j** does support other similarity functions as well ([ref](https://neo4j.com/docs/graph-data-science/current/algorithms/similarity-functions/)).

So the key is to understand how to optimize the text & keywords to get the _most accurate_ results out of search.  Some of this can be tuned using techniques like _Multi-Query_ or _RAG Fusion_.  However, based on my experience so far, this seems limited.  I am currently working on another project at work where I am working on a similar problem.  In my example document, I have a list item (`<li>`) which itself contains a comma separated list of programming languages.  The question I have been using asked the the retriever to find documents related to 'Javascript'.  Unfortunately even with the _Multi-Query_ technique I have been using, the retriever never grabs the comma separated list and thus the LLM responds that it cannot definitively answer the question even though the information is available in the database.

To start my understanding I first want to make sure I have a clear definition of similarity in the context:

> Similarity is the distance between two vectors where the vector dimensions represent the features of two objects. In simple terms, similarity is the measure of how different or alike two data objects are. If the distance is small, the objects are said to have a high degree of similarity and vice versa. Generally, it is measured in the range 0 to 1. This score in the range of [0, 1] is called the similarity score. [Ultimate Guide to Text Similarity with Python - NewsCatcher](https://www.newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python)

With this in mind I went ahead and started researching out to do the optimization (specifically on the text content to achieve the best results).

## Document Cleaning

I started researching techniques on document cleaning (or the process of making a document more computer readable) by exploring various articles and videos on the web.

### Article: Four Data Cleaning Techniques to Improve Large Language Model (LLM) Performance

[Link](https://medium.com/intel-tech/four-data-cleaning-techniques-to-improve-large-language-model-llm-performance-77bee9003625)

