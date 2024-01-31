from .router import create_model as create_router_agent
from .router import prompt_infos as propmt_infos
from .analyze import create_agent_sql as create_analyze_agent
from .general import create_agent as create_general_agent
from .predict import create_agent as create_predict_agent

mapping = {
    'data analysis': create_analyze_agent,
    'general question answering': create_general_agent,
    'future prediction': create_predict_agent
}