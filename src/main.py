from src.parser import read_file_from_csv, read_file_from_xlsx
from src.utils import print_json

# Тестирование работы
# data = read_file_from_xlsx("operations.xslx")
data = read_file_from_csv("operations.csv")
print_json(data[0:1])
