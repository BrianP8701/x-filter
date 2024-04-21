from x_filter.ai.filter import Filter, run_x_filter
from x_filter.data.models.filter import Filter
from x_filter import Database
import asyncio
db = Database()

# temporary_filter = Filter(
#     id="4",
#     user_id="123",
#     name="RAG Research",
#     keyword_groups=[["RAG", "new methods"], ["RAG", "vector databases"], ["state of the art", "LLM navigation"], ["file structure, RAG"]],
#     primary_prompt="I am looking for tweets that provide insights into innovative methods in Retrieval-Augmented Generation (RAG) that address new challenges. Specifically, I am interested in: 1. New techniques for chunking in RAG. 2. The latest state-of-the-art vector databases. 3. Models that are fine-tuned specifically for RAG applications. Additionally, I am seeking information on novel approaches that go beyond vector similarity, such as using metadata, descriptions, and language models to navigate through a structured hierarchy like folders or trees. A particular area of interest is the development of systems capable of autonomously organizing arbitrary data into a file structure, complete with descriptive labels, and enabling a language model to search through this organized content.",
#     report_guide="The report will be concise, simple, and technical, focusing primarily on insights related to innovative methods in Retrieval-Augmented Generation (RAG). It will include information on new techniques for chunking in RAG, the latest state-of-the-art vector databases, and models fine-tuned for RAG applications. The report will also highlight novel approaches that utilize metadata, descriptions, and language models to navigate structured hierarchies, as well as systems that autonomously organize data into a file structure for LLM search capabilities. The tone will be technical, presenting the most relevant and insightful findings from the tweets.",
#     filter_period=14,
#     target="reports",
# )

# try:
#     db.insert("filters", temporary_filter.model_dump())

#     results = asyncio.run(run_x_filter(temporary_filter.id, first_cap=30))
#     print(results)
# except Exception as e:
#     import traceback
#     print(f"Error: {e}")
#     traceback.print_exc()
# finally:
#     db.delete("filters", temporary_filter.model_dump())

try:
    results = asyncio.run(run_x_filter('45aefae8-ad99-4345-ba93-138dd7e9cb12'))
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
