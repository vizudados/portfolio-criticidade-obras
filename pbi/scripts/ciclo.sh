#!/usr/bin/env bash
# ciclo completo: fecha o Desktop do projeto, gera modelo e relatório, reabre com refresh e roda as provas
set -e
cd "$(dirname "$0")/.."
python -X utf8 scripts/contador.py --aplicar >/dev/null
python -X utf8 scripts/gerar_t3_js.py 2>&1 | head -1
python -X utf8 scripts/gerar_t7_js.py 2>&1 | tail -1
python -X utf8 scripts/lint_conta_desenho.py dax --so-erros 2>&1 | tail -2
pwsh -NoProfile -File scripts/desktop.ps1 -Acao fechar 2>&1 | tail -1 || true
python -X utf8 scripts/gerar_modelo.py --aplicar 2>&1 | tail -1
python -X utf8 scripts/montar_pbip.py --aplicar ${ATIVA:+--ativa $ATIVA} 2>&1 | tail -2
pwsh -NoProfile -File scripts/desktop.ps1 -Acao abrir -Espera 540 2>&1 | grep -E "refresh|ERRO|erro" || true
