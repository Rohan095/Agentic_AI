
class AgentState:
    def __init__(self, user_input):
        self.user_input = user_input
        self.plan = None
        self.observations = []
        self.iteration = 0
        self.replan_count = 0
        self.status = "Not Started"
        self.error = False
        self.final_answer = None

    def add_observation(self, observation):
        self.observations.append(observation)

    def set_plan(self, plan):
        self.plan = plan

    def get_context(self):
        return {
            "user_input": self.user_input,
            "observations": self.observations,
            "plan": self.plan,
        }
    