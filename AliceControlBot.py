"""
Дипломный проект по теме
Разработка голосового интерфейса взаимодействия человека и робота манипулятора
Разработал: Кусенов Никита Андреевич
** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
Задание: Разработать серверную часть для голосового помощника, реализующую получение и обработку команд от голосового помощника.
"""
import self as self
# -*- coding: utf-8 -*-
from robolink import *
from robodk import *
import re
import flask

78
import pymorphy2
from werkzeug.local import LocalProxy
import logging
import threading
import random

def suggest(*options):
    def modifier(response):
        if 'buttons' not in response:
            response['buttons'] = []

    response['buttons'] += [{'title': item, 'hide': True}
                            for item in options]
    return modifier


morph = pymorphy2.MorphAnalyzer()

class Request(dict):


    def __init__(self, dictionary):
        super().__init__(dictionary)

    self._command = self['request']['command'].rstrip('.')
    self._words = re.findall(r'[\w-]+', self._command, flags=re.UNICODE)
    self._lemmas = [morph.parse(word)[0].normal_form
                    for word in self._words]


    @property
    def command(self):
        return self._command



    @property
    def words(self):
        return self._words



    def matches(self, pattern):
        return re.fullmatch(pattern, self._command) is not None



    @property
    def lemmas(self):
        return self._lemmas



    @property
    def session_id(self):
        return self['session']['session_id']



    @property
    def user_id(self):
        return self['session']['user_id']



    def has_lemmas(self, *lemmas):
        return any(morph.parse(item)[0].normal_form in self._lemmas
                   for item in lemmas)

    request = LocalProxy(lambda: flask.g.request)


    def say(*args, **kwargs):
        if not all(isinstance(item, str) or callable(item)
                   for item in args):
            raise ValueError('Each argument of say(...) must be str or callable')
        response = kwargs.copy()
        phrases = [item for item in args if isinstance(item, str)]
        if phrases:
            response['text'] = random.choice(phrases)
        if 'end_session' not in response:
            response['end_session'] = False
        for item in args:
            if callable(item):
                item(response)
        return response


    class Skill(flask.Flask):

    def __init__(self):
        super().__init__()

    self._sessions = {}
    self._session_lock = threading.RLock()


    def script(self, generator):
        @self.route("/", methods=['POST'])
        def handle_post():
            flask.g.request = Request(flask.request.get_json())

        logging.debug('Request: %r', flask.g.request)
        content = self._switch_state(generator)
        response = {
            'version': flask.g.request['version'],
            'session': flask.g.request['session'],
            'response': content,
        }
        logging.debug('Response: %r', response)


    return flask.jsonify(response)
    return generator

    def _switch_state(self, generator):
        session_id = flask.g.request['session']['session_id']

    with self._session_lock:
        if session_id not in self._sessions:
            state = self._sessions[session_id] = generator()
    else:
    state = self._sessions[session_id]
    content = next(state)
    if content['end_session']:
        with self._session_lock:
            del self._sessions[session_id]
    return content
    skill = Skill(__name__)  # skill - объект класса, контролирующий обмен
    # данными с голосовым помощником
    RDK = Robolink()  # RDK- объект класса, контролирующий обмен
    # данными со средой симуляции
    85
    robot = RDK.Item('UR10')  # robot - объект класса, контролирующий движение
    # робота
    start_pos = [0, -90, 90, 0, 90, 0]  # Список градусных мер стартовых позиций всех
    # суставов робота манипулятора
    pos = [0, -90, 90, 0, 90, 0]  # Список градусных мер текущих позиций всех
    # суставов робота манипулятора

    def move_joint(joint, step):
        yield say('Скажите "плюс", чтобы повернуть сустав по направлению движения ' +
                  'часовой стрелки, и "минус" - против часовой',
                  suggest('плюс', 'минус'))  # Отправление реплики голосовому помощнику
        if (request.has_lemmas('плюс', '+', 'по часовой стрелке') and pos[joint] < 170):
            pos[joint] += step  # Проверка, есть ли в запросе пользователя “плюс”
        elif (request.has_lemmas('минус', '-', 'против часовой стрелки') and pos[joint] > -170):
            pos[joint] -= step
        else:
        yield say('Я Вас не поняла, #Если пользователь не сказал “плюс” или
        повторите, пожалуйста
        ') #“минус”, голосовой помощник просит повторить
        # еще раз
        return



    robot.MoveJ(pos)  # Движение робота
    return


    def move_home():
        robot.MoveJ(start_pos)
        return



    def clean():
        list_items = RDK.ItemList()
        for item in list_items:
            if item.Name().startswith('Auto'):
                item.Delete()



    def MakePoints(xStart, xEnd, numPoints):
        if len(xStart) != 3 or len(xEnd) != 3:  # Проверка на валидность параметров
            raise Exception("Start and end point must be 3-dimensional vectors")
        if numPoints < 2:
            raise Exception("At least two points are required")

        pt_list = []
        x = xStart[0]
        y = xStart[1]
        z = xStart[2]
        x_steps = (xEnd[0] - xStart[0]) / (numPoints - 1)  # Вычисление расстояния между
        y_steps = (xEnd[1] - xStart[1]) / (numPoints - 1)  # точками по каждой из осей
        z_steps = (xEnd[2] - xStart[2]) / (numPoints - 1)
        for i in range(numPoints):  # Генерация промежуточных точек
            point_i = [x, y, z]
        pt_list.append(point_i)
        x = x + x_steps
        y = y + y_steps
        z = z + z_steps
        return pt_list

    P_START = [17, -50, 21]  # Координаты стартовой позиции
    P_END = [17, 60, 21]  # Координаты целевой позиции

    NUM_POINTS = 10  # Количество промежуточных точек
    POINTS = MakePoints(P_START, P_END,  # Список, содержащий координаты
                        NUM_POINTS)  # промежуточных точек


    def move_points():
        clean()
        reference = robot.Parent()  # Получение системы координат
        robot.setPoseFrame(reference)
        pose_ref = robot.Pose()  # Получение текущей позиции робота
        for i in range(NUM_POINTS):
            pose_i = pose_ref
        pose_i.setPos(POINTS[i])
        robot.MoveJ(pose_i)  # Движение

    @skill.script



    def run_script():
        move_home()
        yield say('Приветствуем Вас в навыке Алисы "UR10", он позволяет управлять ' +
                  'роботом-манипулятором Universal Robots UR-5 с помощью голоса. ' +
                  'Скажите что-нибудь, чтобы начать')

        while not request.has_lemmas('назад',  # Главный цикл программы, работает,
                                     'закончить', 'завершить'):  # пока пользователь не скажет
        # ”назад”,”закончить” или ”завершить”
        yield say('Чтобы закончить, скажите "стоп" в любой момент, чтобы вернуться,
                  '+
                  'скажите "назад", а пока ' +
                  'выберите режим работы',
                  suggest('дискретный', 'рисование', 'вернуться в стартувую позицию'))
        while not request.has_lemmas('дискретный',  # Выбор режима работы
                                     'рисование', 'вернуться в стартувую позицию', 'назад'):
            yield say('Такого режима работы #Обработка неправильных входных
            не
            предусмотрено, выберите  # данных
            один
            из
            предложенных
            ',
            suggest('дискретный', 'рисование', 'вернуться в стартувую позицию'))

            if (request.command == 'назад'):  # Возврат к выбору режима работы
                break;
            mode = request.command
            if (mode == 'дискретный'):
                yield say('Выберите номер сустава робота, суставы нумеруются от основания',
                          suggest('1', '2', '3', '4', '5', '6'))
            while not
        request.has_lemmas('1', '2', '3', '4', '5', '6', 'первый', 'второй', 'третий', 'четвертый', 'пятый', 'ше
        стой
        ','
        назад
        '):

        yield say('Робот имеет только 6 #Обработка неправильных входных
        степеней
        свободы, выберите  # данных от пользователя
        валидный
        номер
        сустава
        ')
        if (request.command != 'назад'):
            joint = int(request.command)
        yield say('Выберите угол поворота, угол может быть любым, не обязательно
        одним
        из
        предложенных
        ', #Определение номера сустава, который
        suggest('10', '15', '30', '57'))  # требуется повернуть
        while not ((request.matches(r'\d+') and int(request.command) < 100) or
                   request.command != 'назад'):
            yield say('Назавите угол поворота, меньший 100')
            if (request.command != 'назад'):
                step = int(request.command)
            while not request.matches('назад'):
                yield from move_joint(joint - 1, step)
            elif (request.has_lemmas('стартовый',  # Обработка запроса на возврат в
                                     'стартовую', 'вернуться')):  # стартовую позицию
            move_home()
            elif (mode == 'рисование')
            move_points()
            yield say('Продолжить управление или закончить?')
            yield say('Управление окончено')
        port = int(os.environ.get('PORT', 5000))

        from dialogic.server.flask_ngrok import run_ngrok
        ngrok_address = run_ngrok(port)  # Запуск туннеля ngrok для получения
        # доступа к навыку из Интернета
        base_url = ngrok_address
        skill.run(host="0.0.0.0", port=port,  # Запуск сервера навыка
                  debug=False)
