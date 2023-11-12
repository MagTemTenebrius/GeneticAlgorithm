import copy
import csv
import json
import os
import random
from datetime import datetime
from random import sample


class Group:
    def __init__(self, group_id, name, students, mandatory_courses):
        self.group_id = group_id
        self.name = name if name is not None else group_id
        self.students = students
        self.schedule = []
        self.mandatory_courses = mandatory_courses  # Список обязательных предметов


class Instructor:
    def __init__(self, instructor_id, name, courses_taught):
        self.instructor_id = instructor_id
        self.name = name
        self.courses_taught = courses_taught
        self.schedule = []

    def get_courses_taught(self):
        return self.courses_taught


class Classroom:
    def __init__(self, classroom_id, name, capacity, availability):
        self.classroom_id = classroom_id
        self.name = name
        self.capacity = capacity
        self.availability = availability


class Lecture:
    def __init__(self, lecture_id, course, group, instructor, classroom, start_time, end_time, day_of_week=None):
        self.lecture_id = lecture_id
        self.course = course
        self.group = group
        self.instructor = instructor
        self.classroom = classroom
        self.start_time = start_time
        self.end_time = end_time
        self.day_of_week = day_of_week


class Schedule:
    def __init__(self, schedule_id, name):
        self.schedule_id = schedule_id
        self.name = name
        self.groups = []
        self.instructors = []
        self.courses = []
        self.classrooms = []
        self.lectures = []

    def add_group(self, group):
        self.groups.append(group)

    def add_instructor(self, instructor):
        self.instructors.append(instructor)

    def add_course(self, course):
        self.courses.append(course)

    def get_instructor(self):
        return self.instructors

    def add_classroom(self, classroom):
        self.classrooms.append(classroom)

    def add_lecture(self, lecture):
        self.lectures.append(lecture)

    def generate_random_schedule(self):
        schedule = Schedule(None, None)
        for group in self.groups:
            for day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                for _ in range(4):
                    course = random.choice([c for c in self.courses if c.name in group.mandatory_courses])
                    instructor = random.choice(self.instructors)
                    classroom = random.choice(self.classrooms)
                    start_time, end_time = self.get_random_time()

                    lecture = Lecture(course=course,
                                      group=group,
                                      instructor=instructor,
                                      classroom=classroom,
                                      day_of_week=day_of_week,
                                      start_time=start_time,
                                      end_time=end_time,
                                      lecture_id="AAA")

                    schedule.lectures.append(lecture)

        return schedule

    def get_random_time(self):
        # Предполагается, что у вас есть некоторый список временных интервалов
        timeslots = [("8:00 AM", "10:00 AM"), ("10:00 AM", "12:00 PM"), ("1:00 PM", "3:00 PM"), ("3:00 PM", "5:00 PM")]
        return random.choice(timeslots)

    def to_csv(self, output_folder='csv_output'):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Создание CSV-файлов для каждой группы
        for group in self.groups:
            filename = f"{output_folder}/{group.name}_schedule.csv"

            # Фильтрация занятий по группе
            filtered_lectures = [lecture for lecture in self.lectures if lecture.group == group]

            # Создание списка кортежей из отфильтрованных занятий
            schedule_data = [
                (
                    lecture.lecture_id,
                    lecture.course,
                    lecture.group.name,
                    lecture.instructor.name,
                    lecture.classroom.name,
                    lecture.day_of_week,
                    lecture.start_time,
                    lecture.end_time
                )
                for lecture in filtered_lectures
            ]

            # Сортировка по дню недели и времени
            sorted_schedule = sorted(schedule_data, key=lambda x: (x[5], self.parse_time(x[6])))

            # Создание CSV-файла
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["lecture_id", "course", "group", "instructor", "classroom", "day_of_week", "start_time",
                              "end_time"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                # Запись отсортированных данных в CSV
                for lecture in sorted_schedule:
                    writer.writerow({
                        "lecture_id": lecture[0],
                        "course": lecture[1],
                        "group": lecture[2],
                        "instructor": lecture[3],
                        "classroom": lecture[4],
                        "day_of_week": lecture[5],
                        "start_time": lecture[6],
                        "end_time": lecture[7]
                    })

    @staticmethod
    def parse_time(time_str):
        # Функция для извлечения времени из строки диапазона
        if "-" in time_str:
            start_str, end_str = map(str.strip, time_str.split("-"))
            start_time = datetime.strptime(start_str, "%I:%M %p").time()
            end_time = datetime.strptime(end_str, "%I:%M %p").time()
            return f"{start_time} - {end_time}"
        else:
            return time_str


class ScheduleGenerator:
    def __init__(self, schedule):
        self.schedule = schedule
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.2
        self.elite_percentage = 0.2

    def fitness(self, schedule):
        # Оценка приспособленности учитывает обязательные предметы для каждой группы
        total_fitness = 0

        for group in schedule.groups:
            mandatory_courses = set(group.mandatory_courses)
            scheduled_courses = set()

            for lecture in schedule.lectures:
                if lecture.group == group:
                    scheduled_courses.add(lecture.course)

            # Чем ближе запланированные курсы к обязательным, тем лучше
            fitness_group = len(mandatory_courses.intersection(scheduled_courses))

            total_fitness += fitness_group

        return total_fitness

    def crossover(self, parent1, parent2):
        # Одноточечный кроссовер
        crossover_point = random.randint(1, len(parent1.lectures) - 1)
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        child1.lectures = parent1.lectures[:crossover_point] + parent2.lectures[crossover_point:]
        child2.lectures = parent2.lectures[:crossover_point] + parent1.lectures[crossover_point:]

        return child1, child2

    def mutate(self, individual):
        # Мутация: перемещение случайной лекции в другое время
        mutated_individual = copy.deepcopy(individual)
        lecture_to_mutate = random.choice(mutated_individual.lectures)
        new_time = self.schedule.get_random_time()  # Предполагается, что есть метод get_random_time()

        # Обновим время лекции
        lecture_to_mutate.start_time = new_time[0]
        lecture_to_mutate.end_time = new_time[1]

        return mutated_individual

    def evolve(self, population_size=100, generations=50):
        # Генетическая эволюция для создания расписания
        population = [self.schedule.generate_random_schedule() for _ in range(population_size)]

        for generation in range(generations):
            # Оценка приспособленности
            fitness_scores = [(schedule, self.fitness(schedule)) for schedule in population]

            # Сортировка по приспособленности (чем больше, тем лучше)
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            # Отбор лучших особей
            selected_population = [schedule for schedule, _ in fitness_scores[:int(population_size * 0.2)]]

            # Создание нового поколения
            new_population = selected_population[:]

            # Кроссовер
            for _ in range(int(population_size * 0.6)):
                parent1, parent2 = random.sample(selected_population, 2)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([child1, child2])

            # Мутация
            for _ in range(int(population_size * 0.2)):
                individual_to_mutate = random.choice(new_population)
                mutated_individual = self.mutate(individual_to_mutate)
                new_population.append(mutated_individual)

            population = new_population

        # Возврат лучшего расписания
        best_schedule = max(population, key=self.fitness)
        return best_schedule


def generate_schedule():
    # Генерация фиктивных данных
    group1 = Group("МК101", None, 30, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group2 = Group("МК102", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group3 = Group("МК201", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group4 = Group("МК202", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group5 = Group("МК203", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group6 = Group("МК301", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group7 = Group("МК401", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group8 = Group("МК501", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])
    group9 = Group("МК601", None, 25, ["Системное программирование 1", "Защита кода", "Геометрия"])

    instructor1 = Instructor("I001", "Маткин Илья Александрович", [
        "Системное программирование 1",
        "Системное программирование 2",
        "Защита кода"
        "Валуны 1",
        "Валуны 2"])
    instructor2 = Instructor("I002", "Сбродовав Елена Васильевна", [
        "Геометрия"
    ])
    instructor3 = Instructor("I003", "Шалагинов Леонид Викторович", [
        "Теория графов 1",
        "Теория графов 2",
        "Теория чисел"
    ])
    instructor4 = Instructor("I004", "Панов А. В.", [
        "Мат. анализ"
    ])
    instructor5 = Instructor("I005", "Ручай Алексей Николаевич", [
        "Нейронные сети 1",
        "Нейронные сети 2"
    ])
    instructor6 = Instructor("I006", "Ручай Алексей Николаевич", [
        "Нейронные сети 1",
        "Нейронные сети 2"
    ])
    instructor7 = Instructor("I007", "Тарелкин Борис", [
        "Java 1",
        "Java 2"
    ])

    classroom1 = Classroom("C101", "Room 421", 50, {
        "Monday": ["8:00 AM - 10:00 AM", "1:00 PM - 12:00 PM"],
        "Tuesday": ["8:00 AM - 10:00 AM", "1:00 PM - 3:00 PM"],
        "Wednesday": ["8:00 AM - 10:00 AM", "1:00 PM - 3:00 PM"],
        "Thursday": ["8:00 AM - 10:00 AM", "1:00 PM - 3:00 PM"],
        "Friday": ["8:00 AM - 10:00 AM", "1:00 PM - 3:00 PM"]
    })

    classroom2 = Classroom("C102", "Room 423", 40, {
        "Monday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Tuesday": ["10:00 AM - 12:00 PM"],
        "Wednesday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Thursday": ["10:00 AM - 12:00 PM"],
        "Friday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"]
    })

    classroom3 = Classroom("C102", "Room 401", 40, {
        "Monday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Tuesday": ["10:00 AM - 12:00 PM"],
        "Wednesday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Thursday": ["10:00 AM - 12:00 PM"],
        "Friday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"]
    })

    classroom4 = Classroom("C102", "Room 402", 40, {
        "Monday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Tuesday": ["10:00 AM - 12:00 PM"],
        "Wednesday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Thursday": ["10:00 AM - 12:00 PM"],
        "Friday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"]
    })

    classroom5 = Classroom("C102", "Room 403", 40, {
        "Monday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Tuesday": ["10:00 AM - 12:00 PM"],
        "Wednesday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"],
        "Thursday": ["10:00 AM - 12:00 PM"],
        "Friday": ["10:00 AM - 12:00 PM", "3:00 PM - 5:00 PM"]
    })

    # Создание расписания
    schedule = Schedule("S001", "Fall 2023 Schedule")
    schedule.add_group(group1)
    schedule.add_group(group2)
    schedule.add_group(group3)
    schedule.add_group(group4)
    schedule.add_group(group5)
    schedule.add_group(group6)
    schedule.add_group(group7)
    schedule.add_group(group8)
    schedule.add_group(group9)

    schedule.add_instructor(instructor1)
    schedule.add_instructor(instructor2)
    schedule.add_instructor(instructor3)
    schedule.add_instructor(instructor4)
    schedule.add_instructor(instructor5)
    schedule.add_instructor(instructor6)
    schedule.add_instructor(instructor7)

    schedule.add_classroom(classroom1)
    schedule.add_classroom(classroom2)
    schedule.add_classroom(classroom3)
    schedule.add_classroom(classroom4)
    schedule.add_classroom(classroom5)

    # Генерация занятий
    courses = []
    for teacher in schedule.get_instructor():
        courses += teacher.get_courses_taught()

    for group in schedule.groups:
        for course in courses:
            instructor = sample(schedule.instructors, 1)[0]
            classroom = sample(schedule.classrooms, 1)[0]
            start_time = sample(classroom.availability["Monday"], 1)[0]
            end_time = start_time.split(" - ")[1]

            lecture = Lecture(f"L{len(schedule.lectures) + 1}", course, group, instructor, classroom, start_time,
                              end_time)
            schedule.add_lecture(lecture)

    # Вывод данных в JSON
    # schedule_json = json.dumps(schedule.__dict__, default=lambda x: x.__dict__, indent=2)
    # print(schedule_json)
    return schedule


if __name__ == "__main__":
    generator = ScheduleGenerator(generate_schedule())
    best_schedule = generator.evolve()
    best_schedule.to_csv()

    # Вывод результатов
    best_schedule_json = json.dumps(best_schedule.__dict__, ensure_ascii=False, default=lambda x: x.__dict__, indent=2)
    print(best_schedule_json)
