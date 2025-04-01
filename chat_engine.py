from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import SystemMessage

class ChatBot:
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.model_name = "llama-3.2-3b-preview"
        self.llm = self._setup_llm()
        self.app = self._setup_workflow()

    def _setup_llm(self):
        return ChatGroq(
            temperature=0.1,
            groq_api_key=self.groq_api_key,
            model_name=self.model_name
        )

    def _setup_workflow(self, system_prompt="You are a helpful IT and CloudOPS assistant. Respond in French."):
        workflow = StateGraph(state_schema=MessagesState)
        
        def call_model(state: MessagesState):
            # Add system message at the beginning of the conversation
            sys_prompt = SystemMessage(content=system_prompt)
            modified_messages = [sys_prompt] + state["messages"]
            
            response = self.llm.invoke(modified_messages)
            return {"messages": response}

        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)
        
        return workflow.compile(checkpointer=MemorySaver())

    def chat(self, message: str, thread_id: str = 'guest', system_prompt=None):
        # If a custom system prompt is provided, recreate the workflow
        if system_prompt:
            self.app = self._setup_workflow(system_prompt)
        
        return self.app.invoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": thread_id}}
        )
