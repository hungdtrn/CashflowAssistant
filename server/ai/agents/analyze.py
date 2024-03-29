from .base import SQLAgentBase, PERMISSION_ERROR

class SQLAgentAnalyze(SQLAgentBase):
    def __init__(self, llm, userID, **kwargs) -> None:
        super().__init__(llm, userID, **kwargs)

def create_agent(llm, **kwargs):
    return SQLAgentAnalyze(llm, **kwargs)