import sys
import os.path

class dict_writer:

    def __init__(self, dictionary = {}, file = "dict.txt"):
        self.vars = dictionary
        self.filename = file
        self.does_exist = os.path.exists(self.filename)

    def generate_file(self, dictionary = None):
        """
        Writes the current value of self.vars to the file specified by self.filename.
        If a custom dictionary is supplied by using the keyword argument "dictionary," then 
        the specified dictionary will be written instead.
        """
        if dictionary == None: dictionary = self.vars
        with open (self.filename, 'w') as f:
            for keys in dictionary.keys():
                f.write(str(keys) + " = " + str(dictionary.get(keys)) + "\n")

    def read_file(self, sanity = True):
        """
        Reads the file specified by self.filename (defined at initalization) and returns the contents of the file as a dictionary.
        If sanity checking is turned off with the use of the keyword argument "sanity = false" keys in the file will not 
        be checked against the dictionary supplied at initialization.
        """
        _dict = {}
        with open (self.filename, 'r') as f:
            for line in enumerate(f):
                value = line[1].strip()
                if value.find("=") < 0 and not value == "":
                    sys.stderr.write("Missing '=' in "+self.filename+" on line " + str(line[0] + 1) + ". Cancelling read.\n")
                    return
                else: valIndex = value.find("=")
                key = value[0:valIndex].strip()
                value = value[valIndex + 1:].strip()
                hasQuote = False
                if '"' in value and sanity:
                    hasQuote = True
                    value = self._parse_quote(value, '"', str(line[0] + 1), sanity = sanity)
                if "'" in value and sanity:
                    hasQuote = True
                    value = self._parse_quote(value, "'", str(line[0] + 1), sanity = sanity)
                if not hasQuote: value = value.replace(" ", "")
                if self.vars.get(key) == None and not sanity:
                    sys.stderr.write('\nInvalid key assignment in '+self.filename+' on line '+str(line[0] + 1)+'.\n'+
                    "Ignoring line "+str(line[0] + 1)+'.\n\n')
                else:
                    _dict.update({key: value})
        return _dict
    
    def get_dict(self): 
        """Returns self.vars"""
        return self.vars

    def get_key(self, lineNum):
        """
        Returns the key at the specified line number (lineNum) in self.filename.
        If the line does not contain an entry, returns None
        """
        with open(self.filename, 'r') as f:
            for i in range(lineNum):
                f.readline()
            line = f.readline().strip()
            if line.find("=") < 0 and not line == "":
                sys.stderr.write("Missing '=' in "+self.filename+" on line " + str(lineNum + 1) + ".")
                return None
            else: valIndex = line.find("=")
            key = line[:valIndex - 1]
            return key
    
    def get_val_from_line(self, lineNum):
        """
        Returns the value at the specified line number (lineNum) in self.filename.
        If the line does not contain an entry, returns None
        """
        with open(self.filename, 'r') as f:
            for i in range(lineNum):
                f.readline()
            line = f.readline().strip()
            if line == "": return None
            if line.find("=") < 0:
                sys.stderr.write("Missing '=' in "+self.filename+" on line " + str(lineNum + 1) + ".")
                return None
            else: valIndex = line.find("=")
            value = line[valIndex + 1:].strip()
            return value

    def get_definition(self, key):
        """
        Searches the dictionary contained by the file at self.filename for the given key and returns it's definition.\n
        If none is found, returns None
        """
        lineNum = self._get_line(key)
        if lineNum == -2:
            return None
        with open(self.filename, 'r') as f:
            for i in range(lineNum):
                f.readline()
            line = f.readline()
            value = line.strip()
            if value.find("=") < 0:
                sys.stderr.write("Missing '=' in "+self.filename+" on line " + str(lineNum + 1) + ". Continuing read after key.")
                valIndex = len(key) + 1
            else: valIndex = value.find("=")
            value = value[valIndex + 1:].strip()
            hasQuote = False
            if '"' in value:
                hasQuote = True
                value = self._parse_quote(value, '"', str(line[0] + 1))
            if "'" in value:
                hasQuote = True
                value = self._parse_quote(value, "'", str(line[0] + 1))
            if not hasQuote: value = value.replace(" ", "")
            return value
    
    def update_value(self, _dict):
        """
        Takes a dictionary as it's argument and updates the dictionary contained by the file at self.filename.
        Does not update self.vars.
        """
        tmp = self.read_file()
        tmp.update(_dict)
        self.generate_file(dictionary=tmp)

    def get_length(self):
        """
        Returns the number of lines in self.filename
        """
        numLines = 0
        with open (self.filename, 'r') as f:
            curLine = f.readline()
            while curLine != "":
                curLine = f.readline()
                numLines += 1
        return numLines
    
    def _parse_quote(self, readStr, char, lineNum):
        """
        Internal class use only
        Ensures that readStr has only one pair of quotes and that they are used correctly
        """
        if len(readStr.strip()[:readStr.find(char)]) > 1:
            sys.stderr.write('\nValue in '+self.filename+' on line '+lineNum+' contains a quote (" '+char+' ") but does not begin with it.\n' +
            'If whitespace is needed within the value please begin and end value with a quote (" '+char+' ") character.\n'+
            "Ignoring quotes on line "+lineNum+".\n\n")
            return readStr.replace(char, "").strip()
        else:
            tmpStr = readStr[readStr.find(char) + 1:]
            if tmpStr.find(char) < 0:
                sys.stderr.write('\nValue in '+self.filename+' on line '+lineNum+' does not contain a corresponding quote (" '+char+' ").\n'
                "Ignoring quotes on line "+lineNum+".\n\n")
                return readStr.replace(char, "").strip()
            if len(tmpStr[tmpStr.find(char) + 1:]) > 0:
                sys.stderr.write('\nValue in '+self.filename+' on line '+lineNum+' continues after second quote (" '+char+' ").\n'+
                "Ignoring extraneous text on line "+lineNum+".\n\n")
                return tmpStr[:tmpStr.find(char)].strip()
        #this should be unreachable, but is here just in case
        return readStr

    def _get_line(self, key):
        """
        Internal class use only
        Returns the line number in the self.filename of the given key.\n
        If no key is found, returns -2
        """
        with open(self.filename, 'r') as f:
            for i,line in enumerate(f):
                value = line.strip()
                if value.find("=") < 0:
                    sys.stderr.write("Missing '=' in "+str(self.filename)+" on line " + str(i) + ". Continuing read after key.")
                    valIndex = len(key) + 1
                else: valIndex = value.find("=")
                match = value[0:valIndex].strip()
                if key == match:
                    return i
            return -2
#
"""
stats = dict_writer(file = "usage_stats.txt")
_max = [0, 0]
for i in range(0, stats.get_length()):
    tmp = int(stats.get_val_from_line(i))
    if _max[1] < tmp:
        _max = [i, tmp]

print(str(_max))
"""