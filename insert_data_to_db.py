from random import randrange, choice
from pprint import pprint
from app import db, app
from models import GroupModel, StudentModel, CourseModel, students_courses
from slugify import slugify
from collections import Counter
from sqlalchemy.orm import lazyload



first_names = "Марк, Александр, Варвара, Александра, Екатерина, Ярослав, Арина, Тимофей, Лука, Аделина, Анастасия, Вера, Артур, Матвей, Мария, Алиса, Егор, Вероника, Павел, Давид".split(", ")
last_names = "Романова А. М., Лукина В. М., Маркина С. М., Рыбаков Г. А., Морозова А. И., Чернова Л. И., Котов А. Д., Никифоров К. С., Козлов Ю. В., Плотникова М. А., Кудрявцева М. Н., Антонов Я. З., Егорова А. А., Кузнецова В. М., Матвеева Е. А., Носова Т. Г., Андрианова С. М., Казанцев Д. М., Еремина М. А., Баранов И. И.".split(", ")
last_names = [last_n[:-6] for last_n in last_names]
courses = {"Курсы SQL":"Вы освоите язык запросов SQL. Научитесь самостоятельно собирать, обрабатывать данные и анализировать их. Сможете решать бизнес-задачи с помощью SQL.",
           "Курсы Python":"На практике научитесь писать программы и разрабатывать веб-приложения с индивидуальной помощью от наставника. За 12 месяцев станете востребованным разработчиком, даже если вы новичок впрограммировании. Опыт программирования не нужен.",
           "Курсы аналитик данных (Data Science + Big Data)":"В рамках микрокурса вы получите выжимку необходимой информации для старта в новой профессии: от необходимых навыков до секретов успешного прохождения собеседования, от кейсов до подробного разбора инструментов.",
           "Обучение искусственному интеллекту и машинному обучению с Нуля":"В данном курсе пользователи получат практические навыки в работе с аналитическими инструментами Python. В обучение входит 6 месяцев обучения бесплатного контента с возможностью выполнения домашних заданий.",
           "Курсы Data Engineer":"Обучающая программа: освоите дата-инженерию с нуля. Научитесь собирать и обрабатывать данные, работать с Big Data и программировать на Python и SQL. Через год сможете устроиться Junior-аналитиком, а параллельно с работой продолжите проходить курс и дорастёте до уровня Middle.",
           "Курсы Вёрстки сайтов на HTML и CSS":"Прежде чем перейти к написанию первой программы, мы систематизируем знания о веб-разработке и познакомимся с сопутствующими технологиями. Этот курс поможет разобраться, что необходимо знать и куда можно двигаться начинающему разработчику.",
           "Обучение PHP":"В ходе уроков «Курс PHP обучение для новичков с нуля» мы с вами рассмотрим язык PHP. Научимся работать с основными концепциями: с переменными, циклами, условиями и прочими конструкциями. Также мы научимся работать с пользователем: обрабатывать формы, отправлять почту, подключать файлы, выполнять настройку сервера и многое другое.",
           "Курсы 1С, C++ и C#":"Освойте профессию программиста 1С с нуля. Вы научитесь создавать архитектуру приложения, разрабатывать подсистемы и подготовитесь к сдаче экзаменов 1С.",
           "Курсы Java":"Вы изучите Spring-фреймворк, без знания которого невозможно развиваться в разработке на Java. Узнаете, как создавать и оптимизировать веб-приложения, и сделаете собственный книжный интернет-магазин.",
           "Курсы Swift":"iOS-разработчик создаёт приложения для онлайн-банкинга, навигаторы, интернет-магазины, фитнес-трекеры и другие полезные сервисы, которые упрощают людям жизнь."
           }

def groups_creating(number):
    groups = []
    while number-1 >= len(groups):
        char = chr(randrange(65, 90)) + chr(randrange(65, 90))
        num = "{}{}".format(randrange(0, 9), randrange(0, 9))
        groups_name = "{}-{}".format(char, num)
        if groups_name not in groups:
            groups.append(groups_name)
    return groups


def students_creating(names, surnames, number):
    students = []
    while number-1 >= len(students):
        name = names[randrange(0, 19)]
        surname = surnames[randrange(0, 19)]
        full_name = "{} {}".format(name, surname)
        if full_name not in students:
            students.append(full_name)
    return students


def add_groups_to_db():
    groups_db = []
    for grp in groups_creating(10):
        group = GroupModel(name=grp,
                           slug=slugify(grp, allow_unicode=True))
        groups_db.append(group)
    with app.app_context():
        db.session.add_all(groups_db)
        db.session.commit()
    return groups_db

def add_students_to_db(groups_db):
    students_db = []
    students = students_creating(first_names, last_names, 200)
    counter = Counter()
    for std in students:
        name, surname = std.split()
        group = choice(groups_db)
        while not (counter[group] <= 30):
            group = choice(groups_db)
        student = StudentModel(first_name=name, last_name=surname, group_id=group.id)
        counter[group] += 1
        students_db.append(student)
        with app.app_context():
            db.session.add_all(students_db)
            db.session.commit()

# with app.app_context():
#     students_db = db.session.query(StudentModel).all()
#     for group in groups_db:
#         pprint(group.name)
#     for student in students_db:
#         pprint(student.group.name)


def add_courses_to_db():
    cources_db = []
    for name, desc in courses.items():
        course = CourseModel(name=name,
                             description=desc,
                             slug=slugify(name))
        cources_db.append(course)
    with app.app_context():
        db.session.add_all(cources_db)
        db.session.commit()
    with app.app_context():
        cources = db.session.query(CourseModel).all()
        for c in cources:
            print(c.id, c.name, c.slug)

def change_slug():
    with app.app_context():
        course = CourseModel.query.filter(CourseModel.slug == "kursy-1s-c-i-c").first()
        course.slug = "kursy-1c-cplusplus-csharp"
        db.session.add(course)
        db.session.commit()

def print_course():
    with app.app_context():
        cources = CourseModel.query.all()
        for c in cources:
            print(c.id, c.name, c.slug)

def add_new():
    with app.app_context():
        course = CourseModel(name="Курсы Swift", description=courses["Курсы Swift"], slug=slugify("Курсы Swift"))
        db.session.add(course)
        db.session.commit()


def make_many_to_many():
    with app.app_context():
        courses = CourseModel.query.all()
        students = StudentModel.query.all()
        for student in students:
            number = randrange(1, 4)
            for n in range(number):
                ch = randrange(0, len(courses))
                i = 0
                for course in courses:
                    if i == ch:
                        student.courses.append(course)
                        pass
                    i += 1
        db.session.add_all(students)
        db.session.commit()



def print_couse():
    with app.app_context():
        courses = CourseModel.query.all()
        students = StudentModel.query.all()
        for c in courses:
            print(c.name)
            for s in c.students:
                print(s.first_name, s.last_name, "| ", end="")
            print()
        for s in students:
            print(s.first_name, s.last_name)
            for c in s.courses:
                print(c.name)

def change_group():
    with app.app_context():
        group = GroupModel.query.all()
        students = StudentModel.query.all()
        for std in students:
            i = 0
            n = randrange(0, 10)
            for grp in group:
                if n == i:
                    std.group_id = grp.id
                    break
                else:
                    i += 1
        db.session.add_all(students)
        db.session.commit()
        group = GroupModel.query.all()


def set_courses():
    with app.app_context():
        courses = CourseModel.query.all()
        students = StudentModel.query.all()
        for student in students:
            number_of_courses = randrange(1, 4)
            list_of_corses = []
            i = 0
            course_tmp = choice(courses)
            while len(list_of_corses) != number_of_courses:
                if course_tmp in list_of_corses:
                    course_tmp = choice(courses)
                    continue
                else:
                    list_of_corses.append(course_tmp)
                    student.courses.append(course_tmp)
                    course_tmp = choice(courses)
        db.session.add_all(students)
        db.session.commit()
        students = StudentModel.query.all()
        for s in students:
            print(s.id, s.courses)


def ppp():
    with app.app_context():
        students = StudentModel.query.all()
        students.sort(key=lambda x: x.id)
        for student in students:
            print(student.id, student.first_name, student.last_name)
            for c in student.courses:
                print(c.name)

def pppp():
    with app.app_context():
        students = StudentModel.query.order_by(StudentModel.id).all()
        for student in students:
            print(student.id, student.courses)


