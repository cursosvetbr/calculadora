import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QDoubleSpinBox, QMessageBox, QFileDialog, QGroupBox, QFormLayout, QHeaderView, QTimeEdit,
    QDialog, QDialogButtonBox, QComboBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTime, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator


class EditProfessorDialog(QDialog):
    def __init__(self, parent, prof_name, minutes, percentage, pix_type="CPF", pix_key=""):
        super().__init__(parent)
        self.setWindowTitle(f"Editar Professor: {prof_name}")
        self.setGeometry(200, 200, 420, 280)

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

        self.pix_type_input = QComboBox()
        self.pix_type_input.addItems(["CPF", "Celular", "E-mail", "Chave Aleatória"])
        self.pix_type_input.setCurrentText(pix_type if pix_type else "CPF")

        self.pix_key_input = QLineEdit(pix_key)

        form_layout.addRow("Nome do Professor:", self.name_input)
        form_layout.addRow("Duração Gravada (HH:mm):", self.time_input)
        form_layout.addRow("Porcentagem (%):", self.percentage_input)
        form_layout.addRow("Tipo de Chave PIX:", self.pix_type_input)
        form_layout.addRow("Chave PIX:", self.pix_key_input)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_data(self):
        time = self.time_input.time()
        new_minutes = time.hour() * 60 + time.minute()
        return (
            self.name_input.text().strip(),
            new_minutes,
            self.percentage_input.value(),
            self.pix_type_input.currentText(),
            self.pix_key_input.text().strip()
        )


class TeacherHourCalculator(QMainWindow):
    COMMISSION_LIMIT_PERCENT = 25.0

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Valor Hora/Aula & Repasses PIX")
        self.setGeometry(100, 100, 1100, 720)

        # Dados locais do curso atual
        self.professors = {}  # {prof_name: {"minutes": minutes, "percentage": percentage}}
        
        # Base global de formas de pagamento dos professores (salvo separadamente do curso)
        self.pix_data_file = "professors_pix_data.json"
        self.global_pix_data = self.load_global_pix_data()

        self.init_ui()
        self.apply_theme()

    def load_global_pix_data(self):
        if os.path.exists(self.pix_data_file):
            try:
                with open(self.pix_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar banco de dados global de PIX: {e}")
        return {}

    def save_global_pix_data(self):
        try:
            with open(self.pix_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_pix_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar chaves PIX globais: {e}")

    def check_existing_pix_key(self):
        name = self.prof_name_input.text().strip()
        if name in self.global_pix_data:
            pix_info = self.global_pix_data[name]
            self.prof_pix_type_input.setCurrentText(pix_info.get("pix_type", "CPF"))
            self.prof_pix_key_input.setText(pix_info.get("pix_key", ""))
        else:
            # Não limpa se o usuário já estiver digitando para evitar apagar dados novos acidentalmente
            pass

    def apply_theme(self):
        # QSS Premium Theme (Dark Mode with green/blue accents)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a24;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2d3748;
                border-radius: 6px;
                margin-top: 1.5ex;
                background-color: #21222c;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #2bbd7e;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit, QTimeEdit, QDoubleSpinBox, QComboBox {
                background-color: #2d313f;
                border: 1px solid #4a5568;
                border-radius: 4px;
                padding: 5px;
                color: #ffffff;
                min-height: 20px;
            }
            QLineEdit:focus, QTimeEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #2bbd7e;
                background-color: #34394a;
            }
            QPushButton {
                background-color: #3b4252;
                border: none;
                color: white;
                padding: 8px 14px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4c566a;
            }
            QPushButton:pressed {
                background-color: #2e3440;
            }
            QTableWidget {
                background-color: #282a36;
                gridline-color: #3b4252;
                border: 1px solid #3b4252;
                border-radius: 4px;
                color: #e5e9f0;
            }
            QHeaderView::section {
                background-color: #3b4252;
                color: #e5e9f0;
                padding: 6px;
                border: 1px solid #2e3440;
                font-weight: bold;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #3b4252;
                border: 1px solid #2e3440;
            }
            QTableWidgetItem {
                padding: 5px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2e3440;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #4c566a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2bbd7e;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QTextEdit {
                background-color: #1e1f29;
                border: 1px solid #3b4252;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
                color: #f8f8f2;
            }
        """)

    @staticmethod
    def parse_duration(text):
        """Converte 'HH:mm' em minutos. Retorna 0 se estiver vazio ou incompleto."""
        try:
            hours, _, minutes = str(text).strip().partition(":")
            return int(hours) * 60 + int(minutes or 0)
        except ValueError:
            return 0

    @staticmethod
    def format_duration(minutes):
        """Converte minutos em 'HH:mm'."""
        minutes = int(round(minutes))
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def course_total_minutes(self):
        """Carga horaria total do curso, em minutos."""
        return self.parse_duration(self.course_hours_input.text())

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()

        # --- COLUNA ESQUERDA (Configuração, Cadastro e Cálculo) ---
        left_layout = QVBoxLayout()

        # 1. Configurar Curso
        top_group = QGroupBox("Configurar Curso")
        top_layout = QVBoxLayout(top_group)
        course_form = QFormLayout()

        self.course_value_input = QDoubleSpinBox()
        self.course_value_input.setMaximum(999999.99)
        self.course_value_input.setPrefix("R$ ")
        self.course_value_input.setDecimals(2)
        self.course_value_input.setSingleStep(10.0)
        self.course_value_input.setValue(100.0)
        self.course_value_input.valueChanged.connect(self.calculate_results)

        # HH:mm em vez de horas decimais: a carga horaria vem da EAD nesse formato
        # e valores como 12:17 nao sao representaveis com uma casa decimal.
        self.course_hours_input = QLineEdit(self.format_duration(600))
        self.course_hours_input.setPlaceholderText("HH:mm — ex: 12:17")
        self.course_hours_input.setValidator(QRegExpValidator(QRegExp(r"\d{1,4}:[0-5]\d")))
        self.course_hours_input.textChanged.connect(self.calculate_results)

        course_form.addRow("Valor Total do Curso:", self.course_value_input)
        course_form.addRow("Carga Horária Total (HH:mm):", self.course_hours_input)
        top_layout.addLayout(course_form)
        left_layout.addWidget(top_group)

        # 2. Gerenciar Professores (Cadastro)
        middle_group = QGroupBox("Gerenciar Professores (Cadastro)")
        middle_layout = QVBoxLayout(middle_group)
        
        prof_form = QFormLayout()
        self.prof_name_input = QLineEdit()
        self.prof_name_input.setPlaceholderText("Ex: João Silva")
        self.prof_name_input.textChanged.connect(self.check_existing_pix_key)

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

        self.prof_pix_type_input = QComboBox()
        self.prof_pix_type_input.addItems(["CPF", "Celular", "E-mail", "Chave Aleatória"])

        self.prof_pix_key_input = QLineEdit()
        self.prof_pix_key_input.setPlaceholderText("Digite a chave PIX do professor")
        
        prof_form.addRow("Nome do Professor:", self.prof_name_input)
        prof_form.addRow("Duração Gravada (HH:mm):", self.prof_time_input)
        prof_form.addRow("Porcentagem (%):", self.prof_percentage_input)
        prof_form.addRow("Tipo de Chave PIX:", self.prof_pix_type_input)
        prof_form.addRow("Chave PIX:", self.prof_pix_key_input)

        middle_layout.addLayout(prof_form)

        add_prof_btn = QPushButton("➕ Adicionar Professor")
        add_prof_btn.setStyleSheet("""
            QPushButton {
                background-color: #2bbd7e;
                color: white;
            }
            QPushButton:hover {
                background-color: #32d991;
            }
        """)
        add_prof_btn.clicked.connect(self.add_professor)
        middle_layout.addWidget(add_prof_btn)
        
        left_layout.addWidget(middle_group)

        # 3. Resultado do Cálculo
        bottom_group = QGroupBox("Resultado do Cálculo de Distribuição")
        bottom_layout = QVBoxLayout(bottom_group)
        
        self.result_text = QLabel("Adicione professores para ver o resultado...")
        self.result_text.setWordWrap(True)
        font = self.result_text.font()
        font.setPointSize(9)
        self.result_text.setFont(font)
        bottom_layout.addWidget(self.result_text)
        
        # Botões de Ações Gerais
        export_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Salvar Curso")
        save_btn.clicked.connect(self.save_data)
        load_btn = QPushButton("📂 Carregar Curso")
        load_btn.clicked.connect(self.load_data_dialog)
        clear_btn = QPushButton("🗑️ Limpar Tudo")
        clear_btn.clicked.connect(self.clear_all)

        export_layout.addWidget(save_btn)
        export_layout.addWidget(load_btn)
        export_layout.addWidget(clear_btn)
        bottom_layout.addLayout(export_layout)
        
        left_layout.addWidget(bottom_group)
        main_layout.addLayout(left_layout, stretch=4)


        # --- COLUNA DIREITA (Tabela e Simulador de Vendas PIX) ---
        right_layout = QVBoxLayout()

        # 4. Tabela de Professores
        table_group = QGroupBox("Lista de Professores do Curso")
        table_layout = QVBoxLayout(table_group)
        
        self.professors_table = QTableWidget()
        # Somente leitura: editar a celula mudava so o rotulo, nunca o valor do calculo.
        self.professors_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.professors_table.setColumnCount(7)
        self.professors_table.setHorizontalHeaderLabels([
            "Professor", "Duração", "Porcentagem", 
            "Tipo PIX", "Chave PIX", "Editar", "Remover"
        ])
        self.professors_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.professors_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.professors_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.professors_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        table_layout.addWidget(self.professors_table)
        right_layout.addWidget(table_group)

        # 5. Simulador de Vendas e Repasses PIX
        sales_group = QGroupBox("Simulador de Vendas (Repasse PIX Instantâneo)")
        sales_layout = QVBoxLayout(sales_group)

        self.buy_btn = QPushButton("🛒 Simular Compra do Curso (Recebimento PIX Instantâneo)")
        self.buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2bbd7e; 
                color: white; 
                font-weight: bold; 
                font-size: 13px; 
                padding: 10px; 
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #32d991;
            }
        """)
        self.buy_btn.clicked.connect(self.simulate_purchase)
        sales_layout.addWidget(self.buy_btn)

        sales_layout.addWidget(QLabel("Histórico de Repasses (Logs de Transação):"))
        self.sales_log = QTextEdit()
        self.sales_log.setReadOnly(True)
        self.sales_log.setPlaceholderText("Aguardando simulação de compra...")
        sales_layout.addWidget(self.sales_log)

        clear_log_btn = QPushButton("🗑️ Limpar Histórico")
        clear_log_btn.clicked.connect(self.clear_sales_log)
        sales_layout.addWidget(clear_log_btn)

        right_layout.addWidget(sales_group)
        main_layout.addLayout(right_layout, stretch=6)

        central_widget.setLayout(main_layout)

    def add_professor(self):
        prof_name = self.prof_name_input.text().strip()
        if not prof_name:
            QMessageBox.warning(self, "Erro", "Digite o nome do professor")
            return
        
        # Converter QTime para minutos
        time = self.prof_time_input.time()
        prof_minutes = time.hour() * 60 + time.minute()
        total_course_minutes = self.course_total_minutes()

        if prof_minutes <= 0:
            QMessageBox.warning(self, "Erro", "Digite uma duração maior que 0")
            return

        if total_course_minutes <= 0:
            QMessageBox.warning(self, "Erro", "Informe a carga horária total do curso (HH:mm)")
            return

        # Comparacao em minutos inteiros, sem passar por horas decimais
        total_current_minutes = sum(p["minutes"] for p in self.professors.values())
        new_total_minutes = total_current_minutes + prof_minutes

        if new_total_minutes > total_course_minutes:
            QMessageBox.warning(
                self,
                "⚠️ Excede Total de Horas",
                f"Total atual: {total_current_minutes:.0f} min ({self.format_duration(total_current_minutes)})\n"
                f"Total após adicionar: {new_total_minutes:.0f} min ({self.format_duration(new_total_minutes)})\n"
                f"Máximo permitido: {self.format_duration(total_course_minutes)}"
            )
            return
        
        prof_percentage = self.prof_percentage_input.value()
        candidate_professors = dict(self.professors)
        candidate_professors[prof_name] = {"minutes": prof_minutes, "percentage": prof_percentage}
        total_commission_percentage = self.calculate_total_commission_percentage(candidate_professors)

        if total_commission_percentage > self.COMMISSION_LIMIT_PERCENT:
            self.show_commission_limit_alert(total_commission_percentage)
            return

        # Adicionar aos professores locais do curso
        self.professors[prof_name] = {"minutes": prof_minutes, "percentage": prof_percentage}

        # Salvar chave PIX na base global
        pix_type = self.prof_pix_type_input.currentText()
        pix_key = self.prof_pix_key_input.text().strip()
        
        self.global_pix_data[prof_name] = {
            "pix_type": pix_type,
            "pix_key": pix_key
        }
        self.save_global_pix_data()

        # Limpar inputs
        self.prof_name_input.clear()
        self.prof_time_input.setTime(QTime(0, 0, 0))
        self.prof_percentage_input.setValue(25.0)
        self.prof_pix_key_input.clear()

        self.update_professors_table()
        self.calculate_results()

    def calculate_total_commission_percentage(self, professors=None):
        if professors is None:
            professors = self.professors
        total_minutes = self.course_total_minutes()

        if total_minutes <= 0:
            return 0.0

        total_commission_percent = 0.0
        for data in professors.values():
            total_commission_percent += (data["minutes"] / total_minutes) * data["percentage"]

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

            # Obter PIX da base global de professores
            pix_info = self.global_pix_data.get(prof_name, {})
            pix_type = pix_info.get("pix_type", "")
            pix_key = pix_info.get("pix_key", "")

            if not pix_key:
                pix_type = "Não cadastrado"
                pix_key = "Chave PIX ausente ⚠️"

            type_item = QTableWidgetItem(pix_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            key_item = QTableWidgetItem(pix_key)
            key_item.setTextAlignment(Qt.AlignCenter)

            self.professors_table.setItem(row, 0, name_item)
            self.professors_table.setItem(row, 1, time_item)
            self.professors_table.setItem(row, 2, perc_item)
            self.professors_table.setItem(row, 3, type_item)
            self.professors_table.setItem(row, 4, key_item)

            edit_btn = QPushButton("✏️ Editar")
            edit_btn.clicked.connect(lambda checked, p=prof_name: self.edit_professor(p))
            self.professors_table.setCellWidget(row, 5, edit_btn)

            delete_btn = QPushButton("❌ Remover")
            delete_btn.clicked.connect(lambda checked, p=prof_name: self.remove_professor(p))
            self.professors_table.setCellWidget(row, 6, delete_btn)

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

        # Buscar dados globais de PIX do professor
        pix_info = self.global_pix_data.get(prof_name, {})
        old_pix_type = pix_info.get("pix_type", "CPF")
        old_pix_key = pix_info.get("pix_key", "")

        dialog = EditProfessorDialog(self, prof_name, old_minutes, old_percentage, old_pix_type, old_pix_key)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_minutes, new_percentage, new_pix_type, new_pix_key = dialog.get_data()

            if not new_name:
                QMessageBox.warning(self, "Erro", "Digite o nome do professor")
                return

            if new_minutes <= 0:
                QMessageBox.warning(self, "Erro", "Digite uma duração maior que 0")
                return

            # Calcular diferença de tempo
            time_difference = new_minutes - old_minutes
            total_current_minutes = sum(p["minutes"] for p in self.professors.values())
            new_total_minutes = total_current_minutes + time_difference
            total_course_minutes = self.course_total_minutes()

            if new_total_minutes > total_course_minutes:
                QMessageBox.warning(
                    self,
                    "⚠️ Excede Total de Horas",
                    f"A nova duração excederia o total permitido!\n"
                    f"Total atual seria: {self.format_duration(new_total_minutes)}\n"
                    f"Máximo permitido: {self.format_duration(total_course_minutes)}\n\n"
                    f"Aumente a carga horária total do curso antes de aumentar a do professor."
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

            # Se mudou o nome, remover entrada antiga local e global
            if new_name != prof_name:
                del self.professors[prof_name]
                if prof_name in self.global_pix_data:
                    del self.global_pix_data[prof_name]

            # Adicionar/atualizar com novos valores no curso
            self.professors[new_name] = {"minutes": new_minutes, "percentage": new_percentage}

            # Atualizar chaves globais de PIX
            self.global_pix_data[new_name] = {
                "pix_type": new_pix_type,
                "pix_key": new_pix_key
            }
            self.save_global_pix_data()

            self.update_professors_table()
            self.calculate_results()

            QMessageBox.information(self, "✅ Sucesso", f"Professor '{new_name}' atualizado!")

    def calculate_results(self):
        if not self.professors:
            self.result_text.setText("Nenhum professor adicionado")
            return
        
        total_value = self.course_value_input.value()
        total_minutes = self.course_total_minutes()

        if total_value <= 0:
            self.result_text.setText("⚠️ Digite um valor de curso maior que 0")
            return

        if total_minutes <= 0:
            self.result_text.setText("⚠️ Informe a carga horária total do curso (HH:mm)")
            return

        # Calcular valor por hora/aula total do curso
        total_hours = total_minutes / 60.0
        value_per_hour_total = total_value / total_hours

        # Total de minutos dos professores (converter para horas)
        total_prof_minutes = sum(p["minutes"] for p in self.professors.values())
        total_prof_hours = total_prof_minutes / 60.0

        result_lines = [
            f"<b>💰 Valor Total do Curso:</b> R$ {total_value:.2f}",
            f"<b>⏱️ Carga Horária (Curso):</b> {self.format_duration(total_minutes)} "
            f"({total_minutes:.0f} min / {total_hours:.4f}h)",
            f"<b>💳 Valor da Hora/Aula:</b> R$ {value_per_hour_total:.2f}",
            f"<br>",
            f"<b>🎯 Total de Horas Gravadas:</b> {total_prof_minutes:.0f} min ({total_prof_hours:.2f}h)",
            "<br>",
            "<b>👥 Distribuição de Repasse por Venda:</b>",
            "<table style='margin-top: 5px;' width='100%'>",
        ]
        
        total_distributed = 0
        for prof_name, data in sorted(self.professors.items()):
            minutes = data["minutes"]
            percentage = data["percentage"]
            hours = minutes / 60.0

            # Valor da hora/aula do professor é baseado na sua porcentagem em cima da hora/aula do curso
            prof_hour_value = value_per_hour_total * (percentage / 100.0)
            prof_total_value = hours * prof_hour_value
            prof_total_percentage = (prof_total_value / total_value) * 100.0
            total_distributed += prof_total_value

            result_lines.append(
                f"<tr><td>&nbsp;<b>{prof_name}:</b></td>"
                f"<td>&nbsp;{self.format_duration(minutes)} ({percentage:.1f}% H/A)</td>"
                f"<td>&nbsp;→ <b>R$ {prof_total_value:.2f}</b></td>"
                f"<td>&nbsp;<b>{prof_total_percentage:.2f}%</b></td></tr>"
            )
        
        result_lines.append("</table>")
        total_distributed_percentage = (total_distributed / total_value) * 100.0
        result_lines.append(f"<br><b>✅ Total Distribuído:</b> R$ {total_distributed:.2f} ({total_distributed_percentage:.2f}%)")

        if total_distributed_percentage > self.COMMISSION_LIMIT_PERCENT:
            result_lines.append(
                f"<br><span style='color: #ff5555;'><b>Alerta:</b> Total excede "
                f"{self.COMMISSION_LIMIT_PERCENT:.1f}% do valor do curso!</span>"
            )

        self.result_text.setText("\n".join(result_lines))
    
    def save_data(self):
        # Apenas salva os dados do curso e a porcentagem do professor, NÃO salva as chaves PIX (fiel ao requisito)
        total_minutes = self.course_total_minutes()
        data = {
            "course_value": self.course_value_input.value(),
            "course_minutes": total_minutes,
            # mantido para os arquivos salvos pela versao antiga continuarem legiveis
            "course_hours": total_minutes / 60.0,
            "professors": self.professors
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Dados do Curso", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "✅ Sucesso", f"Dados do curso salvos em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def load_data_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Dados do Curso", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.course_value_input.setValue(data.get("course_value", 0))
                # arquivos novos trazem minutos exatos; os antigos, horas decimais
                if data.get("course_minutes") is not None:
                    total_minutes = float(data["course_minutes"])
                else:
                    total_minutes = float(data.get("course_hours", 0)) * 60
                self.course_hours_input.setText(self.format_duration(total_minutes))

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

                # A tabela será atualizada buscando automaticamente os PIX correspondentes da base global
                self.update_professors_table()
                self.calculate_results()
                QMessageBox.information(self, "✅ Sucesso", "Dados do curso carregados!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar: {e}")
    
    def clear_all(self):
        reply = QMessageBox.question(
            self, "Confirmar", "Deseja limpar todos os dados do curso atual?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.professors = {}
            self.course_value_input.setValue(100.0)
            self.course_hours_input.setText(self.format_duration(600))
            self.prof_name_input.clear()
            self.prof_time_input.setTime(QTime(0, 0, 0))
            self.prof_percentage_input.setValue(25.0)
            self.prof_pix_key_input.clear()
            self.update_professors_table()
            self.result_text.setText("Adicione professores para ver o resultado...")

    def simulate_purchase(self):
        if not self.professors:
            QMessageBox.warning(self, "Erro", "Nenhum professor cadastrado no curso atual para receber repasses.")
            return

        total_value = self.course_value_input.value()
        total_minutes = self.course_total_minutes()

        if total_value <= 0 or total_minutes <= 0:
            QMessageBox.warning(self, "Erro", "Defina o valor e a carga horária do curso antes de simular.")
            return
        total_hours = total_minutes / 60.0

        # Verificar se existem chaves PIX de todos os professores
        missing_pix = []
        for prof_name in self.professors:
            pix_info = self.global_pix_data.get(prof_name, {})
            if not pix_info.get("pix_key"):
                missing_pix.append(prof_name)

        if missing_pix:
            names = ", ".join(missing_pix)
            reply = QMessageBox.question(
                self,
                "⚠️ PIX Faltando",
                f"Os seguintes professores não possuem chave PIX cadastrada:\n{names}\n\n"
                "Deseja continuar? O repasse para esses professores falhará.",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Iniciar simulação e registrar logs
        from datetime import datetime
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        log_lines = []
        log_lines.append(f"<span style='color: #4cd137;'>[{now_str}]</span> <b>🛒 CURSO ADQUIRIDO!</b> Valor da venda: <b style='color: #00a8ff;'>R$ {total_value:.2f}</b>")

        value_per_hour_total = total_value / total_hours

        for prof_name, data in sorted(self.professors.items()):
            minutes = data["minutes"]
            percentage = data["percentage"]
            hours = minutes / 60.0

            prof_hour_value = value_per_hour_total * (percentage / 100.0)
            prof_total_value = hours * prof_hour_value

            pix_info = self.global_pix_data.get(prof_name, {})
            pix_type = pix_info.get("pix_type", "")
            pix_key = pix_info.get("pix_key", "")

            if not pix_key:
                log_lines.append(
                    f"&nbsp;&nbsp;<span style='color: #e84118;'>❌ Repasse Falhou para <b>{prof_name}</b>: R$ {prof_total_value:.2f}</span> (Nenhuma chave PIX cadastrada)"
                )
            else:
                log_lines.append(
                    f"&nbsp;&nbsp;<span style='color: #2ece89;'>⚡ PIX Enviado para <b>{prof_name}</b>: <b>R$ {prof_total_value:.2f}</b></span> "
                    f"(Chave {pix_type}: {pix_key}) - <i style='color: #2ece89;'>Pago Instantaneamente! ✅</i>"
                )

        log_lines.append("<hr style='border: 1px solid #3b4252;'>")
        
        # Append HTML logs
        current_logs = self.sales_log.toHtml()
        if "Aguardando simulação" in current_logs or not current_logs.strip():
            self.sales_log.setHtml("<br>".join(log_lines))
        else:
            self.sales_log.setHtml(current_logs + "<br>" + "<br>".join(log_lines))
        
        # Auto-scroll para o final
        self.sales_log.verticalScrollBar().setValue(self.sales_log.verticalScrollBar().maximum())

    def clear_sales_log(self):
        self.sales_log.clear()
        self.sales_log.setPlaceholderText("Aguardando simulação de compra...")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = TeacherHourCalculator()
    calculator.show()
    sys.exit(app.exec_())
