from string_with_arrows import *

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
        result += '\n\n' + string_with_arrows(self.posn_start.ftxt, self.posn_start, self.posn_end)
        return result
    

class IllegalCharError(Error):
    def __init__(self,posn_start, posn_end, details):
        super().__init__(posn_start, posn_end,"Illegal character ", details)


class InvalidSyntaxError(Error):
    def __init__(self,posn_start, posn_end, details):
        super().__init__(posn_start, posn_end,"Invalid Syntax ", details)

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

    def advance(self, current_char=None):
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
TT_EOF      =   'EOF'

class Token:
    def __init__(self,type_, value=None, posn_start=None, posn_end=None):
        self.type = type_
        self.value = value

        if posn_start:
            self.posn_start = posn_start.copy()
            self.posn_end = posn_start.copy()
            self.posn_end.advance()
        if posn_end:
            self.posn_end = posn_end

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
                tokens.append(Token(TT_PLUS, posn_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, posn_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, posn_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, posn_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, posn_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, posn_start=self.pos))
                self.advance()
            else:
                posn_start = self.pos.copy()
                char =  self.current_char
                self.advance()
                return [], IllegalCharError(posn_start, self.pos , "'"+ char+ "'")
        tokens.append(Token(TT_EOF, posn_start=self.pos))
        return tokens, None
    
    def make_number(self):
        num_str = ''
        dot_count = 0
        posn_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str +=  self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), posn_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), posn_start, self.pos)
            
# =================================
#               NODES
# =================================

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


# =================================
#               PARSER
# =================================

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        
        return res


    def success(self,node ):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

# =================================
#               PARSER
# =================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.tok_index = -1 
        self.advance() 

    def advance(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_tok = self.tokens[self.tok_index]
        
        return self.current_tok
    
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.posn_start, self.current_tok.posn_end, "Expected + - * / something like this!"))
        return res

# =====================================================================================================================================================================
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        elif tok.type ==TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)  
        else:
            return res.failure(InvalidSyntaxError(
                self.current_tok.posn_start, self.current_tok.posn_end, "Expected ')'"
            ))

        
        return res.failure(InvalidSyntaxError(tok.posn_start, tok.posn_end, "Expected Int or Float"))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
# =====================================================================================================================================================================


    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
    



# =================================
#               RUN
# ================================= 

def run(fn, text):    
    # For generating tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    # return tokens, error
    if error: return None, error

    # For generating AST
    # (Abstract Syntax Tree)
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error