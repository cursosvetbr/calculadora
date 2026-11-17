"""Testa a calculadora contra o caso real do curso Medicina de Aves (EAD).

Roda headless: QT_QPA_PLATFORM=offscreen python test_calculo.py
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication, QTableWidget

from main import TeacherHourCalculator

# Cursos unificados em "Medicina de Aves" (produto 567 / curso 519 da EAD)
CASO = {
    "Ana Silvia":   {"minutes": 240, "percentage": 25.0},   # 04:00 - Psittaciformes
    "Camilo":       {"minutes": 240, "percentage": 25.0},   # 04:00 - Accipitriformes
    "Raquel":       {"minutes": 120, "percentage": 25.0},   # 02:00 - Passeriformes
    "Bruno":        {"minutes": 137, "percentage": 10.0},   # 02:17 - Semiologia
}
CARGA_TOTAL = "12:17"          # 737 min
ESPERADO = {"Ana Silvia": 8.14, "Camilo": 8.14, "Raquel": 4.07, "Bruno": 1.86}
ESPERADO_TOTAL = 22.21

falhas = []


def checa(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  {'OK  ' if ok else 'FALHA'} {nome:38s} obtido={obtido!r:22s} esperado={esperado!r}")
    if not ok:
        falhas.append(nome)


app = QApplication(sys.argv)
calc = TeacherHourCalculator()

print("\n1) parse/format de HH:mm")
checa("parse 12:17", calc.parse_duration("12:17"), 737)
checa("parse 02:17", calc.parse_duration("02:17"), 137)
checa("parse 100:30 (>24h)", calc.parse_duration("100:30"), 6030)
checa("parse vazio", calc.parse_duration(""), 0)
checa("parse incompleto '12:'", calc.parse_duration("12:"), 720)
checa("parse lixo", calc.parse_duration("abc"), 0)
checa("format 737", calc.format_duration(737), "12:17")
checa("format 120", calc.format_duration(120), "02:00")

print("\n2) carga horaria 12:17 e representavel (era o furo do spinbox de 1 decimal)")
calc.course_hours_input.setText(CARGA_TOTAL)
checa("course_total_minutes", calc.course_total_minutes(), 737)

print("\n3) comissoes batem com o que esta gravado na EAD")
calc.professors = dict(CASO)
total = calc.calculate_total_commission_percentage()
minutos = calc.course_total_minutes()
for nome, d in CASO.items():
    pct = round((d["minutes"] / minutos) * d["percentage"], 2)
    checa(f"{nome} %", pct, ESPERADO[nome])
checa("total das comissoes", round(total, 2), ESPERADO_TOTAL)
checa("dentro do teto de 25%", total <= calc.COMMISSION_LIMIT_PERCENT, True)

print("\n4) tabela nao pode ser editada a mao")
checa("editTriggers", calc.professors_table.editTriggers(), QTableWidget.NoEditTriggers)

print("\n5) rotulo e valor da celula saem do MESMO numero")
calc.update_professors_table()
linhas = {}
for row in range(calc.professors_table.rowCount()):
    linhas[calc.professors_table.item(row, 0).text()] = calc.professors_table.item(row, 1).text()
checa("linha do Bruno", linhas.get("Bruno"), "02:17 (137 min)")

print("\n6) round-trip de salvar/carregar preserva os minutos exatos")
salvo = {"course_value": 240.0, "course_minutes": 737, "professors": CASO}
calc.course_hours_input.setText(calc.format_duration(salvo["course_minutes"]))
checa("recarregado", calc.course_total_minutes(), 737)
antigo = {"course_value": 240.0, "course_hours": 12.0, "professors": CASO}
calc.course_hours_input.setText(calc.format_duration(antigo["course_hours"] * 60))
checa("arquivo antigo (course_hours)", calc.course_total_minutes(), 720)

print("\n" + "=" * 66)
if falhas:
    print(f"FALHOU: {len(falhas)} -> {falhas}")
    sys.exit(1)
print("Todos os testes passaram.")
