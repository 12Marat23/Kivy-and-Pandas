import requests
import datetime

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.button import Button
from kivy.core.window import Window

# Загрузка файла разметки Kivy
Builder.load_file('weather.kv')

# Константы
APPID = 'Ваш API-ключ'


class Main(FloatLayout):
    def __init__(self, **kwargs):
        """Конструктор класса, который используется для инициализации нового объекта класса.
        super().__init__(**kwargs) - метод, который помогает вызвать методы родительского класса
        из дочернего класса
        """
        super().__init__(**kwargs)
        self.my_city = None
        today = datetime.datetime.today()  # берем дату и время в данный момент
        self.ids.time_id.text = today.strftime("%H.%M")  # Преобразует в строку и выводит время на экран при запуске
        self.ids.data_id.text = today.strftime("%d/%m/%Y")  # Преобразует в строку и выводит дату на экран при запуске

    def press_me(self, item):
        """ Вызывается при нажатьи EnterButton
        self.my_city принимать значение из TextInput
        """
        self.my_city = self.ids.text_id.text
        # создаем объект класса Data, инициализируем его с атрибутом my_city
        data_handler = Data(self.my_city)
        # вызовам метод fetch_coordinates объекта data_handler для получения координат.
        data_handler.fetch_coordinates(self)


class Data:
    def __init__(self, city_name):
        """Конструктор класса, который используется для инициализации нового объекта класса."""
        self.city_name = city_name
        self.weather_data = None
        self.weather_url = None

    def fetch_coordinates(self, main_screen):
        """ Метод делает запрос в openweathermap.org для получения координат города,
         который получает из класса Main. Так же идет обработка ошибок.
         """
        url = f'http://api.openweathermap.org/geo/1.0/direct?q={self.city_name}&limit=1&appid={APPID}'
        response = requests.get(url)
        if response.status_code == 200:  # Проверка запроса
            self.coor_data = response.json()
            try:
                self.get_weather_data()
                self.update_weather(main_screen)
                self.update_time(main_screen)
                self.update_background(main_screen)
                self.clear_input(main_screen)
                self.update_city(main_screen)
                # Создает объект класса FiveDaysWeather и передает координаты
                five_days_handler = FiveDaysWeather(self.coor_data[0]['lat'], self.coor_data[0]['lon'])
                # Вызывает методы объекта five_days_handler
                five_days_handler.fetch_five_days_forecast()
                five_days_handler.display_five_days_forecast(main_screen)
            except Exception as e:
                print(f'Возникла ошибка {e}')
                self.clear_input(main_screen)
        else:
            print('Ошибка запроса координат: ', response.status_code)

    def update_city(self, main_screen):
        """Выводить название города на экран.
        При этом, при помощи capitalize() форматирует что бы первая буква была заглавная"""
        main_screen.ids.city_id.text = self.city_name.capitalize()

    def clear_input(self, main_screen):
        """ Очищает поле ввода TextInput"""
        main_screen.ids.text_id.text = ''

    def get_weather_data(self):
        """Получает данные о погоде и записывает в переменную """
        self.lat = self.coor_data[0]['lat']
        self.lon = self.coor_data[0]['lon']
        self.weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={APPID}&units=metric&lang=ru'
        self.weather_data = requests.get(self.weather_url).json()

    def update_weather(self, main_screen):
        """Вывод полученных данных на экран"""
        main_screen.ids.label_id.text = f"{round(self.weather_data['main']['temp'])}\u00B0C"
        main_screen.ids.icon.source = f"image/{self.weather_data['weather'][0]['icon']}.png"
        main_screen.ids.feels_like.text = f"Чувствуется как {round(self.weather_data['main']['feels_like'])}\u00B0C"
        main_screen.ids.humidity.text = f"Влажность {self.weather_data['main']['humidity']}%"
        main_screen.ids.wind.text = f"{self.weather_data['wind']['speed']} м/с"

    def update_time(self, main_screen):
        """ Получаем данные о времени и часовом поясе и выводим в удобочитаемом формате """
        utc_datetime = datetime.datetime.utcfromtimestamp(self.weather_data['dt'])
        timezone_offset = datetime.timedelta(seconds=self.weather_data['timezone'])
        local_datetime = utc_datetime + timezone_offset
        main_screen.ids.data_id.text = local_datetime.strftime('%d/%m/%Y')
        main_screen.ids.time_id.text = local_datetime.strftime('%H.%M')

    def update_background(self, main_screen):
        """ Функция переключает фон в зависимости от времени суток """
        times = int(main_screen.ids.time_id.text.split('.')[0])
        if 0 <= times < 6:
            main_screen.ids.weather_image.source = 'image/ночь.jpg'
        elif 6 <= times < 12:
            main_screen.ids.weather_image.source = 'image/утро.png'
        elif 12 <= times < 18:
            main_screen.ids.weather_image.source = 'image/день.jpg'
        elif 18 <= times <= 24:
            main_screen.ids.weather_image.source = 'image/вечер.jpg'


class FiveDaysWeather:
    """Класс получает и выводит информацию о погоде на ближайшие 5 дней"""
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.weather_url_five = f'https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={APPID}&units=metric&lang=ru'
        self.weather_data_five = None
        self.select_data_2 = {}
        self.temp = []
        self.pressure = []
        self.wind = []

    def fetch_five_days_forecast(self):
        """Метод делает запрос и обрабатывает его: проверяет на ошибки запроса
         и записывает данные в переменную"""
        response = requests.get(self.weather_url_five)
        if response.status_code == 200:
            self.weather_data_five = response.json()
            self.extract_five_days_data()
        else:
            print('Ошибка запроса прогноза на 5 дней: ', response.status_code)

    def extract_five_days_data(self):
        """
            Извлекает данные прогноза на 5 дней из общего массива данных.

            Проходит по списку прогнозов и выбирает данные, соответствующие времени 12:00
            каждого дня. Извлеченные данные сохраняются в словаре `select_data_2`, где ключом
            является дата в формате 'дд/мм'. Также извлекает и сохраняет температуру, давление
            и скорость ветра для каждого дня в соответствующие списки `temp`, `pressure` и `wind`.

            Это необходимо для отображения прогноза на 5 дней с более детальной информацией по
            каждому дню.

            Пример структуры словаря `select_data_2`:
            {
                '18/06': {данные прогноза на 18 июня в 12:00},
                '19/06': {данные прогноза на 19 июня в 12:00},
                ...
            }
        """
        for data in self.weather_data_five['list']:
            dt_txt = data['dt_txt']
            dt_obj = datetime.datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
            if dt_obj.hour == 12:
                dt_inp = dt_obj.strftime('%d/%m')
                self.select_data_2[dt_inp] = data

        for data in self.select_data_2.values():
            self.temp.append(str(data['main']['temp']))
            self.pressure.append(str(data['main']['pressure']))
            self.wind.append(str(data['wind']['speed']))

    def display_five_days_forecast(self, main_screen):
        keys_weather = list(self.select_data_2.keys())
        ids = ['one', 'two', 'three', 'four', 'five']
        for id_, keys in zip(ids, keys_weather):
            getattr(main_screen.ids, id_).text = keys
        self.update_temp_five_days(main_screen)
        self.update_pressure_five_days(main_screen)
        self.update_wind_five_days(main_screen)

    def update_temp_five_days(self, main_screen):
        ids = ['one_temp', 'two_temp', 'three_temp', 'four_temp', 'five_temp']
        for id_, temp in zip(ids, self.temp):
            getattr(main_screen.ids, id_).text = f'{temp} \u00B0C'

    def update_pressure_five_days(self, main_screen):
        ids = ['one_pressur', 'two_pressur', 'three_pressur', 'four_pressur', 'five_pressur']
        for id_, pressure in zip(ids, self.pressure):
            getattr(main_screen.ids, id_).text = f'{pressure} мм.рт.ст.'

    def update_wind_five_days(self, main_screen):
        ids = ['one_win', 'two_win', 'three_win', 'four_win', 'five_win']
        for id_, wind in zip(ids, self.wind):
            getattr(main_screen.ids, id_).text = f'{wind} м/с'


class EnterButton(FocusBehavior, Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_parent(self, widget, parent):
        Window.bind(on_key_down=self.key_action)

    def key_action(self, *args):
        if args[1] == 13:  # Клавиша Enter
            self.dispatch('on_release')
            app = App.get_running_app()
            app.root.press_me(app.root.ids.text_id.text)


class MyWeather(App):
    def build(self):
        return Main()


if __name__ == '__main__':
    MyWeather().run()
