import os
import dotenv
from langchain.chat_models import ChatOpenAI

dotenv.load_dotenv()
from .agents import create_router_agent, create_analyze_agent, mapping, propmt_infos

def create_model():
    return ChatOpenAI(model="gpt-3.5-turbo")

def get_result(query, retries=3, **kwargs):
    """
    Get the result from the AI agent.
    """
    # Create the agent
    router_agent = create_router_agent(create_model())

    # Get the result
    next_agent_dict = router_agent.invoke(query)

    # next_agent = mapping[next_agent_dict["destination"]](create_model(), tool_infos=propmt_infos, **kwargs)
    # out = next_agent(next_agent_dict, verbose=True)
    # return out

    def _fn(retries):
        try:
            next_agent = mapping[next_agent_dict["destination"]](create_model(), tool_infos=propmt_infos, **kwargs)
            out = next_agent(next_agent_dict, verbose=True)
            return out
        except Exception as e:
            print("Error: ", e)
            if retries:
                return _fn(retries-1)
            else:
                return "We encounter an error, please try again later."
            
    return _fn(retries)