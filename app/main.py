from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.bank_agent import get_agent_instance
from app.schemas import AskRequest, AskResponse


app = FastAPI(
    title="Intelligent Bank FAQ Agent",
    description="LangChain + Gemini banking FAQ assistant with tool-augmented responses.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    try:
        agent = get_agent_instance()
        answer = agent.ask(
            session_id=payload.session_id,
            question=payload.question,
        )
        return AskResponse(
            answer=answer,
            model=agent.model,
            session_id=payload.session_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc
