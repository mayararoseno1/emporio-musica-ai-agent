"""Safe operator diagnostics: never expose provider bodies or credentials."""


def provider_diagnostic(exc: Exception) -> tuple[str, str]:
    body = getattr(exc, 'body', None)
    error = body.get('error', body) if isinstance(body, dict) else {}
    error = error if isinstance(error, dict) else {}
    # Only compare known values; arbitrary provider strings never reach logs.
    codes = (getattr(exc, 'code', None), error.get('code'), error.get('type'))
    if any(isinstance(code, str) and code in {
        'insufficient_quota', 'credit_balance_exhausted',
        'billing_hard_limit_reached', 'organization_usage_limit_exceeded',
        'project_spend_limit_exceeded', 'organization_spend_limit_exceeded',
    } for code in codes):
        return 'insufficient_quota', 'A API está sem cota disponível. Verifique créditos e limites de uso do projeto/organização na plataforma OpenAI.'
    status = getattr(exc, 'status_code', None)
    if status == 429:
        return 'rate_limit_or_quota', 'A API retornou 429. Verifique o limite temporário e a cota da API; o provedor não informou uma categoria reconhecida.'
    if status == 401:
        return 'authentication', 'A API recusou a autenticação. Verifique OPENAI_API_KEY e o projeto associado.'
    if status in (403, 404):
        return 'model_or_access', 'Verifique OPENAI_MODEL e a permissão de acesso do projeto ao modelo.'
    if status == 400:
        return 'invalid_request', 'A API recusou os parâmetros da chamada. Revise o contrato da integração.'
    if type(exc).__name__ in {'APIConnectionError', 'APITimeoutError'}:
        return 'connection', 'Não foi possível conectar à API. Verifique conexão, proxy e firewall.'
    return 'unexpected', 'Falha não classificada. Execute os testes locais e o diagnóstico da API.'
