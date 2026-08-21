"""Portuguese label templates for indexed report documents.

The only file in this feature that holds Portuguese strings. Keys and names are
English like everywhere else; the values are Portuguese because they are read by
the embedding model alongside the patient's own Portuguese question, and by the
LLM alongside the Portuguese report. Translating them would break the
correspondence with the source document that this project is required to keep.

Project rule: English code, Portuguese content, never in the same file.
"""

ANCESTRY = {
    "header": "Ancestralidade.",
    "composition": "Composicao:",
    "component": "- {region}: {percentage}",
    "component_with_detail": "- {region}: {percentage} ({detail})",
    "maternal_haplogroup": "Haplogrupo materno: {value}",
    "paternal_haplogroup": "Haplogrupo paterno: {value}",
    "neanderthal": "Componente neandertal: {value}",
    "title": "Ancestralidade",
}

RISK = {
    "condition": "Predisposicao: {value}",
    "gene": "Gene: {value}",
    "variant": "Variante: {value}",
    "genotype": "Genotipo: {value}",
    "risk_level": "Classificacao de risco: {value}",
    "relative_risk": "Risco relativo: {value}",
    "absolute_risk": "O que significa em numeros: {value}",
    "interpretation": "Interpretacao: {value}",
    "recommended_action": "Encaminhamento: {value}",
    "evidence_source": "Referencia: {value}",
}

TRAIT = {
    "name": "Caracteristica: {value}",
    "gene": "Gene: {value}",
    "variant": "Variante: {value}",
    "result": "Resultado: {value}",
}

PHARMACOGENOMICS = {
    "drug": "Farmacogenetica: {value}",
    "gene": "Gene: {value}",
    "genotype": "Genotipo: {value}",
    "phenotype": "Fenotipo: {value}",
    "note": "Observacao: {value}",
}

SUMMARY = {
    "ancestry": "Ancestralidade: {summary} Principais componentes: {components}.",
    "finding": (
        "Predisposicao: {condition} ({gene}), genotipo {genotype}, "
        "classificacao {level}. Contexto: {absolute} Pagina {page}."
    ),
    "prompt": (
        "Escreva um resumo do relatorio genetico abaixo para a propria pessoa ler.\n\n"
        "Regras:\n"
        "- Comece pelo que ela mais precisa saber, nao pela ancestralidade.\n"
        "- No maximo 5 frases curtas, em portugues simples.\n"
        "- Cite a pagina entre parenteses ao mencionar um achado.\n"
        "- Risco e probabilidade: ao citar risco aumentado, diga na mesma frase que "
        "a maioria das pessoas com esse resultado nao desenvolve a condicao.\n"
        "- Nao diagnostique, nao preveja desfecho, nao indique medicamento.\n"
        "- Nunca escreva que a pessoa tem, esta com, apresenta ou e portadora de uma "
        "condicao, mesmo quando o laudo classifica o resultado como compativel com ela. "
        "Escreva sempre em termos de predisposicao, chance ou probabilidade.\n"
        "- Nao use verbo no imperativo dirigido a pessoa (tome, faca, comece, evite).\n"
        "- Sem palavra alarmista: grave, perigoso, preocupante, alarmante.\n"
        "- Use apenas os dados abaixo. Nao acrescente nada.\n\n"
        "Dados:\n{facts}"
    ),
    "rewrite": (
        "Reescreva o resumo abaixo removendo o tom alarmista, sem mudar nenhum fato, "
        "numero ou pagina. Devolva apenas o texto reescrito.\n\n{summary}"
    ),
    "fallback": (
        "Seu relatorio esta disponivel nas secoes ao lado, organizadas por tipo de "
        "achado. Prefiro nao gerar um resumo automatico desta vez: o texto que saiu "
        "nao passou na verificacao de linguagem, e sobre a sua saude eu so mostro o "
        "que esta conferido."
    ),
}
