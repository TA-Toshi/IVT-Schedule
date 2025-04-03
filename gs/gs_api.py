from datetime import datetime
from pathlib import Path
import gspread
import re
from pprint import pprint

current_dir = Path(__file__).parent
creds_path = current_dir.parent / "creds.json"

gc = gspread.service_account(filename=str(creds_path))
wks = gc.open_by_key("164JbfoXNQVtHmsUGcReAKX81pZPDimaIORAKQ1Fi6Hg")

worksheet_schedule = wks.get_worksheet(0)
worksheet_cabs = wks.get_worksheet(1)
# worksheet_teacher = wks.get_worksheet(2)

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


# pprint(lines_cabs)

def get_day_place(name):
    place = str(worksheet_schedule.find(name, in_column=5)).split()[1]
    numbers = re.findall(r'\d+', place)
    row, col = map(int, numbers)
    first_last = [row, row + 9]
    return first_last


def get_group_place(name):
    cell = worksheet_schedule.find(name)
    place = str(cell).split()[1]

    numbers = re.findall(r'\d+', place)
    row, col = map(int, numbers)
    return col


def remove_consecutive_duplicates(tuples_list):
    if not tuples_list:
        return []

    result = [tuples_list[0]]
    for i in range(1, len(tuples_list)):
        if tuples_list[i] != tuples_list[i - 1]:
            result.append(tuples_list[i])
    return result


def extract_aud_number(text):
    # Ищем "ауд." (регистронезависимо) + 3 цифры после
    match = re.search(r'\b\d{3}\b', text)
    if match:
        return match.group()  # возвращаем найденные 3 цифры
    return None


def parse_time(time_interval):
    start_time = time_interval.split('-')[0]
    dt = datetime.strptime(start_time, "%H:%M")
    return dt.hour * 60 + dt.minute


def get_by_day(group, day):
    first_last = get_day_place(day)
    row_first = first_last[0] - 1
    row_last = first_last[1]
    col = get_group_place(group) - 1

    cell_value = []
    for row in range(row_first, row_last):
        time = lines_schedule[row][5][1:].replace("\n", "")
        cell_value.append((time.replace(" ", ""), lines_schedule[row][col].replace("\n", "")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


# pprint(get_by_day("ИВТ-13БО", "четверг"))
def get_by_group(group):
    col = get_group_place(group) - 1
    rows = len(lines_schedule)
    cell_value = ["понедельник"]
    for row in range(2, rows):
        if lines_schedule[row][5]:
            time = lines_schedule[row][5][1:].replace("\n", "")
            cell_value.append((time.replace(" ", ""), lines_schedule[row][col].replace("\n", "")))
        else:
            cell_value.append((lines_schedule[row][col].replace("\n", "")))
    cell_value = remove_consecutive_duplicates(cell_value)
    return cell_value


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


# pprint(get_free_classroom("понедельник", 2))
def alarm():
    pass
