# import asyncio,nest_asyncio
# from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
# from llama_index.llms.ollama import Ollama
# from llama_index.core import Settings
# from llama_index.tools.mcp import McpToolSpec
# from llama_index.core.agent.workflow import FunctionAgent
# from llama_index.core.agent.workflow import (
#     FunctionAgent, 
#     ToolCallResult, 
#     ToolCall)
# from llama_index.core.workflow import Context


# nest_asyncio.apply()
# llm = Ollama(model="qwen2.5:3b", request_timeout=120.0)
# Settings.llm = llm

# mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
# mcp_tools = McpToolSpec(client=mcp_client)


# SYSTEM_PROMPT = """\
# You are an AI assistant for a defect detection system in an ecommerce website. 
# """

# async def get_agent(tools: McpToolSpec):
#     tools = await tools.to_tool_list_async()
#     agent = FunctionAgent(
#         name="Agent",
#         description="An agent that can work with Our Database software.",
#         tools=tools,
#         llm=llm,
#         system_prompt=SYSTEM_PROMPT,
#     )
#     return agent

# async def handle_user_message(
#     message_content: str,
#     agent: FunctionAgent,
#     agent_context: Context,
#     verbose: bool = False,
# ):
#     handler = agent.run(message_content, ctx=agent_context)
#     async for event in handler.stream_events():
#         if verbose and type(event) == ToolCall:
#             print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
#         elif verbose and type(event) == ToolCallResult:
#             print(f"Tool {event.tool_name} returned {event.tool_output}")

#     response = await handler
#     return str(response)

# async def x():
#     agent = await get_agent(mcp_tools)
#     return agent

# agent = asyncio.run(x())

# agent_context = Context(agent)

#     user_input = input("Enter your message: ")
#     if user_input == "exit":
#         break
#     print("User: ", user_input)
#     async def y():
#         return await handle_user_message(user_input, agent, agent_context, verbose=True)
#     response = asyncio.run(y())
#     print("Agent: ", response)