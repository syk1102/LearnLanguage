
class SyntaxAnalyzer:
    def __init__(self, lex_symbol_table):
        self.symbol_table = lex_symbol_table
        self.attribute_dict = {}
        self.name_symbol_dict = {}
        self.token_list = []
        self.parse_table = []
        self.nonterminal_list = []
        self.follows_list = []

        # *, /, div, mod, and
        self.mulops = [
            'MULT',
            'DIVIDE',
            'DIV',
            'MOD',
            'AND',
        ]

        # <, <>, <=, >, >=, =
        self.relops = [
            'LESS',
            'NOTEQUAL',
            'LEQUAL',
            'GREATER',
            'GEQUAL',
            'EQUAL'
        ]

        # +, -, or
        self.addops = [
            'PLUS',
            'MINUS',
            'OR'
        ]

        # :=
        self.assignops = [
            ':='
        ]

        self.tok = None
        self.index = 0

        self.set_attribute_dict()
        self.read_name_to_symbol()
        self.generate_parsetable()

    def set_attribute_dict(self):
        # attribute values of keywords
        keywords_file = open('Input/Keywords.txt', 'r')
        for line in keywords_file:
            line_split = line.split()
            attribute_name = line_split[0]
            attribute_value = int(line_split[1])
            self.attribute_dict.update({attribute_name : attribute_value})

        # attribute values of non-keyword(RELOP, ADDOP, etc.) tokens
        token_info_file = open('Input/AttributeList.txt', 'r')
        for line in token_info_file:
            line_split = line.split()
            attribute_name = line_split[0]
            attribute_value = int(line_split[1])
            self.attribute_dict.update({attribute_name : attribute_value})

        # ASSIGNOP and other misc reserved characters
        self.attribute_dict.update({'ASSIGNOP' : 60})
        self.attribute_dict.update({'OPENPAREN' : 61})
        self.attribute_dict.update({'CLOSEDPAREN' : 62})
        self.attribute_dict.update({'SEMICOLON' : 63})
        self.attribute_dict.update({'COMMA' : 64})
        self.attribute_dict.update({'OPENBRACK' : 65})
        self.attribute_dict.update({'CLOSEDBRACK' : 66})
        self.attribute_dict.update({'DOT' : 67})
        self.attribute_dict.update({'DOUBLEDOT' : 68})
        self.attribute_dict.update({'COLON' : 69})

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

    def get_token_lexeme(self):
        return self.tok.keys()[0]

    def get_token_type(self):
        return self.tok.values()[0][0]

    def get_token_attribute(self):
        return self.tok.values()[0][1]

    def check_token(self, expected):
        # checks multiple expected items
        checked = False
        if 'num' in expected:
            if self.get_token_type() == 'INT':
                return True
            elif self.get_token_type() == 'REAL':
                return True
        for item in expected:
            checked = (self.get_token_attribute() == self.attribute_dict[item])
            if checked: # short-circuited
                return checked
        return checked # only time it is returned here, checked should be False

    def read_token_table(self):
        token_file = open('Output/token.txt', 'r')
        token_file.readline()
        for line in token_file:
            line_split = line.split()
            self.token_list.append({line_split[1] : [line_split[2], line_split[3]]})

    def read_name_to_symbol(self):
        txt_file = open('Input/NameToSymbol.txt', 'r')
        for line in txt_file:
            line_split = line.split()
            self.name_symbol_dict[line_split[0]] = line_split[1]

    def syntax_error(self, nonterminal, epsilon=False, symbols_expected=[]):
        expected_string = ''
        if nonterminal in ['match_err']:
            # sent from match error where the symbols_expected already provided
            expected_string = ', '.join(symbols_expected)
        else:
            # sent from nonterminal where the symbols_expected not provided
            ind = self.nonterminal_list.index(nonterminal)
            expected_list = self.create_expected_list(ind, epsilon)
            expected_string = ', '.join(expected_list)
        err_msg = 'SYNERR: Expected {0} got {1}'.format(
            expected_string, self.get_token_lexeme())
        # sync token
        sync_set = self.parse_table[ind]['follows']
        sync_set.append('$')
        if self.tok not in sync_set:
            while self.tok not in sync_set:
                self.get_token()
            self.index -= 1

    def parse(self):
        self.get_token()
        self.program()
        self.match('$')

    def match(self, expected):
        symbols_expected = []
        for name in expected:
            symbol = self.name_symbol_dict[name]
            symbols_expected.append(symbol)
        if (self.get_token_lexeme() in symbols_expected and
            '$' in symbols_expected):
            return print '!!! Syntax Analyzer Completed !!!'
        elif '$' not in symbols_expected:
            if 'num' in symbols_expected:
                if self.get_token_type in ['INT', 'REAL']: # longreal?
                    self.get_token()
                    return print '---Getting next token---'
                else:
                    return self.syntax_error(
                        'match_err',
                        False,
                        ['INT', 'REAL']
                    )
            # elif expected == 'ADDOP':
            #     if self.get_token_type in self.addops:
            #         self.get_token()
            #     else:
            #         self.syntax_error('misc', False, self.addops)
            # elif expected == 'MULOP':
            #     if self.get_token_type in self.mulops:
            #         self.get_token()
            #     else:
            #         self.syntax_error('misc', False, self.mulops)
            # elif expected == 'RELOP':
            #     if self.get_token_type in self.relops:
            #         self.get_token()
            #     else:
            #         self.syntax_error('misc', False, self.relops)
            # elif expected == 'ASSIGNOP':
            #     if self.get_token_type in self.relops:
            #         self.get_token()
            #     else:
            #         self.syntax_error('misc', False, self.assignops)
            elif self.get_token_lexeme() in symbols_expected:
                # not expecting EOF is obvious if inside this clause
                self.get_token()
                return print '---Getting next token---'

            self.syntax_error('match_err', False, err_msg)
            self.get_token()

    def program(self):
        # 1.1.1
        if self.check_token(['program']):
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
        if self.check_token(['var']):
            self.match('var')
            self.declarations()
            self.program2()
        # 1.2.2
        elif self.check_token(['procedure']):
            self.match('procedure')
            self.subprogram_declarations
            self.compound_statement
            self.match('.')
        # 1.2.3
        elif self.check_token(['begin']):
            self.match('begin')
            self.compound_statement
            self.match('.')
        else:
            self.syntax_error('program1')

    def program2(self):
        # 1.3.1
        if self.check_token(['procedure']):
            self.match('procedure')
            self.subprogram_declarations()
            self.compound_statement
            self.match('.')
        # 1.3.2
        elif self.check_token(['begin']):
            self.match('begin')
            self.compound_statement()
            self.match('.')
        else:
            self.syntax_error('program2')

    def identifier_list(self):
        # 2.1.1
        if self.check_token(['id']):
            self.match('id')
            self.identifier_list1()
        else:
            self.syntax_error('identifier_list')

    def identifier_list1(self):
        # 2.2.1
        if self.check_token(['COMMA']):
            self.match(',')
            self.identifier_list1()
        # 2.2.2
        elif self.check_token(['CLOSEDPAREN']):
            pass
            # for epsilon you don't match because the match should happen
            # when checking the next nonterminal
        else:
            self.syntax_error('identifier_list1', True)
            # has epsilon so must check follows as well in expected

    def declarations(self):
        # 3.1.1
        if self.check_token(['var']):
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
        if self.check_token(['var']):
            self.match('var')
            self.match('id')
            self.match(':')
            self.type()
            self.match(';')
            self.declarations1()
        # 3.2.2
        elif self.check_token(['begin', 'procedure']):
            pass
        else:
            self.syntax_error('declarations1', True)

    def type(self):
        # 4.1.1
        if self.check_token(['integer', 'real']):
            self.standard_type()
            # also no matching here since it will be matched at
            # the call of standard_type
        # 4.1.2
        elif self.check_token(['array']):
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
        if self.check_token(['integer']):
            self.match('integer')
        # 5.1.2
        elif self.check_token(['real']):
            self.match('real')
        else:
            self.syntax_error('standard_type')

    def subprogram_declarations(self):
        # 6.1.1
        if self.check_token(['procedure']):
            self.subprogram_declaration()
            self.match(';')
            self.subprogram_declarations1()
        else:
            self.syntax_error('subprogram_declarations')

    def subprogram_declarations1(self):
        # 6.2.1
        if self.check_token(['procedure']):
            self.subprogram_declaration()
            self.match(';')
            self.subprogram_declarations1()
        # 6.2.2
        elif self.check_token(['begin']):
            pass
        else:
            self.syntax_error('subprogram_declarations1', True)

    def subprogram_declaration(self):
        # 7.1.1
        if self.check_token(['procedure']):
            self.subprogram_head()
            self.subprogram_declaration1()
        else:
            self.syntax_error('subprogram_declaration')

    def subprogram_declaration1(self):
        # 7.2.1
        if self.check_token(['var']):
            self.declarations()
            self.subprogram_declaration2()
        # 7.2.2
        elif self.check_token(['procedure']):
            self.subprogram_declarations()
            self.compound_statement()
        # 7.2.3
        elif self.check_token(['begin']):
            self.compound_statement()
        else:
            self.syntax_error('subprogram_declaration1')

    def subprogram_declaration2(self):
        # 7.3.1
        if self.check_token(['procedure']):
            self.subprogram_declarations()
            self.compound_statement()
        # 7.3.2
        elif self.check_token(['begin']):
            self.compound_statement()
        else:
            self.syntax_error('subprogram_declaration2')

    def subprogram_head(self):
        # 8.1.1
        if self.check_token(['procedure']):
            self.match('procedure')
            self.match('id')
            self.subprogram_head1()
        else:
            self.syntax_error('subprogram_head')

    def subprogram_head1(self):
        # 8.2.1
        if self.check_token(['(']):
            self.arguments()
            self.match(';')
        # 8.2.2
        elif self.check_token([';']):
            self.match(';')
        else:
            self.syntax_error('subprogram_head1')

    def arguments(self):
        # 9.1.1
        if self.check_token(['(']):
            self.match('(')
            self.parameter_list()
            self.match(')')
        else:
            self.syntax_error('arguments')

    def paramter_list(self):
        # 10.1.1
        if self.check_token(['id']):
            self.match('id')
            self.match(':')
            self.type()
            self.paramter_list1()
        else:
            self.syntax_error('parameter_list')

    def parameter_list1(self):
        # 10.2.1
        if self.check_token([';']):
            self.match(';')
            self.match('id')
            self.match(':')
            self.type()
            self.paramter_list1()
        # 10.2.2
        elif self.check_token([')']):
            pass
        else:
            self.syntax_error('parameter_list1', True)

    def compound_statement(self):
        # 11.1.1
        if self.check_token(['begin']):
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
        if self.check_token(check_firsts):
            self.optional_statements()
            self.match('end')
        # 11.2.2
        elif self.check_token(['end']):
            self.match('end')
        else:
            self.syntax_error('compound_statement1')

    def optional_statements(self):
        # 12.1.1
        check_firsts = [
            'id',
            'call',
            'begin',
            'if',
            'while',
        ]
        if self.check_token(check_firsts):
            self.statement_list()
        else:
            self.syntax_error('optional_statements')

    def statement_list(self):
        # 13.1.1
        check_firsts = [
            'id',
            'call',
            'begin',
            'if',
            'while',
        ]
        if self.check_token(check_firsts):
            self.statement()
            self.statement_list1()
        else:
            self.syntax_error('statement_list')

    def statement_list1(self):
        # 13.2.1
        if self.check_token(['SEMICOLON']):
            self.match(';')
            self.statement()
            self.statement_list1()
        # 13.2.2
        elif self.check_token(['end']):
            pass
        else:
            self.syntax_error('statement_list1', True)

    def statement(self):
        # 14.1.1
        if self.check_token(['id']):
            self.match('id')
            self.variable()
            self.match('ASSIGNOP')
            # it can be the different stuff that is assignop like :=
            self.expression()
        # 14.1.2
        elif self.check_token(['call']):
            self.match('call')
            self.procedure_statement()
        # 14.1.3
        elif self.check_token(['begin']):
            self.match('begin')
            self.compound_statement()
        # 14.1.4
        elif self.check_token(['if']):
            self.match('if')
            self.expression()
            self.match('then')
            self.statement()
            self.statement1()
        # 14.1.5
        elif self.check_token(['while']):
            self.match('while')
            self.expression()
            self.match('do')
            self.statement()
        else:
            self.syntax_error('statement')

    def statement1(self):
        # 14.2.1
        if self.check_token(['else']):
            self.match('else')
            self.statement()
        # 14.2.2
        elif self.check_token(['end', 'else', 'SEMICOLON']):
            pass
        else:
            self.syntax_error('statement1', True)

    def variable(self):
        # 15.1.1
        if self.check_token(['id']):
            self.match('id')
            self.variable1()
        else:
            self.syntax_error('variable')

    def variable1(self):
        # 15.2.1
        if self.check_token(['OPENBRACK']):
            self.match('[')
            self.expression()
            self.match(']')
        # 15.2.2
        elif self.check_token(['ASSIGNOP']):
            pass
        else:
            self.syntax_error('variable1', True)

    def procedure_statement(self):
        # 16.1.1
        if self.check_token(['call']):
            self.match('call')
            self.match('id')
            self.procedure_statement1()
        else:
            self.syntax_error('procedure_statement')

    def procedure_statement1(self):
        # 16.2.1
        if self.check_token(['OPENPAREN']):
            self.match('(')
            self.expression_list()
            self.match(')')
        # 16.2.2
        elif self.check_token(['end', 'else', 'SEMICOLON']):
            pass
        else:
            self.syntax_error('procedure_statement1', True)

    def expression_list(self):
        # 17.1.1
        check_firsts = [
            'id',
            'num',
            'OPENPAREN',
            'not',
            'PLUS',
            'MINUS'
        ]
        if self.check_token(check_firsts):
            self.match(check_firsts)
            self.expression()
            self.expression_list1()
        else:
            self.syntax_error('expression_list')

    def expression_list1(self):
        # 17.2.1
        if self.check_token(['COMMA']):
            self.match(',')
            self.expression()
            self.expression_list1()
        # 17.2.2
        elif self.check_token(['CLOSEDPAREN']):
            pass
        else:
            self.syntax_error('expression_list1', True)

    def expression(self):
        # 18.1.1
        check_firsts = [
            'id',
            'num',
            'OPENPAREN',
            'not',
            'PLUS',
            'MINUS'
        ]
        if self.check_token(check_firsts):
            self.simple_expression()
            self.expression1()
        else:
            self.syntax_error('expression')

    def expression1(self):
        check_follows = [
            'CLOSEDPAREN',
            'then',
            'do',
            'CLOSEDBRACK',
            'end',
            'else',
            'SEMICOLON',
            'COMMA'
        ]
        # 18.2.1
        if self.check_token(self.relops):
            self.match('RELOP')
            self.simple_expression
        # 18.2.2
        elif self.check_token(check_follows):
            pass
        else:
            self.syntax_error('expression1', True)

    def is_sign(self):
        if self.check_token(['PLUS']):
            self.match('+')
            return True
        elif self.check_token(['MINUS']):
            self.match('-')
            return True
        return False

    def simple_expression(self):
        # 19.1.1
        check_firsts = [
            'id',
            'num',
            'OPENPAREN',
            'not'
        ]
        if self.check_token(check_firsts):
            self.term()
            self.simple_expression1()
        # 19.1.2
        elif self.is_sign():
            self.term()
            self.simple_expression1()
        else:
            self.syntax_error('simple_expression')

    def simple_expression1(self):
        check_follows = [
            'OPENPAREN',
            'then',
            'do',
            'OPENBRACK',
            'end',
            'else',
            'SEMICOLON',
            'COMMA'
        ]
        check_follows.extend(self.relop)
        # 19.2.1
        if self.check_token(self.addops):
            self.match('ADDOP')
            self.term()
            self.simple_expression1()
        # 19.2.2
        elif self.check_token(check_follows):
            pass
        else:
            self.syntax_error('simple_expression1', True)

    def term(self):
        # 20.1.1
        check_firsts = [
            'id',
            'num',
            'OPENPAREN',
            'not'
        ]
        if self.check_token(check_firsts):
            self.factor
            self.term1
        else:
            self.syntax_error('term')

    def term1(self):
        check_follows = [
            'CLOSEDPAREN',
            'then',
            'do',
            'CLOSEDBRACK',
            'end',
            'else',
            'SEMICOLON',
            'COMMA'
        ]
        check_follows.extend(self.relops)
        check_follows.extend(self.addops)
        # 20.2.1
        if self.check_token(self.mulops):
            self.match('MULOPS')
            self.factor()
            self.term1()
        # 20.2.2
        elif self.check_token(check_follows):
            pass
        else:
            self.syntax_error('term1', True)

    def factor(self):
        # 21.1.1
        if self.check_token(['id']):
            self.match('id')
            self.factor1()
        # 21.1.2
        elif self.check_token('num'): #TODO: check is num
            self.match('num')
        # 21.1.3
        elif self.check_token(['OPENPAREN']):
            self.match('(')
            self.expression()
            self.match(')')
        # 21.1.4
        elif self.check_token(['not']):
            self.match('not')
            self.factor()
        else:
            self.syntax_error('factor')

    def factor1(self):
        check_follows = [
            'CLOSEDPAREN',
            'then',
            'do',
            'CLOSEDBRACK',
            'end',
            'else',
            'SEMICOLON',
            'COMMA'
        ]
        check_follows.extend(self.mulops)
        check_follows.extend(self.addops)
        check_follows.extend(self.relops)
        # 21.2.1
        if self.check_token(['OPENBRACK']):
            self.match('[')
            self.expression()
            self.match(']')
        # 21.2.2
        elif self.check_token(check_follows):
            pass
        else:
            self.syntax_error('factor1', True)

    def sign(self):
        # 22.1.1
        if self.check_token('PLUS'):
            self.match('+')
        # 22.1.2
        elif self.check_token('MINUS'):
            self.match('-')
        else:
            self.syntax_error('sign')
