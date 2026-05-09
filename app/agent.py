import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from tools.calculator import calculator_tool
from tools.web_search import web_search_tool
from tools.datetime_tool import datetime_tool
from tools.wiki_tool import wiki_tool

load_dotenv()

SYSTEM_PROMPT = """You are a helpful, intelligent AI assistant with access to tools.
You have memory of the current conversation and can refer back to earlier messages.

Your available tools:
- calculator: for any math calculations
- web_search: for current news, facts, prices, weather or anything requiring recent info
- get_datetime: for current date, time, day of week
- wikipedia: for definitions, history, people, places, general knowledge

Rules:
- Always use a tool when the question requires real data (dates, math, facts, news)
- Be concise but thorough
- If the user refers to something said earlier in the conversation, use your memory
- Acknowledge when you used a tool so the user understands how you got the answer
"""


class ChatAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set.")

        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.4,
            openai_api_key=api_key,
        )

        self.tools = [
            calculator_tool,
            web_search_tool,
            datetime_tool,
            wiki_tool,
        ]

        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=20,  # remember last 20 messages
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

        self._tools_used_log: list[str] = []

    def chat(self, message: str) -> dict:
        """Run a message through the agent and return reply + tools used."""
        self._tools_used_log = []

        result = self.executor.invoke({"input": message})
        reply = result.get("output", "I could not generate a response.")

        # Extract tool names from intermediate steps
        tools_used = []
        for step in result.get("intermediate_steps", []):
            if isinstance(step, tuple) and len(step) == 2:
                action = step[0]
                if hasattr(action, "tool"):
                    tools_used.append(action.tool)

        return {"reply": reply, "tools_used": list(set(tools_used))}

    def get_history(self) -> list[dict]:
        """Return conversation history as list of dicts."""
        messages = self.memory.chat_memory.messages
        history = []
        for msg in messages:
            role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
            history.append({"role": role, "content": msg.content})
        return history
