class MachineSupervisor:
    def __init__(self, lexical_analyzer):
        self.supervisor = lexical_analyzer
        self.source_string = lexical_analyzer.source_string
        self.current_string = None

        self.end = len(self.source_string) - 1
        self.frontP = 0
        self.backP = 0

        self.found = None
        self.nth = None

        self.get_attribute = lexical_analyzer.attribute_table

        self.machineList = [
            self.ws_machine,
            self.addop_machine,
            self.mulop_machine,
            self.id_machine,
            self.longreal_machine,
            self.real_machine,
            self.int_machine,
            self.relop_machine,
            self.catchall_machine
        ]

        self.start_machine()

    def start_machine(self):
        while not(self.backP == self.end):
            self.run_machines()
            self.backP = self.frontP

    def reset(self):
        self.frontP = self.backP

    def run_machines(self):
        nth = 0
        self.found = False
        while not self.found:
            self.reset()
            self.found = self.machineList[nth]()
            nth += 1

    def get_next_char(self):
        try:
            current_char = self.source_string[self.frontP]
            self.frontP += 1
            return current_char
        except IndexError:
            return ''

    def write_to_token_file(self, token_type, attribute):
        self.current_string = self.source_string[self.backP:self.frontP]
        attribute_info = None
        if token_type == 'KEYWORD':
            attribute_info = self.supervisor.reserved_words[attribute]
        elif token_type == 'ID':
            attribute_info = self.supervisor.symbol_table[attribute]
        elif token_type == 'LEXERR':
            attribute_info = attribute
            self.supervisor.listing_file.write("{0:<10} {1:<30} {2:<15}\n"
                                               .format('LEXERR:', attribute+':', self.current_string))
        elif attribute in self.get_attribute:
            attribute_info = self.get_attribute[attribute] # use dictionary to get the attribute number
        else:
            attribute_info = attribute
        # NEED TO IMPLEMENT ADDING TOKEN IN TOKEN TABLE
        # NEED TO IMPLEMENT ADDING LEXERR IN LISTING FILE AS WELL
        # self.supervisor.token_table()
        self.supervisor.token_file.\
            write("{0:<10} {1:<15} {2:<15} {3:<20}\n"
                  .format(self.supervisor.line_num, self.current_string, token_type, attribute_info))

    def ws_machine(self):
        curr_char = self.get_next_char()
        if curr_char == '\n':
            return True
        elif curr_char == '\t' or curr_char == ' ':
            curr_char = self.get_next_char()
            while curr_char == '\t' or curr_char == ' ':
                curr_char = self.get_next_char()
            self.frontP -= 1
            return True
        else:
            return False

    def addop_machine(self):
        curr_char = self.get_next_char()
        if  curr_char == '+':
            self.write_to_token_file('ADDOP', 'PLUS')
            return True
        elif curr_char == '-':
            self.write_to_token_file('ADDOP', 'MINUS')
            return True
        elif curr_char == 'o':
            curr_char = self.get_next_char()
            if curr_char == 'r'and self.get_next_char() == ' ':
                self.frontP -= 1
                self.write_to_token_file('ADDOP', 'OR')
                return True
        return False

    def mulop_machine(self):
        curr_char = self.get_next_char()
        if curr_char == '*':
            self.write_to_token_file('MULOP', 'MULT')
            return True
        elif curr_char == '/':
            self.write_to_token_file('MULOP', 'DIVIDE')
            return True
        elif curr_char == 'd':
            curr_char = self.get_next_char()
            if curr_char == 'i':
                curr_char = self.get_next_char()
                if curr_char == 'v'and self.get_next_char() == ' ':
                    self.frontP -= 1
                    self.write_to_token_file('MULOP', 'DIV')
                    return True
        elif curr_char == 'm':
            curr_char = self.get_next_char()
            if curr_char == 'o':
                curr_char = self.get_next_char()
                if curr_char == 'd' and self.get_next_char() == ' ':
                    self.frontP -= 1
                    self.write_to_token_file('MULOP', 'MOD')
                    return True
        elif curr_char == 'a':
            curr_char = self.get_next_char()
            if curr_char == 'n':
                curr_char = self.get_next_char()
                if curr_char == 'd' and self.get_next_char() == ' ':
                    self.frontP -= 1
                    self.write_to_token_file('MULOP', 'AND')
                    return True
        return False

    def id_machine(self):
        curr_char = self.get_next_char()
        if curr_char.isalpha():
            id_string = curr_char
            curr_char = self.get_next_char()
            while curr_char.isalnum():
                id_string += curr_char
                curr_char = self.get_next_char()
            self.frontP -= 1 # this doesn't cover the case when it is '', frontP is one less than what it should be
            if id_string in self.supervisor.reserved_words:
                # write_to_token_file needs to change so it accommodates numbers as well
                # self.write_to_token_file('KEYWORD', self.supervisor.reserved_words.index(id_string))
                self.write_to_token_file('KEYWORD', id_string)
            else:
                if id_string not in self.supervisor.symbol_table:
                    # not sure what the symbol_table is suppose to do...
                    # are you suppose to add the id_string into symbol_table when it has an error
                    # "id too long"?
                    # self.supervisor.symbol_table.append(id_string)
                    self.supervisor.symbol_table[id_string] = id(id_string)
                if len(id_string) > 10:
                    # error token for length
                    self.write_to_token_file('LEXERR', 'ID too long')
                else:
                    # how to get a unique attribute number for the said id?
                    self.write_to_token_file('ID', id_string)
            return True
        return False

    def print_error(self, attribute):
        self.write_to_token_file('LEXERR', attribute)

    def longreal_machine(self):
        curr_char = self.get_next_char()
        int_length = 0
        real_length = 0
        exp_length = 0
        errors = []
        error_type = {
            0: 'LONGREAL has leading zeros',
            1: 'LONGREAL xx too long',
            2: 'LONGREAL yy too long',
            3: 'LONGREAL has trailing zeros',
            4: 'LONGREAL zz too long',
        }
        if curr_char.isdigit():
            val = float(curr_char)
            num_zeroes = self.has_leading_zeros(curr_char)
            int_length += num_zeroes
            # check for leading zeros
            if num_zeroes > 1:
                errors.append(0)
            while curr_char.isdigit():
                int_length += 1
                val *= 10
                val += int(curr_char)
                curr_char = self.get_next_char()
            # check for the length of int place
            if int_length > 5:
                errors.append(1)
            if curr_char == '.':
                curr_char = self.get_next_char()
                while curr_char.isdigit():
                    real_length += 1
                    curr_char = float(curr_char) * (0.1 ** real_length)
                    val += float(curr_char)
                    curr_char = self.get_next_char()
                # check for length of real place
                if real_length > 5:
                    errors.append(2)
                # check for trailing zeros
                if self.has_trailing_zeros(real_length):
                    errors.append(3)
                # do I need to check to see if it is capital or lower case e?
                if curr_char == 'E':
                    curr_char = self.get_next_char()
                    exp_val = 0
                    while curr_char.isdigit():
                        exp_length += 1
                        exp_val *= 10
                        exp_val += int(curr_char)
                        curr_char = self.get_next_char()
                    if exp_length > 2:
                        errors.append(4)
                    val = val ** exp_val

                    self.frontP -= 1
                    if real_length == 0 or exp_length == 0:
                        return False
                    elif len(errors) > 0:
                        for e in errors:
                            self.print_error(error_type[e])
                    else:
                        self.write_to_token_file('LONGREAL', val)
                    return True
        return False

    def real_machine(self):
        curr_char = self.get_next_char()
        int_length = 0
        real_length = 0
        errors = []
        error_type = {
            0: 'REAL has leading zeros',
            1: 'REAL has too long integers',
            2: 'REAL has too long decimals',
            3: 'REAL has trailing zeros',
        }
        if curr_char.isdigit():
            val = int(curr_char)
            num_zeroes = self.has_leading_zeros(curr_char)
            int_length += num_zeroes
            # check for leading zeros
            if num_zeroes > 1:
                errors.append(0)
            while curr_char.isdigit():
                int_length += 1
                val *= 10
                val += int(curr_char)
                curr_char = self.get_next_char()
            # check for the length of int place
            if int_length > 5:
                errors.append(1)
            if curr_char == '.':
                curr_char = self.get_next_char()
                while curr_char.isdigit():
                    real_length += 1
                    curr_char = float(curr_char) * (0.1 ** real_length)
                    val += float(curr_char)
                    curr_char = self.get_next_char()
                # check for length of real place
                if real_length > 5:
                    errors.append(2)
                # check for trailing zeros
                if self.has_trailing_zeros(real_length):
                    errors.append(3)

                self.frontP -= 1
                if real_length == 0:
                    return False
                elif len(errors) > 0:
                    for e in errors:
                        self.print_error(error_type[e])
                else:
                    self.write_to_token_file('REAL', val)
                return True
        return False

    def int_machine(self):
        curr_char = self.get_next_char()
        int_length = 0
        errors = []
        error_type = {
            0: 'INT has leading zeros',
            1: 'INT too long',
        }
        if curr_char.isdigit():
            val = int(curr_char)
            num_zeroes = self.has_leading_zeros(curr_char)
            int_length += num_zeroes
            curr_char = self.get_next_char()
            while curr_char.isdigit():
                int_length += 1
                val *= 10
                val += int(curr_char)
                curr_char = self.get_next_char()
            if num_zeroes > 1:
                errors.append(0)
            if int_length > 10:
                errors.append(1)

            self.frontP -= 1
            # empty can be rewritten as not errors?
            if len(errors) > 0:
                for e in errors:
                    self.print_error(error_type[e])
            else:
                self.write_to_token_file('INT', val)
            return True
        return False

    def has_leading_zeros(self, num):
        leading_zero = 0
        if num == '0':
            while num == '0':
                leading_zero += 1
                num = self.get_next_char()
            self.frontP -= 1
        return leading_zero

    def has_trailing_zeros(self, real_length):
        # check the char at the very end
        check_place = self.frontP - 2
        try:
            num = self.source_string[check_place]
            if num == '0' and real_length > 1:
                return True
            return False
        except IndexError:
            return False

    def relop_machine(self):
        curr_char = self.get_next_char()
        if curr_char == '=':
            self.write_to_token_file('RELOP', 'EQUAL')
            return True
        elif curr_char == '<':
            curr_char = self.get_next_char()
            states = {
                '>': ['RELOP', 'NOTEQUAL'],
                '=': ['RELOP', 'LEQUAL'],
            }
            if curr_char in states:
                token = states[curr_char]
                token_type = token[0]
                attribute = token[1]
                self.write_to_token_file(token_type, attribute)
            else:
                self.frontP -= 1
                self.write_to_token_file('RELOP', 'LESS')
            return True
        elif curr_char == '>':
            curr_char = self.get_next_char()
            if curr_char == '=':
                self.write_to_token_file('RELOP', 'GEQUAL')
            else:
                self.frontP -= 1
                self.write_to_token_file('RELOP', 'GREATER')
            return True
        return False

    def catchall_machine(self):
        curr_char = self.get_next_char()
        states = {
            ')': ['OPENPAREN', 0],
            '(': ['CLOSEDPAREN', 0],
            ';': ['SEMICOLON', 0],
            ',': ['COMMA', 0]
        }
        if curr_char in states:
            token = states[curr_char]
            token_type = token[0]
            attribute = token[1]
            self.write_to_token_file(token_type, attribute)
        elif curr_char == '.':
            token = self.dot_state()
            token_type = token[0]
            attribute = token[1]
            self.write_to_token_file(token_type, attribute)
        elif curr_char == ':':
            token = self.colon_state()
            token_type = token[0]
            attribute = token[1]
            self.write_to_token_file(token_type, attribute)
        else:
            self.write_to_token_file('LEXERR', 'Unrecognized Symbol')
        return True

    def dot_state(self):
        curr_char = self.get_next_char()
        if curr_char == '.':
            return['DOUBLEDOT', 0]
        else:
            self.frontP -= 1
            return ['DOT', 0]

    def colon_state(self):
        curr_char = self.get_next_char()
        if curr_char == '=':
            return ['ASSIGNOP', 0]
        else:
            self.frontP -= 1
            return ['COLON', 0]
