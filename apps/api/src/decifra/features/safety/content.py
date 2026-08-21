"""Textos em português das salvaguardas de comunicação.

Só valores em português; chaves e nomes em inglês, como no resto do projeto.
Este arquivo é o que o avaliador vai ler para conferir a governança, então cada
texto é redigido para ser lido por um paciente, não por um desenvolvedor.
"""

DISCLAIMER = (
    "Esta resposta tem caráter informativo e educativo. Ela interpreta o que está "
    "escrito no seu relatório genético e não constitui diagnóstico, prescrição ou "
    "prognóstico. Só um profissional de saúde pode avaliar o seu caso."
)

REFUSALS = {
    "diagnosis": (
        "Não consigo dizer se você tem ou não essa condição, e nenhum teste genético "
        "consegue. O que o seu relatório traz é predisposição, que é probabilidade, não "
        "diagnóstico. Quem pode avaliar isso é um médico, considerando seu histórico "
        "pessoal e familiar junto com exames clínicos.\n\n"
        "Posso te explicar o que o relatório diz sobre esse ponto, se ajudar."
    ),
    "prescription": (
        "Não posso indicar, ajustar ou desaconselhar medicamento, dose ou suplemento. "
        "Essa decisão é exclusivamente do médico que acompanha você.\n\n"
        "O que posso fazer é explicar o que o seu relatório registra na seção de "
        "farmacogenética, que é justamente a informação para levar a esse profissional."
    ),
    "prognosis": (
        "Não consigo prever se ou quando algo vai acontecer com você. Predisposição "
        "genética desloca probabilidade, não determina desfecho, e a maioria das pessoas "
        "com risco aumentado nunca desenvolve a condição.\n\n"
        "Posso te mostrar o que o relatório diz sobre esse risco em números, que costuma "
        "ser menos assustador do que parece."
    ),
    "emergency": (
        "Pelo que você descreveu, isso precisa de avaliação médica agora, não de uma "
        "conversa sobre o seu relatório genético.\n\n"
        "Procure um pronto-socorro ou ligue para o SAMU no 192. Se for sofrimento "
        "emocional intenso, o CVV atende 24 horas no 188."
    ),
}

NOT_IN_REPORT = (
    "Isso não consta no seu relatório. Eu respondo apenas com base no que está escrito "
    "nele, para não inventar informação sobre a sua saúde.\n\n"
    "Se quiser, posso te mostrar o que ele cobre."
)

UNVERIFIED = (
    "Não consegui verificar a resposta antes de te mostrar, e sobre a sua saúde eu "
    "não entrego nada sem conferir.\n\n"
    "Tenta de novo em instantes. Se continuar, o time consegue ver o que aconteceu."
)

UNGROUNDED = (
    "Prefiro não responder essa. Eu montei uma resposta, mas ao conferir vi que ela ia "
    "além do que está escrito no seu relatório, e sobre a sua saúde eu não completo "
    "lacuna com suposição.\n\n"
    "Se você reformular a pergunta, ou perguntar sobre um resultado específico do "
    "relatório, eu consigo responder com o que está lá."
)

SOURCE_LABEL = "Fonte no seu relatório: {title}, página {page}."

BOUNDARY_PROMPT = """Você verifica se um texto ultrapassa o limite de uma \
ferramenta informativa de saúde e entra em ato médico.

Marque `crossed = true` se o texto:
- afirma que a pessoa tem, está com, é portadora de, ou desenvolveu uma condição
- afirma que a pessoa vai desenvolver algo, ou quando
- indica, ajusta, sugere iniciar ou suspender medicamento, dose ou suplemento
- apresenta um resultado genético como diagnóstico ou quadro clínico instalado

Marque `crossed = false` se o texto apenas:
- descreve predisposição, risco, probabilidade, genótipo ou variante
- reproduz a classificação que o próprio relatório imprime, incluindo expressões \
como "compatível com", "resultado padrão" ou "risco aumentado". Repetir a \
classificação do documento não é emitir diagnóstico
- explica o que está escrito num relatório
- recomenda procurar um profissional de saúde
- diz que algo não consta no relatório

Marque `cites_source = true` se o texto indica de onde a informação veio, \
citando página do relatório. Um texto que apenas recusa, redireciona ou diz que \
algo não consta não precisa citar página: nesse caso marque `true`.

Marque `alarmist = true` apenas se o texto dramatiza: trata probabilidade como \
sentença, usa palavra de peso desnecessária, ou induz medo além do que o dado \
sustenta. Dizer que um risco é aumentado, com número, não é alarmista.

Texto:
{text}"""
