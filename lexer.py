"""
This is a tokenizer
"""
class Lexer:
    
    def __init__( self, data ):
        self.data = data
        self.begin = 0
        self.forward = 0
        self.length = len( data )
    
    def getToken( self ):
        for index in range( self.begin, self.length ):
            if self.data[ index ] != '<':
                self.forward += 1
            else:
                break
        for index in range( self.forward, self.length ):
            if self.data[ index ] != '>':
                self.forward += 1
            else:
                break
        
        token = self.data[ self.begin : self.forward + 1 ].strip()
        self.begin = self.forward + 1
        self.forward = self.begin
        if self.begin < self.length:
            return ( token, True )
        else:
            return ( token, False )
