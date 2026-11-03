"""Diagnose provider access without printing credentials or raw response bodies."""
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from src.tools import Store, Tools


from src.errors import provider_diagnostic


def main():
    load_dotenv(Path(__file__).resolve().parents[1]/'.env')
    try:
        import os
        client=OpenAI(timeout=20,max_retries=0)
        result=client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),input='Vocês têm violões até mil reais?',tools=Tools(Store(Path('data/original'))).schemas(),tool_choice='required',max_output_tokens=150,store=False)
        print('Provider request succeeded. Output types:',[item.type for item in result.output])
    except Exception as exc:
        category, hint = provider_diagnostic(exc)
        print('Diagnostic:', category)
        print(hint)
        raise SystemExit(1) from None


if __name__=='__main__':
    main()
