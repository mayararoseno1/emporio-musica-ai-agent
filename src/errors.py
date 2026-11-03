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
        return 'insufficient_quota', 'A API está sem cota disponível. Verifique a cota gratuita, créditos (se usar plano pago) e limites do projeto no Google AI Studio.'
    status = getattr(exc, 'status_code', None)
    details = error.get('details', [])
    if isinstance(details, list) and any(isinstance(d, dict) and d.get('reason') == 'API_KEY_INVALID' for d in details):
        return 'authentication', 'A chave Gemini foi recusada. Configure GEMINI_API_KEY com uma chave válida do Google AI Studio.'
    if status == 429:
        return 'rate_limit_or_quota', 'A API retornou 429. Verifique os limites por minuto/dia e a cota gratuita no Google AI Studio; o provedor não informou uma categoria reconhecida.'
    if status == 401:
        return 'authentication', 'A API recusou a autenticação. Verifique GEMINI_API_KEY e o projeto associado no Google AI Studio.'
    if status in (403, 404):
        return 'model_or_access', 'Verifique GEMINI_MODEL e a permissão de acesso do projeto ao modelo.'
    if status == 400:
        return 'invalid_request', 'A API recusou os parâmetros da chamada. Revise o contrato da integração.'
    if type(exc).__name__ in {'APIConnectionError', 'APITimeoutError'}:
        return 'connection', 'Não foi possível conectar à API. Verifique conexão, proxy e firewall.'
    return 'unexpected', 'Falha não classificada. Execute os testes locais e o diagnóstico da API.'
