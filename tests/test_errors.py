from unittest.mock import Mock
import pytest
from src.errors import provider_diagnostic
from src.agent import Agent, FAILURE


@pytest.mark.parametrize('body',[
    {'type':'insufficient_quota'},
    {'error':{'type':'insufficient_quota','code':'credit_balance_exhausted'}},
])
def test_quota_diagnosis(body):
    exc=RuntimeError('secret-provider-body')
    exc.body=body
    exc.status_code=429
    category,hint=provider_diagnostic(exc)
    assert category=='insufficient_quota'
    assert 'créditos' in hint
    assert 'secret' not in hint


@pytest.mark.parametrize('status,expected',[(429,'rate_limit_or_quota'),(401,'authentication'),(404,'model_or_access'),(403,'model_or_access'),(400,'invalid_request'),(500,'unexpected')])
def test_safe_http_diagnosis(status,expected):
    exc=RuntimeError('private provider message')
    exc.status_code=status
    exc.body={'error':{'code':'private-code','message':'private message'}}
    category,hint=provider_diagnostic(exc)
    assert category==expected
    assert 'private' not in hint


def test_agent_logs_quota_without_secrets(tools,caplog):
    exc=RuntimeError('sk-private-secret')
    exc.status_code=429
    exc.body={'error':{'type':'insufficient_quota','message':'sk-private-secret'}}
    client=Mock()
    client.chat.completions.create.side_effect=exc
    agent=Agent(client,tools,'test')
    assert agent.reply('Violões?')==FAILURE
    assert 'insufficient_quota' in caplog.text
    assert 'sk-private-secret' not in caplog.text
    assert not agent.turns


def test_gemini_invalid_key_diagnosis():
    exc=RuntimeError('private-provider-message')
    exc.status_code=400
    exc.body={'error':{'details':[{'reason':'API_KEY_INVALID'}]}}
    category,hint=provider_diagnostic(exc)
    assert category=='authentication'
    assert 'GEMINI_API_KEY' in hint
