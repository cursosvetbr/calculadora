import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QDoubleSpinBox, QMessageBox, QFileDialog, QGroupBox, QFormLayout, QHeaderView, QTimeEdit,
    QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont


class EditProfessorDialog(QDialog):
    def __init__(self, parent, prof_name, minutes, percentage):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Professor: {prof_name}")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit(prof_name)
        
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime(hours, mins, 0))
        self.time_input.setDisplayFormat("HH:mm")

        self.percentage_input = QDoubleSpinBox()
        self.percentage_input.setMaximum(100.0)
        self.percentage_input.setMinimum(0.0)
        self.percentage_input.setDecimals(1)
        self.percentage_input.setSingleStep(1.0)
        self.percentage_input.setSuffix(" %")
        self.percentage_input.setValue(percentage)

        form_layout.addRow("Nome do Professor:", self.name_input)
        form_layout.addRow("Duração Gravada (HH:mm):", self.time_input)
        form_layout.addRow("Porcentagem (%):", self.percentage_input)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_data(self):
        time = self.time_input.time()
        new_minutes = time.hour() * 60 + time.minute()
        return self.name_input.text().strip(), new_minutes, self.percentage_input.value()


class TeacherHourCalculator(QMainWindow):
    COMMISSION_LIMIT_PERCENT = 25.0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Valor Hora/Aula")
        self.setGeometry(100, 100, 900, 600)

        self.professors = {}  # {prof_name: {"minutes": minutes, "percentage": percentage}}

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Top panel - Course Values
        top_layout = QHBoxLayout()
        top_group = QGroupBox("Configurar Curso")
        top_group.setLayout(top_layout)

        course_form = QFormLayout()

        self.course_value_input = QDoubleSpinBox()
        self.course_value_input.setMaximum(999999.99)
        self.course_value_input.setPrefix("R$ ")
        self.course_value_input.setDecimals(2)
        self.course_value_input.setSingleStep(10.0)
        self.course_value_input.setValue(100.0)
        self.course_value_input.valueChanged.connect(self.calculate_results)

        self.course_hours_input = QDoubleSpinBox()
        self.course_hours_input.setMaximum(9999.0)
        self.course_hours_input.setDecimals(1)
        self.course_hours_input.setSingleStep(0.5)
        self.course_hours_input.setSuffix(" horas")
        self.course_hours_input.setValue(10.0)
        self.course_hours_input.valueChanged.connect(self.calculate_results)

        course_form.addRow("Valor Total do Curso:", self.course_value_input)
        course_form.addRow("Total de Horas:", self.course_hours_input)

        top_layout.addLayout(course_form)
        main_layout.addWidget(top_group)

        # Middle panel - Professor Management
        middle_layout = QVBoxLayout()
        middle_group = QGroupBox("Gerenciar Professores")
        middle_group.setLayout(middle_layout)
        # Professor input
        prof_form = QFormLayout()
        self.prof_name_input = QLineEdit()
        self.prof_time_input = QTimeEdit()
        self.prof_time_input.setTime(QTime(0, 0, 0))
        self.prof_time_input.setDisplayFormat("HH:mm")
        
        self.prof_percentage_input = QDoubleSpinBox()
        self.prof_percentage_input.setMaximum(100.0)
        self.prof_percentage_input.setMinimum(0.0)
        self.prof_percentage_input.setDecimals(1)
        self.prof_percentage_input.setSingleStep(1.0)
        self.prof_percentage_input.setSuffix(" %")
        self.prof_percentage_input.setValue(25.0)
        
        prof_form.addRow("Nome do Professor:", self.prof_name_input)
        prof_form.addRow("Duração Gravada (HH:mm):", self.prof_time_input)
        prof_form.addRow("Porcentagem (%):", self.prof_percentage_input)

        middle_layout.addLayout(prof_form)

        add_prof_btn = QPushButton("➕ Adicionar Professor")
        add_prof_btn.clicked.connect(self.add_professor)
        middle_layout.addWidget(add_prof_btn)

        # Professors table
        middle_layout.addWidget(QLabel("Professores:"))
        self.professors_table = QTableWidget()
        self.professors_table.setColumnCount(5)
        self.professors_table.setHorizontalHeaderLabels(["Professor", "Duração (Minutos)", "Porcentagem (%)", "Editar", "Remover"])
        self.professors_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.professors_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        middle_layout.addWidget(self.professors_table)

        main_layout.addWidget(middle_group)

        # Bottom panel - Results
        bottom_layout = QVBoxLayout()
        bottom_group = QGroupBox("Resultado do Cálculo")
        bottom_group.setLayout(bottom_layout)
        
        self.result_text = QLabel("Adicione professores para ver o resultado...")
        self.result_text.setWordWrap(True)
        font = self.result_text.font()
        font.setPointSize(10)
        self.result_text.setFont(font)
        bottom_layout.addWidget(self.result_text)
        
        # Export buttons
        export_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Salvar")
        save_btn.clicked.connect(self.save_data)
        load_btn = QPushButton("📂 Carregar")
        load_btn.clicked.connect(self.load_data_dialog)
        clear_btn = QPushButton("🗑️ Limpar")
        clear_btn.clicked.connect(self.clear_all)

        export_layout.addWidget(save_btn)
        export_layout.addWidget(load_btn)
        export_layout.addWidget(clear_btn)
        bottom_layout.addLayout(export_layout)
        
        main_layout.addWidget(bottom_group)

        central_widget.setLayout(main_layout)

    def add_professor(self):
        prof_name = self.prof_name_input.text().strip()
        if not prof_name:
            QMessageBox.warning(self, "Erro", "Digite o nome do professor")
            return
        
        # Converter QTime para minutos
        time = self.prof_time_input.time()
        prof_minutes = time.hour() * 60 + time.minute()
        prof_hours = prof_minutes / 60.0
        total_course_hours = self.course_hours_input.value()

        if prof_minutes <= 0:
            QMessageBox.warning(self, "Erro", "Digite uma duração maior que 0")
            return
        
        # Calcular total atual de horas dos professores (convertendo de minutos)
        total_current_minutes = sum(p["minutes"] for p in self.professors.values())
        total_current_hours = total_current_minutes / 60.0
        new_total_hours = total_current_hours + prof_hours

        if new_total_hours > total_course_hours:
            QMessageBox.warning(
                self,
                "⚠️ Excede Total de Horas",
                f"Total atual: {total_current_minutes:.0f} min ({total_current_hours:.2f}h)\n"
                f"Total após adicionar: {total_current_minutes + prof_minutes:.0f} min ({new_total_hours:.2f}h)\n"
                f"Máximo permitido: {total_course_hours:.1f}h"
            )
            return
        
        prof_percentage = self.prof_percentage_input.value()
        candidate_professors = dict(self.professors)
        candidate_professors[prof_name] = {"minutes": prof_minutes, "percentage": prof_percentage}
        total_commission_percentage = self.calculate_total_commission_percentage(candidate_professors)

        if total_commission_percentage > self.COMMISSION_LIMIT_PERCENT:
            self.show_commission_limit_alert(total_commission_percentage)
            return

        self.professors[prof_name] = {"minutes": prof_minutes, "percentage": prof_percentage}

        self.prof_name_input.clear()
        self.prof_time_input.setTime(QTime(0, 0, 0))
        self.prof_percentage_input.setValue(25.0)

        self.update_professors_table()
        self.calculate_results()

    def calculate_total_commission_percentage(self, professors=None):
        if professors is None:
            professors = self.professors
        total_hours = self.course_hours_input.value()

        if total_hours <= 0:
            return 0.0

        total_commission_percent = 0.0
        for data in professors.values():
            hours = data["minutes"] / 60.0
            percentage = data["percentage"]
            total_commission_percent += (hours / total_hours) * percentage

        return total_commission_percent

    def show_commission_limit_alert(self, commission_percentage):
        QMessageBox.warning(
            self,
            "Limite de Comissoes Excedido",
            f"O valor total das comissoes nao pode passar de {self.COMMISSION_LIMIT_PERCENT:.1f}% do curso.\n"
            f"Com estes dados, as comissoes chegariam a {commission_percentage:.2f}%."
        )

    def update_professors_table(self):
        self.professors_table.setRowCount(0)
        
        for row, (prof_name, data) in enumerate(sorted(self.professors.items())):
            self.professors_table.insertRow(row)
            
            minutes = data["minutes"]
            percentage = data["percentage"]
            hours = minutes / 60.0
            hours_int = int(minutes // 60)
            minutes_int = int(minutes % 60)

            name_item = QTableWidgetItem(prof_name)
            time_item = QTableWidgetItem(f"{hours_int:02d}:{minutes_int:02d} ({minutes:.0f} min)")
            time_item.setTextAlignment(Qt.AlignCenter)
            perc_item = QTableWidgetItem(f"{percentage:.1f}%")
            perc_item.setTextAlignment(Qt.AlignCenter)

            self.professors_table.setItem(row, 0, name_item)
            self.professors_table.setItem(row, 1, time_item)
            self.professors_table.setItem(row, 2, perc_item)

            edit_btn = QPushButton("✏️ Editar")
            edit_btn.clicked.connect(lambda checked, p=prof_name: self.edit_professor(p))
            self.professors_table.setCellWidget(row, 3, edit_btn)

            delete_btn = QPushButton("❌ Remover")
            delete_btn.clicked.connect(lambda checked, p=prof_name: self.remove_professor(p))
            self.professors_table.setCellWidget(row, 4, delete_btn)

    def remove_professor(self, prof_name):
        if prof_name in self.professors:
            del self.professors[prof_name]
            self.update_professors_table()
            self.calculate_results()
    
    def edit_professor(self, prof_name):
        """Editar professor existente"""
        old_data = self.professors[prof_name]
        old_minutes = old_data["minutes"]
        old_percentage = old_data["percentage"]

        dialog = EditProfessorDialog(self, prof_name, old_minutes, old_percentage)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_minutes, new_percentage = dialog.get_data()

            if not new_name:
                QMessageBox.warning(self, "Erro", "Digite o nome do professor")
                return

            if new_minutes <= 0:
                QMessageBox.warning(self, "Erro", "Digite uma duração maior que 0")
                return

            # Calcular diferença de tempo
            time_difference = new_minutes - old_minutes
            total_current_minutes = sum(p["minutes"] for p in self.professors.values())
            new_total_hours = (total_current_minutes + time_difference) / 60.0
            total_course_hours = self.course_hours_input.value()

            if new_total_hours > total_course_hours:
                QMessageBox.warning(
                    self,
                    "⚠️ Excede Total de Horas",
                    f"A nova duração excederia o total permitido!\n"
                    f"Total atual seria: {new_total_hours:.2f}h\n"
                    f"Máximo permitido: {total_course_hours:.1f}h"
                )
                return

            candidate_professors = dict(self.professors)
            if new_name != prof_name:
                del candidate_professors[prof_name]
            candidate_professors[new_name] = {"minutes": new_minutes, "percentage": new_percentage}
            total_commission_percentage = self.calculate_total_commission_percentage(candidate_professors)

            if total_commission_percentage > self.COMMISSION_LIMIT_PERCENT:
                self.show_commission_limit_alert(total_commission_percentage)
                return

            # Se mudou o nome, remover entrada antiga
            if new_name != prof_name:
                del self.professors[prof_name]

            # Adicionar/atualizar com novos valores
            self.professors[new_name] = {"minutes": new_minutes, "percentage": new_percentage}

            self.update_professors_table()
            self.calculate_results()

            QMessageBox.information(self, "✅ Sucesso", f"Professor '{new_name}' atualizado!")

    def calculate_results(self):
        if not self.professors:
            self.result_text.setText("Nenhum professor adicionado")
            return
        
        total_value = self.course_value_input.value()
        total_hours = self.course_hours_input.value()
        
        # Se valor ou horas são zerados, avisar
        if total_value <= 0:
            self.result_text.setText("⚠️ Digite um valor de curso maior que 0")
            return
        
        if total_hours <= 0:
            self.result_text.setText("⚠️ Digite o total de horas maior que 0")
            return
        
        # Calcular valor por hora/aula total do curso
        value_per_hour_total = total_value / total_hours
        
        # Total de minutos dos professores (converter para horas)
        total_prof_minutes = sum(p["minutes"] for p in self.professors.values())
        total_prof_hours = total_prof_minutes / 60.0
        
        result_lines = [
            f"<b>💰 Valor Total do Curso:</b> R$ {total_value:.2f}",
            f"<b>⏱️ Total de Horas (Curso):</b> {total_hours:.1f}h",
            f"<b>💳 Valor da Hora/Aula (Curso):</b> R$ {value_per_hour_total:.2f}",
            f"<br>",
            f"<b>🎯 Total de Horas Gravadas (Professores):</b> {total_prof_minutes:.0f} min ({total_prof_hours:.2f}h)",
            "<br>",
            "<b>👥 Distribuição por Professor:</b>",
            "<table style='margin-top: 10px;' width='100%'>",
        ]
        
        total_distributed = 0
        for prof_name, data in sorted(self.professors.items()):
            minutes = data["minutes"]
            percentage = data["percentage"]
            hours = minutes / 60.0
            hours_int = int(minutes // 60)
            minutes_int = int(minutes % 60)

            # Valor da hora/aula do professor é baseado na sua porcentagem em cima da hora/aula do curso
            prof_hour_value = value_per_hour_total * (percentage / 100.0)
            prof_total_value = hours * prof_hour_value
            prof_total_percentage = (prof_total_value / total_value) * 100.0
            total_distributed += prof_total_value

            result_lines.append(
                f"<tr><td>&nbsp;<b>{prof_name}:</b></td>"
                f"<td>&nbsp;{hours_int:02d}:{minutes_int:02d} ({minutes:.0f} min / {hours:.2f}h)</td>"
                f"<td>&nbsp;({percentage:.1f}% da H/A: R$ {prof_hour_value:.2f}/h)</td>"
                f"<td>&nbsp;{prof_total_percentage:.2f}% do total do curso</td>"
                f"<td>&nbsp;→ <b>R$ {prof_total_value:.2f}</b></td></tr>"
            )
        
        result_lines.append("</table>")
        total_distributed_percentage = (total_distributed / total_value) * 100.0
        result_lines.append(f"<br><b>✅ Total Distribuído aos Professores:</b> R$ {total_distributed:.2f}")
        result_lines.append(f"<b>Percentual distribuido:</b> {total_distributed_percentage:.2f}% do total do curso")

        if total_distributed_percentage > self.COMMISSION_LIMIT_PERCENT:
            result_lines.append(
                f"<br><b>Alerta:</b> O total de comissoes ultrapassa "
                f"{self.COMMISSION_LIMIT_PERCENT:.1f}% do valor do curso."
            )

        self.result_text.setText("\n".join(result_lines))
    
    def save_data(self):
        data = {
            "course_value": self.course_value_input.value(),
            "course_hours": self.course_hours_input.value(),
            "professors": self.professors
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Dados", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "✅ Sucesso", f"Dados salvos em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def load_data_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Dados", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.course_value_input.setValue(data.get("course_value", 0))
                self.course_hours_input.setValue(data.get("course_hours", 0))

                loaded_professors = data.get("professors", {})
                self.professors = {}
                for p_name, p_val in loaded_professors.items():
                    if isinstance(p_val, (int, float)):
                        self.professors[p_name] = {"minutes": float(p_val), "percentage": 25.0}
                    elif isinstance(p_val, dict):
                        self.professors[p_name] = {
                            "minutes": float(p_val.get("minutes", 0)),
                            "percentage": float(p_val.get("percentage", 25.0))
                        }

                self.update_professors_table()
                self.calculate_results()
                QMessageBox.information(self, "✅ Sucesso", "Dados carregados!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")
    
    def clear_all(self):
        reply = QMessageBox.question(
            self, "Confirmar", "Deseja limpar todos os dados?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.professors = {}
            self.course_value_input.setValue(100.0)
            self.course_hours_input.setValue(10.0)
            self.prof_name_input.clear()
            self.prof_time_input.setTime(QTime(0, 0, 0))
            self.prof_percentage_input.setValue(25.0)
            self.update_professors_table()
            self.result_text.setText("Adicione professores para ver o resultado...")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = TeacherHourCalculator()
    calculator.show()
    sys.exit(app.exec_())

