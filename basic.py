
# =================================
#               CONSTANTS
# =================================

DIGITS  = '0123456789'

# =================================
#               ERRORS
# =================================

class Error:
    def __init__(self, posn_start, posn_end, error_name, details):
        self.posn_start = posn_start
        self.posn_end = posn_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        red = '\033[91m'  
        cyan = '\033[36m' 
        reset = '\033[0m' 

        # result = f'{self.error_name}: {self.details} \n'
        # result += f'File {self.posn_start.fn} Line {self.posn_start.line + 1}'
        result = f'{red}{self.error_name}: {self.details}{reset}\n'
        result += f'{cyan}File {self.posn_start.fn} Line {self.posn_start.line + 1}{reset}'
        return result
    

class IllegalCharError(Error):
    def __init__(self,posn_start, posn_end, details):
        super().__init__(posn_start, posn_end,"Illegal character!", details)

# =================================
#               POSITIONS
# =================================

class Position:
    def __init__(self, index, line, col, fn, ftxt): # fn -> file name ; ftxt -> file txt
            self.index = index
            self.line = line
            self.col = col
            self.fn = fn
            self.ftxt = ftxt

    def advance(self, current_char):
        self.index += 1
        self.col += 1

        if current_char == '\n':
            self.line += 1
            self.col = 0

            return self
    
    def copy(self):
        return Position(self.index, self.line, self.col, self.fn, self.ftxt )
    

# =================================
#               TOKENS
# =================================

TT_INT       =   "INT"   # The "TT" before the name is shorthand for "token type"
TT_FLOAT     =   "FLOAT"
TT_PLUS     =   "PLUS"
TT_MINUS    =   "MINUS"
TT_MUL      =   "MUL"
TT_DIV      =   'DIV'
TT_LPAREN   =   'LPAREN'
TT_RPAREN   =   "RPAREN"

class Token:
    def __init__(self,type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f"{self.type} : {self.value}"
        return f"{self.type}"
    
# =================================
#               LEXER
# =================================

class Lexer:
    def __init__(self,fn, text):
        self.fn = fn
        self.text = text 
        self.pos = Position(-1,0,-1, fn , text)
        # to ensure proper behavior when the advance() method is called for the first time.
        # since the advance() method increments the pos before setting the current char, by setting the pos at -1 the first call will set the posn to 0 i.e. pointing to the first character of the input string 
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    
    def make_tokens(self):
        tokens = []

        while self.current_char != None :
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                posn_start = self.pos.copy()
                char =  self.current_char
                self.advance()
                return [], IllegalCharError(posn_start, self.pos , "'"+ char+ "'")
            
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str +=  self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
            
# =================================
#               RUN
# =================================

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

