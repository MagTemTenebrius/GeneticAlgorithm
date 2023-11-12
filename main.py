import csv
import random


class Group:
    def __init__(self, name):
        self.name = name


class Teacher:
    def __init__(self, name):
        self.name = name


class Course:
    def __init__(self, name, teacher, groups, lessons_per_week):
        self.name = name
        self.teacher = teacher
        self.groups = groups
        self.lessons_per_week = lessons_per_week


class TimeSlot:
    def __init__(self, day, time, is_morning):
        self.day = day
        self.time = time
        self.is_morning = is_morning


class Classroom:
    def __init__(self, name):
        self.name = name


class ScheduleGenerator:
    def __init__(self, courses, classrooms, timeslots):
        self.courses = courses
        self.classrooms = classrooms
        self.timeslots = timeslots

    def create_schedule(self, population_size):
        population = []

        for _ in range(population_size):
            schedule = {}
            for course in self.courses:
                for group in course.groups:
                    for _ in range(course.lessons_per_week):
                        # Получаем утренний временной слот для конкретного дня
                        morning_timeslots = [slot for slot in self.timeslots if slot.is_morning]
                        timeslot = random.choice(morning_timeslots)

                        lesson_key = f"{course.name}_{group.name}_{timeslot.day}_{timeslot.time}"
                        if lesson_key not in schedule:
                            schedule[lesson_key] = {
                                'Teacher': course.teacher.name,
                                'Classroom': random.choice(self.classrooms).name,
                            }

            population.append(schedule)

        return population

    def fitness(self, schedule):
        conflicts = 0
        lessons_info = {key: info for key, info in schedule.items() if isinstance(info, dict)}

        for lesson_key, info in lessons_info.items():
            for other_lesson_key, other_info in lessons_info.items():
                if lesson_key != other_lesson_key:
                    if (info['Classroom'] == other_info['Classroom'] and
                            info['Teacher'] == other_info['Teacher']):
                        conflicts += 1

        return 1 / (1 + conflicts)

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        child = {}

        for lesson_key, info in parent1.items():
            if lesson_key in parent2 and isinstance(info, dict):
                child[lesson_key] = info
            else:
                child[lesson_key] = parent2.get(lesson_key, info)

        return child

    def mutate(self, schedule, mutation_rate=0.1):
        for lesson_key, info in schedule.items():
            if isinstance(info, dict) and random.random() < mutation_rate:
                info['Classroom'] = random.choice(self.classrooms).name
        return schedule

    def genetic_algorithm(self, population_size, generations):
        population = self.create_schedule(population_size)

        for generation in range(generations):
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)

            parents = population[:2]

            offspring = [self.crossover(parents[0], parents[1]) for _ in range(population_size - 2)]
            offspring = [self.mutate(child) for child in offspring]

            population = parents + offspring

            best_schedule = max(population, key=lambda x: self.fitness(x))
            print(f"Generation {generation + 1}, Fitness: {self.fitness(best_schedule)}")

        return best_schedule


# Создаем группы
group101 = Group("МК-101")
group102 = Group("МК-102")
group201 = Group("МК-201")
group301 = Group("МК-301")
group401 = Group("МК-401")
group501 = Group("МК-501")

# Создаем преподавателей
teacher1 = Teacher("Маткин И.А.")
teacher2 = Teacher("Ручай А.Н.")
teacher3 = Teacher("Сбродова Е.В.")
teacher4 = Teacher("Шалагинов Л.В.")
teacher5 = Teacher("Иванов А.А.")
teacher6 = Teacher("Светлов А.А.")
teacher7 = Teacher("Светлов А.Б.")

# Создаем курсы
course1 = Course("Геометрия", teacher3, [group101, group102], 2)
course2 = Course("Физическая Культура Теория", teacher5, [group101, group102, group201, group301], 3)
course3 = Course("Искусственный Интеллект", teacher2, [group401, group501], 2)
course4 = Course("Системное программирование", teacher1, [group301, group401], 2)
course5 = Course("Защита кода", teacher1, [group501], 2)
course6 = Course("Теория чисел", teacher4, [group201], 2)
course7 = Course("Математический анализ", teacher6, [group101, group102, group201], 2)
course8 = Course("Математический анализ 2", teacher7, [group301, group401, group501], 2)

# Создаем аудитории
classroom1 = Classroom("401")
classroom2 = Classroom("402")
classroom3 = Classroom("403")
classroom4 = Classroom("404")
classroom5 = Classroom("405")
classroom6 = Classroom("406")

# Создаем временные слоты
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
timeslots = []
for day in days_of_week:
    for hour in range(8, 18, 2):
        timeslots.append(TimeSlot(day, f"{hour:02d}:00", hour <= 12))

# Создаем генератор расписания
schedule_generator = ScheduleGenerator(courses=[course1, course2, course3, course4, course5, course6, course7, course8],
                                       classrooms=[classroom1, classroom2, classroom3, classroom4, classroom5,
                                                   classroom6],
                                       timeslots=timeslots)

# Запуск генетического алгоритма
best_schedule = schedule_generator.genetic_algorithm(population_size=20, generations=100)

# Вывод лучшего расписания
print("\nBest Schedule:")
for lesson_key, info in best_schedule.items():
    if isinstance(info, dict):
        print(f"{lesson_key}: {info}")


# Функция для записи расписания в CSV-файл
def write_schedule_to_csv(schedule, output_file):
    groups = {}
    teacher = {}
    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Записываем заголовок
        header = ['Day', 'Time', 'Classroom', 'Teacher', 'Course', 'Group']
        writer.writerow(header)

        # Группируем уроки по дням недели
        grouped_schedule = {}
        for lesson_key, info in schedule.items():
            if isinstance(info, dict):
                day, time = lesson_key.split("_")[-2:]
                if day not in grouped_schedule:
                    grouped_schedule[day] = []
                grouped_schedule[day].append(
                    [day, time, info['Classroom'], info['Teacher'], lesson_key.split("_")[0], lesson_key.split("_")[1]])

                if lesson_key.split("_")[1] not in groups.keys():
                    groups[lesson_key.split("_")[1]] = []
                groups[lesson_key.split("_")[1]].append(
                    {
                        "Day": day,
                        "Time": time,
                        "Classroom": info['Classroom'],
                        "Teacher": info['Teacher'],
                        "Course": lesson_key.split("_")[0]
                    }
                )

                if info['Teacher'] not in teacher.keys():
                    teacher[info['Teacher']] = []
                teacher[info['Teacher']].append(
                    {
                        "Day": day,
                        "Time": time,
                        "Classroom": info['Classroom'],
                        "Group": lesson_key.split("_")[1],
                        "Course": lesson_key.split("_")[0]
                    }
                )

        # Записываем данные в CSV
        for day, lessons in grouped_schedule.items():
            for lesson in lessons:
                writer.writerow(lesson)

    grouped_schedule = {}
    for groupName, data_ in groups.items():
        if groupName not in grouped_schedule.keys():
            grouped_schedule[groupName] = {}
        for data in data_:
            if data["Day"] not in grouped_schedule[groupName].keys():
                grouped_schedule[groupName][data["Day"]] = []
            grouped_schedule[groupName][data["Day"]].append(
                [data["Time"], data['Classroom'], data['Teacher'], data['Course']])

    for groupName in grouped_schedule.keys():
        with open(groupName + ".csv", mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            header = ['Day', 'Time', 'Classroom', 'Teacher', 'Course']
            writer.writerow(header)
            for day in grouped_schedule[groupName].keys():
                for element in grouped_schedule[groupName][day]:
                    writer.writerow(
                        (day,
                        element[0],
                        element[1],
                        element[2],
                        element[3])
                    )

    teachered_schedule = {}
    for teacherName, data_ in teacher.items():
        if teacherName not in teachered_schedule.keys():
            teachered_schedule[teacherName] = {}
        for data in data_:
            if data["Day"] not in teachered_schedule[teacherName].keys():
                teachered_schedule[teacherName][data["Day"]] = []
            teachered_schedule[teacherName][data["Day"]].append(
                [data["Time"], data['Classroom'], data['Group'], data['Course']])

    for teacherName in teachered_schedule.keys():
        with open(teacherName + ".csv", mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            header = ['Day', 'Time', 'Classroom', 'Group', 'Course']
            writer.writerow(header)
            for day in teachered_schedule[teacherName].keys():
                for element in teachered_schedule[teacherName][day]:
                    writer.writerow(
                        (day,
                        element[0],
                        element[1],
                        element[2],
                        element[3])
                    )



# Записываем лучшее расписание в CSV-файл
output_file_path = 'schedule.csv'
write_schedule_to_csv(best_schedule, output_file_path)
print(f"Schedule written to {output_file_path}")
