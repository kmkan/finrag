import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from agent.retriever_tool import search_financial_news
from agent.stock import get_stock_price

load_dotenv()

SYSTEM_PROMPT = """You are a financial research assistant. You have access to two tools:
1. search_financial_news - searches recent financial news articles for context and events
2. get_stock_price - gets the current price and performance for a stock ticker symbol
Use search_financial_news for questions about news, events, or market context.
Use get_stock_price when the user asks about a specific stock's current price or performance.
You can use both tools together if a question needs current price plus news context.
Always cite which source (article or live price data) your information came from.
If your first search doesn't return clearly relevant results, do not retry with
minor rewordings of the same query. Either try a genuinely different angle once,
or tell the user you don't have relevant information - do not search more than twice
for the same underlying question."""

AVAILABLE_TOOLS = {
    'search_financial_news': search_financial_news,
    'get_stock_price': get_stock_price,
}

MAX_ROUNDS_OF_TOOL = 3
LEAKED_TOKEN_PATTERN = re.compile(r'【[^】]*】|commentary to=functions\.\S+')

def clean_response(text: str) -> str:
    cleaned = LEAKED_TOKEN_PATTERN.sub('', text)
    return cleaned.strip()

def build_agent():
    llm = ChatGroq(
        model='openai/gpt-oss-20b',
        temperature=0,
        api_key=os.environ['GROQ_API_KEY'],
    )
    return llm.bind_tools([search_financial_news, get_stock_price])


def run_agent(question):
    llm_with_tools = build_agent()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    seen_queries = set()

    for _ in range(MAX_ROUNDS_OF_TOOL):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return clean_response(response.content)

        for tool_call in response.tool_calls:
            tool_fn = AVAILABLE_TOOLS[tool_call['name']]

            dedup_key = f'{tool_call['name']}:{str(tool_call['args']).lower().strip()}'
            if dedup_key in seen_queries:
                messages.append({
                    'role': 'tool',
                    'content': "You already made this exact call. No new results. "
                               'Answer using what you have, or tell the user '
                               "you couldn't find relevant information.",
                    'tool_call_id': tool_call['id'],
                })
                continue

            seen_queries.add(dedup_key)
            result = tool_fn.invoke(tool_call['args'])
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
