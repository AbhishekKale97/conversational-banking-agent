from collections import defaultdict

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agents.prompts import SYSTEM_PROMPT
from app.agents.tools import BankingToolset
from app.config import get_settings


class BankFAQAgent:
    def __init__(self) -> None:
        settings = get_settings()

        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=0.2,
        )

        toolset = BankingToolset(
            faq_path=settings.faq_data_path,
            kb_path=settings.kb_data_path,
        )
        self.tools = toolset.build_tools()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(llm=llm, tools=self.tools, prompt=prompt)
        self.executor = AgentExecutor(agent=agent, tools=self.tools, verbose=False)
        self.chat_sessions = defaultdict(list)
        self.model = settings.gemini_model

    @staticmethod
    def _is_in_scope(question: str) -> bool:
        keywords = {
            "bank",
            "loan",
            "emi",
            "interest",
            "credit",
            "debit",
            "nbfc",
            "kyc",
            "savings",
            "current account",
            "fd",
            "rd",
            "card",
            "upi",
            "neft",
            "rtgs",
            "imps",
            "mortgage",
            "insurance",
            "foreclosure",
        }
        text = question.lower()
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _safe_fallback() -> str:
        return (
            "I can help with banking and NBFC topics such as accounts, loans, cards, transfers, "
            "EMI, KYC, and related FAQs. Please ask a finance-related question."
        )

    @staticmethod
    def _post_guardrail(answer: str) -> str:
        risky_terms = ["guaranteed approval", "100% approved", "no risk"]
        normalized = answer.lower()
        if any(term in normalized for term in risky_terms):
            return (
                "I can share general guidance, but approvals, rates, and charges depend on lender policy "
                "and your profile. Please verify final terms with your bank or NBFC."
            )
        return answer

    def ask(self, session_id: str, question: str) -> str:
        if not self._is_in_scope(question):
            return self._safe_fallback()

        history = self.chat_sessions[session_id]

        result = self.executor.invoke(
            {
                "input": question,
                "chat_history": history,
            }
        )
        answer = self._post_guardrail(result["output"])

        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=answer))

        self.chat_sessions[session_id] = history[-12:]
        return answer


_agent_instance: BankFAQAgent | None = None
_agent_init_error: Exception | None = None


def get_agent_instance() -> BankFAQAgent:
    global _agent_instance, _agent_init_error

    if _agent_instance is not None:
        return _agent_instance

    if _agent_init_error is not None:
        raise RuntimeError(
            "Agent initialization failed. Create .env from .env.example and set GOOGLE_API_KEY (or GEMINI_API_KEY)."
        ) from _agent_init_error

    try:
        _agent_instance = BankFAQAgent()
        return _agent_instance
    except Exception as exc:
        _agent_init_error = exc
        raise RuntimeError(
            "Agent initialization failed. Create .env from .env.example and set GOOGLE_API_KEY (or GEMINI_API_KEY)."
        ) from exc
