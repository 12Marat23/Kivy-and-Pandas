from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
import pandas as pd
from pandas import DataFrame
import sqlite3
from kivy.uix.screenmanager import ScreenManager, Screen
from functools import partial

Builder.load_file('mydb.kv')


class MainPage(Screen):
    def selected(self, filename):
        """ Метод selected получает путь файлу из списка файлов
        file_paths = filename[0] используется для получения пути
        к первому выбранному файлу из списка файлов поученного через FileChooserIconView
        Предполагается, что filename содержит информацию о выбранных файлах,
        и нужен только первый файл для открытия соединения с базой данных SQLite.

        conn = sqlite3.connect(f'{file_paths}') устанавливаем соединение с БД используя порченый путь.
        query = "SELECT * FROM Observation" выполняем SQL запрос для выборки всех данных из таблицы Observation.
        """
        file_paths = filename[0]
        conn = sqlite3.connect(f'{file_paths}')
        query = "SELECT * FROM Observation"
        self.data = pd.read_sql(query, conn)

        data_page = self.manager.get_screen('Data')  # Получаем экземпляр экрана с именем 'Data'
        data_page.display_data(self.data)  # Вызов метода display_data на экране 'Data'
        # и передает данные self.data для отображения на экране

    def open_data_page(self):
        """
            Данный метод отвечает за переключения между экранами
            При вызове метода open_data_page значение текущего экрана менеджера
            экранов меняется на 'Второй', что приводит к отображению содержимого DataPage.
        """
        self.manager.current = 'Data'


class DataPage(Screen):
    def __init__(self, **kwargs):
        """
        Данный класс выполняет инициализацию класса при его создании
        super(DataPage, self).__init__(**kwargs) вызывает метод __init__ родительского класса.
        Он используется для инициализации родительского класса и передачи любых дополнительных аргументов,
        которые могут быть переданы в конструктор.
        self.data = DataFrame() Здесь происходит инициализация атрибута data экземпляра класса DataPage.
        В данном случае, self.data инициализируется объектом пустого DataFrame из библиотеки pandas.
        Таким образом, когда экземпляр класса DataPage создается, у него уже есть атрибут data,
        который представляет собой пустой DataFrame.
        """
        super(DataPage, self).__init__(**kwargs)
        self.data = DataFrame()  # Инициализация пустым DataFrame

    def on_start(self):
        """
        Метод  on_start  вызывается при старте экрана DataPage.
        data_layout = self.root.ids.data_layout: Эта строка получает доступ к элементу data_layout
         на экране DataPage с помощью идентификатора data_layout. self.root
         относится к корневому виджету DataPage.

         self.display_data(self.data, data_layout): В этой строке вызывается метод display_data,
         который отображает данные на экране.
         Он принимает два аргумента: self.data (данные, которые нужно отобразить) и
         data_layout (макет, куда нужно отобразить данные).
        """
        data_layout = self.root.ids.data_layout
        self.display_data(self.data, data_layout)

    def display_data(self, data):
        """
        Данный метод отвечает за отображение данных на экране.
         Этот метод принимает два аргумента:
         self (ссылка на экземпляр класса DataPage) и data (данные, которые нужно отобразить).
         layout = self.ids.data_layout код получает доступ к виджету с идентификатором data_layout на экране DataPage
        layout.clear_widgets() Этот метод очищает все виджеты в data_layout

        layout.cols = len(data.columns) устанавливается количество столбцов в layout
        равным количеству столбцов в переданных данных.
        Это помогает правильно организовать отображение данных в виде таблицы или сетки.
        buttons_layout = self.ids.buttons_layout код получает доступ к виджету с идентификатором buttons_layout
        buttons_layout.clear_widgets() Этот метод очищает все виджеты в buttons_layout

        """
        self.data = data
        layout = self.ids.data_layout
        layout.clear_widgets()
        layout.cols = len(data.columns)
        buttons_layout = self.ids.buttons_layout
        buttons_layout.clear_widgets()
        """for column in data.columns: Формирует в цикле кнопки с названиями столбцов
         в зависимости 
         """
        for column in data.columns:
            button = Button(text=str(column), size_hint_y=None, height=40)
            button.bind(on_press=partial(self.sort_data, column))  # Привязываем обработчик
            buttons_layout.add_widget(button)
        """
        for index, row in data.iterrows(): Выводит в цикле данные 
        """
        for index, row in data.iterrows():
            for value in row:
                layout.add_widget(Label(text=str(value), size_hint_y=None, height=40))

    def sort_data(self, column_name, *args):
        """
       sort_data функция сортировки. Проверяет условие если
       self.data.empty не пустое, то сортирует, при вызове, по названиям столбцов
        """
        if not self.data.empty:
            self.data = self.data.sort_values(by=column_name)
            self.display_data(self.data)


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainPage(name='Main'))
        sm.add_widget(DataPage(name='Data'))

        return sm

    def open_data_page(self):
        sm = self.root
        sm.current = 'Data'


if __name__ == '__main__':
    MyApp().run()
