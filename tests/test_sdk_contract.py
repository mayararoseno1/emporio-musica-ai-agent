"""Exercise the installed OpenAI SDK serialization through an in-memory HTTP transport."""
import json
import httpx2
from openai import OpenAI
from src.agent import Agent


def test_responses_sdk_contract(tools):
    requests=[]
    def handle(request):
        body=json.loads(request.content)
        requests.append(body)
        output = ([{'type':'function_call','id':'fc_1','call_id':'call_1','name':'get_product_details','arguments':'{"product_id":81}','status':'completed'}] if len(requests)==1 else [{'type':'message','id':'msg_1','role':'assistant','status':'completed','content':[{'type':'output_text','text':'O Yamaha C40 custa R$ 599,90 no catálogo.','annotations':[]}]}])
        return httpx2.Response(200,json={'id':'resp_test','object':'response','created_at':0,'model':'gpt-4.1-mini','status':'completed','output':output,'parallel_tool_calls':False,'tool_choice':'auto','tools':[]})
    client=OpenAI(api_key='test-only',http_client=httpx2.Client(transport=httpx2.MockTransport(handle)),max_retries=0)
    try:
        agent=Agent(client,tools,'gpt-4.1-mini')
        answer=agent.reply('Qual o preço do C40?')
        assert '599,90' in answer
        assert len(requests)==2
        second=requests[1]['input']
        assert any(i.get('type')=='function_call_output' and '599.9' in i['output'] for i in second)
        assert requests[0]['store'] is False
        assert requests[0]['tools'][0]['parameters']['additionalProperties'] is False
    finally:
        client.close()
