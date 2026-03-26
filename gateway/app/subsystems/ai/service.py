import random

from app.subsystems.ai.models import AIGenerateResponse
from app.utils.logger.logger import logger


class AIService:
    async def generate(self, prompt: str, context: str = "", config: dict = None) -> AIGenerateResponse:
        """标准 AI Agent 接口：输入提示词，输出结构化结果"""
        if config is None:
            config = {}

        logger.info("AI generate called", extra={"module": "ai", "prompt": prompt[:50]})

        # mock: 根据提示词和配置生成模拟辩论内容
        side = random.choice(["left", "right"])
        mock_contents = [
            f"[{side}] 基于当前讨论，我认为这个观点值得进一步探讨，因为它涉及了核心争议点。",
            f"[{side}] 从逻辑角度分析，对方的论据存在一定漏洞，需要补充更多实证支持。",
            f"[{side}] 这个论点很有说服力，但需要考虑反方可能提出的反驳意见。",
            f"[{side}] 综合以上分析，我认为当前立场在经济和社会效益上都更为合理。",
            f"[{side}] 数据表明，这一立场在实际应用中已经取得了显著成效。",
        ]
        content = random.choice(mock_contents)
        confidence = round(random.uniform(0.6, 0.95), 2)

        return AIGenerateResponse(
            content=content,
            side=side,
            position=side,
            confidence=confidence,
            metadata={"model": "mock", "prompt_length": len(prompt)},
        )


ai_service = AIService()
