"""Source content for the synthetic reports.

Two fictional patients with deliberately different profiles, só per-patient
retrieval can actually be tested: if one leaks into the other, the content
gives it away.

Genes, variants and risk figures are real and referenced (see
docs/data-sources.md). Patients, genotypes and ancestry percentages are made up.

Report text stays in Portuguese because it is domain content the patient reads.
"""

MARCA = "DOCUMENTO SINTÉTICO - USO ACADÊMICO - NÃO É UM LAUDO REAL"

REPORTS = [
    {
        "patient_id": "GEN-2026-00417",
        "nome": "Helena Vasconcelos Prado",
        "idade": 34,
        "sexo": "Feminino",
        "amostra": "Saliva, coletada em 12/03/2026",
        "emissao": "04/04/2026",
        "ancestralidade": {
            "resumo": (
                "A composição genômica indica origem majoritariamente europeia, com "
                "contribuição africana relevante e componente ameriundia menor, padrao "
                "compatível com a formação populacional do Sudeste brasileiro."
            ),
            "componentes": [
                ("Europa Ibérica", "41,2%", "Portugal e Espanha"),
                ("África Ocidental", "27,8%", "Golfo da Guiné, Nigéria e Benim"),
                ("Europa Italiana", "14,5%", "Sul da Itália"),
                ("Ameríndia", "11,1%", "Populações do Brasil central"),
                ("África Centro-Ocidental", "3,9%", "Angola e Congo"),
                ("Oriente Medio", "1,5%", "Levante"),
            ],
            "haplogrupo_materno": "L3e2b, linhagem materna de origem africana ocidental",
            "neandertal": "1,8% do genoma, dentro da média da população brasileira",
        },
        "predisposicoes": [
            {
                "condicao": "Trombofilia hereditária",
                "fonte": (
                    "Tosetto et al., Genetics of venous thrombosis (Elsevier); Blood 143(23):2425, 2024"
                    ", coorte FinnGen e UK Biobank"
                ),
                "gene": "F5",
                "variante": "rs6025 (Fator V de Leiden)",
                "genotipo": "Heterozigoto (G/A)",
                "risco": "Aumentado",
                "risco_relativo": "Cerca de 3x (a literatura reporta de 2x a 5x)",
                "risco_absoluto": (
                    "O risco na população geral gira em torno de 1 em 1000 pessoas por ano. "
                    "Com esta variante em heterozigose, sobe para algo entre 2 e 5 em 1000 "
                    "por ano. Isso significa que a grande maioria das pessoas portadoras "
                    "nunca desenvolve um evento trombótico."
                ),
                "interpretacao": (
                    "Portadores em heterozigose têm maior chance de trombose venosa, "
                    "especialmente em situações de imobilidade prolongada, cirurgia, "
                    "gestação ou uso de contraceptivo hormonal combinado. A informação e "
                    "acionável principalmente como contexto para decisões clínicas futuras."
                ),
                "acao": (
                    "Vale informar esta variante ao ginecologista antes de iniciar ou manter "
                    "contraceptivo hormonal, e ao cirurgião antes de qualquer procedimento."
                ),
            },
            {
                "condicao": "Deficiência de folato e hiper-homocisteinemia",
                "fonte": (
                    "BMC Cardiovascular Disorders, 2025, coorte multietnica; PMC1074713, homocisteína e"
                    " C677T"
                ),
                "gene": "MTHFR",
                "variante": "rs1801133 (C677T)",
                "genotipo": "Homozigoto (T/T)",
                "risco": "Levemente aumentado",
                "risco_relativo": "1,2x para elevação de homocisteína",
                "risco_absoluto": (
                    "A associação é modesta e fortemente influenciada pela dieta. Muitas "
                    "pessoas com este genótipo têm homocisteína normal."
                ),
                "interpretacao": (
                    "O genótipo T/T reduz a atividade da enzima MTHFR, o que pode elevar "
                    "homocisteína quando a ingestão de folato e baixa. E um achado comum: "
                    "a prevalência do genótipo TT na população geral fica entre 5 e 10%, variando "
                    "bastante entre populações. A atividade da enzima e cerca de 70% menor "
                    "que a do genótipo comum."
                ),
                "acao": (
                    "Dosagem de homocisteína e folato sérico em exame de rotina resolve a "
                    "dúvida com dado concreto, em vez de suposição a partir do genótipo."
                ),
            },
            {
                "condicao": "Doenca de Alzheimer de inicio tardio",
                "fonte": ("Meta-análise de variantes APOE na America Latina, PMC12927995"),
                "gene": "APOE",
                "variante": "rs429358 / rs7412",
                "genotipo": "e3/e3",
                "risco": "Padrao",
                "risco_relativo": "1,0x, equivalente a população geral",
                "risco_absoluto": "Sem elevação de risco atribuível a este gene.",
                "interpretacao": (
                    "O genótipo e3/e3 é o mais frequente na população e não confere aumento "
                    "de risco. Este resultado não exclui a doença, que tem múltiplas causas."
                ),
                "acao": "Nenhuma ação específica decorre deste resultado.",
            },
            {
                "condicao": "Intolerância a lactose do adulto",
                "fonte": ("Persistência de lactase associada a rs4988235, literatura estabelecida"),
                "gene": "MCM6 / LCT",
                "variante": "rs4988235",
                "genotipo": "Homozigoto (G/G)",
                "risco": "Compatível com intolerância",
                "risco_relativo": "Não aplicável",
                "risco_absoluto": (
                    "O genótipo indica provável redução da produção de lactase após a "
                    "infância. A tolerância real varia muito entre pessoas com o mesmo "
                    "genótipo."
                ),
                "interpretacao": (
                    "Este é o genótipo ancestral, presente na maioria da população mundial. "
                    "O sintoma, quando existe, é desconforto digestivo após laticínios."
                ),
                "acao": "A própria experiência com laticínios informa mais que o genótipo.",
            },
        ],
        "tracos": [
            ("Metabolismo de cafeína", "CYP1A2", "rs762551 A/C", "Metabolização intermediária"),
            ("Percepção de sabor amargo", "TAS2R38", "rs713598 G/C", "Percepção moderada"),
            ("Cor dos olhos", "HERC2", "rs12913832 A/A", "Probabilidade alta de olhos castanhos"),
            ("Tipo de cabelo", "TCHH", "rs11803731 T/T", "Tendência a cabelo ondulado"),
            (
                "Resposta ao exercicio",
                "ACTN3",
                "rs1815739 C/T",
                "Perfil misto, forca e resistência",
            ),
        ],
        "farmacogenetica": [
            (
                "Clopidogrel",
                "CYP2C19",
                "*1/*2",
                "Metabolizador intermediário",
                "Possível redução de eficácia. Decisao e exclusivamente do médico prescritor.",
            ),
            (
                "Varfarina",
                "VKORC1",
                "rs9923231 A/G",
                "Sensibilidade aumentada",
                "Pode demandar ajuste de dose, sempre sob acompanhamento médico.",
            ),
            (
                "Sinvastatina",
                "SLCO1B1",
                "rs4149056 T/T",
                "Metabolismo típico",
                "Sem alteração esperada de risco muscular.",
            ),
        ],
    },
    {
        "patient_id": "GEN-2026-00892",
        "nome": "Rogerio Kimura Tavares",
        "idade": 52,
        "sexo": "Masculino",
        "amostra": "Saliva, coletada em 27/03/2026",
        "emissao": "18/04/2026",
        "ancestralidade": {
            "resumo": (
                "A composição genômica indica origem predominantemente do Leste Asiático, "
                "com contribuição europeia iberica, padrao compatível com descendência "
                "japonesa em familia miscigenada no Brasil."
            ),
            "componentes": [
                ("Japão", "52,4%", "Honshu e Kyushu"),
                ("Europa Ibérica", "24,7%", "Portugal"),
                ("Coreia e Norte da China", "12,3%", "Peninsula coreana"),
                ("Ameríndia", "6,8%", "Populações do Brasil meridional"),
                ("África Ocidental", "2,4%", "Golfo da Guiné"),
                ("Sudeste Asiático", "1,4%", "Vietnã e sul da China"),
            ],
            "haplogrupo_materno": "D4b2, linhagem materna comum no Japão",
            "haplogrupo_paterno": "O-M122, linhagem paterna do Leste Asiático",
            "neandertal": "2,3% do genoma, levemente acima da média brasileira",
        },
        "predisposicoes": [
            {
                "condicao": "Diabetes tipo 2",
                "fonte": (
                    "Mutagenesis 28(1):25, meta-análise com 121.174 individuos; HuGE review PMC2653476"
                ),
                "gene": "TCF7L2",
                "variante": "rs7903146",
                "genotipo": "Heterozigoto (C/T)",
                "risco": "Aumentado",
                "risco_relativo": "1,41x para heterozigotos (IC 95%: 1,34 a 1,48)",
                "risco_absoluto": (
                    "Traduzido em números: se o risco típico ao longo da vida é de cerca de "
                    "10 em 100 pessoas, com esta variante fica em torno de 14 em 100. A "
                    "maioria dos portadores não desenvolve a doença, e peso, dieta e "
                    "atividade física pesam mais que o genótipo."
                ),
                "interpretacao": (
                    "Esta é a variante com associação mais consistente com diabetes tipo 2 "
                    "descrita até hoje. Ainda assim, é um fator entre muitos, é um dos "
                    "poucos onde o comportamento tem efeito comprovadamente maior."
                ),
                "acao": (
                    "Glicemia de jejum e hemoglobina glicada em exame de rotina mostram a "
                    "situação real, que é o dado que importa para conduta."
                ),
            },
            {
                "condicao": "Degeneração macular relacionada a idade",
                "fonte": (
                    "Maugeri et al., Acta Ophthalmologica, 2019, meta-análise estratificada por estagio"
                    " e etnia"
                ),
                "gene": "CFH",
                "variante": "rs1061170 (Y402H)",
                "genotipo": "Homozigoto (C/C)",
                "risco": "Aumentado",
                "risco_relativo": "De 2,45x a 5,57x conforme o estudo é a população",
                "risco_absoluto": (
                    "O risco típico após os 60 anos gira em torno de 2 em 100 pessoas. Com este "
                    "genótipo, sobe para uma faixa de 5 a 11 em 100, dependendo do estudo. "
                    "Mesmo no cenário mais alto, a maioria dos portadores não desenvolve "
                    "a condição."
                ),
                "interpretacao": (
                    "Trata-se de condição ocular associada ao envelhecimento. O achado e "
                    "acionável porque o acompanhamento oftalmológico periódico permite "
                    "detecção precoce."
                ),
                "acao": (
                    "Vale mencionar este resultado ao oftalmologista na próxima consulta de "
                    "rotina, para que ele decide a periodicidade adequada de exame de fundo "
                    "de olho."
                ),
            },
            {
                "condicao": "Doenca de Alzheimer de inicio tardio",
                "fonte": ("Meta-análise de variantes APOE na America Latina, PMC12927995"),
                "gene": "APOE",
                "variante": "rs429358 / rs7412",
                "genotipo": "e3/e4",
                "risco": "Aumentado",
                "risco_relativo": "2,59x em relação a e3/e3 (IC 95%: 2,31 a 2,91)",
                "risco_absoluto": (
                    "Este é um resultado que costuma assustar mais do que deveria. Ter uma "
                    "cópia do alelo e4 não significa que a doença vai acontecer: a maioria "
                    "das pessoas com e3/e4 nunca desenvolve Alzheimer, e parte das pessoas "
                    "que desenvolve não tem o alelo. O gene desloca probabilidade, não "
                    "determina desfecho."
                ),
                "interpretacao": (
                    "O APOE e4 é o fator genético mais estudado para Alzheimer tardio. Não "
                    "existe teste genético que diagnostique a doença, e não ha conduta "
                    "médica estabelecida que decorra apenas deste resultado."
                ),
                "acao": (
                    "Este é um resultado para conversar com um médico ou com um geneticista, "
                    "que pode contextualizar o achado junto ao histórico familiar. Não ha "
                    "ação que se tome sozinho a partir dele."
                ),
            },
            {
                "condicao": "Hemocromatose hereditária",
                "fonte": (
                    "Pooled analysis, PubMed 11399207; NEJM, doença por sobrecarga de ferro em hemocrom"
                    "atose HFE"
                ),
                "gene": "HFE",
                "variante": "rs1800562 (C282Y)",
                "genotipo": "Heterozigoto (G/A)",
                "risco": "Levemente aumentado",
                "risco_relativo": "OR 4,1 para sobrecarga de ferro (IC 95%: 2,9 a 5,8), com penetrância clinica baixa",
                "risco_absoluto": (
                    "Embora exista associação estatística com sobrecarga de ferro, portadores em "
                    "heterozigose raramente desenvolvem doença clinicamente relevante. Mesmo "
                    "entre homozigotos, a penetrância fica entre 24 e 43% nos homens e entre "
                    "1 e 14% nas mulheres. O achado tem mais valor como informação familiar "
                    "do que individual."
                ),
                "interpretacao": (
                    "Uma cópia da variante geralmente não causa a doença. Duas cópias "
                    "aumentam o risco de forma relevante, o que torna o dado útil caso "
                    "familiares venham a investigar."
                ),
                "acao": "Ferritina em exame de rotina esclarece se ha acúmulo real de ferro.",
            },
        ],
        "tracos": [
            ("Metabolismo de cafeína", "CYP1A2", "rs762551 C/C", "Metabolização lenta"),
            ("Rubor facial ao álcool", "ALDH2", "rs671 G/A", "Rubor provável após álcool"),
            ("Cor dos olhos", "HERC2", "rs12913832 A/A", "Probabilidade alta de olhos castanhos"),
            ("Tipo de cerume", "ABCC11", "rs17822931 T/T", "Cerume seco, comum no Leste Asiático"),
            ("Resposta ao exercicio", "ACTN3", "rs1815739 T/T", "Perfil orientado a resistência"),
        ],
        "farmacogenetica": [
            (
                "Clopidogrel",
                "CYP2C19",
                "*2/*2",
                "Metabolizador lento",
                (
                    "Redução significativa de eficácia esperada. Somente o médico prescritor "
                    "pode avaliar alternativa."
                ),
            ),
            (
                "Sinvastatina",
                "SLCO1B1",
                "rs4149056 C/C",
                "Transporte reduzido",
                "Maior chance de efeito muscular adverso em doses altas. Conduta e do médico.",
            ),
            (
                "Codeina",
                "CYP2D6",
                "*1/*1",
                "Metabolizador normal",
                "Resposta esperada dentro do típico.",
            ),
        ],
    },
]
