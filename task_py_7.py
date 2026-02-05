from collections import UserDict
from datetime import datetime, date, timedelta

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return f"Error: {ve}"
        except IndexError:
            return "Error: missing arguments"
        except Exception as e:
            return f"Unexpected error: {e}"
    return wrapper

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0].lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, *args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError("Phone must be 10 digits")

class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date_obj)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_string):
        phone_obj = Phone(phone_string)
        self.phones.append(phone_obj)

    def remove_phone(self, phone_string):
        for phone in self.phones:
            if phone.value == phone_string:
                self.phones.remove(phone)
                break

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value
                return
        raise ValueError("Old phone not found")

    def find_phone(self, phone_string):
        for phone in self.phones:
            if phone.value == phone_string:
                return phone
        return None

    def add_birthday(self, birthday_string):
        birthday_obj = Birthday(birthday_string)
        self.birthday = birthday_obj

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value.strftime("%d.%m.%Y")
        else:
            return None

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        bday_str = self.show_birthday() or "No birthday set"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {bday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.data.pop(name, None)

    @staticmethod
    def find_next_weekday(start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = record.birthday.value.replace(year=today.year + 1)
                if 0 <= (birthday_this_year - today).days <= days:
                    congratulation_date = self.adjust_for_weekend(birthday_this_year)
                    congratulation_date_str = congratulation_date.strftime("%d.%m.%Y")
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date_str
                    })
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found"
    record.add_birthday(birthday_str)
    return f"Birthday added for {name}"

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found"
    birthday = record.show_birthday()
    if birthday:
        return f"{name}'s birthday: {birthday}"
    else:
        return f"{name} has no birthday set"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays"
    return "\n".join(f"{entry['name']}: {entry['congratulation_date']}" for entry in upcoming)

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found"
    record.edit_phone(old_phone, new_phone)
    return "Phone updated"

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found"
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}'s phones: {phones}" if phones else f"{name} has no phones"

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()