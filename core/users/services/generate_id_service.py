import random

class GenerateIDService:
    @staticmethod
    def generate_unique_department_id():
        """Генерация уникального идентификатора департамента"""
        while True:
            random_digits = ''.join(random.choices('0123456789', k = 4))
            department_id = f'00{random_digits}'

            return department_id

