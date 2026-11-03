"""Diagnose Gemini access without printing credentials or raw response bodies."""
from pathlib import Path
from dotenv import load_dotenv
from src.config import create_client, model_name
from src.errors import provider_diagnostic
from src.tools import Store, Tools

ROOT = Path(__file__).resolve().parents[1]


def main():
    load_dotenv(ROOT/'.env')
    try:
        with create_client(timeout=20,max_retries=0) as client:
            result=client.chat.completions.create(
                model=model_name(), messages=[{'role':'user','content':'Vocês têm violões até mil reais?'}],
                tools=Tools(Store(ROOT/'data'/'original')).schemas(),
                tool_choice='required',max_tokens=250,reasoning_effort='minimal')
            if not result.choices or not result.choices[0].message.tool_calls:
                raise ValueError('No tool call returned')
            print('Gemini request succeeded; function calling returned a tool call.')
    except ValueError:
        print('Verifique GEMINI_API_KEY no .env e a configuração de ferramentas/modelo.')
        raise SystemExit(1) from None
    except Exception as exc:
        category, hint = provider_diagnostic(exc)
        print('Diagnostic:', category)
        print(hint)
        raise SystemExit(1) from None


if __name__=='__main__':
    main()
