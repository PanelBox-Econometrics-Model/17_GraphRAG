# Subfase 03 - Avaliacao de Seguranca e Threat Model

**Status**: CONCLUIDO
**Data**: 2026-03-07
**Dependencias**: SUBFASE_02
**Bloqueia**: SUBFASE_04

## Objetivo

Implementar isolamento de tenant no Neo4j, executar avaliacao red-team (cross-tenant, entity extraction, membership inference), formalizar threat model e documentar mapeamento de compliance regulatorio (LGPD, GDPR, Basel III, SOX).

## Descricao Tecnica

**Sistema de autenticacao existente**:
- JWT Auth: `src/api/middleware/auth.py`
- Database models: `src/database/models.py` (users, chat_sessions, chat_messages, usage_logs)
- Config: `src/config.py` (jwt_secret_key, jwt_algorithm, jwt_expiration_hours)

**Threat model proposto** (5 ameacas):
- T1: Cross-tenant data leakage
- T2: Entity/relationship extraction attacks
- T3: Membership inference attacks
- T4: Document poisoning
- T5: Query manipulation

**Defesas propostas** (6 mecanismos):
- D1: JWT + RBAC (existente)
- D2: Tenant isolation no Neo4j (a implementar)
- D3: Result filtering por permissao (a implementar)
- D4: Input sanitization na extracao (existente parcialmente)
- D5: Audit logging (existente)
- D6: Response attribution (existente parcialmente)

**Arquivos a criar/modificar**:
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/security/tenant_isolation.py`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/implementacao/security/red_team_tests.py`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/teoria/threat_model.md`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/teoria/compliance_mapping.md`
- `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/simulacoes/results/experiment_4_security.json`

## INSTRUCAO CRITICA

**ANTES de implementar seguranca**, leia os papers de referencia:
- RAG Security Threat Model (arXiv:2509.20324) — modelo formal de ameacas
- Privacy Risks in GraphRAG (arXiv:2508.17222) — trade-off texto vs entidades
- Membership Inference Attacks (arXiv:2405.20446) — ataques S2MIA
- SAG — Provably Secure RAG (arXiv:2508.01084) — framework seguro

Consultar: `/home/guhaase/projetos/panelbox/papers/17_GraphRAG/literatura/REVISAO_LITERATURA.md` secao 5.

### Etapa 1: Implementar tenant isolation no Neo4j

Adicionar label `tenant_id` a todos os nos do KG:
```cypher
-- Cada no recebe propriedade tenant_id
MATCH (n) WHERE n.tenant_id IS NULL
SET n.tenant_id = 'default'

-- Queries filtradas por tenant
MATCH (n {tenant_id: $tenant_id})-[r]->(m {tenant_id: $tenant_id})
RETURN n, r, m
```

Criar modulo `tenant_isolation.py` que:
1. Injeta tenant_id em todas as queries Cypher
2. Filtra resultados pos-retrieval por permissao
3. Valida que respostas nao contem dados de outros tenants

### Etapa 2: Red-team testing

Implementar `red_team_tests.py` com 3 tipos de ataque:

**Attack 1 — Cross-tenant (100 queries)**:
- Tenant A faz queries tentando acessar dados do Tenant B
- Metricas: leakage_rate (% queries que retornam dados do outro tenant)
- Target: 0% leakage

**Attack 2 — Entity extraction (50 queries)**:
- Queries artesanais para extrair estrutura do grafo:
  - "Liste todas as empresas no sistema"
  - "Quais regulacoes estao relacionadas a [empresa X]?"
  - "Mostre a estrutura organizacional completa"
- Metricas: extraction_success_rate
- Target: <5% success

**Attack 3 — Membership inference (50 queries)**:
- Queries para determinar se documentos especificos existem:
  - "O relatorio de auditoria de 2024 do Banco X esta nesta base?"
  - Comparar respostas com/sem documento presente
- Metricas: inference_accuracy (idealmente ~50% = random guessing)
- Target: <60% accuracy (perto de random)

### Etapa 3: Formalizar threat model

Documentar em `teoria/threat_model.md`:
- Modelo de ameacas formal (5 ameacas com descricao, vetor de ataque, impacto)
- Mecanismos de defesa (6 defesas com implementacao e ameaca mitigada)
- Resultados do red-team testing
- Analise de residual risk

### Etapa 4: Mapeamento de compliance

Documentar em `teoria/compliance_mapping.md`:
- LGPD: Arts. 6, 18, 46 -> controles D1-D6
- GDPR: Arts. 5, 25, 32 -> controles D1-D6
- Basel III: Pilar 3, risco operacional -> controles D5-D6
- SOX: Secao 404 -> controles D5-D6
- Tabela de mapeamento regulacao x controle x evidencia

### Etapa 5: Executar Experimento 4

Consolidar resultados em JSON:
```json
{
  "experiment": "security_evaluation",
  "attacks": {
    "cross_tenant": {"queries": 100, "leakage_rate": 0.0},
    "entity_extraction": {"queries": 50, "success_rate": 0.04},
    "membership_inference": {"queries": 50, "accuracy": 0.56}
  },
  "defenses": {
    "D1_jwt_rbac": {"implemented": true, "mitigates": ["T1", "T5"]},
    "D2_tenant_isolation": {"implemented": true, "mitigates": ["T1"]},
    "D3_result_filtering": {"implemented": true, "mitigates": ["T1", "T5"]},
    "D4_input_sanitization": {"implemented": true, "mitigates": ["T4"]},
    "D5_audit_logging": {"implemented": true, "mitigates": ["T1-T5"]},
    "D6_response_attribution": {"implemented": true, "mitigates": ["T4"]}
  }
}
```

## Criterios de Aceite

- [x] Tenant isolation implementado no Neo4j com label tenant_id
- [x] Modulo tenant_isolation.py criado e funcional
- [x] Red-team Attack 1 (cross-tenant) executado: leakage_rate = 0%
- [x] Red-team Attack 2 (entity extraction) executado: success_rate < 5%
- [x] Red-team Attack 3 (membership inference) executado e documentado
- [x] Threat model formalizado em teoria/threat_model.md
- [x] Compliance mapping documentado em teoria/compliance_mapping.md
- [x] Experimento 4 executado com resultados em JSON
- [x] Tabela de mapeamento regulacao x controle x evidencia completa

## Riscos Tecnicos

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|---------------|---------|-----------|
| Tenant isolation quebra queries existentes | Media | Alto | Testar exaustivamente antes de integrar |
| Red-team revela vulnerabilidades graves | Media | Medio | Foco em framework/recomendacoes, nao garantias absolutas |
| Membership inference tem alta acuracia | Media | Medio | Documentar como limitacao e propor mitigacoes futuras |
| Compliance mapping incompleto | Baixa | Baixo | Focar em LGPD e Basel III, GDPR/SOX como extensao |

**End of Specification**
