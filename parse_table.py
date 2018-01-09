import xlrd
import xlwt


class TableGenerator:
    def generate_parse_table(self):
        table = ParseTable()
        table.read_in_inputs('Input/DataFolder/Inputs.txt')
        table.read_in_nonterminals('Input/DataFolder/Nonterminals.txt')
        table.read_in_first('Input/DataFolder/Firsts.txt')
        table.read_in_follows('Input/DataFolder/Follows.txt')
        table.read_in_grammars('Input/DataFolder/grammars')
        table.write_table_to_excel('Output/parse_table.xls')


class ParseTable:
    def __init__(self):
        self.data = []
        # for bolding/italicizing reasons
        self.nonterminals = []
        self.inputs = []

    def read_in_inputs(self, input_file):
        terminals = {}
        inputs_file = open(input_file, 'r')

        for line in inputs_file:
            terminals[line[:-1]] = 0

        for key in terminals:
            self.inputs.append(key)

        self.inputs.sort()

    def read_in_nonterminals(self, input_file):
        nonterminals_file = open(input_file, 'r')
        # Create a list for the first and follows for each of the nonterminals
        for line in nonterminals_file:
            self.nonterminals.append(line[:-1])
            self.data.append({'nonterminal': line[:-1], 'first': [], 'follows': [], 'grammar': []})

    def read_in_first(self, input_file):
        first_file = open(input_file, 'r')
        count = 0
        for line in first_file:
            line = line.replace(' ', '')
            line = line.replace('\n', '')
            split_line = line.split('|')
            self.data[count]['first'] = split_line
            count += 1

    def read_in_follows(self, input_file):
        follows_file = open(input_file, 'r')
        count = 0
        for line in follows_file:
            line = line.replace(' ', '')
            line = line.replace('\n', '')
            split_line = line.split('|')
            self.data[count]['follows'] = split_line
            count += 1

    def read_in_grammars(self, input_file):
        grammar_file = open(input_file, 'r')
        count = 0
        for line in grammar_file:
            line = line.replace('\n', '')
            split_line = line.split(' | ')
            self.data[count]['grammar'] = split_line
            count += 1

    def write_table_to_excel(self, output_file):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Parse Table')

        # Set up the table with Headings
        sheet.write(0, 0, 'Nonterminal')
        count = 1
        for terminal in self.inputs:
            sheet.write(0, count, terminal)
            count += 1

        row = 1
        for nonterminal in self.nonterminals:

            # Print the nonterminal
            sheet.write(row, 0, nonterminal)

            col = 1
            for terminal in self.inputs:
                # Print the calculated Value otherwise print Syntax Error
                if 'epsilon' in self.data[row-1]['first']:
                    if terminal in self.data[row-1]['first'] or terminal in self.data[row-1]['follows']:
                        my_string = ""
                        for item in self.data[row-1]['grammar']:
                            my_string += item + " | "
                        my_string = my_string[:-3]

                        sheet.write(row, col, my_string)

                else:
                    if terminal in self.data[row-1]['first']:
                        my_string = ""
                        for item in self.data[row-1]['grammar']:
                            my_string += item + " | "
                        my_string = my_string[:-3]
                        sheet.write(row, col, my_string)

                col += 1
            row += 1

        workbook.save(output_file)
