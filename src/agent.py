"""Bounded Responses API function-calling loop, with atomic conversation history."""
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
            # Force consultation on every turn; the LLM still chooses the relevant tool.
            # For off-topic/greetings it may retrieve scope/hours before replying.
            for step in range(6):
                response = self.client.responses.create(
                    model=self.model, instructions=SYSTEM_PROMPT,
                    input=conversation + current, tools=self.tools.schemas(),
                    tool_choice='required' if step == 0 else 'auto',
                    parallel_tool_calls=False, max_output_tokens=1800, store=False)
                calls = [item for item in response.output if item.type == 'function_call']
                if not calls:
                    answer = response.output_text.strip()
                    if not answer:
                        return FAILURE
                    current.extend(response.output)
                    self.turns.append(current)
                    return answer
                if len(calls) > 8:
                    return FAILURE
                current.extend(response.output)
                for call in calls:
                    result = self.tools.call(call.name, call.arguments)
                    self.last_trace.append({'tool':call.name,'result':result})
                    current.append({'type':'function_call_output','call_id':call.call_id,
                                    'output':json.dumps(result, ensure_ascii=False)})
        except Exception as exc:
            category, hint = provider_diagnostic(exc)
            log.error('Agent request failed [%s]: %s', category, hint)
        return FAILURE
