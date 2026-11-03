# 02-store

Status: ILLUSTRATIVE CONVERSATION; no LLM executed. Tool evidence below was executed against supplied data.

Order example uses operator-provided demo identity 3. This is not authentication.

**Cliente (cenário):** Qual é o endereço e o horário da loja?

**Resposta ilustrativa, escrita para revisão; não gerada pelo agente:** A loja fica na Rua 14 de Maio, 3200, Centro, Campo Grande/MS. Funciona de segunda a sexta, das 9h às 18h, e sábado, das 9h às 13h. Fecha aos domingos e feriados; datas especiais podem ter alterações.

## Executed tool evidence

```json
[
  {
    "tool": "get_store_information",
    "result": {
      "retrieved_pages": [
        1,
        2,
        6
      ],
      "passage_count": 4
    }
  }
]
```
