
class SyntaxAnalyzer:
    def __init__(self):
        self.token_list = []
        self.parse_table = []
        self.nonterminal_list = []
        self.follows_list = []

        self.tok = None
        self.index = 0

        self.generate_parsetable()


    def generate_parsetable(self):
        self.read_nonterminals()
        self.read_firsts()
        self.read_follows()

    def read_nonterminals(self):
        nonterminals = open('Input/Nonterminals.txt', 'r')
        for line in nonterminals:
            self.nonterminal_list.append(line[:-1])
            self.parse_table.append({'nonterminal': line[:-1], 'first': [], 'follows': []})

    def read_firsts(self):
        firsts = open('Input/Firsts.txt', 'r')
        count = 0
        for line in firsts:
            line = line.replace(' ', '')
            first_list = line[:-1].split('|')
            self.parse_table[count]['first'] = first_list
            count += 1

    def read_follows(self):
        follows = open('Input/Follows.txt', 'r')
        count = 0
        for line in follows:
            line = line.replace(' ', '')
            f_list = line[:-1].split('|')
            self.follows_list.append(f_list)
            self.parse_table[count]['follows'] = f_list
            count += 1

    def create_expected_list(self, ind, epsilon):
        expected_list = self.parse_table[ind]['first']
        if epsilon:
            expected_list.append(self.parse_table[ind]['follows'])
        return expected_list

    def get_token(self):
        self.tok = self.token_list[self.index]
        self.index += 1

    def syntax_error(self, nonterminal, epsilon=False):
        ind = self.nonterminal_list.index(nonterminal)
        expected_list = self.create_expected_list(ind, epsilon)
        # print SYNERR: Expected 'expected_list' got 'self.tok'
        print 'SYNERR: Expected ' + expected_list
        sync_set = self.parse_table[ind]['follows']
        sync_set.append('$')
        if self.tok not in sync_set:
            while self.tok not in sync_set:
                self.get_token()
            self.index -= 1

    def parse(self):
        self.get_token()
        # call_prod()
        self.match('$')

    def match(self, expected):
        if expected == self.tok and not expected == '$':
            self.get_token()
        elif expected == self.tok and expected == '$':
            print "Nothing"
        else:
            # print SYNERR: Expected t got tok
            self.get_token()

    def program(self):
        # 1.1.1
        if self.tok == 'program':
            self.match('program')
            self.match('id')
            self.match('(')
            self.identifier_list()
            self.match(')')
            self.match(';')
            self.program1()
        else:
            self.syntax_error('program')

    def program1(self):
        # 1.2.1
        if self.tok == 'var':
            self.match('var')
            self.declarations()
            self.program2()
        # 1.2.2
        elif self.tok == 'procedure':
            self.match('procedure')
            self.subprogram_declarations
            self.compound_statement
            self.match('.')
        # 1.2.3
        elif self.tok == 'begin':
            self.match('begin')
            self.compound_statement
            self.match('.')
        else:
            self.syntax_error('program1')

    def program2(self):
        # 1.3.1
        if self.tok == 'procedure':
            self.match('procedure')
            self.subprogram_declarations()
            self.compound_statement
            self.match('.')
        # 1.3.2
        elif self.tok == 'begin':
            self.match('begin')
            self.compound_statement()
            self.match('.')
        else:
            self.syntax_error('program2')

    def identifier_list(self):
        # 2.1.1
        if self.tok == 'id':
            self.match('id')
            self.identifier_list1()
        else:
            self.syntax_error('identifier_list')

    def identifier_list1(self):
        # 2.2.1
        if self.tok == ',':
            self.match(',')
            self.identifier_list1()
        # 2.2.2
        elif self.tok == ')':
            pass
            # for epsilon you don't match because the match should happen
            # when checking the next nonterminal
        else:
            self.syntax_error('identifier_list1', True)
            # has epsilon so must check follows as well

    def declarations(self):
        # 3.1.1
        if self.tok == 'var':
            self.match('var')
            self.match('id')
            self.match(':')
            self.type()
            self.match(';')
            self.declarations1()
        else:
            self.syntax_error('declarations')

    def declarations1(self):
        # 3.2.1
        if self.tok == 'var':
            self.match('var')
            self.match('id')
            self.match(':')
            self.type()
            self.match(';')
            self.declarations1()
        # 3.2.2
        elif self.tok == 'begin' or self.tok == 'procedure':
            pass
        else:
            self.syntax_error('declarations1', True)

    def type(self):
        # 4.1.1
        if self.tok == 'integer' or self.tok == 'real':
            self.standard_type()
            # also no matching here since it will be matched at
            # the call of standard_type
        # 4.1.2
        elif self.tok == 'array':
            self.match('array')
            self.match('[')
            self.num() # ??? it can be int or real?
            self.match(']')
            self.match('of')
            self.standard_type()
        else:
            self.syntax_error('type')

    def standard_type(self):
        # 5.1.1
        if self.tok == 'integer':
            self.match('integer')
        # 5.1.2
        elif self.tok == 'real':
            self.match('real')
        else:
            self.syntax_error('standard_type')

    def subprogram_declarations(self):
        # 6.1.1
        if self.tok == 'procedure':
            self.subprogram_declaration()
            self.match(';')
            self.subprogram_declarations1()
        else:
            self.syntax_error('subprogram_declarations')

    def subprogram_declarations1(self):
        # 6.2.1
        if self.tok == 'procedure':
            self.subprogram_declaration()
            self.match(';')
            self.subprogram_declarations1()
        # 6.2.2
        elif self.tok == 'begin':
            pass
        else:
            self.syntax_error('subprogram_declarations1', True)

    def subprogram_declaration(self):
        # 7.1.1
        if self.tok == 'procedure':
            self.subprogram_head()
            self.subprogram_declaration1()
        else:
            self.syntax_error('subprogram_declaration')

    def subprogram_declaration1(self):
        # 7.2.1
        if self.tok == 'var':
            self.declarations()
            self.subprogram_declaration2()
        # 7.2.2
        elif self.tok == 'procedure':
            self.subprogram_declarations()
            self.compound_statement()
        # 7.2.3
        elif self.tok == 'begin':
            self.compound_statement()
        else:
            self.syntax_error('subprogram_declaration1')

    def subprogram_declaration2(self):
        # 7.3.1
        if self.tok == 'procedure':
            self.subprogram_declarations()
            self.compound_statement()
        # 7.3.2
        elif self.tok == 'begin':
            self.compound_statement()
        else:
            self.syntax_error('subprogram_declaration2')

    def subprogram_head(self):
        # 8.1.1
        if self.tok == 'procedure':
            self.match('procedure')
            self.match('id')
            self.subprogram_head1()

    def subprogram_head1(self):
        # 8.2.1
        if self.tok == '(':
            self.arguments()
            self.match(';')
        # 8.2.2
        elif self.tok == ';':
            self.match(';')
        else:
            self.syntax_error('subprogram_head1')

    def arguments(self):
        # 9.1.1
        if self.tok == '(':
            self.match('(')
            self.parameter_list()
            self.match(')')
        else:
            self.syntax_error('arguments')

    def paramter_list(self):
        # 10.1.1
        if self.tok == 'id':
            self.match('id')
            self.match(':')
            self.type()
            self.paramter_list1()
        else:
            self.syntax_error('parameter_list')

    def parameter_list1(self):
        # 10.2.1
        if self.tok == ';':
            self.match(';')
            self.match('id')
            self.match(':')
            self.type()
            self.paramter_list1()
        # 10.2.2
        elif self.tok == ')':
            pass
        else:
            self.syntax_error('parameter_list1', True)

    def compound_statement(self):
        # 11.1.1
        if self.tok == 'begin':
            self.match('begin')
            self.compound_statement1()
        else:
            self.syntax_error('compound_statement')

    def compound_statement1(self):
        # 11.2.1
        check_firsts = [
            'id',
            'call',
            'begin',
            'if',
            'while',
        ]
        if self.tok in check_firsts:
            self.optional_statements()
            self.match('end')
        # 11.2.2
        elif self.tok == 'end':
            self.match('end')

    def optional_statements(self):
        # 12.1.1
        check_firsts = [
            'id',
            'call',
            'begin',
            'if',
            'while',
        ]
        if self.tok in check_firsts:
            self.statement_list()
        else:
            self.syntax_error('statement_list')

    def statement_list(self):
        # 13.1.1
        check_firsts = [
            'id',
            'call',
            'begin',
            'if',
            'while',
        ]
        if self.tok in check_firsts:
            self.statement()
            self.statement_list1()
        else:
            self.syntax_error('statement_list')

    def statement_list1(self):
        # 13.2.1
        if self.tok == ';':
            self.match(';')
            self.statement()
            self.statement_list1()
        # 13.2.2
        elif self.tok == 'end':
            pass
        else:
            self.syntax_error('statement_list1', True)

    def statement(self):
        # 14.1.1
        if self.tok == 'id':
            self.match('id')
            self.variable()
            self.assignop()
            # it can be the different stuff that is assignop like :=
            self.expression()
        # 14.1.2
        elif self.tok == 'call':
            self.match('call')
            self.procedure_statement()
        # 14.1.3
        elif self.tok == 'begin':
            self.match('begin')
            self.compound_statement()
        # 14.1.4
        elif self.tok == 'if':
            self.match('if')
            self.expression()
            self.match('then')
            self.statement()
            self.statement1()
        # 14.1.5
        elif self.tok == 'while':
            self.match('while')
            self.expression()
            self.match('do')
            self.statement()
        else:
            self.syntax_error('statement')

    def statement1(self):
        # 14.2.1
        if self.tok == 'else':
            self.match('else')
            self.statement()
        # 14.2.2
        elif self.tok == 'end' or self.tok == 'else' or self.tok == ';':
            pass
        else:
            self.syntax_error('statement1', True)

    def variable(self):
        # 15.1.1
        if self.tok == 'id':
            self.match('id')
            self.variable1()
        else:
            self.syntax_error('variable')

    def variable1(self):
        # 15.2.1
        if self.tok == '[':
            self.match('[')
            self.expression()
            self.match(']')
        # 15.2.2
        elif self.tok == ':=': # match assignop?
            pass
        else:
            self.syntax_error('variable1', True)

    def procedure_statement(self):
        # 16.1.1
        if self.tok == 'call':
            self.match('call')
            self.match('id')
            self.procedure_statement1()
        else:
            self.syntax_error('procedure_statement')

    def procedure_statement1(self):
        # 16.2.1
        if self.tok == '(':
            self.match('(')
            self.expression_list()
            self.match(')')
        # 16.2.2
        elif self.tok == 'end' or self.tok == 'else' or self.tok == ';':
            pass
        else:
            self.syntax_error('procedure_statement1', True)

    def expression_list(self):
        # 17.1.1
        check_firsts = [
            'id',
            'num',
            '(',
            'not',
            '+',
            '-'
        ]
        if self.tok in check_firsts:
            self.expression()
            self.expression_list1()
        else:
            self.syntax_error('expression_list')

    def expression_list1(self):
        # 17.2.1
        if self.tok == ',':
            self.match(',')
            self.expression()
            self.expression_list1()
        # 17.2.2
        elif self.tok == ')':
            pass
        else:
            self.syntax_error('expression_list1', True)

    def expression(self):
        # 18.1.1
        check_firsts = [
            'id',
            'num',
            '(',
            'not',
            '+',
            '-'
        ]
        if self.tok in check_firsts:
            self.simple_expression()
            self.expression1()
        else:
            self.syntax_error('expression')

    def is_relop(self):
        # <, <>, <=, >, >=, =
        relops = [
            '<',
            '<>',
            '<=',
            '>',
            '>=',
            '='
        ]
        if self.tok in relops:
            self.match(relops[self.tok])
            return True
        return False

    def expression1(self):
        # 18.2.2
        check_follows = [
            ')', 'then', 'do', ']', 'end', 'else', ';', ','
        ]
        if self.is_relop():
            self.simple_expression
        # 18.2.2
        elif self.tok in check_follows:
            pass
        else:
            self.syntax_error('expression1', True)

    def is_sign(self):
        if self.tok == '+':
            self.match('+')
            return True
        elif self.tok == '-':
            self.match('-')
            return True
        return False

    def simple_expression(self):
        # 19.1.1
        check_firsts = [
            'id',
            'num',
            '(',
            'not'
        ]
        if self.tok in check_firsts:
            self.term()
            self.simple_expression1()
        # 19.1.2
        elif self.is_sign():
            self.term()
            self.simple_expression1()
        else:
            self.syntax_error('simple_expression')

    def is_addop(self):
        addops = ['+', '-', 'or']
        if self.tok in addops:
            self.match(addops[self.tok])
            return True
        return False

    def simple_expression1(self):
        # 19.2.1
        check_follows = [
            relop, ')', 'then', 'do', ']', 'end', 'else', ';', ','
        ]
        if self.is_addop:
            self.term()
            self.simple_expression1()
        # 19.2.2
        elif self.tok in check_follows:
            pass
        else:
            self.syntax_error('simple_expression1')

    def simple_expression1(self):
        # 19.2.1
        check_follows = [
            relop, ')', 'then', 'do', ']', 'end', 'else', ';', ','
        ]
        if self.is_addop:
            self.term()
            self.simple_expression1()
        # 19.2.2
        elif self.tok in check_follows:
            pass
        else:
            self.syntax_error('simple_expression1')

