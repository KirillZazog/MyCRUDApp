import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QDialog)
from database import get_db_connection
from task_dialog import TaskDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой CRUD — Задачи")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить список")
        self.btn_add = QPushButton("Добавить задачу")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Описание", "Статус", "Срок", "Создано"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Подключение сигналов
        self.btn_refresh.clicked.connect(self.load_tasks)
        self.btn_add.clicked.connect(self.add_task)
        self.btn_edit.clicked.connect(self.edit_task)
        self.btn_delete.clicked.connect(self.delete_task)

        self.load_tasks()

    def load_tasks(self):
        conn = get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, status, due_date, created_at 
                    FROM tasks 
                    ORDER BY id DESC
                """)
                tasks = cur.fetchall()

            self.table.setRowCount(len(tasks))
            for row, task in enumerate(tasks):
                self.table.setItem(row, 0, QTableWidgetItem(str(task['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(task['title']))
                self.table.setItem(row, 2, QTableWidgetItem(task.get('description') or ''))
                self.table.setItem(row, 3, QTableWidgetItem(task['status']))
                due = task['due_date'].strftime("%Y-%m-%d") if task['due_date'] else ''
                self.table.setItem(row, 4, QTableWidgetItem(due))
                created = task['created_at'].strftime("%Y-%m-%d %H:%M") if task['created_at'] else ''
                self.table.setItem(row, 5, QTableWidgetItem(created))

            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            conn.close()

    def add_task(self):
        dialog = TaskDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_task_data()
            conn = get_db_connection()
            if not conn:
                return
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO tasks (title, description, status, due_date)
                        VALUES (%s, %s, %s, %s)
                    """, (data['title'], data['description'], data['status'], data['due_date']))
                conn.commit()
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                conn.close()

    def edit_task(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите задачу для редактирования")
            return

        task_id = int(self.table.item(row, 0).text())

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                task = cur.fetchone()
        finally:
            conn.close()

        if not task:
            return

        dialog = TaskDialog(task, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_task_data()
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tasks 
                        SET title=%s, description=%s, status=%s, due_date=%s
                        WHERE id=%s
                    """, (data['title'], data['description'], data['status'], data['due_date'], task_id))
                conn.commit()
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                conn.close()

    def delete_task(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите задачу для удаления")
            return

        task_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Подтверждение",
                                    f"Удалить задачу №{task_id}?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
                self.load_tasks()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
            finally:
                conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())