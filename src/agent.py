"""Bounded Gemini function-calling loop, with atomic conversation history."""
import json
import logging
from collections import deque
from .prompts import SYSTEM_PROMPT
from .errors import provider_diagnostic

log = logging.getLogger(__name__)
FAILURE = 'Não consegui consultar as informações agora. Tente novamente em instantes ou procure a equipe da loja.'


class Agent:
    def __init__(self, client, tools, model: str):
        self.client, self.tools, self.model = client, tools, model
        self.turns = deque(maxlen=8)
        self.last_trace = []

    def reply(self, message: str) -> str:
        if not isinstance(message, str) or not message.strip() or len(message) > 4000:
            return 'Envie uma mensagem de até 4.000 caracteres para eu ajudar.'
        conversation = [item for turn in self.turns for item in turn]
        current = [{'role':'user','content':message}]
        self.last_trace = []
        try:
            for step in range(6):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{'role':'system','content':SYSTEM_PROMPT}] + conversation + current,
                    tools=self.tools.schemas(), tool_choice='required' if step == 0 else 'auto',
                    max_tokens=1800, reasoning_effort='minimal')
                choice = response.choices[0]
                reply = choice.message
                calls = reply.tool_calls or []
                # Never keep truncated responses or execute incomplete tool arguments.
                if choice.finish_reason not in {'stop','tool_calls'}:
                    return FAILURE
                if not calls:
                    answer = (reply.content or '').strip()
                    if not answer:
                        return FAILURE
                    current.append({'role':'assistant','content':answer})
                    self.turns.append(current)
                    return answer
                if len(calls) > 8:
                    return FAILURE
                # Preserve provider-specific tool-call metadata (including thought signatures).
                current.append({'role':'assistant','content':reply.content,
                                'tool_calls':[call.model_dump(exclude_none=True) for call in calls]})
                for call in calls:
                    result = self.tools.call(call.function.name, call.function.arguments)
                    self.last_trace.append({'tool':call.function.name,'result':result})
                    current.append({'role':'tool','tool_call_id':call.id,
                                    'content':json.dumps(result, ensure_ascii=False)})
        except Exception as exc:
            category, hint = provider_diagnostic(exc)
            log.error('Agent request failed [%s]: %s', category, hint)
        return FAILURE
