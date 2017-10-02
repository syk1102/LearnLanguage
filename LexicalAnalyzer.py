from MachineSupervisor import *
__author__ = 'Se Yeon'


class LexicalAnalyzer:
    def __init__(self):
        self.source_string = None
        self.line_num = None

        self.listing_file = open('Output/listing.txt', 'w')
        #self.listing_file.write("{0:<5} {1:<70} {2:<15}\n")

        self.token_file = open('Output/token.txt', 'w')
        self.token_file.write("{0:<10} {1:<15} {2:<15} {3:<20}\n"
                              .format('Line No.', 'Lexeme', 'Token-Type', 'Attribute'))

        self.reserved_words = {}
        self.symbol_table = {}
        self.token_table = {}
        self.attribute_table = {}

        self.read_inputs()

    def process_file(self):
        source_file = open('Input/worstcase2.p', 'r')
        self.line_num = 1

        for line in source_file:
            self.source_string = line

            self.listing_file.write("{0:<5} {1:<70}\n".format(self.line_num, line[:-1]))
            #self.listing_file.write("{0:<5} {1:<70} {2:<15}\n".format(self.line_num, line, None))

            MachineSupervisor(self)
            # new_supervisor.start_machine()

            self.line_num += 1

        self.generate_eof_token()
        source_file.close()
        self.listing_file.close()
        self.token_file.close()

    def read_inputs(self):
        # Add all the keywords in reserved words list
        keywords = open('Input/Keywords.txt', 'r')
        for line in keywords:
            lhs, rhs = line[:-1].split(" ")
            self.reserved_words[lhs] = rhs
            # Add the keyword without the newline symbol
            # self.reserved_words.append(line[:-1])

        attributes = open('Input/AttributeList.txt', 'r')
        for line in attributes:
            lhs, rhs = line[:-1].split(" ")
            self.attribute_table[lhs] = rhs

    def generate_eof_token(self):
        self.listing_file.write("{0:<5} {1:<70}\n".format(self.line_num, '$'))
        self.token_file.write("{0:<10} {1:<15} {2:<15} {3:<20}\n".format(self.line_num, '$', 'EOF', 0))
