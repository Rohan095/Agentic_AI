from agent.registry import ToolRegistry
from agent.runtime import AgentRuntime
from tools.calculator import calculator_tool 
from tools.weather import weather_tool
from tools.Image_tool import image_generator_tool
from agent.state import AgentState
from agent.planner import Planner
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json


load_dotenv()
try:
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )
except Exception as e:
    print("CLIENT_ERROR:", e)
    exit(1)


try:
    registry = ToolRegistry()
    registry.register(calculator_tool)
    registry.register(weather_tool)
    registry.register(image_generator_tool)
    tool_definitions = registry.get_tool_definitions()
except Exception as e:
    print("ERROR_REGISTERING_TOOLS :", e)
    exit(1)

try:
    runtime = AgentRuntime(registry)
except Exception as e:
    print("ERROR_INITIALIZING_AGENT_RUNTIME:", e)
    exit(1)

try:
    state = AgentState("Create a image ultron rising from the ashes of a destroyed city, with a dramatic sunset in the background.")
except Exception as e:
    print("ERROR_INITIALIZING_AGENT_STATE:", e)
    exit(1)

try:
    planner = Planner(client, "gemini-3.5-flash-lite")    
except Exception as e:
    print("ERROR IN PLANNER SETUP:", e)
    exit(1)

prompt = f"""
You are an AI agent.

Your job is to understand the user's request and decide the next action.

User request:
{state.user_input}

Available tools:
{tool_definitions}

You have three possible actions:

1. DIRECT TOOL CALL
Use this when the task can be completed directly with one tool call.

Return:

{{
    "type": "tool_call",
    "tool": "<tool_name>",
    "arguments": {{
        ...
    }}
}}

2. CREATE PLAN
Use this when the task requires multiple meaningful steps, multiple tool calls,
coordination between steps, or when later steps depend on earlier results.

Return:

{{
    "type": "plan"
}}

Do NOT create a plan for simple tasks that can be completed directly.

3. FINAL ANSWER
Use this when no tool is required or when the task has already been completed.

Return:

{{
    "type": "final",
    "answer": "<a brief, natural-language answer for the user>"
}}

Important:
- Choose only ONE action.
- Do not call tools unnecessarily.
- Do not create a plan for a simple task.
- If a tool is required for a simple task, use "tool_call".
- If the task requires multiple steps, use "plan".
- Return ONLY valid JSON.
"""
max_iterations = 10

while state.iteration < max_iterations:

    state.iteration += 1
    state.status = "running"

    # 1. LLM makes ONE decision
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
    except Exception as e:
        print("ERROR_GENERATING_CONTENT:", e)
        state.status = "ERROR_GENERATING_CONTENT"
        break

    # 2. Parse decision
    try:
        decision = json.loads(response.text)
    except json.JSONDecodeError:
        print("ERROR_PARSING_JSON:", response.text)
        state.status = "ERROR_PARSING_JSON"
        break

    print("Decision:", decision)

    decision_type = decision.get("type")

    # --------------------------------
    # FINAL
    # --------------------------------

    if decision_type == "final":

        state.final_answer = decision.get(
            "answer",
            "Sorry, I couldn't complete that."
        )

        state.status = "completed"

        print("\nAnswer:", state.final_answer)

        break

    # --------------------------------
    # PLAN
    # --------------------------------

    elif decision_type == "plan":

        if state.plan is not None:
            state.replan_count += 1 
            if state.replan_count > 3:
                state.status = "ERROR_EXCESSIVE_REPLANNING"
                break

        try:
            plan = planner.create_plan(
                state.user_input,
                tool_definitions,
                previous_plan=state.plan,
                observations=state.observations
            )
            state.set_plan(plan)
            print("Plan created:", plan)

        except Exception as e:
            print("ERROR_CREATING_PLAN:", e)
            state.status = "ERROR_CREATING_PLAN"
            break

    # --------------------------------
    # TOOL CALL
    # --------------------------------

    elif decision_type == "tool_call":

        if "tool" not in decision:
            print("Missing tool")
            state.status = "ERROR_MISSING_TOOL"
            break

        if "arguments" not in decision:
            print("Missing arguments")
            state.status = "ERROR_MISSING_ARGUMENTS"
            break

        result = runtime.execute_tool(
            decision["tool"],
            decision["arguments"]
        )

        print("Tool observation:", result)

        # Store result in state
        state.add_observation(result)

    # --------------------------------
    # INVALID DECISION
    # --------------------------------

    else:

        print("Unexpected decision:", decision)

        state.status = "ERROR_UNEXPECTED_DECISION"
        break

    # ==================================
    # Prepare prompt for NEXT iteration
    # ==================================

    context = state.get_context()

    prompt = f"""
        You are an AI agent.

        Continue solving the user's request based on the current state.

        User request:
        {context["user_input"]}

        Current plan:
        {context["plan"]}

        Previous tool observations:
        {context["observations"]}

        Available tools:
        {tool_definitions}

        Decide the next action.

        Return ONE of:

        Tool call:
        {{
            "type": "tool_call",
            "tool": "<tool_name>",
            "arguments": {{ ... }}
        }}

        Plan (only if the CURRENT plan is missing, incomplete, or no longer valid):
        {{
            "type": "plan"
        }}

        Final:
        {{
            "type": "final",
            "answer": "<answer>"
        }}

        Important:
        - Choose only ONE action.
        - A plan already exists above. Do NOT choose "plan" just because it's an option —
        only choose it if a tool observation revealed the current plan is wrong,
        incomplete, or based on an assumption that turned out false.
        - Prefer following the existing plan's next step via "tool_call" over re-planning.
        - If a tool failed, first consider whether retrying the same tool with corrected
        arguments would fix it, before deciding the whole plan needs to change.
        - Only choose "plan" as a last resort when the failure clearly invalidates the
        remaining steps, not for a single fixable tool error.
        - Return ONLY valid JSON.
        """

else:

    state.status = "MAX_ITERATIONS_REACHED"

    print(
        "\nAnswer: I wasn't able to fully resolve "
        "this request within the allowed steps."
    )