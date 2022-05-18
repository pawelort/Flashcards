import json, logging, io, argparse

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("--import_from", help="file with cards to be loaded")
argument_parser.add_argument("--export_to", help="file where cards should be exported")

class Flashcards:
    def __init__(self):
        self.flashcards_dict = dict()
        self.auto_export_file_name = None
        self.buffer = io.StringIO()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)


    def print_to_buffer(self, msg, separ=' '):
        print_save_to_buffer(msg, separ, self.buffer)


    def write_to_buffer(self):
        user_input = input()
        self.buffer.write(user_input + '\n')
        return user_input


    def option_selection(self):
        while True:
            self.print_to_buffer("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
            user_selection = self.write_to_buffer()
            if user_selection == "add":
                self.add_new_card()
            elif user_selection == 'remove':
                self.remove_card()
            elif user_selection == 'import':
                self.card_import()
            elif user_selection == 'export':
                self.card_export()
            elif user_selection == 'ask':
                self.answering()
            elif user_selection == 'exit':
                self.print_to_buffer("Bye bye!")
                if self.auto_export_file_name != None:
                    self.card_export(self.auto_export_file_name)
                break
            elif user_selection == 'log':
                self.log()
            elif user_selection == 'hardest card':
                self.hardest_card()
            elif user_selection == 'reset stats':
                self.reset_stats()
            else:
                self.print_to_buffer("Invalid command")


    def term_verif(self, term):
        if term in self.flashcards_dict.keys():
            raise TermDuplicationError(term)
        else:
            return term


    def definition_verif(self, definition):
        for term, info in self.flashcards_dict.items():
            if definition in info.get('definition'):
                raise DefinitionDuplicationError(definition)
        else:
            return definition


    def card_to_rem_verif(self, term):
        if term not in self.flashcards_dict.keys():
            raise CardNotInDatabaseError(term)
        else:
            return term


    def add_new_card(self):
        self.print_to_buffer("The card:")
        while True:
            try:
                current_term = self.term_verif(self.write_to_buffer())
                break
            except TermDuplicationError as err:
                self.print_to_buffer(err)
        self.print_to_buffer("The definition of the card")
        while True:
            try:
                current_definition = self.definition_verif(self.write_to_buffer())
                break
            except DefinitionDuplicationError as err:
                self.print_to_buffer(err)
        self.flashcards_dict[current_term] = {'definition': current_definition, 'errors': 0}
        self.print_to_buffer(f'The pair ("{current_term}":"{current_definition}") has been added.')


    def remove_card(self):
        self.print_to_buffer("Which card?")
        try:
            card_to_be_removed = self.card_to_rem_verif(self.write_to_buffer())
            del self.flashcards_dict[card_to_be_removed]
            self.print_to_buffer("The card has been removed.")
        except CardNotInDatabaseError as err:
            self.print_to_buffer(err)


    def answering(self):
        self.print_to_buffer("How many times to ask?")
        cards_to_show = int(self.write_to_buffer())
        card_showed = 0
        if len(self.flashcards_dict) > 0:
            while True:
                for key, info in self.flashcards_dict.items():
                    card_showed += 1
                    self.print_to_buffer(f'Print the definition of "{key}":')
                    current_answer = self.write_to_buffer()
                    all_definitions = [info.get('definition') for terms, info in self.flashcards_dict.items() for definition in info.keys() if definition == 'definition']
                    if current_answer == info.get('definition'):
                        self.print_to_buffer("Correct!")
                    elif current_answer in all_definitions:
                        for term, additional_inf in self.flashcards_dict.items():
                            if current_answer == additional_inf.get('definition'):
                                correct_val = term
                                break
                        self.print_to_buffer(f'Wrong.The right answer is {info.get("definition")}, but your definition is correct for {correct_val}.')
                        self.flashcards_dict[key]['errors'] += 1
                    else:
                        self.print_to_buffer(f'Wrong. The right answer is "{info.get("definition")}".')
                        self.flashcards_dict[key]['errors'] += 1
                    if card_showed >= cards_to_show:
                        break
                if card_showed >= cards_to_show:
                    break
        else:
            self.print_to_buffer("There is no cards added")


    def card_export(self, file_name=None):
        if file_name == None:
            self.print_to_buffer("File name:")
            file_name = self.write_to_buffer()
        with open(file_name, 'w') as export_file:
            json.dump(self.flashcards_dict ,export_file)
            self.print_to_buffer(f"{len(list(self.flashcards_dict.keys()))} cards have been saved.")


    def card_import(self):
        self.print_to_buffer("File name:")
        file_name = self.write_to_buffer()
        try:
            with open(file_name, 'r') as import_file:
                loaded_database = json.load(import_file)
                self.flashcards_dict.update(loaded_database)
                self.print_to_buffer(f"{len(list(loaded_database.keys()))} cards have been loaded.")
        except FileNotFoundError:
            self.print_to_buffer("File not found.")


    def arg_import_from(self, file_name):
        try:
            with open(file_name, 'r') as import_file:
                loaded_database = json.load(import_file)
                self.flashcards_dict.update(loaded_database)
                self.print_to_buffer(f"{len(list(loaded_database.keys()))} cards have been loaded.")
        except FileNotFoundError:
            self.print_to_buffer("File not found.")


    def hardest_card(self):
        try:
            highest_mistake_amount = max([info.get('errors') for term, info in self.flashcards_dict.items() for errors in info.keys() if errors == 'errors'])
            if highest_mistake_amount == 0:
                self.print_to_buffer("There are no cards with errors.")
            else:
                hardest_terms = []
                for term, info in self.flashcards_dict.items():
                    if info.get('errors') == highest_mistake_amount:
                        hardest_terms.append(term)

                if len(hardest_terms) < 2:
                    msg = ''.join((f'The hardest card is "', *hardest_terms, f'". You have {highest_mistake_amount} errors answering it.'))
                    self.print_to_buffer(msg, separ='')
                else:
                    msg = ''.join(('The hardest cards are "', '", "'.join(hardest_terms), f'". You have {highest_mistake_amount} errors answering them.'))
                    self.print_to_buffer(msg, separ='')
        except ValueError:
            self.print_to_buffer("There are no cards with errors.")


    def reset_stats(self):
        for term, info in self.flashcards_dict.items():
            info['errors'] = 0
            self.print_to_buffer("Card statistics have been reset.")


    def log(self):
        self.print_to_buffer("File name:")
        file_name = self.write_to_buffer()
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        for line in self.buffer.getvalue().split('\n'):
            self.logger.info(line)
        file_handler.close()
        self.print_to_buffer("The log has been saved.")


class TermDuplicationError(Exception):
    def __init__(self, term):
        self.message = f'The term "{term}" already exists. Try again:'
        super().__init__(self.message)


class DefinitionDuplicationError(Exception):
    def __init__(self, definition):
        self.message = f'The definition "{definition}" already exists. Try again:'
        super().__init__(self.message)


class CardNotInDatabaseError(Exception):
    def __init__(self, term):
        self.message = f'Can\'t remove "{term}": there is no such card.'
        super().__init__(self.message)

def print_save_to_buffer(message, separator, buffer_name):
    print(message, file=buffer_name, sep=separator)
    print(message, sep=separator)

arguments = argument_parser.parse_args()
flashcards_instance = Flashcards()

if arguments.import_from != None:
    flashcards_instance.arg_import_from(arguments.import_from)

if arguments.export_to != None:
    flashcards_instance.auto_export_file_name = arguments.export_to

flashcards_instance.option_selection()


