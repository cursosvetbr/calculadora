"""Comissoes do curso unificado de anestesia/emergencia em aves (cursos 81, 474, 27).

Usa a propria TeacherHourCalculator, sem reimplementar a formula.
Rodar: QT_QPA_PLATFORM=offscreen python calcular_anestesia_aves.py
"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from main import TeacherHourCalculator

# (nome, minutos gravados, % hora/aula que ja tem no produto de origem, curso origem)
PROFESSORES = [
    ("Profa Carolina Hagy Girotto",  240, 10.0, "81  Anestesiologia em Aves Pet"),
    ("Prof. Barbara Silva Correia",  240, 25.0, "474 Contencao Quimica e Anestesia"),
    ("Prof. Fabricio Rassy",         181, 10.0, "27  Emergencia em Aves Silv/Exot"),
]
VALOR_CURSO = 310.00  # soma dos precos atuais: 142 + 105 + 63

app = QApplication(sys.argv)
calc = TeacherHourCalculator()

total_minutos = sum(m for _, m, _, _ in PROFESSORES)
calc.course_value_input.setValue(VALOR_CURSO)
calc.course_hours_input.setText(calc.format_duration(total_minutos))
calc.professors = {n: {"minutes": m, "percentage": p} for n, m, p, _ in PROFESSORES}

minutos_curso = calc.course_total_minutes()
print(f"Carga horaria total : {calc.format_duration(minutos_curso)} ({minutos_curso} min)")
print(f"Valor do curso      : R$ {VALOR_CURSO:.2f}")
print(f"Valor da hora/aula  : R$ {VALOR_CURSO / (minutos_curso / 60):.2f}\n")

print(f"{'Professor':30s} {'Origem':34s} {'Dur':>6} {'%H/A':>6} {'% curso':>9} {'R$/venda':>9}")
print("-" * 100)
for nome, mins, pha, origem in PROFESSORES:
    pct = (mins / minutos_curso) * pha
    valor = VALOR_CURSO * pct / 100
    print(f"{nome:30s} {origem:34s} {calc.format_duration(mins):>6} {pha:5.1f}% "
          f"{pct:8.4f}% {valor:8.2f}")

total = calc.calculate_total_commission_percentage()
print("-" * 100)
print(f"{'TOTAL':30s} {'':34s} {calc.format_duration(total_minutos):>6} {'':6} {total:8.4f}% "
      f"{VALOR_CURSO * total / 100:8.2f}")

arredondado = [round((m / minutos_curso) * p, 2) for _, m, p, _ in PROFESSORES]
print(f"\nPara gravar na EAD (2 casas): {arredondado}  soma {sum(arredondado):.2f}%")
print(f"Teto de {calc.COMMISSION_LIMIT_PERCENT:.1f}%: "
      f"{'OK, cabe' if total <= calc.COMMISSION_LIMIT_PERCENT else 'ESTOURA'} "
      f"(folga de {calc.COMMISSION_LIMIT_PERCENT - total:.2f} pontos)")
