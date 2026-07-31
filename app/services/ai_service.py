from google import genai

from ..config import settings
from ..repositories.ai_repository import AIRepository
from ..schemas.ai_chat import AIChatResponse


class AIAssistantService:
    def __init__(self, db):
        self.repo = AIRepository(db)
        self.llm = LLMClient()

    async def chat(self, user_id: int, data):
        if data.conversation_id:
            conversation = await self.repo.get_conversation_by_id(data.conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found")
            conv_id = data.conversation_id
        else:
            conv = await self.repo.create_conversation(user_id)
            conv_id = conv.id

        await self.repo.add_message(conv_id, "user", data.message)
        history = await self.repo.get_messages_by_conversation(conv_id)
        messages = [{"role": m.role, "content": m.content} for m in history]
        reply = await self.llm.send_message(messages)
        await self.repo.add_message(conv_id, "assistant", reply)

        return AIChatResponse(conversation_id=conv_id, reply=reply)

    async def analyze_spending(self, user_id: int):
        conv = await self.repo.create_conversation(user_id)
        reply = await self.llm.send_message(
            [{"role": "user", "content": "Analyze my spending habits."}],
            system_prompt="You are a financial assistant.",
        )
        await self.repo.add_message(conv.id, "assistant", reply)
        return AIChatResponse(conversation_id=conv.id, reply=reply)


class LLMClient:
    """Отдельный клиент для общения с LLM API — сервис не знает деталей, как это работает."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    async def send_message(self, messages: list[dict], system_prompt: str = "") -> str:
        contents = []
        for m in messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config={"system_instruction": system_prompt} if system_prompt else None,
        )

        return response.text