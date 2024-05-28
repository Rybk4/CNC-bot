class User:
    def __init__(self):
        self.city = None
        self.full_name = None
        self.phone_number = None
        self.service_or_product = None
        self.description = None
        self.preferred_time = None
        self.remarks = None

    def __str__(self):
        return (f"Город: {self.city}\n"
                f"ФИО: {self.full_name}\n"
                f"Номер телефона: {self.phone_number}\n"
                f"Услуга или товар: {self.service_or_product}\n"
                f"Описание: {self.description}\n"
                f"Удобное время для связи: {self.preferred_time}\n"
                f"Примечания: {self.remarks}")
