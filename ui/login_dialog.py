from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from typing import Dict, List, Optional
from api.owencloud import OwenCloudClient
from services.auth_storage import AuthStorage


class LoginDialog(QDialog):
    """
    Окно входа:
        1) ввод логина/пароля
        2) выбор устройства (если их несколько)
    После успешного выбора:
        - self.api_client
        - self.selected_device_id
        - self.param_ids_by_key
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.resize(1000, 550)

        self.api_client = OwenCloudClient()
        self.devices: List[Dict] = []
        self.selected_device_id: Optional[int] = None
        self.param_ids_by_key: Dict[str, int] = {}

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(30)

        # Левая колонка (лого/описание)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(15)

        title_lbl = QLabel("Термовизор")
        title_lbl.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        left_layout.addWidget(title_lbl)

        descr_lbl = QLabel(
            "Войдите под своей учётной записью, выберите котельную\n"
            "и получайте данные в реальном времени."
        )
        descr_lbl.setStyleSheet("color: #AAAAAA; font-size: 11pt;")
        descr_lbl.setWordWrap(True)
        left_layout.addWidget(descr_lbl)

        left_layout.addStretch()

        main_layout.addWidget(left_frame, 1)

        # Правая колонка (формы)
        right_frame = QFrame()
        right_frame.setObjectName("AuthCard")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        self.stack = QStackedLayout()
        right_layout.addLayout(self.stack)

        # Страница 1: логин/пароль
        self.login_page = QWidget()
        lp_layout = QVBoxLayout(self.login_page)
        lp_layout.setSpacing(12)

        lp_title = QLabel("Авторизация")
        lp_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lp_layout.addWidget(lp_title)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин (e-mail)")
        lp_layout.addWidget(self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Пароль")
        lp_layout.addWidget(self.password_edit)

        self.login_error_lbl = QLabel("")
        self.login_error_lbl.setStyleSheet("color: #ff8080;")
        lp_layout.addWidget(self.login_error_lbl)

        lp_layout.addStretch()

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.on_login_clicked)
        lp_layout.addWidget(self.login_btn)

        self.stack.addWidget(self.login_page)

        # Страница 2: выбор устройства
        self.device_page = QWidget()
        dp_layout = QVBoxLayout(self.device_page)
        dp_layout.setSpacing(12)

        dp_title = QLabel("Выбор устройства")
        dp_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        dp_layout.addWidget(dp_title)

        self.device_combo = QComboBox()
        dp_layout.addWidget(self.device_combo)

        self.device_error_lbl = QLabel("")
        self.device_error_lbl.setStyleSheet("color: #ff8080;")
        dp_layout.addWidget(self.device_error_lbl)

        dp_layout.addStretch()

        self.device_btn = QPushButton("Продолжить")
        self.device_btn.clicked.connect(self.on_device_choose)
        dp_layout.addWidget(self.device_btn)

        self.stack.addWidget(self.device_page)

        main_layout.addWidget(right_frame, 1)

        self.stack.setCurrentIndex(0)
        # === АВТОЗАГРУЗКА ЛОГИНА/ПАРОЛЯ ===
        saved_login, saved_password = AuthStorage.load()

        if saved_login:
            self.login_edit.setText(saved_login)
        if saved_password:
            self.password_edit.setText(saved_password)

    # ---------- Обработчики ----------

    def on_login_clicked(self):
        """Обработка нажатия 'Войти'."""
        login = self.login_edit.text().strip()
        pwd = self.password_edit.text().strip()

        if not login or not pwd:
            self.login_error_lbl.setText("Введите логин и пароль.")
            return

        self.login_error_lbl.setText("")
        self.login_btn.setEnabled(False)

        try:
            # Авторизация
            self.api_client.auth(login, pwd)
            AuthStorage.save(login, pwd)

            # Получаем устройства
            self.devices = self.api_client.get_devices()
            if not self.devices:
                raise RuntimeError("Для этого аккаунта нет устройств.")

            # Заполняем комбобокс
            self.device_combo.clear()
            for dev in self.devices:
                name = dev.get("name", "Без имени")
                dev_id = dev.get("id")
                self.device_combo.addItem(f"{name} (ID: {dev_id})", dev_id)

            # Переключаемся на страницу выбора устройства
            self.stack.setCurrentIndex(1)

        except Exception as e:
            self.login_error_lbl.setText(str(e))
            print("Ошибка входа:", e)
        finally:
            self.login_btn.setEnabled(True)

    def on_device_choose(self):
        """Обработка нажатия 'Продолжить' (выбор устройства)."""
        idx = self.device_combo.currentIndex()
        if idx < 0:
            self.device_error_lbl.setText("Выберите устройство.")
            return

        self.device_error_lbl.setText("")
        self.selected_device_id = int(self.device_combo.currentData())
        self.accept()