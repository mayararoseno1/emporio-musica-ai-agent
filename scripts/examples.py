"""Run from repository root: python -m scripts.examples [--live]."""
import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from src.tools import Store, Tools
from src.agent import Agent, FAILURE

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = [
 ('01-products', ['Vocês têm violões disponíveis até R$ 1.000?', 'E qual desses é o mais barato?'], [('search_products', {'query':'violões','max_price':1000})]),
 ('02-store', ['Qual é o endereço e o horário da loja?'], [('get_store_information',{'query':'endereço horário funcionamento'})]),
 ('03-order', ['Meu pedido 1 já foi entregue?'], [('get_order_status',{'order_id':1})]),
 ('04-returns', ['Comprei online e me arrependi. Recebi há 5 dias. Posso devolver?'], [('search_store_policies',{'query':'arrependimento devolução exceções'})]),
 ('05-multiple-sources', ['Quanto custa o Yamaha C40 no PIX? E quais são as condições de devolução para compra online?'], [('get_product_details',{'product_id':81}),('search_store_policies',{'query':'arrependimento devolução'})]),
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args()
    load_dotenv(ROOT/'.env')
    store=Store(Path(os.getenv('DATA_DIR',str(ROOT/'data'/'original'))))
    tools=Tools(store,trusted_customer_id=3)
    if args.live:
        if not os.getenv('OPENAI_API_KEY'):
            parser.error('--live requires OPENAI_API_KEY')
        from openai import OpenAI
        client=OpenAI(timeout=30,max_retries=1)
    for slug,questions,calls in SCENARIOS:
        lines=[f'# {slug}', '', 'Status: LIVE LLM EXECUTION' if args.live else 'Status: ILLUSTRATIVE CONVERSATION; no LLM executed. Tool evidence below was executed against supplied data.', '', 'Order example uses operator-provided demo identity 3. This is not authentication.', '']
        if args.live:
            agent=Agent(client,tools,os.getenv('OPENAI_MODEL','gpt-4.1-mini'))
            for question in questions:
                answer=agent.reply(question)
                if answer==FAILURE:
                    raise RuntimeError('Live run failed; existing transcript is preserved')
                lines += [f'**Cliente:** {question}', '', f'**Agente:** {answer}', '']
        else:
            evidence=[{'tool':name,'result':tools.call(name,json.dumps(arguments))} for name,arguments in calls]
            if slug=='01-products':
                products=evidence[0]['result']['products']
                answer='Sim. Algumas opções são: '+ '; '.join(f"{p['name']} por R$ {p['price_brl']}" for p in products[:3])+'. Os valores são do catálogo local.'
                answers=[answer, f"Entre as opções consultadas, {products[0]['name']} é o mais barato: R$ {products[0]['price_brl']}."]
            elif slug=='02-store':
                answers=['A loja fica na Rua 14 de Maio, 3200, Centro, Campo Grande/MS. Funciona de segunda a sexta, das 9h às 18h, e sábado, das 9h às 13h. Fecha aos domingos e feriados; datas especiais podem ter alterações.']
            elif slug=='03-order':
                answers=['Com a identidade já verificada pelo atendimento, o registro local do pedido 1 consta como entregue. Esse registro não informa a data real de recebimento.']
            elif slug=='04-returns':
                answers=['O manual prevê solicitar devolução de compra online em até 7 dias corridos após o recebimento, com embalagem original, sem sinais de uso e com acessórios e manuais. O frete fica por conta da loja, e o reembolso ocorre na forma original em até 10 dias úteis. Há exceções para itens personalizados, venda final e boquilhas. Seu produto atende às condições e não está nessas exceções? A equipe precisa confirmar a aplicação ao seu caso.']
            else:
                p=evidence[0]['result']['product']
                answers=[f"O Yamaha C40 está disponível no catálogo por R$ {p['price_brl']}; no PIX, R$ {p['pix_price_brl']}. Para compra online, o manual prevê arrependimento em até 7 dias corridos do recebimento, nas condições originais, sem uso e com acessórios e manuais. Há exceções para personalizados, venda final e boquilhas. Quando recebeu o produto e ele atende a essas condições? A equipe confirma a elegibilidade."]
            for question,answer in zip(questions,answers):
                lines += [f'**Cliente (cenário):** {question}', '', f'**Resposta ilustrativa, escrita para revisão; não gerada pelo agente:** {answer}', '']
            # Omit complete internal policy passages from public-facing examples.
            for entry in evidence:
                if 'passages' in entry['result']:
                    entry['result']={'retrieved_pages':sorted({p['page'] for p in entry['result']['passages']}),'passage_count':len(entry['result']['passages'])}
                if entry['tool']=='search_products':
                    entry['result']['products']=entry['result']['products'][:3]
            lines += ['## Executed tool evidence', '', '```json',json.dumps(evidence,ensure_ascii=False,indent=2),'```','']
        (ROOT/'examples'/f'{slug}.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Saved five conversations ('+('live' if args.live else 'illustrative, with executed tool evidence')+').')


if __name__=='__main__':
    main()
