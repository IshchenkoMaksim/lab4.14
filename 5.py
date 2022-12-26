#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import (
    QTableView,
    QApplication,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QFrame,
    QLabel,
    QHeaderView,
    QDateEdit,
    QTabWidget,
)
from PySide2.QtCore import (
    Signal,
)
from PySide2.QtCore import QSortFilterProxyModel, Qt, QRect
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    ForeignKey,
    insert,
    delete,
)
import sys


class DateBase:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///database.db")
        self.engine.connect()
        metadata = MetaData()
        self.Subscribers = Table(
            "Subscribers",
            metadata,
            Column("ФИО", Text(), nullable=False),
            Column("Статус", Text(), nullable=False),
            Column("Дата_рождения", Text(), nullable=False),
            Column("Серия_и_номер_паспорта", Text(), primary_key=True),
        )
        self.Periodical = Table(
            "Periodical",
            metadata,
            Column("Идентификатор", Text(), primary_key=True),
            Column("Название", Text(), nullable=False),
            Column("Дата_начала_выпуска", Text(), nullable=False),
            Column("Дата_окончания_выпуска", Text(), nullable=False),
        )
        self.Subscriptions = Table(
            "Subscriptions",
            metadata,
            Column("Серия_номер_паспорта", ForeignKey(self.Subscribers.c.Серия_и_номер_паспорта)),
            Column("Идентификатор_изд", ForeignKey(self.Periodical.c.Идентификатор)),
            Column("Начало_подписки", Text(), nullable=False),
            Column("Конец_подписки", Text(), nullable=False),
        )
        metadata.create_all(self.engine)
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("database.db")
        if not db.open():
            return False
        self.conn = self.engine.connect()

        if not self.table_is_empty():
            ins = insert(self.Subscribers)
            r = self.conn.execute(
                ins,
                ФИО="Артур Хейли",
                Статус="Обычный",
                Дата_рождения="05.04.1920",
                Серия_и_номер_паспорта="1212344556",
            )
            r = self.conn.execute(
                ins,
                ФИО="Эльдар Татар",
                Статус="Писатель",
                Дата_рождения="09.09.2009",
                Серия_и_номер_паспорта="0399568675",
            )
            r = self.conn.execute(
                ins,
                ФИО="Барин Володимир",
                Статус="Vip",
                Дата_рождения="17.11.1985",
                Серия_и_номер_паспорта="6412344556",
            )
            ins = insert(self.Periodical)
            r = self.conn.execute(
                ins,
                Идентификатор="#4537",
                Название="Аргументы и факты",
                Дата_начала_выпуска="1.01.1999",
                Дата_окончания_выпуска="30.01.2030",
            )
            r = self.conn.execute(
                ins,
                Идентификатор="#0004",
                Название="Анекдоты от",
                Дата_начала_выпуска="08.08.2017",
                Дата_окончания_выпуска="08.08.2024",
            )
            r = self.conn.execute(
                ins,
                Идентификатор="#1186",
                Название="Время",
                Дата_начала_выпуска="11.11.1991",
                Дата_окончания_выпуска="11.11.2111",
            )
            ins = insert(self.Subscriptions)
            r = self.conn.execute(
                ins,
                Серия_номер_паспорта="1212344556",
                Идентификатор_изд="#0004",
                Начало_подписки="01.01.2022",
                Конец_подписки="01.01.2023",
            )
            r = self.conn.execute(
                ins,
                Серия_номер_паспорта="6412344556",
                Идентификатор_изд="#4537",
                Начало_подписки="20.12.2021",
                Конец_подписки="20.06.2023",
            )
            r = self.conn.execute(
                ins,
                Серия_номер_паспорта="0399568675",
                Идентификатор_изд="#1186",
                Начало_подписки="11.11.2020",
                Конец_подписки="11.11.2025",
            )

    def table_is_empty(self):
        data = self.Subscribers.select()
        table_data = self.conn.execute(data)
        return table_data.fetchall()


class TableView:
    tabBarClicked = Signal(int)

    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.SetupUI()
        self.current_tab = "Subscribers"
        self.tab_id = "Серия_и_номер_паспорта"

    def SetupUI(self):
        self.parent.setGeometry(50, 100, 750, 450)
        self.parent.setWindowTitle("Подписчики периодических изданий")
        self.main_conteiner = QGridLayout()
        self.frame1 = QFrame()
        self.frame2 = QFrame()
        self.frame2.setVisible(False)
        self.main_conteiner.addWidget(self.frame1, 0, 0)
        self.main_conteiner.addWidget(self.frame2, 0, 0)
        self.frame1.setStyleSheet(
            """
            font-size: 13px;
            """
        )
        self.frame2.setStyleSheet(
            """
            font-size: 13px;
            """
        )
        self.table_view = QTableView()
        self.table_view.setModel(self.tableSubscribers())
        self.table_view2 = QTableView()
        self.table_view2.setModel(self.tablePeriodical())
        self.table_view3 = QTableView()
        self.table_view3.setModel(self.tableSubscriptions())
        self.table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view2.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_view3.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.layout_main = QGridLayout(self.frame1)
        self.layh = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_del = QPushButton("Удалить")
        self.layh.addWidget(self.btn_add)
        self.layh.addWidget(self.btn_del)
        self.tab_conteiner = QTabWidget()
        self.tab_conteiner.setTabShape(QTabWidget.Rounded)
        self.tab_conteiner.setTabPosition(QTabWidget.South)
        self.tab_conteiner.addTab(self.table_view, "Подписчики")
        self.tab_conteiner.addTab(self.table_view2, "Издания")
        self.tab_conteiner.addTab(self.table_view3, "Подписки")
        self.layout_main.addWidget(self.tab_conteiner, 3, 0)
        self.layout_main.addLayout(self.layh, 0, 0)
        self.parent.setLayout(self.main_conteiner)
        self.btn_del.clicked.connect(self.delete)
        self.btn_add.clicked.connect(self.add)
        self.layout_grid = QGridLayout(self.frame2)
        self.btn_add2 = QPushButton("Добавить данные")
        self.btn_add2.setFixedWidth(300)
        self.btn_otmena = QPushButton("Отмена")
        self.name_line = QLineEdit()
        self.name = QLabel("ФИО: ")
        self.status_line = QLineEdit()
        self.status = QLabel("Статус: ")
        self.dateb_line = QDateEdit()
        self.dateb_line.setCalendarPopup(True)
        self.dateb_line.setTimeSpec(Qt.LocalTime)
        self.dateb_line.setGeometry(QRect(220, 31, 133, 20))
        self.dateb = QLabel("Дата рождения: ")
        self.pasport_line = QLineEdit()
        self.pasport = QLabel("Номер и серия паспорта: ")
        self.periodical_line = QLineEdit()
        self.periodical = QLabel("Издание: ")
        self.daten_line = QDateEdit()
        self.daten_line.setCalendarPopup(True)
        self.daten_line.setTimeSpec(Qt.LocalTime)
        self.daten_line.setGeometry(QRect(220, 31, 133, 20))
        self.daten = QLabel("Дата начала подписки: ")
        self.datek_line = QDateEdit()
        self.datek_line.setCalendarPopup(True)
        self.datek_line.setTimeSpec(Qt.LocalTime)
        self.datek_line.setGeometry(QRect(220, 31, 133, 20))
        self.datek = QLabel("Дата конца подписки: ")
        self.layout_grid.addWidget(self.name_line, 0, 1)
        self.layout_grid.addWidget(self.name, 0, 0)
        self.layout_grid.addWidget(self.status, 1, 0)
        self.layout_grid.addWidget(self.status_line, 1, 1)
        self.layout_grid.addWidget(self.dateb, 2, 0)
        self.layout_grid.addWidget(self.dateb_line, 2, 1)
        self.layout_grid.addWidget(self.pasport_line, 3, 1)
        self.layout_grid.addWidget(self.pasport, 3, 0)
        self.layout_grid.addWidget(self.periodical_line, 4, 1)
        self.layout_grid.addWidget(self.periodical, 4, 0)
        self.layout_grid.addWidget(self.daten, 5, 0)
        self.layout_grid.addWidget(self.daten_line, 5, 1)
        self.layout_grid.addWidget(self.datek, 6, 0)
        self.layout_grid.addWidget(self.datek_line, 6, 1)
        self.layout_grid.addWidget(self.btn_add2, 7, 1)
        self.layout_grid.addWidget(self.btn_otmena, 7, 0)
        self.btn_otmena.clicked.connect(self.back)
        self.btn_add2.clicked.connect(self.add_data)
        self.tab_conteiner.tabBarClicked.connect(self.handle_tabbar_clicked)

    def tableSubscribers(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Subscribers.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Subscribers"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tablePeriodical(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Periodical.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Periodical"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def tableSubscriptions(self):
        self.raw_model = QSqlTableModel()
        self.query = self.db.Subscriptions.select()
        self.sqlquery = QSqlQuery()
        self.sqlquery.exec_(str(self.query))
        self.raw_model.setQuery(self.sqlquery)
        self.current_tab = "Subscriptions"
        self.model = QSortFilterProxyModel()
        self.model.setSourceModel(self.raw_model)
        return self.model

    def add(self):
        self.frame1.setVisible(False)
        self.frame2.setVisible(True)

    def back(self):
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def update(self):
        self.table_view.setModel(self.tableSubscribers())
        self.table_view2.setModel(self.tablePeriodical())
        self.table_view3.setModel(self.tableSubscriptions())

    def add_data(self):
        ins = insert(self.db.Subscribers)
        r = self.db.conn.execute(
            ins,
            ФИО=self.name_line.text(),
            Статус=self.status_line.text(),
            Дата_рождения=self.dateb_line.text(),
            Серия_и_номер_паспорта=self.pasport_line.text(),
        )
        ins = insert(self.db.Subscriptions)
        r = self.db.conn.execute(
            ins,
            Серия_номер_паспорта=self.pasport_line.text(),
            Идентификатор_изд=self.periodical_line.text(),
            Начало_подписки=self.daten_line.text(),
            Конец_подписки=self.datek_line.text(),
        )
        self.update()
        self.frame1.setVisible(True)
        self.frame2.setVisible(False)

    def cell_click(self):
        if self.current_tab == "Subscribers":
            return self.table_view.model().data(self.table_view.currentIndex())
        if self.current_tab == "Periodical":
            return self.table_view2.model().data(self.table_view2.currentIndex())
        if self.current_tab == "Subscriptions":
            return self.table_view3.model().data(self.table_view3.currentIndex())

    def delete(self):
        if self.current_tab == "Subscribers":
            del_item = delete(self.db.Subscribers).where(
                self.db.Subscribers.c.Серия_и_номер_паспорта.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Periodical":
            del_item = delete(self.db.Periodical).where(
                self.db.Periodical.c.Идентификатор.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        if self.current_tab == "Subscriptions":
            del_item = delete(self.db.Subscriptions).where(
                self.db.Subscriptions.c.Серия_номер_паспорта.like(self.cell_click())
            )
            r = self.db.conn.execute(del_item)
        self.update()

    def handle_tabbar_clicked(self, index):
        if index == 0:
            self.current_tab = "Subscribers"
            self.tab_id = "Серия_и_номер_паспорта"
        elif index == 1:
            self.current_tab = "Periodical"
            self.tab_id = "Идентификатор_изд"
        else:
            self.current_tab = "Subscriptions"
            self.tab_id = "Серия_номер_паспорта"


class MainWindow(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)
        my_datebase = DateBase()
        self.main_view = TableView(self, my_datebase)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
