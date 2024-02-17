import os
import dotenv
from langchain.chat_models import ChatOpenAI

dotenv.load_dotenv()
from .agents import create_switch_agent, create_analyze_agent, create_predict_agent, mapping, propmt_infos

def create_model(**kwargs):
    return ChatOpenAI(model=os.environ["OPENAI_MODEL"], **kwargs)

class AIApplication:
    def __init__(self, **kwargs) -> None:
        self.switch_agent = create_switch_agent(create_model())
        self.agents = {}
        for key, value in mapping.items():
            self.agents[key] = value(create_model(), tool_infos=propmt_infos, **kwargs)
        print("created AI")

    def run(self, query, retires=3, **kwargs):
        next_agent_dict = self.switch_agent.run(query, verbose=os.environ.get("VERBOSE", False))
        print("next_agent_dict", next_agent_dict)


        next_agent = self.agents[next_agent_dict["destination"]]
        out = next_agent.run(next_agent_dict["next_inputs"], verbose=os.environ.get("VERBOSE", False))
        return out

        # def _fn(retries):
        #     try:
        #         next_agent = self.agents[next_agent_dict["destination"]]
        #         out = next_agent.run(next_agent_dict["next_inputs"], verbose=os.environ.get("VERBOSE", False))
        #         return out
        #     except Exception as e:
        #         print("Error: ", e)
        #         if retries:
        #             return _fn(retries-1)
        #         else:
        #             return "We encounter an error, please try again later."
        # return _fn(retires)
