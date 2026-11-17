"""Comissoes dos cursos unificados Silvestres e Felinos, via TeacherHourCalculator."""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from main import TeacherHourCalculator

GRUPOS = {
    "Silvestres: Contenção e Diagnóstico": {
        "valor": 310.00,   # soma dos precos atuais: R$ 430,00
        "profs": [
            # nome, minutos, %H/A atual, curso de origem
            ("Lourdes Marina Bezerra Pessoa", 120, 25.0, "428 Contencao Fisica | Atualizacao"),
            ("Prof. Alexandre Pessoa",        200,  0.0, "7   Contencao/Coleta Silvestres"),
            ("Profa Danae F. Avanze Cacao",   240, 25.0, "432 Interpretacao de Exames"),
            ("Profa Carolina Vaz Cabral Nery",360, 10.0, "76  Avaliacao Radiografica"),
        ],
    },
    "Felinos: Clínica Digestiva": {
        "valor": 290.00,   # soma dos precos atuais: R$ 408,00
        "profs": [
            ("Profa Leticia de P. S. Isidoro", 240, 25.0, "462 Hepatobiliares e Pancreaticas"),
            ("Profa Eloiza de S. e S. Ribeiro", 480, 25.0, "459 Infecciosas, Zoonoses e Dor"),
            ("Prof. Felipe Saab Romano",        180, 10.0, "58  Enteropatias em Caes e Gatos"),
        ],
    },
}

app = QApplication(sys.argv)
calc = TeacherHourCalculator()

for grupo, cfg in GRUPOS.items():
    profs = cfg["profs"]
    valor = cfg["valor"]
    total_min = sum(m for _, m, _, _ in profs)

    calc.course_value_input.setValue(valor)
    calc.course_hours_input.setText(calc.format_duration(total_min))
    calc.professors = {n: {"minutes": m, "percentage": p} for n, m, p, _ in profs}
    minutos = calc.course_total_minutes()

    print("\n" + "=" * 104)
    print(f"{grupo}   |   CH {calc.format_duration(minutos)} ({minutos} min)   |   "
          f"R$ {valor:.2f}   |   hora/aula R$ {valor / (minutos / 60):.2f}")
    print("=" * 104)
    print(f"{'Professor':33s} {'Origem':36s} {'Dur':>6} {'%H/A':>6} {'% curso':>9} {'R$/venda':>9}")
    print("-" * 104)
    for nome, mins, pha, origem in profs:
        pct = (mins / minutos) * pha
        print(f"{nome:33s} {origem:36s} {calc.format_duration(mins):>6} {pha:5.1f}% "
              f"{pct:8.4f}% {valor * pct / 100:8.2f}")
    total = calc.calculate_total_commission_percentage()
    print("-" * 104)
    print(f"{'TOTAL':33s} {'':36s} {calc.format_duration(total_min):>6} {'':6} "
          f"{total:8.4f}% {valor * total / 100:8.2f}")
    arred = [round((m / minutos) * p, 2) for _, m, p, _ in profs]
    print(f"\n  gravar na EAD (2 casas): {arred}  soma {sum(arred):.2f}%")
    print(f"  teto {calc.COMMISSION_LIMIT_PERCENT:.1f}%: "
          f"{'OK' if total <= calc.COMMISSION_LIMIT_PERCENT else 'ESTOURA'} "
          f"(folga {calc.COMMISSION_LIMIT_PERCENT - total:.2f} pontos)")
