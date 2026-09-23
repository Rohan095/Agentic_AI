import json
from google.genai import types


class Planner:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_plan(self, user_input, tool_definitions, previous_plan=None, observations=None):
        context_block = ""

        if previous_plan is not None:
            context_block = f"""
            Previous plan:
            {previous_plan}

            Previous observations:
            {observations}

            The previous plan did not fully succeed or is no longer valid.
            Revise it based on what the observations reveal — don't just repeat it.
            """

        prompt = f"""
        You are a planning component of an AI agent.

        Your job is to break the user's request into clear, ordered steps.

        User request:
        {user_input}

        {context_block}
        
        Available tools:
        {tool_definitions}

        Create a plan that contains only the necessary steps.

        Return ONLY JSON in this format:

        {{
            "goal": "<user's goal>",
            "steps": [
                "<step 1>",
                "<step 2>",
                "<step 3>"
            ]
        }}
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

