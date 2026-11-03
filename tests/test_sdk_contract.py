"""Exercise Gemini-compatible chat serialization using the installed SDK, offline."""
import json
import httpx2
from openai import OpenAI
from src.agent import Agent
from src.config import GEMINI_BASE_URL, create_client, model_name, DEFAULT_MODEL
import pytest


def test_gemini_sdk_contract(tools):
    requests=[]
    def handle(request):
        assert request.url.host=='generativelanguage.googleapis.com'
        assert request.url.path=='/v1beta/openai/chat/completions'
        body=json.loads(request.content)
        requests.append(body)
        if len(requests)==1:
            message={'role':'assistant','content':None,'tool_calls':[{'type':'function','id':'c1',
                'function':{'name':'get_product_details','arguments':'{"product_id":81}'},
                'extra_content':{'google':{'thought_signature':'test-signature'}}}]}
            reason='tool_calls'
        else:
            message={'role':'assistant','content':'O Yamaha C40 custa R$ 599,90 no catálogo.'}
            reason='stop'
        return httpx2.Response(200,json={'id':'test','object':'chat.completion','created':0,'model':DEFAULT_MODEL,
            'choices':[{'index':0,'message':message,'finish_reason':reason}]})
    with OpenAI(api_key='test-only',base_url=GEMINI_BASE_URL,
                http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),max_retries=0) as client:
        agent=Agent(client,tools,DEFAULT_MODEL)
        assert '599,90' in agent.reply('Qual o preço do C40?')
    assert len(requests)==2
    second=requests[1]['messages']
    assert any(i.get('role')=='tool' and '599.9' in i['content'] for i in second)
    call=next(i for i in second if i.get('tool_calls'))['tool_calls'][0]
    assert call['extra_content']['google']['thought_signature']=='test-signature'
    assert requests[0]['tools'][0]['function']['parameters']['additionalProperties'] is False
    assert requests[0]['tool_choice']=='required'
    assert 'store' not in requests[0]


def test_config_requires_gemini_key(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    monkeypatch.setenv('OPENAI_API_KEY','test-old-openai-key')
    with pytest.raises(ValueError,match='GEMINI_API_KEY'):
        create_client()


def test_config_targets_only_google(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','test-google-key')
    monkeypatch.setenv('OPENAI_BASE_URL','https://example.invalid/')
    with create_client() as client:
        assert str(client.base_url)==GEMINI_BASE_URL
        assert client.api_key=='test-google-key'
    monkeypatch.delenv('GEMINI_MODEL',raising=False)
    assert model_name()==DEFAULT_MODEL
    monkeypatch.setenv('GEMINI_MODEL','another-gemini-model')
    assert model_name()=='another-gemini-model'
