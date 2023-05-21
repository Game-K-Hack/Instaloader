import requests

class progress_bar():
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.length = 50
        self.pattern = '[=.]%'

    def format(self, format=None, side=None, full=None, empty=None, percent=True):
        if format is not None and side is None and full is None and empty is None:
            self.pattern = format
        elif format is None and side is not None and full is not None and empty is not None:
            if len(side) != 2:
                raise ValueError("Error: side is not equal to 2, but is equal to " + str(len(side)))
            self.pattern = f"{side[0]}{full}{empty}{side[0]}{'%' if percent else ''}"
        else:
            raise ValueError("Invalid arguments")

    def update(self):
        self.current += 1
        # Val to percent
        valp = round(100*self.current/self.total, 1)
        # Val to format bar
        valb = round(self.length*self.current/self.total)
        # Patern
        try: b = f"{self.pattern[0]}{self.pattern[1]*int(valb)}{self.pattern[2]*int(self.length-valb)}{self.pattern[3]}"
        except: pass
        p = f"{' '*(5-len(str(valp)))}{valp}%"
        # Return
        if len(self.pattern) == 5: return f'{b} {p}'
        elif len(self.pattern) == 4 and '%' not in self.pattern: return b
        elif '%' == self.pattern: return p
        else: raise ValueError("Invalid pattern")

def download(url:str, filename:str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
