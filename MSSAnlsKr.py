import pandas as pd
file_path = '3. для анализа.xlsx'
data = pd.read_excel(file_path, header=0)
print(data)
data_columns = data.columns[2:]# Убедимся, что все числовые колонки имеют корректный числовой формат
for column in data_columns:# Преобразование данных в числовой формат, игнорируя ошибки (чтобы не конвертировать текст)
    data[column] = pd.to_numeric(data[column], errors='ignore')

# Проверка на наличие показателя "Структурная модель"
structural_model_indicator = "Структурная модель (создано единое юридическое лицо, создана единая диспетчерская служба, отдельные юридические лица без функционального объединения)"
structural_model_exists = structural_model_indicator in data['имя показателя'].unique()

# Если показатель присутствует, подготовим данные для корреляционного анализа
if structural_model_exists:
    # Выделение данных по ключевому показателю
    structural_model_data = data[data['имя показателя'] == structural_model_indicator].copy()

    # Кодирование категорий "Структурная модель"
    # Заменяем текстовые значения на 0 и 1
    coding_map = {
        "отдельные юридические лица без функционального объединения": 0,
        "создана единая диспетчерская служба": 1,
        "создано единое юридическое лицо": 2
    }
    # Применяем кодирование ко всем годам
    for year in data_columns:
        structural_model_data[year] = structural_model_data[year].map(coding_map)

# Исключаем показатель "Финансовая модель" из анализа
non_financial_data = data[data['имя показателя'] != "Финансовая модель (подушевое финансирование, подушевое+вызов, оплата за вызов)"].copy()

# Соединим данные по "Структурной модели" с остальными показателями по имени региона и годам
# Для этого сначала преобразуем данные "Структурной модели" в формат, подходящий для соединения
structural_model_melted = structural_model_data.melt(id_vars=['Имя региона'], value_vars=data_columns, var_name='Год', value_name='Структурная модель')

# Преобразуем остальные данные в подобный формат для упрощения соединения
non_financial_melted = non_financial_data.melt(id_vars=['имя показателя', 'Имя региона'], value_vars=data_columns, var_name='Год', value_name='Значение показателя')

# Соединение данных
merged_data = pd.merge(left=non_financial_melted, right=structural_model_melted, on=['Имя региона', 'Год'])

# Преобразование 'Значение показателя' в числовой формат
merged_data['Значение показателя'] = pd.to_numeric(merged_data['Значение показателя'], errors='coerce')

# Группировка данных и вычисление средних значений
grouped_data = merged_data.groupby(['имя показателя', 'Год']).agg({
    'Значение показателя':'mean',
    'Структурная модель':'first'  # Предполагаем, что 'Структурная модель' одинакова для одного показателя в течение года
}).reset_index()
print("Всего уникальных показателей в сгруппированных данных:", len(grouped_data['имя показателя'].unique()))

# Вычисление корреляции для каждого показателя и года
correlation_results = []
missing_correlation_indicators = []

for indicator in grouped_data['имя показателя'].unique():
    indicator_data = grouped_data[grouped_data['имя показателя'] == indicator]
    correlation = indicator_data['Значение показателя'].corr(indicator_data['Структурная модель'])
    if not pd.isna(correlation):  # Исключаем NaN значения корреляции
        correlation_results.append({
            'имя показателя': indicator,
            'Корреляция': correlation
        })
    else:
        missing_correlation_indicators.append(indicator)

print("Показатели, для которых не вычисляется корреляция:", missing_correlation_indicators)
print("Всего показателей, для которых не вычисляется корреляция:", len(missing_correlation_indicators))

# Преобразование результатов в DataFrame для удобства отображения
correlation_df = pd.DataFrame(correlation_results).sort_values(by='Корреляция', ascending=False)

# Вывод результатов
print(correlation_df)
correlation_df.to_excel("2.xlsx")
