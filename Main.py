from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
from parse_table import TableGenerator

# project 1: run lexical analyzer and create token file
print '...Starting Lexical Analyzer'
lex = LexicalAnalyzer()
lex.process_file()
print 'Lexical Analyzer has finished running.\n'

# # project 2: create parse table
# print '...Starting Parse Table generator'
# tbl = TableGenerator()
# tbl.generate_parse_table()
# print 'Parse Table created.\n'

# project 2: run syntax analyzer
print '...Starting Syntax Analyzer'
symbol_table = lex.get_symbol_table()
syn = SyntaxAnalyzer(symbol_table)
print 'Syntax Analyzer has finished running.\n'
