import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from agent.retriever_tool import search_financial_news

load_dotenv()

SYSTEM_PROMPT = """You are a financial research assistant. You have access to a tool
that searches recent financial news articles. When a user asks about companies,
markets, or financial events, use the search tool to find relevant, current
information before answering. Always cite which article/source your information
came from. If the search returns nothing relevant, say so honestly instead of
making up information. If your first search doesn't return clearly relevant results, do not retry with
minor rewordings of the same query. Either try a genuinely different angle once,
or tell the user you don't have relevant information — do not search more than twice
for the same underlying question."""


def build_agent():
    llm = ChatGroq(
        model='openai/gpt-oss-20b',
        temperature=0,
        api_key=os.environ['GROQ_API_KEY'],
    )
    return llm.bind_tools([search_financial_news])


MAX_ROUNDS_OF_TOOL = 3


def run_agent(question):
    llm_with_tools = build_agent()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    for _ in range(MAX_ROUNDS_OF_TOOL):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:
            result = search_financial_news.invoke(tool_call["args"])
            messages.append({
                'role': 'tool',
                'content': result,
                'tool_call_id': tool_call['id'],
            })

    return "I wasn't able to find a clear answer after several search attempts."


if __name__ == '__main__':
    import sys
    question = ' '.join(sys.argv[1:]) or 'No question.'
    answer = run_agent(question)
    print(f'Q: {question}')
    print(f'A: {answer}')