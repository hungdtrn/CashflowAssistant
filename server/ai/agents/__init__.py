from .switch import create_agent as create_switch_agent
from .switch import prompt_infos as propmt_infos
from .analyze import create_agent as create_analyze_agent, PERMISSION_ERROR
from .general import create_agent as create_general_agent
from .predict import create_agent as create_predict_agent

mapping = {
    'data analysis': create_analyze_agent,
    'general chat': create_general_agent,
    'future prediction': create_predict_agent
}