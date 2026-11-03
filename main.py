"""Local CLI. Customer identity is an operator-only demo context, not authentication."""
import argparse
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from src.agent import Agent
from src.tools import Store, Tools

ROOT = Path(__file__).resolve().parent


def main():
    load_dotenv(ROOT / '.env')
    parser = argparse.ArgumentParser(description='Empório da Música - atendimento local')
    parser.add_argument('--check-data', action='store_true')
    parser.add_argument('--demo-customer-id', type=int, help='Trusted local operator context only; not customer authentication')
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    try:
        store = Store(Path(os.getenv('DATA_DIR', str(ROOT / 'data' / 'original'))))
    except Exception as exc:
        parser.exit(2, f'Dados locais indisponíveis ou inválidos ({type(exc).__name__}). Consulte o README.\n')
    if args.check_data:
        print('Dados e políticas carregados e validados.')
        return
    if not os.getenv('OPENAI_API_KEY'):
        parser.exit(2, 'Configure OPENAI_API_KEY no arquivo .env. Use --check-data para validação sem credenciais.\n')
    client = OpenAI(timeout=30, max_retries=1)
    agent = Agent(client, Tools(store, args.demo_customer_id), os.getenv('OPENAI_MODEL','gpt-4.1-mini'))
    print('Empório da Música: Olá! Como posso ajudar? (digite sair para encerrar)')
    while True:
        try:
            message = input('Você: ')
        except (EOFError, KeyboardInterrupt):
            print('\nAté mais!')
            break
        if message.strip().lower() in {'sair','exit','quit'}:
            break
        print('Empório da Música:', agent.reply(message))


if __name__ == '__main__':
    main()
