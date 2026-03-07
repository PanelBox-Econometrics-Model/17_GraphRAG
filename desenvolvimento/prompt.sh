#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Script para executar SUBFASES do Paper GraphRAG para ESWA
# Objetivo: Construir paper completo para Expert Systems with Applications
# Execucao automatizada via Claude CLI
# COM LOGGING COMPLETO para acompanhamento em tempo real
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# --- CONFIGURACOES ---
TARGET_TIME="00:01"
MAX_ITERATIONS=50

# --- DIRETORIO DE LOG ---
LOG_DIR="/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/LOG"
mkdir -p "$LOG_DIR"

# Log principal com timestamp no nome
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
MAIN_LOG="${LOG_DIR}/graphrag_paper_${TIMESTAMP}.log"
LATEST_LOG="${LOG_DIR}/latest.log"

# Criar link simbolico para o log mais recente
ln -sf "$MAIN_LOG" "$LATEST_LOG"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARQUIVOS DE SUBFASE
#
# Ordem de execucao:
#   1. SUBFASE_01 (Ontologia + Corpus + KG) - fundamentacao
#   2. SUBFASE_02 (Experimentos e Benchmarks) - metricas quantitativas
#   3. SUBFASE_03 (Seguranca + Threat Model) - pilar de seguranca
#   4. SUBFASE_04 (Paper: Intro, Related Work, Methodology) - primeiras secoes
#   5. SUBFASE_05 (Paper: Results, Applications, Discussion) - secoes finais
#   6. SUBFASE_06 (Formatacao ESWA + Submissao) - preparacao final
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FASE_FILES=(
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_01.md"
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_02.md"
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_03.md"
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_04.md"
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_05.md"
    "/home/guhaase/projetos/panelbox/papers/17_GraphRAG/desenvolvimento/SUBFASE_06.md"
)

# Cores para output no terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUNCOES DE LOG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg" | tee -a "$MAIN_LOG"
}

log_file() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MAIN_LOG"
}

log_separator() {
    local sep="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$sep" | tee -a "$MAIN_LOG"
}

update_status() {
    local status_file="${LOG_DIR}/status.txt"
    cat > "$status_file" <<EOF
=== STATUS DA EXECUCAO - GRAPHRAG PAPER ESWA ===
Atualizado em: $(date '+%Y-%m-%d %H:%M:%S')
Subfase atual: $1
Arquivo:       $2
Iteracao:      $3
Pendentes:     $4
Completos:     $5
Estado:        $6
Log completo:  $MAIN_LOG
===========================
EOF
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUNCAO DE AGENDAMENTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "Verificando horario de inicio programado para: ${TARGET_TIME}..."

CURRENT_EPOCH=$(date +%s)
TARGET_EPOCH=$(date -d "$TARGET_TIME" +%s)

if [ "$TARGET_EPOCH" -lt "$CURRENT_EPOCH" ]; then
    TARGET_EPOCH=$(date -d "tomorrow $TARGET_TIME" +%s)
fi

SLEEP_SECONDS=$((TARGET_EPOCH - CURRENT_EPOCH))

if [ "$SLEEP_SECONDS" -gt 0 ]; then
    HOURS=$((SLEEP_SECONDS / 3600))
    MINS=$(((SLEEP_SECONDS % 3600) / 60))
    log "Entrando em modo sleep. O script iniciara em ${HOURS}h ${MINS}m."
    echo -e "${GREEN}Pressione ENTER para iniciar imediatamente!${NC}"
    echo -e "${BLUE}Ou pressione Ctrl+C para cancelar o agendamento.${NC}"

    ELAPSED=0
    while [ $ELAPSED -lt $SLEEP_SECONDS ]; do
        read -t 1 -n 1 && break
        ELAPSED=$((ELAPSED + 1))
    done
fi

log "Horario atingido! Iniciando rotinas..."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FUNCOES AUXILIARES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

count_pending_checkboxes() {
    local file="$1"
    local count=$(grep -c "^- \[ \]" "$file" 2>/dev/null || true)
    echo "${count:-0}"
}

count_completed_checkboxes() {
    local file="$1"
    local count=$(grep -c "^- \[x\]" "$file" 2>/dev/null || true)
    echo "${count:-0}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GERADOR DE PROMPT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

build_prompt() {
    local fase_file="$1"
    local iteration="$2"
    local fase_basename=$(basename "$fase_file")

    cat <<PROMPT_EOF
You are building an academic paper for submission to Expert Systems with Applications (ESWA) — Elsevier.

## Context

- **Paper topic**: GraphRAG for Financial Institutions — Security, Grounding, and Token Economy
- **Project root**: \`/home/guhaase/projetos/panelbox/\`
- **GraphRAG implementation**: \`/home/guhaase/projetos/panelbox/graphrag/\`
- **Paper directory**: \`/home/guhaase/projetos/panelbox/papers/17_GraphRAG/\`
- **Full proposal**: \`/home/guhaase/projetos/panelbox/papers/17_GraphRAG/PROPOSTA_6_GraphRAG.md\`
- **Literature review**: \`/home/guhaase/projetos/panelbox/papers/17_GraphRAG/literatura/REVISAO_LITERATURA.md\`

## Paper Overview

This paper proposes a multi-strategy GraphRAG architecture for financial institutions, addressing four pillars: security, hallucination reduction, token economy, and processing speed. The system uses Neo4j + PostgreSQL + Claude API with intent-aware retrieval fusion (Graph + Vector + Community retrievers).

## ESWA Journal Requirements (CRITICAL)

- **LaTeX class**: \`\documentclass[review]{elsarticle}\`
- **Abstract**: Max 250 words, single paragraph, no references
- **Highlights**: 3-5 bullet points, max 85 characters each
- **Keywords**: 1-7 keywords after abstract
- **References**: Author-year format (Smith, 2024), \`\bibliographystyle{model5-names}\` with \`\biboptions{authoryear}\`
- **Sections**: Numbered (1, 1.1, 1.1.1)
- **Figures/Tables**: High resolution, descriptive captions, referenced in text
- **Target length**: 25-35 pages single column
- **Review**: Double-anonymized (remove author identifiers)
- **Impact Factor**: 7.5 | Acceptance rate: ~16%

## GraphRAG Implementation Details

The implementation at \`/graphrag\` includes:
- **Ingestion**: Chunker (Python/Markdown/Notebook parsers) -> Triple Extractor (Claude API + Batch API) -> Entity Resolver (alias + fuzzy, threshold=85%) -> Graph Loader (Neo4j)
- **Retrieval**: Intent Parser (6 types: VALIDATION, COMPARISON, RECOMMENDATION, EXPLANATION, CODE_EXAMPLE, GENERAL) -> 3 parallel retrievers (Graph N-hop, Vector cosine, Community Leiden) -> Context Ranker (weighted fusion, token budget)
- **Generation**: Claude API with retrieved context + source attribution
- **Security**: JWT auth + PostgreSQL audit logging + usage tracking
- **Cost**: Batch API for 50% savings, query caching in PostgreSQL

**Intent-aware retrieval weights**:
| Intent       | Graph | Vector | Community |
|-------------|-------|--------|-----------|
| VALIDATION  | 0.7   | 0.2    | 0.1       |
| COMPARISON  | 0.5   | 0.3    | 0.2       |
| RECOMMENDATION | 0.3 | 0.4   | 0.3       |
| EXPLANATION | 0.4   | 0.4    | 0.2       |
| CODE_EXAMPLE| 0.3   | 0.6    | 0.1       |
| GENERAL     | 0.3   | 0.3    | 0.4       |

## Key Literature (43 papers catalogued)

Core papers:
- Edge et al. (2024) — Microsoft GraphRAG (arXiv:2404.16130)
- Sarmah et al. (2024) — HybridRAG, BlackRock/NVIDIA (arXiv:2408.04948)
- Han et al. (2025) — RAG vs GraphRAG evaluation: 86.31% vs 72.36% (arXiv:2502.11371)
- TERAG (2025) — 89-97% token reduction (arXiv:2509.18667)
- LazyGraphRAG (2025) — 700x cheaper queries
- PolyG (2025) — 95% token reduction, 4x speedup (arXiv:2504.02112)
- Privacy Risks in GraphRAG (2025) — entity leakage trade-off (arXiv:2508.17222)
- FinReflectKG (2025) — SEC 10-K financial KG (arXiv:2508.17906)
- GraphCompliance (2025) — +4.1-7.2 pp micro-F1 for GDPR (arXiv:2510.26309)

## Your Task

1. Read the specification document below carefully.
2. Read the proposal file (\`PROPOSTA_6_GraphRAG.md\`) for detailed methodology.
3. Read the literature review (\`REVISAO_LITERATURA.md\`) for references.
4. Read relevant source code files from \`/graphrag/src/\` as needed.
5. Execute each task in the specification, creating or modifying files as instructed.
6. **CRITICAL**: After completing each deliverable, mark its checkbox:
   Change \`- [ ]\` to \`- [x]\` in: \`${fase_file}\`
7. Skip items already marked \`[x]\`.
8. Continue until ALL checkboxes are \`[x]\`.

## Important Notes

- Use absolute paths when creating files.
- All paper text must be in **English** (ESWA is an English-language journal).
- All code comments and documentation in English.
- Do NOT add emojis to any files.
- Format LaTeX properly with consistent indentation.
- Use \`booktabs\` for tables (no vertical lines).
- Use author-year citations: (Edge et al., 2024), NOT [1].
- Mark each checkbox as you complete it.
- If a task requires reading files, read them FIRST before creating output.
- This is iteration #${iteration}. Focus on uncompleted items (unmarked checkboxes).

## Specification Document: ${fase_basename}

---
$(cat "$fase_file")
---

REMEMBER: Mark each checkbox (\`- [ ]\` -> \`- [x]\`) in \`${fase_file}\` as you complete each task.
PROMPT_EOF
}

show_progress() {
    local pending=$1
    local completed=$2
    local fase_name=$3
    local total=$((pending + completed))
    local percentage=0
    if [ $total -gt 0 ]; then
        percentage=$((completed * 100 / total))
    fi

    log_separator
    log "PROGRESSO ${fase_name}"
    log "  Completos:  ${completed}"
    log "  Pendentes:  ${pending}"
    log "  Total:      ${total}"
    log "  Progresso:  ${percentage}%"
    log_separator
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICACAO DE PRE-REQUISITOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log "============================================"
log "LOG DE EXECUCAO INICIADO"
log "Modulo: GRAPHRAG PAPER - Expert Systems with Applications"
log "Objetivo: Construir paper completo para ESWA"
log "Arquivo de log: $MAIN_LOG"
log "Para acompanhar em tempo real:"
log "  tail -f $LATEST_LOG"
log "Para ver status rapido:"
log "  cat ${LOG_DIR}/status.txt"
log "============================================"

# Verificar se Claude CLI esta disponivel
if ! command -v claude &> /dev/null; then
    log "ERRO: Claude CLI nao encontrado. Instale com: npm install -g @anthropic-ai/claude-code"
    exit 1
fi

# Verificar se todos os arquivos existem
log "Verificando arquivos de subfase..."
for FASE_FILE in "${FASE_FILES[@]}"; do
    if [ ! -f "$FASE_FILE" ]; then
        log "ERRO: Arquivo $FASE_FILE nao encontrado!"
        exit 1
    fi
    log_file "  OK: $(basename "$FASE_FILE")"
done

# Verificar arquivos de referencia
log "Verificando arquivos de referencia..."
PROPOSTA="/home/guhaase/projetos/panelbox/papers/17_GraphRAG/PROPOSTA_6_GraphRAG.md"
LITERATURA="/home/guhaase/projetos/panelbox/papers/17_GraphRAG/literatura/REVISAO_LITERATURA.md"
if [ ! -f "$PROPOSTA" ]; then
    log "AVISO: Proposta nao encontrada: $PROPOSTA"
fi
if [ ! -f "$LITERATURA" ]; then
    log "AVISO: Revisao de literatura nao encontrada: $LITERATURA"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INICIO DA EXECUCAO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL_FASES=${#FASE_FILES[@]}
EXEC_START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
log "Iniciando execucao automatica de ${TOTAL_FASES} SUBFASES"
log "Inicio: ${EXEC_START_TIME}"

# Loop externo: para cada subfase
for FASE_INDEX in "${!FASE_FILES[@]}"; do
    FASE_FILE="${FASE_FILES[$FASE_INDEX]}"
    FASE_NUM=$((FASE_INDEX + 1))
    FASE_NAME="SUBFASE ${FASE_NUM}/${TOTAL_FASES}"
    FASE_BASENAME=$(basename "$FASE_FILE")

    log ""
    log "======================================================"
    log "INICIANDO ${FASE_NAME} - ${FASE_BASENAME}"
    log "Arquivo: ${FASE_FILE}"
    log "======================================================"

    # Log especifico para cada subfase
    FASE_LOG="${LOG_DIR}/graphrag_step${FASE_NUM}_${FASE_BASENAME%.md}_${TIMESTAMP}.log"
    log "Log desta subfase: ${FASE_LOG}"

    FASE_START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    ITERATION=0

    while [ $ITERATION -lt $MAX_ITERATIONS ]; do
        ITERATION=$((ITERATION + 1))
        PENDING=$(count_pending_checkboxes "$FASE_FILE")
        COMPLETED=$(count_completed_checkboxes "$FASE_FILE")

        show_progress "$PENDING" "$COMPLETED" "$FASE_NAME"
        update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "$PENDING" "$COMPLETED" "EXECUTANDO"

        if [ "$PENDING" -eq 0 ]; then
            FASE_END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
            log "SUCESSO! ${FASE_NAME} concluida!"
            log "  Inicio: ${FASE_START_TIME}"
            log "  Fim:    ${FASE_END_TIME}"
            update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "0" "$COMPLETED" "CONCLUIDA"
            break
        fi

        CLAUDE_START=$(date '+%Y-%m-%d %H:%M:%S')
        CLAUDE_START_EPOCH=$(date +%s)
        log "[CLAUDE] Iniciando chamada #${ITERATION} - ${FASE_NAME} (pendentes: ${PENDING})"
        log "[CLAUDE] Inicio da chamada: ${CLAUDE_START}"

        # Arquivos para esta iteracao
        CLAUDE_RAW="${LOG_DIR}/claude_raw_graphrag_step${FASE_NUM}_iter${ITERATION}.jsonl"
        CLAUDE_READABLE="${LOG_DIR}/claude_readable_graphrag_step${FASE_NUM}_iter${ITERATION}.log"
        > "$CLAUDE_RAW"
        > "$CLAUDE_READABLE"

        # Links simbolicos para acompanhamento em tempo real
        ln -sf "$CLAUDE_RAW" "${LOG_DIR}/claude_current_raw.jsonl"
        ln -sf "$CLAUDE_READABLE" "${LOG_DIR}/claude_current.log"

        update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "$PENDING" "$COMPLETED" \
            "CLAUDE EXECUTANDO (inicio: ${CLAUDE_START}) -- tail -f ${LOG_DIR}/claude_current.log"

        # Rodar claude com prompt completo
        log "[CLAUDE] Modo: prompt completo (spec + instrucoes) - iteracao ${ITERATION} (stream-json)"
        build_prompt "$FASE_FILE" "$ITERATION" | claude -p --dangerously-skip-permissions --verbose --output-format stream-json > "$CLAUDE_RAW" 2>&1 &
        CLAUDE_PID=$!

        # Processar stream JSONL em background -> log legivel
        (
            tail -f "$CLAUDE_RAW" --pid=$CLAUDE_PID 2>/dev/null | while IFS= read -r line; do
                TYPE=$(echo "$line" | grep -oP '"type"\s*:\s*"\K[^"]+' | head -1)

                case "$TYPE" in
                    assistant)
                        TEXT=$(echo "$line" | grep -oP '"content"\s*:\s*"\K[^"]*' | head -1)
                        if [ -n "$TEXT" ]; then
                            echo "[$(date '+%H:%M:%S')] [TEXTO] ${TEXT:0:300}" >> "$CLAUDE_READABLE"
                        fi
                        ;;
                    content_block_start)
                        TOOL=$(echo "$line" | grep -oP '"name"\s*:\s*"\K[^"]+' | head -1)
                        if [ -n "$TOOL" ]; then
                            echo "[$(date '+%H:%M:%S')] [TOOL START] $TOOL" >> "$CLAUDE_READABLE"
                        fi
                        ;;
                    content_block_delta)
                        TEXT=$(echo "$line" | grep -oP '"text"\s*:\s*"\K[^"]*' | head -1)
                        if [ -n "$TEXT" ] && [ ${#TEXT} -gt 2 ]; then
                            echo "[$(date '+%H:%M:%S')] [DELTA] ${TEXT:0:200}" >> "$CLAUDE_READABLE"
                        fi
                        ;;
                    result)
                        echo "[$(date '+%H:%M:%S')] [RESULTADO FINAL]" >> "$CLAUDE_READABLE"
                        ;;
                esac
            done
        ) &
        PARSER_PID=$!

        # Monitor: atualiza status a cada 15s enquanto claude roda
        LAST_RAW_SIZE=0
        while kill -0 $CLAUDE_PID 2>/dev/null; do
            RAW_SIZE=$(wc -c < "$CLAUDE_RAW" 2>/dev/null || echo 0)
            RAW_LINES=$(wc -l < "$CLAUDE_RAW" 2>/dev/null || echo 0)
            NOW_EPOCH=$(date +%s)
            ELAPSED_SECS=$((NOW_EPOCH - CLAUDE_START_EPOCH))
            ELAPSED_MIN=$((ELAPSED_SECS / 60))
            ELAPSED_SEC=$((ELAPSED_SECS % 60))

            LIVE_PENDING=$(count_pending_checkboxes "$FASE_FILE")
            LIVE_COMPLETED=$(count_completed_checkboxes "$FASE_FILE")
            LIVE_DONE=$((LIVE_COMPLETED - COMPLETED))

            if [ "$RAW_SIZE" -gt "$LAST_RAW_SIZE" ]; then
                ACTIVITY="ativo (stream crescendo)"
            else
                ACTIVITY="aguardando resposta API"
            fi
            LAST_RAW_SIZE=$RAW_SIZE

            update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "$LIVE_PENDING" "$LIVE_COMPLETED" \
                "CLAUDE EXECUTANDO | ${ELAPSED_MIN}m${ELAPSED_SEC}s | ${RAW_LINES} eventos | ${ACTIVITY} | +${LIVE_DONE} checkboxes"

            log_file "[MONITOR] ${FASE_NAME} iter#${ITERATION} | ${ELAPSED_MIN}m${ELAPSED_SEC}s | ${RAW_LINES} eventos | ${RAW_SIZE} bytes | ${ACTIVITY} | checkboxes: ${LIVE_COMPLETED}/${LIVE_PENDING}"

            sleep 15
        done

        # Claude terminou
        wait $CLAUDE_PID
        CLAUDE_EXIT_CODE=$?

        sleep 2
        kill $PARSER_PID 2>/dev/null
        wait $PARSER_PID 2>/dev/null

        CLAUDE_END=$(date '+%Y-%m-%d %H:%M:%S')
        FINAL_RAW_LINES=$(wc -l < "$CLAUDE_RAW" 2>/dev/null || echo 0)
        FINAL_RAW_SIZE=$(wc -c < "$CLAUDE_RAW" 2>/dev/null || echo 0)
        log "[CLAUDE] Fim da chamada: ${CLAUDE_END} (exit: ${CLAUDE_EXIT_CODE}, ${FINAL_RAW_LINES} eventos JSONL, ${FINAL_RAW_SIZE} bytes)"

        # Copiar logs
        echo "--- CLAUDE READABLE: ${FASE_NAME} iter#${ITERATION} [${CLAUDE_START} -> ${CLAUDE_END}] ---" >> "$FASE_LOG"
        cat "$CLAUDE_READABLE" >> "$FASE_LOG"
        echo "--- END ---" >> "$FASE_LOG"

        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CLAUDE READABLE ${FASE_NAME} iter#${ITERATION}]" >> "$MAIN_LOG"
        cat "$CLAUDE_READABLE" >> "$MAIN_LOG"

        if [ $CLAUDE_EXIT_CODE -ne 0 ]; then
            log "[ERRO] Claude retornou codigo ${CLAUDE_EXIT_CODE}. Tentando novamente em 2s..."
            update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "$PENDING" "$COMPLETED" "ERRO (code ${CLAUDE_EXIT_CODE}) - retentativa em 2s"
            sleep 2
            continue
        fi

        # Verificar progresso
        NEW_PENDING=$(count_pending_checkboxes "$FASE_FILE")
        NEW_COMPLETED=$(count_completed_checkboxes "$FASE_FILE")
        CHECKBOXES_RESOLVIDOS=$((NEW_COMPLETED - COMPLETED))

        log "[PROGRESSO] Antes: ${COMPLETED} completos, ${PENDING} pendentes"
        log "[PROGRESSO] Depois: ${NEW_COMPLETED} completos, ${NEW_PENDING} pendentes"
        log "[PROGRESSO] Checkboxes resolvidos nesta iteracao: ${CHECKBOXES_RESOLVIDOS}"

        if [ "$NEW_PENDING" -eq "$PENDING" ]; then
            log "[ALERTA] Nenhum checkbox foi resolvido nesta iteracao!"
        fi

        sleep 3
    done

    if [ "$PENDING" -ne 0 ]; then
        log "LIMITE DE ITERACOES ATINGIDO para ${FASE_NAME}!"
        update_status "$FASE_NAME" "$FASE_BASENAME" "$ITERATION" "$PENDING" "$COMPLETED" "FALHA - limite de iteracoes"
        exit 1
    fi
done

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICACAO FINAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXEC_END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
log ""
log "======================================================"
log "TODAS AS SUBFASES CONCLUIDAS COM SUCESSO!"
log "Inicio: ${EXEC_START_TIME}"
log "Fim:    ${EXEC_END_TIME}"
log "======================================================"
log ""
log "Paper pronto para revisao em:"
log "  /home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper/main.tex"
log ""
log "Para compilar o PDF:"
log "  cd /home/guhaase/projetos/panelbox/papers/17_GraphRAG/paper"
log "  pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex"

update_status "TODAS" "N/A" "N/A" "0" "N/A" "CONCLUIDO - ${EXEC_END_TIME}"
exit 0
