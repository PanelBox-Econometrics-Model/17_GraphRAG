# Revisão de Literatura: GraphRAG para Instituições Financeiras

> Levantamento bibliográfico completo sobre GraphRAG, knowledge graphs e RAG aplicados ao setor financeiro.
> Última atualização: 2026-03-06

---

## 1. Papers Fundamentais de GraphRAG

### 1.1 From Local to Global: A Graph RAG Approach to Query-Focused Summarization

| Campo | Detalhe |
|-------|---------|
| **Autores** | Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2404.16130) — Microsoft Research |
| **Link** | https://arxiv.org/abs/2404.16130 |

**Contribuições principais:**
Paper fundacional do Microsoft GraphRAG. Propõe o uso de LLMs para construir um índice textual baseado em grafos em duas etapas: (1) derivar um knowledge graph de entidades a partir de documentos-fonte, e (2) pré-gerar resumos de comunidades para grupos de entidades relacionadas usando o algoritmo de detecção de comunidades Leiden. Para perguntas globais de sensemaking sobre datasets na faixa de 1 milhão de tokens, GraphRAG melhora substancialmente a abrangência e diversidade sobre baselines convencionais de RAG.

**Relevância para finanças:** Arquitetura fundacional aplicável a qualquer domínio com grandes corpora documentais, incluindo filings regulatórios, relatórios anuais e documentação de compliance.

---

### 1.2 Graph Retrieval-Augmented Generation: A Survey

| Campo | Detalhe |
|-------|---------|
| **Autores** | Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong, Yan Zhang, Siliang Tang |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2408.08921); ACM Transactions on Information Systems |
| **Link** | https://arxiv.org/abs/2408.08921 |

**Contribuições principais:**
Formaliza o workflow do GraphRAG em três estágios: Graph-Based Indexing, Graph-Guided Retrieval e Graph-Enhanced Generation. Define uma taxonomia das abordagens existentes e delineia tecnologias centrais e métodos de treinamento em cada estágio.

**Relevância para finanças:** Framework compreensivo para entender como RAG baseado em grafos pode ser aplicado em diferentes domínios, incluindo finanças.

---

### 1.3 Retrieval-Augmented Generation with Graphs (GraphRAG) — A Comprehensive Survey

| Campo | Detalhe |
|-------|---------|
| **Autores** | Haoyu Han et al. (18 autores) |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2501.00309) |
| **Link** | https://arxiv.org/abs/2501.00309 |

**Contribuições principais:**
Propõe um framework holístico do GraphRAG definindo componentes-chave: query processor, retriever, organizer, generator e data source. Cobre o ciclo de vida completo dos sistemas GraphRAG.

**Relevância para finanças:** Guia arquitetural para implementação de GraphRAG em ambientes enterprise, incluindo instituições financeiras.

---

### 1.4 GRAG: Graph Retrieval-Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Yuntong Hu, Zhihan Lei, Zheng Zhang, Bo Pan, Chen Ling, Liang Zhao |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2405.16506) |
| **Link** | https://arxiv.org/abs/2405.16506 |

**Contribuições principais:**
Aborda retrieval sobre documentos em rede (grafos de citação, mídias sociais, knowledge graphs). Propõe estratégia divide-and-conquer para retrieval ótimo de subgrafos em tempo linear. Incorpora grafos textuais em LLMs através de visões complementares de texto e grafo. Supera significativamente métodos RAG estado-da-arte em raciocínio multi-hop enquanto mitiga alucinações.

**Relevância para finanças:** Aplicável a redes financeiras onde entidades (empresas, reguladores, mercados) são interconectadas.

---

## 2. GraphRAG Aplicado a Finanças e Banking

### 2.1 HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction

| Campo | Detalhe |
|-------|---------|
| **Autores** | Bhaskarjit Sarmah (BlackRock), Benika Hall (NVIDIA), Rohan Rao (NVIDIA), Sunil Patel (NVIDIA), Stefano Pasquali (BlackRock), Dhagash Mehta (BlackRock) |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2408.04948) |
| **Link** | https://arxiv.org/abs/2408.04948 |

**Contribuições principais:**
Combina RAG baseado em Knowledge Graphs (GraphRAG) e VectorRAG para melhorar sistemas de Q&A na extração de informações de documentos financeiros, especificamente transcrições de earnings calls. HybridRAG supera tanto VectorRAG quanto GraphRAG individualmente nas etapas de retrieval e geração, em termos de acurácia de retrieval e qualidade de geração de respostas.

**Relevância para finanças:** Diretamente voltado para análise de documentos financeiros (earnings calls) com autores da indústria (BlackRock e NVIDIA). Demonstra aplicabilidade prática à extração de informações financeiras.

---

### 2.2 FinReflectKG: Agentic Construction and Evaluation of Financial Knowledge Graphs

| Campo | Detalhe |
|-------|---------|
| **Autores** | Abhinav Arun, Fabrizio Dimino, Tejas Prakash Agarwal, Bhaskarjit Sarmah, Stefano Pasquali |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2508.17906); ACM ICAIF 2025 |
| **Link** | https://arxiv.org/abs/2508.17906 |

**Contribuições principais:**
Disponibiliza um knowledge graph financeiro open-source construído a partir de SEC 10-K filings de todas as empresas S&P 100. Introduz pipeline de extração em três modos (single-pass, multi-pass, reflection-agent-based) com feedback driven por reflexão, alcançando 64.8% de compliance em regras de qualidade. Define tipos de entidades e relações pré-definidos e normaliza nomes de entidades (e.g., mapeando referências de empresas para tickers).

**Relevância para finanças:** Constrói KGs financeiros diretamente de SEC filings, a fonte primária de dados para análise financeira e compliance regulatório.

---

### 2.3 FinDKG: Dynamic Knowledge Graphs with Large Language Models for Detecting Global Trends in Financial Markets

| Campo | Detalhe |
|-------|---------|
| **Autores** | Victor Xiaohui Li et al. |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2407.10909); ACM ICAIF 2024 |
| **Link** | https://arxiv.org/abs/2407.10909 |

**Contribuições principais:**
Constrói um Financial Dynamic Knowledge Graph (FinDKG) com 12 meta-entity types e 15 relation types a partir de artigos de notícias financeiras. Propõe KGTransformer, uma arquitetura GNN baseada em atenção para análise temporal de knowledge graphs. Alcança ~15% de melhoria em métricas-chave de predição TKG (MRR, Hits@3,10). Aplicações incluem gestão de riscos, investimento temático e previsão econômica.

**Relevância para finanças:** Construído especificamente para análise de mercados financeiros globais, aplicável a investimento e gestão de riscos em banking.

---

### 2.4 GraphCompliance: Aligning Policy and Context Graphs for LLM-Based Regulatory Compliance

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2510.26309) |
| **Link** | https://arxiv.org/abs/2510.26309 |

**Contribuições principais:**
Representa textos regulatórios como Policy Graph e contextos de execução como Context Graph, alinhando-os. Usa triplas subject-action-object (SAO) e entity-relation. Em experimentos com 300 cenários reais derivados do GDPR em cinco tarefas de avaliação, obtém 4.1-7.2 pontos percentuais a mais em micro-F1 do que baselines LLM-only e RAG, com maior recall e menor taxa de falsos positivos.

**Relevância para finanças:** Diretamente aplicável à compliance com GDPR e processamento de textos regulatórios em instituições financeiras. A abordagem baseada em grafos para verificação de compliance é altamente relevante para Basel III, AML e KYC.

---

### 2.5 RAGulating Compliance: A Multi-Agent Knowledge Graph for Regulatory QA

| Campo | Detalhe |
|-------|---------|
| **Autores** | Hemant Sunil Jomraj, Bhavik Agarwal, Viktoria Rojkova |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2508.09893); ISWC 2025 |
| **Link** | https://arxiv.org/abs/2508.09893 |

**Contribuições principais:**
Framework multi-agente integrando Knowledge Graph de triplas regulatórias com RAG. Agentes constroem e mantêm um KG ontology-free extraindo triplas sujeito-predicado-objeto (SPO) de documentos regulatórios, limpando, normalizando, deduplicando e atualizando sistematicamente. Triplas são embutidas e armazenadas junto com seções textuais e metadados em um único vector database enriquecido.

**Relevância para finanças:** Aborda diretamente QA regulatório de compliance, necessidade central para bancos e instituições financeiras navegando paisagens regulatórias complexas.

---

### 2.6 FinanceBench: A New Benchmark for Financial Question Answering

| Campo | Detalhe |
|-------|---------|
| **Autores** | Pranab Islam et al. |
| **Ano** | 2023 |
| **Venue** | arXiv preprint (arXiv:2311.11944) |
| **Link** | https://arxiv.org/abs/2311.11944 |

**Contribuições principais:**
Introduz benchmark com 10.231 perguntas sobre empresas de capital aberto com respostas e evidências correspondentes vinculadas a SEC filings dos EUA. Apresenta tipos diversos de perguntas: busca de informação, raciocínio numérico e inferência lógica. Construído sobre 10-K, 10-Q, 8-K e relatórios de earnings.

**Relevância para finanças:** Benchmark primário para avaliar pipelines RAG no domínio financeiro, essencial para avaliar performance do GraphRAG em documentos financeiros.

---

### 2.7 Generative AI Enhanced Financial Risk Management Information Retrieval

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2504.06293) |
| **Link** | https://arxiv.org/html/2504.06293v2 |

**Contribuições principais:**
Aplica IA generativa e técnicas de retrieval à gestão de riscos financeiros, melhorando recuperação de informações de documentos relacionados a riscos.

**Relevância para finanças:** Voltado diretamente para gestão de riscos financeiros, função central em instituições bancárias.

---

## 3. Redução de Alucinações com GraphRAG

### 3.1 RAG vs. GraphRAG: A Systematic Evaluation and Key Insights

| Campo | Detalhe |
|-------|---------|
| **Autores** | Haoyu Han et al. (12 autores) |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2502.11371) |
| **Link** | https://arxiv.org/abs/2502.11371 |

**Contribuições principais:**
Avaliação sistemática de RAG e GraphRAG em tarefas benchmark incluindo Question Answering e Query-based Summarization. GraphRAG melhora métricas de Context Relevance, com perguntas multi-hop se beneficiando mais do retrieval estruturado. **GraphRAG alcança 86.31% vs. 72.36% para RAG em benchmarks RobustQA**, com raciocínio multi-hop reduzindo alucinações. Porém, Community-GraphRAG (Global) tende a alucinar quando a sumarização perde detalhes.

**Relevância para finanças:** Análise financeira frequentemente envolve raciocínio multi-hop (e.g., conectar performance de empresa entre subsidiárias, cadeias de suprimento), onde GraphRAG mostra maior vantagem.

---

### 3.2 How Significant Are the Real Performance Gains? An Unbiased Evaluation Framework for GraphRAG

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2506.06331) |
| **Link** | https://arxiv.org/html/2506.06331v1 |

**Contribuições principais:**
Avalia 3 métodos GraphRAG representativos (MGRAG, LightRAG, FGRAG) usando framework de avaliação imparcial. Descobre que taxas de vitória são geralmente menores que reportado anteriormente, com taxas de empate notáveis. Por exemplo, a taxa de vitória reportada do LightRAG de 66.70% vs. NaiveRAG foi reduzida para 39.06% sob avaliação imparcial.

**Relevância para finanças:** Crítico para instituições financeiras terem expectativas realistas das melhorias de performance do GraphRAG em vez de depender de benchmarks otimistas.

---

### 3.3 When to Use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2506.05690); ICLR 2026 |
| **Link** | https://arxiv.org/abs/2506.05690 |

**Contribuições principais:**
Investiga sistematicamente quando e por que GraphRAG tem sucesso. Fornece diretrizes práticas para aplicação. Nota que apesar da promessa conceitual do GraphRAG, ele frequentemente tem performance inferior ao RAG vanilla em muitas tarefas do mundo real. Introduz o benchmark GraphRAG-Bench.

**Relevância para finanças:** Guia crucial de tomada de decisão para instituições financeiras decidindo quando investir em GraphRAG vs. abordagens mais simples.

---

### 3.4 Think-on-Graph: Deep and Responsible Reasoning of Large Language Model on Knowledge Graph

| Campo | Detalhe |
|-------|---------|
| **Autores** | Jiashuo Sun et al. |
| **Ano** | 2024 |
| **Venue** | ICLR 2024 |
| **Link** | https://arxiv.org/abs/2307.07697 |

**Contribuições principais:**
Propõe paradigma de integração LLM-KG onde LLMs atuam como agentes para explorar interativamente entidades e relações em KGs. Implementa beam search iterativo em KGs para raciocínio. Aborda alucinação através de raciocínio fundamentado em KG. O sucessor, Think-on-Graph 2.0 (ICLR 2025), é um framework RAG híbrido que recupera iterativamente de fontes de conhecimento estruturadas e não estruturadas.

**Relevância para finanças:** Raciocínio passo-a-passo fundamentado em KG é essencial para análise financeira auditável onde transparência no raciocínio é exigida por reguladores.

---

### 3.5 HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

| Campo | Detalhe |
|-------|---------|
| **Autores** | Bernal Jimenez Gutierrez et al. (OSU NLP Group) |
| **Ano** | 2024 |
| **Venue** | NeurIPS 2024 |
| **Link** | https://arxiv.org/abs/2405.14831 |

**Contribuições principais:**
Inspirado na teoria de indexação hipocampal da memória humana de longo prazo. Orquestra sinergicamente LLMs, knowledge graphs e Personalized PageRank para imitar papéis do neocórtex e hipocampo. Supera métodos estado-da-arte em QA multi-hop em até 20%. Retrieval de passo único alcança performance comparável ou superior a retrieval iterativo (IRCoT) sendo **10-30x mais barato e 6-13x mais rápido**.

**Relevância para finanças:** A arquitetura inspirada em memória é relevante para instituições financeiras que precisam integrar continuamente conhecimento de documentos regulatórios e de mercado em evolução.

---

### 3.6 SubgraphRAG: Simple Is Effective — The Roles of Graphs and Large Language Models in Knowledge-Graph-Based RAG

| Campo | Detalhe |
|-------|---------|
| **Autores** | Haoming Li et al. |
| **Ano** | 2025 |
| **Venue** | ICLR 2025 |
| **Link** | https://arxiv.org/abs/2410.20724 |

**Contribuições principais:**
Extrai subgrafos representando conhecimento relevante predito, então LLMs raciocinam sobre eles. LLMs menores (Llama3.1-8B) entregam resultados competitivos com raciocínio explicável; GPT-4o alcança estado-da-arte sem fine-tuning. Demonstra raciocínio multi-hop robusto e generalização cross-dataset efetiva. Reduz alucinações melhorando o fundamentação das respostas.

**Relevância para finanças:** Raciocínio explicável é crítico para auditorias regulatórias em banking; a capacidade de rastrear respostas até evidências específicas do subgrafo suporta requisitos de compliance.

---

## 4. Eficiência de Tokens e Economia

### 4.1 TERAG: Token-Efficient Graph-Based Retrieval-Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2509.18667) |
| **Link** | https://arxiv.org/abs/2509.18667 |

**Contribuições principais:**
Aborda o alto custo de uso de tokens LLM durante construção de grafos. Inspirado no HippoRAG, incorpora Personalized PageRank durante retrieval. **Alcança pelo menos 80% da acurácia de métodos Graph-based RAG amplamente usados consumindo apenas 3%-11% dos tokens de saída.** Torna deployment em larga escala prático.

**Relevância para finanças:** Redução de custo de tokens é crítica para instituições financeiras processando grandes volumes de documentos (10-Ks, filings regulatórios) onde custos de API LLM podem ser proibitivos.

---

### 4.2 LazyGraphRAG: Setting a New Standard for Quality and Cost

| Campo | Detalhe |
|-------|---------|
| **Autores** | Microsoft Research (Darren Edge et al.) |
| **Ano** | 2024-2025 |
| **Venue** | Microsoft Research Blog / Technical Report |
| **Link** | https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/ |

**Contribuições principais:**
Não requer sumarização prévia dos dados-fonte, evitando custos proibitivos de indexação up-front. **Custos de indexação são idênticos ao vector RAG e 0.1% dos custos do GraphRAG completo.** Mostra qualidade de resposta comparável ao GraphRAG Global Search com **custo de query 700x menor**. Combina busca best-first e breadth-first em aprofundamento iterativo.

**Relevância para finanças:** A redução dramática de custos (0.1% indexação, 700x mais barato em queries) torna GraphRAG prático para instituições financeiras com grandes repositórios documentais e sensibilidade a custos.

---

### 4.3 LightRAG: Simple and Fast Retrieval-Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Zirui Guo et al. |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2410.05779) |
| **Link** | https://arxiv.org/abs/2410.05779 |

**Contribuições principais:**
Incorpora estruturas de grafo em indexação textual com retrieval dual-level (descoberta de conhecimento de baixo e alto nível). Suporta atualizações incrementais sem reconstrução completa do grafo. Integra estruturas de grafo com representações vetoriais. **Alcança 200ms de tempo médio de resposta.**

**Relevância para finanças:** A capacidade de atualização incremental é essencial para instituições financeiras que recebem continuamente atualizações regulatórias e dados de mercado.

---

### 4.4 E2GraphRAG: Streamlining Graph-based RAG for High Efficiency and Effectiveness

| Campo | Detalhe |
|-------|---------|
| **Autores** | YiBo Zhao et al. |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2505.24226) |
| **Link** | https://arxiv.org/abs/2505.24226 |

**Contribuições principais:**
Constrói árvore de resumos com LLMs e grafo de entidades com SpaCy, construindo índices bidirecionais entre entidades e chunks. **Alcança até 10x mais rápido em indexação que GraphRAG e 100x speedup sobre LightRAG em retrieval** mantendo performance competitiva em QA.

**Relevância para finanças:** Melhorias massivas de velocidade tornam processamento em tempo real ou quase-real de documentos financeiros viável.

---

### 4.5 PolyG: Adaptive Graph Traversal for Diverse GraphRAG Questions

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2504.02112) |
| **Link** | https://arxiv.org/abs/2504.02112 |

**Contribuições principais:**
Primeiro query planner para GraphRAG. Decompõe e categoriza perguntas segundo taxonomia proposta, gerando dinamicamente queries Cypher para retrieval em banco de grafos. **Alcança 75% de taxa de vitória em qualidade de geração com até 4x speedup e 95% de redução de tokens** comparado a baselines de estratégia fixa.

**Relevância para finanças:** O planejamento adaptativo de queries é valioso para sistemas de QA financeiros que lidam com tipos diversos de perguntas (lookups factuais, raciocínio numérico, análise de tendências).

---

### 4.6 RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

| Campo | Detalhe |
|-------|---------|
| **Autores** | Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh Khanna, Anna Goldie, Christopher D. Manning |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2401.18059); ICLR 2024 |
| **Link** | https://arxiv.org/abs/2401.18059 |

**Contribuições principais:**
Recursivamente embute, clusteriza e resume chunks de texto, construindo uma árvore com diferentes níveis de sumarização de baixo para cima. Na inferência, recupera através de diferentes níveis de abstração. **Melhora a melhor performance no benchmark QuALITY em 20% de acurácia absoluta** com GPT-4.

**Relevância para finanças:** Retrieval de estrutura em árvore é bem adequado para documentos financeiros hierárquicos (relatórios anuais com seções, sub-seções, notas de rodapé).

---

## 5. Segurança em RAG para Finanças

### 5.1 RAG Security and Privacy: Formalizing the Threat Model and Attack Surface

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2509.20324) |
| **Link** | https://arxiv.org/html/2509.20324v1 |

**Contribuições principais:**
Propõe o primeiro modelo formal de ameaças para sistemas RAG. Aborda especificamente contextos financeiros: um usuário malicioso pode sondar o modelo para verificar se relatórios de auditoria confidenciais ou estratégias de investimento estão presentes no banco de retrieval. Categoriza vetores de ataque através do pipeline RAG.

**Relevância para finanças:** Modela diretamente ameaças relevantes para instituições financeiras, incluindo ataques direcionados a relatórios de auditoria confidenciais e estratégias de investimento proprietárias.

---

### 5.2 Privacy-Aware RAG: Secure and Isolated Knowledge Retrieval

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2503.15548) |
| **Link** | https://arxiv.org/html/2503.15548v1 |

**Contribuições principais:**
Propõe metodologia avançada de criptografia para sistemas RAG. O Método B usa derivação de chave dinâmica encadeada para maior proteção de dados sensíveis. Especificamente projetado para ambientes de alto risco como healthcare e finanças.

**Relevância para finanças:** Aborda diretamente a necessidade de retrieval de conhecimento criptografado e isolado em instituições financeiras lidando com dados sensíveis de clientes e regulatórios.

---

### 5.3 Provably Secure Retrieval-Augmented Generation (SAG)

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2508.01084) |
| **Link** | https://arxiv.org/html/2508.01084v1 |

**Contribuições principais:**
Propõe o primeiro framework provavelmente seguro para sistemas RAG. Emprega esquema de criptografia completa pré-armazenamento garantindo proteção dual de conteúdo recuperado e embeddings vetoriais. Fornece provas formais de segurança verificando confidencialidade e integridade sob modelo computacional de segurança.

**Relevância para finanças:** Provas formais de segurança são essenciais para instituições financeiras sujeitas a escrutínio regulatório sobre proteção de dados (LGPD, GDPR, SOX, Basel III).

---

### 5.4 Exposing Privacy Risks in Graph Retrieval-Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2508.17222) |
| **Link** | https://arxiv.org/pdf/2508.17222 |

**Contribuições principais:**
Testa vazamento de privacidade em três sistemas RAG: Native RAG, GraphRAG e LightRAG. **Revela trade-off crítico: embora sistemas GraphRAG possam reduzir vazamento de texto bruto, são significativamente mais vulneráveis à extração de informações estruturadas de entidades e relacionamentos.**

**Relevância para finanças:** Alerta crítico para instituições financeiras: GraphRAG pode inadvertidamente expor informações estruturadas sobre entidades (empresas, transações, relacionamentos) mesmo enquanto protege texto bruto.

---

### 5.5 Membership Inference Attacks Against Retrieval Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2405.20446) |
| **Link** | https://arxiv.org/abs/2405.20446 |

**Contribuições principais:**
Demonstra que pertencimento de documentos em bancos RAG pode ser determinado através de prompts artesanais em configurações black-box e gray-box. Propõe S2MIA, ataque de inferência de pertencimento usando similaridade semântica entre amostras e conteúdo gerado pelo RAG.

**Relevância para finanças:** Instituições financeiras precisam estar cientes de que adversários podem potencialmente determinar se documentos financeiros específicos (e.g., filings de fusão, relatórios de auditoria) existem em seu sistema RAG.

---

### 5.6 FairRAG: A Privacy-Preserving Framework

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | Applied Sciences (MIT Open Access) |
| **Link** | https://dspace.mit.edu/bitstream/handle/1721.1/162375/applsci-15-08282.pdf |

**Contribuições principais:**
Aplica privacidade diferencial para criar base de conhecimento estática segura. Alcança alta acurácia preditiva operando sob garantias formais de privacidade diferencial.

**Relevância para finanças:** Privacidade diferencial é uma abordagem matematicamente rigorosa que pode satisfazer requisitos regulatórios de proteção de dados em serviços financeiros.

---

## 6. Benchmarks de Performance

### 6.1 Benchmarking Vector, Graph and Hybrid Retrieval

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | arXiv preprint (arXiv:2507.03608) |
| **Link** | https://arxiv.org/pdf/2507.03608 |

**Contribuições principais:**
Compara arquiteturas de retrieval vetorial, grafo e híbrido. **GraphRAG entrega 1.5x melhor acurácia geral e 2x melhor em queries complexas, mas com 2.4x maior latência em média.** Arquiteturas GraphRAG híbridas demonstram forte potencial para raciocínio multi-hop.

**Relevância para finanças:** Fornece dados concretos de tradeoff latência/acurácia que instituições financeiras precisam para design de sistemas orientados a SLA.

---

### 6.2 GFM-RAG: Graph Foundation Model for Retrieval Augmented Generation

| Campo | Detalhe |
|-------|---------|
| **Autores** | Linhao Luo et al. |
| **Ano** | 2025 |
| **Venue** | NeurIPS 2025; arXiv preprint (arXiv:2502.01113) |
| **Link** | https://arxiv.org/abs/2502.01113 |

**Contribuições principais:**
Primeiro graph foundation model aplicável a datasets não vistos sem fine-tuning. GNN de 8M parâmetros treinada em 60 knowledge graphs com mais de 14M triplas e 700k documentos. Permite retrieval multi-hop eficiente em passo único. Alcança estado-da-arte em três datasets de QA multi-hop e sete datasets de RAG de domínio específico.

**Relevância para finanças:** Abordagem de foundation model significa que instituições financeiras podem fazer deploy de GraphRAG sem fine-tuning caro específico de domínio.

---

### 6.3 Maximizing RAG Efficiency: A Comparative Analysis of RAG Methods

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | Natural Language Processing (Cambridge University Press), 31, pp. 1-25 |
| **Link** | https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D7B259BCD35586E04358DF06006E0A85/S2977042424000530a.pdf |

**Contribuições principais:**
Otimização por grid-search de 23.625 iterações avaliando múltiplos métodos RAG através de vectorstores, modelos de embedding e LLMs. O método "Reciprocal" demonstrou **12.5% de redução no uso de tokens**; o método "Refine" alcançou **18.6% de redução**.

**Relevância para finanças:** Comparação sistemática ajuda instituições financeiras a selecionar configurações RAG ótimas para seus tipos específicos de documentos e padrões de query.

---

## 7. Knowledge Graphs em Finanças

### 7.1 KG-RAG for SEC 10-Q Filings (Vector Institute)

| Campo | Detalhe |
|-------|---------|
| **Autores** | Vector Institute research team |
| **Ano** | 2024-2025 |
| **Venue** | Open-source framework (GitHub) |
| **Link** | https://github.com/VectorInstitute/kg-rag |

**Contribuições principais:**
Implementa framework compreensivo para Knowledge Graph Retrieval Augmented Generation focado em dados financeiros de SEC 10-Q filings. Explora como knowledge graphs melhoram information retrieval e question answering comparado a abordagens baseline.

**Relevância para finanças:** Voltado diretamente a SEC filings, demonstrando implementação prática de KG-RAG para análise financeira.

---

### 7.2 Knowledge Graph-Guided Retrieval Augmented Generation (KG2RAG)

| Campo | Detalhe |
|-------|---------|
| **Autores** | Xiangrong Zhu, Yuexiang Xie, Yi Liu, Yaliang Li, Wei Hu |
| **Ano** | 2025 |
| **Venue** | NAACL 2025 (Long Papers, pp. 8912-8924) |
| **Link** | https://aclanthology.org/2025.naacl-long.449/ |

**Contribuições principais:**
Usa knowledge graphs para fornecer relações em nível de fato entre chunks, melhorando diversidade e coerência. Emprega expansão de chunks guiada por KG e organização de chunks baseada em KG para entregar conhecimento relevante em parágrafos bem organizados. Demonstra vantagens em HotpotQA em qualidade de resposta e retrieval.

**Relevância para finanças:** Técnicas de expansão e organização de chunks são valiosas para processar documentos financeiros interconectados onde fatos abrangem múltiplas seções.

---

### 7.3 Graph Learning-Empowered Financial Fraud Detection

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2024 |
| **Venue** | Intelligent Computing (Science Partner Journal) |
| **Link** | https://spj.science.org/doi/10.34133/icomputing.0146 |

**Contribuições principais:**
Revisa deep learning baseado em grafos para detecção de fraudes financeiras. Cobre GNNs para anti-money laundering, monitoramento de transações e reconhecimento de padrões de fraude. **Modelo híbrido LSTM-GraphSAGE alcança 95.4% de acurácia** em dados de transações financeiras.

**Relevância para finanças:** Aborda diretamente detecção de fraudes e AML, requisitos centrais de compliance para todas as instituições bancárias.

---

### 7.4 Knowledge Graphs in Intelligent Audit

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2024 |
| **Venue** | Journal of Cloud Computing (Springer) |
| **Link** | https://journalofcloudcomputing.springeropen.com/articles/10.1186/s13677-024-00674-0 |

**Contribuições principais:**
Explora como knowledge graphs combinados com tecnologias de IA (ML, NLP) automatizam análise de dados e descoberta de insights para auditoria inteligente. Demonstra consultas sobre conformidade de demonstrações financeiras com regulamentos e busca de casos de auditoria relacionados a auditores específicos.

**Relevância para finanças:** Diretamente aplicável à auditoria interna e externa de instituições financeiras, requisito regulatório fundamental.

---

### 7.5 Integrating AI-powered Knowledge Graphs and NLP for Financial Reporting

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | World Journal of Advanced Research and Reviews (WJARR) |
| **Link** | https://journalwjarr.com/sites/default/files/fulltext_pdf/WJARR-2025-2517.pdf |

**Contribuições principais:**
Constrói knowledge graphs alimentados por IA mapeando padrões de reporte, interpretações regulatórias e tags semânticos entre jurisdições. Permite extração e alinhamento dinâmico de divulgações de fontes não estruturadas (notas de rodapé, discussões da administração, relatórios narrativos).

**Relevância para finanças:** Mapeamento regulatório cross-jurisdicional é crítico para bancos globais operando sob múltiplos regimes regulatórios.

---

## 8. Detecção de Comunidades em RAG

### 8.1 CommunityKG-RAG: Leveraging Community Structures in Knowledge Graphs for Advanced RAG in Fact-Checking

| Campo | Detalhe |
|-------|---------|
| **Autores** | Rong-Ching Chang, Jiawei Zhang |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2408.08535) |
| **Link** | https://arxiv.org/abs/2408.08535 |

**Contribuições principais:**
Framework zero-shot integrando estruturas de comunidade dentro de KGs com RAG para fact-checking. Emprega algoritmo Louvain para detecção de comunidades, permitindo retrieval contextualmente consciente e raciocínio multi-hop. Durante retrieval, favorece entidades e fatos densamente conectados na mesma comunidade. Alcança 56.24% de acurácia com LLaMa2 7B, superando baselines tradicionais. Adapta-se a novos domínios sem treinamento adicional.

**Relevância para finanças:** Detecção de comunidades pode identificar clusters de entidades financeiras relacionadas (e.g., empresas na mesma cadeia de suprimento, frameworks regulatórios), melhorando acurácia de retrieval para queries financeiras complexas.

---

### 8.2 From Louvain to Leiden: Guaranteeing Well-Connected Communities

| Campo | Detalhe |
|-------|---------|
| **Autores** | Vincent Traag, Ludo Waltman, Nees Jan van Eck |
| **Ano** | 2019 |
| **Venue** | Scientific Reports (Nature) |
| **Link** | https://arxiv.org/abs/1810.08473 |

**Contribuições principais:**
Introduz o algoritmo Leiden, que garante comunidades bem conectadas ao contrário do Louvain (que pode gerar comunidades arbitrariamente mal conectadas ou desconectadas). O algoritmo Leiden tornou-se o método padrão de detecção de comunidades usado no GraphRAG da Microsoft.

**Relevância para finanças:** O algoritmo Leiden é a espinha dorsal da detecção de comunidades em sistemas GraphRAG; suas garantias de qualidade são importantes para particionamento confiável de redes de entidades financeiras.

---

### 8.3 Core-based Hierarchies for Efficient GraphRAG

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2026 |
| **Venue** | arXiv preprint (arXiv:2603.05207) |
| **Link** | https://arxiv.org/abs/2603.05207 |

**Contribuições principais:**
Propõe uso de decomposição k-core de grafos para construir estruturas hierárquicas de comunidade em GraphRAG, como alternativa à detecção de comunidades baseada em Leiden. Visa melhorar eficiência do processo de sumarização de comunidades.

**Relevância para finanças:** Abordagens alternativas de detecção de comunidades podem oferecer melhor performance para knowledge graphs financeiros em larga escala.

---

## 9. Papers Complementares Notáveis

### 9.1 MedGraphRAG: Medical Graph RAG — Towards Safe Medical Large Language Model via Graph RAG

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2024 |
| **Venue** | arXiv preprint (arXiv:2408.04187); ACL 2025 |
| **Link** | https://arxiv.org/abs/2408.04187 |

**Contribuições principais:**
GraphRAG específico de domínio para medicina com construção de grafo triple-linked e U-Retrieval combinando abordagens top-down e bottom-up. Alcança 8% de melhoria sobre RAG padrão em QA médica e 10% em fact-checking. Fornece documentação de fonte credível com cada resposta.

**Relevância para finanças:** Embora focado em medicina, o padrão arquitetural (KG específico de domínio, estrutura triple-linked, rastreabilidade de fonte) é diretamente transferível para aplicações no domínio financeiro.

---

### 9.2 The Role of Retrieval-Augmented Generation (RAG) in Financial Document Processing

| Campo | Detalhe |
|-------|---------|
| **Autores** | Múltiplos autores |
| **Ano** | 2025 |
| **Venue** | International Journal of Management Technology (IJMT), Vol. 12, Issue 3 |
| **Link** | https://eajournals.org/ijmt/vol12-issue-3-2025/ |

**Contribuições principais:**
Examina RAG para automatizar compliance e reporte no processamento de documentos financeiros. Cobre automação de compliance IFRS, Basel III e GDPR através de sistemas baseados em RAG.

**Relevância para finanças:** Aborda diretamente a automação de compliance e reporte, duas das atividades mais intensivas em recursos em banking.

---

### 9.3 Graph LLMs: AI's Next Frontier in Banking and Insurance Transformation

| Campo | Detalhe |
|-------|---------|
| **Autores** | PwC Middle East |
| **Ano** | 2024 |
| **Venue** | PwC Publication |
| **Link** | https://www.pwc.com/m1/en/publications/documents/2024/graph-llms-the-next-ai-frontier-in-banking-and-insurance-transformation.pdf |

**Contribuições principais:**
Relatório da indústria examinando como Graph LLMs (combinando knowledge graphs com LLMs) estão transformando banking e insurance. Cobre use cases em avaliação de riscos, detecção de fraudes, analytics de clientes e compliance regulatório.

**Relevância para finanças:** Perspectiva de firma Big Four (PwC), validando a relevância prática de LLMs enhanced por grafos em banking.

---

## Resumo das Principais Descobertas

### Maturidade arquitetural
GraphRAG evoluiu do paper fundacional da Microsoft em 2024 para um ecossistema rico incluindo LightRAG, LazyGraphRAG, HippoRAG, SubgraphRAG, TERAG, E2GraphRAG e PolyG — cada um abordando diferentes trade-offs entre acurácia, custo, latência e complexidade.

### Adoção no domínio financeiro
Corpo crescente de trabalho voltado diretamente a aplicações financeiras: HybridRAG (BlackRock/NVIDIA), FinReflectKG (knowledge graphs de SEC 10-K), FinDKG (dinâmica de mercados), GraphCompliance (compliance regulatório GDPR) e RAGulating Compliance (QA regulatório). O FinanceBench fornece avaliação padronizada para sistemas RAG financeiros.

### Redução de alucinações
GraphRAG demonstra redução mensurável de alucinações (73% de redução em declarações alucinadas com integração KG), embora avaliações imparciais recentes alertem que melhorias podem ser menores que originalmente reportadas. Tarefas de raciocínio multi-hop mostram o maior benefício.

### Eficiência de tokens
Reduções dramáticas de custo são alcançáveis: LazyGraphRAG atinge 0.1% dos custos de indexação do GraphRAG completo; TERAG alcança 80% de acurácia com 3-11% de consumo de tokens; PolyG reduz consumo de tokens em 95%. Estes avanços tornam GraphRAG prático para instituições financeiras sensíveis a custos.

### Preocupações de segurança
Trade-off crítico existe: embora GraphRAG possa reduzir vazamento de texto bruto, é mais vulnerável à extração de informações estruturadas de entidades e relacionamentos. Instituições financeiras devem implementar frameworks formais de segurança (criptografia provável, privacidade diferencial) junto ao deployment de GraphRAG.

### Detecção de comunidades
O algoritmo Leiden é o padrão para detecção de comunidades em GraphRAG, com CommunityKG-RAG demonstrando como estruturas de comunidade melhoram fact-checking. Trabalhos emergentes sobre hierarquias k-core oferecem abordagens alternativas.

---

## Tabela Resumo: Métricas Quantitativas Principais

| Métrica | Paper | Resultado |
|---------|-------|-----------|
| **Acurácia GraphRAG vs RAG** | RAG vs. GraphRAG (2025) | 86.31% vs 72.36% |
| **Redução de tokens** | TERAG (2025) | 89-97% de redução |
| **Redução de tokens** | PolyG (2025) | 95% de redução |
| **Custo de indexação** | LazyGraphRAG (2025) | 0.1% do GraphRAG completo |
| **Custo de query** | LazyGraphRAG (2025) | 700x mais barato |
| **Speedup retrieval** | E2GraphRAG (2025) | 100x sobre LightRAG |
| **Speedup resposta** | PolyG (2025) | 4x mais rápido |
| **Acurácia fraude** | LSTM-GraphSAGE (2024) | 95.4% |
| **Melhoria multi-hop** | HippoRAG (2024) | +20% |
| **Custo HippoRAG** | HippoRAG (2024) | 10-30x mais barato que iterativo |
| **Melhoria F1 compliance** | GraphCompliance (2025) | +4.1-7.2 pp micro-F1 |
