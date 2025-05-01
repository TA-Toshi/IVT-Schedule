from datetime import datetime
from pathlib import Path
import gspread
import re

from pprint import pprint

from config import AUTUMN_PATH, SPRING_PATH

current_dir = Path(__file__).parent
creds_path = current_dir.parent / "creds.json"

gc = gspread.service_account(filename=str(creds_path))

wks = gc.open_by_key(SPRING_PATH)
# wks = gc.open_by_key(SPRING_PATH)

worksheet_schedule = wks.get_worksheet(0)
worksheet_cabs = wks.get_worksheet(1)
worksheet_teacher = wks.get_worksheet(2)

lines_schedule = worksheet_schedule.get_all_values(
    combine_merged_cells=True,
    maintain_size=True,
    pad_values=True
)
lines_cabs = worksheet_cabs.get(
    range_name="H1:AH2",
    combine_merged_cells=True,
    maintain_size=True,
    pad_values=True
)
lines_teacher = worksheet_teacher.get_all_values(
    combine_merged_cells=True,
    maintain_size=True,
    pad_values=True
)


def get_day_place(name):
    place = str(worksheet_schedule.find(name, in_column=5)).split()[1]
    numbers = re.findall(r'\d+', place)
    row, col = map(int, numbers)
    first_last = [row, row + 9]
    return first_last


def get_group_place(name):
    cells_in_range = worksheet_schedule.range("G1:AK1")
    matching_cells = [
        cell
        for cell in cells_in_range
        if name.lower() in str(cell.value).lower()
    ]
    place = str(matching_cells[0]).split()[1]
    numbers = re.findall(r'\d+', place)
    row, col = map(int, numbers)

    return col


def group_match(name):
    cells_in_range = worksheet_schedule.range("G1:AK1")
    normalized_input = ''.join([c.lower() for c in name if c.isalnum()])
    clear_basket = []
    basket = [
        cell for cell in cells_in_range
        if normalized_input in ''.join([c.lower() for c in str(cell.value) if c.isalnum()])
    ]
    for item in basket:
        clear_basket.append(str(item).split("'")[1].split("\\n")[0])
    return clear_basket


# print(group_match("ивт"))


def get_teacher_place(name):
    cells_in_range = worksheet_teacher.range("G2:BQ2")

    matching_cells = [
        cell
        for cell in cells_in_range
        if name.lower() in str(cell.value).lower()
    ]

    place = str(matching_cells[0]).split()[1]
    numbers = re.findall(r'\d+', place)
    row, col = map(int, numbers)
    return col


def check_namesake(name):
    cells_in_range = worksheet_teacher.range("G2:BQ2")
    matching_cells = [
        cell
        for cell in cells_in_range
        if name.lower() in str(cell.value).lower()
    ]
    basket = []
    for cell in matching_cells:
        name_test = str(cell).split("'")[1]
        basket.append(name_test)
    return basket


def remove_consecutive_duplicates(tuples_list):
    week = ["вторник", "среда", "четверг", "пятница", "суббота"]
    counter = 0
    if not tuples_list:
        return []
    if type(tuples_list[0]) is str:
        result = [tuples_list[0]]
    else:
        result = [[tuples_list[0], "first"]]
    for i in range(1, len(tuples_list)):
        if type(tuples_list[i]) is str:
            if tuples_list[i] != '':
                result.append(tuples_list[i])
                # print(tuples_list[i], counter, week[counter])
                counter += 1
            elif tuples_list[i] == '':
                result.append(week[counter])
                # print(tuples_list[i], counter, week[counter])
                counter += 1
        else:
            if tuples_list[i][0] == tuples_list[i - 1][0] and tuples_list[i][1] == tuples_list[i - 1][1]:
                if type(result[-1]) is not str:
                    result[-1][1] = "full"
            elif tuples_list[i][0] != tuples_list[i - 1][0]:
                result.append([tuples_list[i], "first"])
            elif tuples_list[i][0] == tuples_list[i - 1][0] and tuples_list[i][1] != tuples_list[i - 1][1]:
                result.append([tuples_list[i], "second"])
    return result


def extract_aud_number(text):
    match = re.search(r'\b\d{3}\b', text)
    if match:
        return match.group()
    return None


def parse_time(time_interval):
    start_time = time_interval.split('-')[0]
    dt = datetime.strptime(start_time, "%H:%M")
    return dt.hour * 60 + dt.minute


def get_groups():
    groups = lines_schedule[0]
    return groups[6:len(groups) - 4]


# print(get_groups())


def get_by_day(group, day):
    first_last = get_day_place(day)
    row_first = first_last[0] - 1
    row_last = first_last[1]
    col = get_group_place(group) - 1

    cell_value = []
    for row in range(row_first, row_last):
        time = lines_schedule[row][5][1:].replace("\n", " ")
        cell_value.append((time.replace(" ", ""), lines_schedule[row][col].replace("\n", " ")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


# pprint(get_by_day("ИВТ-21БО", "понедельник"))


def get_teacher_by_day(teacher, day):
    first_last = get_day_place(day)
    row_first = first_last[0] - 1
    row_last = first_last[1]
    col = get_teacher_place(teacher) - 1

    cell_value = []
    for row in range(row_first, row_last):
        time = lines_teacher[row][5][1:].replace("\n", " ")
        cell_value.append((time.replace(" ", ""), lines_teacher[row][col].replace("\n", " ")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


# pprint(get_teacher_by_day("Лагутина", "понедельник"))


def get_by_group(group):
    col = get_group_place(group) - 1
    rows = len(lines_schedule)
    cell_value = ["понедельник"]
    for row in range(2, rows):
        if lines_schedule[row][5]:
            time = lines_schedule[row][5][1:].replace("\n", "")
            cell_value.append((time.replace(" ", ""), lines_schedule[row][col].replace("\n", " ")))
        else:
            cell_value.append((lines_schedule[row][col].replace("\n", " ")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


# pprint(get_by_group("ИВТ-21БО"))


def get_by_teacher(name):
    col = get_teacher_place(name) - 1
    rows = len(lines_teacher)
    cell_value = ["понедельник"]
    for row in range(2, rows):
        if lines_teacher[row][5]:
            time = lines_teacher[row][5][1:].replace("\n", " ")
            cell_value.append((time.replace(" ", ""), lines_teacher[row][col].replace("\n", " ")))
        else:
            cell_value.append((lines_teacher[row][col].replace("\n", " ")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


# pprint(get_by_teacher("Лагутина"))


def get_classrooms():
    cabs_count = len(lines_cabs[0])
    cabs = []
    for i in range(cabs_count):
        cabs.append((lines_cabs[0][i], lines_cabs[1][i]))
    return cabs


# pprint(get_classrooms())
def get_free_classroom(day, number):
    first_last = get_day_place(day)
    row_first = first_last[0] - 1
    row_last = first_last[1]
    cols = len(lines_schedule[0])

    cabs = {}
    for row in range(row_first, row_last):
        time = lines_schedule[row][5][1:].replace("\n", "")
        cabs[time.replace(" ", "")] = set()
        for col in range(6, cols):
            if extract_aud_number(lines_schedule[row][col]):
                cabs[time.replace(" ", "")].add(extract_aud_number(lines_schedule[row][col]))

    free_cabs = {
        key: [item for item in get_classrooms() if item[0] not in values]
        for key, values in cabs.items()
    }
    free_cabs = dict(sorted(
        free_cabs.items(),
        key=lambda x: parse_time(x[0])
    ))
    return list(free_cabs.keys())[number - 1], list(free_cabs.values())[number - 1]


# txt??
last_values = None


# Самый прямой вариант
def check_spreadsheet_changes():
    global last_values
    current_values = worksheet_schedule.get_all_values(
        combine_merged_cells=True,
        maintain_size=True,
        pad_values=True
    )

    if last_values is None:
        last_values = current_values
        return False

    if current_values != last_values:
        upd = []
        for row, (prev_row, curr_row) in enumerate(zip(last_values, current_values)):
            for col in range(len(prev_row)):
                if prev_row[col] != curr_row[col]:
                    tm = current_values[row][5].replace("\n", "")[1:]
                    group = current_values[0][col].replace("\n", "")
                    day = current_values[row][4].replace("\n", "")
                    upd.append(
                        (row + 1, col + 1, current_values[row][col], group, tm, day))
        last_values = current_values
        return upd
    return False


def process_schedule(text):
    lines = text.strip().split('\n')
    result = []

    # Определяем тип расписания
    is_week = '(Неделя)' in lines[0]
    current_day = None
    day_content = []

    for line in lines:
        line = line.rstrip()

        # Обнаружение нового дня (только для недельного расписания)
        if is_week and line.startswith('- ') and ':' in line:
            if current_day is not None:
                # Обработка предыдущего дня
                if not any(c.strip() for c in day_content if c not in ('', '--------')):
                    result.append(f"{current_day} нет пар")
                else:
                    result.append(current_day)
                    result.extend(day_content)
            # Начинаем новый день
            current_day = line
            day_content = []
            continue

        # Сохраняем содержимое дня
        if current_day is not None:
            day_content.append(line)
        else:
            result.append(line)

    # Обработка последнего дня
    if is_week and current_day is not None:
        if not any(c.strip() for c in day_content if c not in ('', '--------')):
            result.append(f"{current_day} нет пар")
        else:
            result.append(current_day)
            result.extend(day_content)

    # Обработка формата для одного дня
    if not is_week:
        has_content = any(
            line.strip() and not line.startswith('--------')
            for line in lines[1:]
        )
        if not has_content:
            result.append("нет пар")

    # Восстанавливаем оригинальные пустые строки между днями
    return '\n'.join(result).replace('нет пар\n-', 'нет пар\n\n-')