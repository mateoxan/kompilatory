bin_op = ['\|\|', '&&', '<<', '>>']
arith_op = ['*', '/', '+', '-']
comp_op = ['<', '>', '==', '!=', '<=', '>=']


class Ttype(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self[key] = type(self)()
            return value


ttype = Ttype()

for op in bin_op + arith_op + ["%"]:
    ttype[op]['int']['int'] = 'int'

for op in arith_op:
    ttype[op]['float']['float'] = 'float'
    ttype[op]['float']['int'] = 'float'

for op in comp_op:
    ttype[op]['int']['int'] = 'int'
    ttype[op]['float']['float'] = 'int'
    ttype[op]['string']['string'] = 'int'

ttype["*"]['int']['float'] = 'float'
ttype["*"]['float']['int'] = 'float'

ttype['=']['int']['int'] = 'int'
ttype['=']['float']['float'] = 'float'
ttype['=']['string']['string'] = 'string'
ttype['=']['float']['int'] = 'float'

ttype['+']['string']['string'] = 'string'
ttype['*']['string']['int'] = 'string'