"""Local CLI. Customer identity is an operator-only demo context, not authentication."""
import argparse
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from src.config import create_client, model_name
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
    try:
        client = create_client()
    except ValueError as exc:
        parser.exit(2, str(exc) + '\n')
    agent = Agent(client, Tools(store, args.demo_customer_id), model_name())
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
