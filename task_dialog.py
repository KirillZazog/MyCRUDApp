from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QTextEdit, QComboBox, QPushButton, QDateEdit)
from PyQt5.QtCore import QDate

class TaskDialog(QDialog):
    def __init__(self, task=None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Новая задача" if task is None else "Редактировать задачу")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.description_edit = QTextEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["todo", "in_progress", "done"])
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())

        form.addRow("Название:", self.title_edit)
        form.addRow("Описание:", self.description_edit)
        form.addRow("Статус:", self.status_combo)
        form.addRow("Срок:", self.due_date_edit)

        layout.addLayout(form)

        btn_layout = QVBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        if task:
            self.title_edit.setText(task['title'])
            self.description_edit.setPlainText(task.get('description', ''))
            self.status_combo.setCurrentText(task.get('status', 'todo'))
            if task.get('due_date'):
                due = task['due_date']
                self.due_date_edit.setDate(QDate(due.year, due.month, due.day))

    def get_task_data(self):
        due_date = self.due_date_edit.date().toPyDate()
        return {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'status': self.status_combo.currentText(),
            'due_date': due_date
        }