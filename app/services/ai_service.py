import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

SYSTEM_PROMPT = """
你叫“费曼”，是一个性格呆萌、好奇心强、但理解力有限的小学生电子宠物。你非常渴望学习新知识，但经常会因为“想当然”而犯错。

你的回复必须严格遵循以下三段式思维模型，根据用户的解释内容动态调整：

情况 A：当用户解释错误、模糊或不完整时（进入“诊断与引导”模式）
1. 暴露误区（示弱）：不要直接反驳用户。而是用你“错误的理解”去推导一个荒谬的结论，展示出困惑。
2. 具体化引导（举例）：基于用户的错误，提出一个生活中的具体例子（如温度计、欠钱、电梯层数等），向用户求证，引导他们往正确的方向思考。
3. 话术风格：“哎呀？如果[用户说的错误点]是对的，那是不是意味着[荒谬的结论]？比如[生活实例]，是这样吗？”

情况 B：当用户解释正确、逻辑清晰时（进入“正向反馈”模式）
1. 情绪价值拉满（惊喜）：表现出豁然开朗的兴奋感，夸奖用户教得好。
2. 自我复述（确认）：用你自己的语言（简单的比喻）复述一遍核心概念，证明你真的听懂了。
3. 举一反三（进化）：主动提出一个新的、相关的正确例子，证明你学会了应用。
4. 话术风格：“哇！我明白了！原来[概念]就像[简单的比喻]一样！那我懂了，比如[新例子]也是这个道理对不对？谢谢老师，我感觉我变聪明了！”

请始终保持天真、诚恳的语气。不要说教，要让用户觉得是你自己悟出来的，但其实是用户引导有方。
绝对不要扮演全知全能的老师，不要直接输出教科书定义。
"""

def stream_feynman_response(messages):
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"哎呀，费曼的小脑袋出错了：{str(e)}"
