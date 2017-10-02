class MachineSupervisor:
    def __init__(self, lexical_analyzer):
        self.supervisor = lexical_analyzer
        self.source_string = lexical_analyzer.sourceString

        self.end = len(self.source_string)
        self.frontP = 0
        self.backP = 0

        self.found = None
        self.nth = None

        self.machineList = [
            self.ws_machine(),
            self.addop_machine(),
            self.mulop_machine(),
            self.id_machine(),
            self.longreal_machine(),
            self.real_machine(),
            self.int_machine(),
            self.relop_machine(),
            self.catchall_machine()
        ]

    def start_machine(self):
        self.source_string = lexical_analyzer.sourceString
        while not(self.backP == self.end):
            self.run_machines()
            self.backP = self.frontP

    def reset(self):
        self.frontP = self.backP

    def run_machines(self):
        self.nth = 0
        self.found = False
        while not self.found:
            self.reset()
            self.found = self.machineList[self.nth]
            self.nth += 1


    def ws_machine(self):
        if self.source_string[self.frontP] == '\n' \
                or self.source_string[self.frontP] == '\t' \
                or self.source_string[self.frontP] == ' ':
            self.frontP += 1
            while self.frontP < self.end:
                if self.source_string[self.frontP] == '\n' \
                        or self.source_string[self.frontP] == '\t' \
                        or self.source_string[self.frontP] == ' ':
                    self.frontP += 1
                else:
                    return True
            return True
        else:
            return False

    def addop_machine(self):
        if self.source_string[self.frontP] == '+':
            self.frontP += 1
            addToken(RELOP, PLUS)
            return True
        elif self.source_string[self.frontP] == '-':
            self.frontP += 1
            addToken(RELOP, MINUS)
            return True
        elif self.sourceString[self.frontP] == 'o':
            self.frontP += 1
            if self.sourceString[self.frontP] == 'r':
                self.frontP += 1
                addToken(RELOP, OR)
                return True
        return False