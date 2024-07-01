import re
import sys
import convertOpenACCtoOpenMP

#funkcja ktora omija komentarze zoznaczone znakiem /* */
def blockComments(s, isCommentOpen):
    #sprawdzamy czy komentarz otwarty
    if not isCommentOpen:
        commentOpen = False
        #jezeli w stringu nie napotkalismy znaku otwartego komentarza,
        #zwracamy commentOpen = Flase
        if '/*' not in s:
            return s, commentOpen

        #zwraca indeks wystąpienia znaku otwartego komentarza
        sblock = s.find("/*")
        #zwaraca indeks wystąpienia znaku zamkniecia komentarza */
        eblock = s.find("*/", sblock)
        if eblock >= 0:
            #
            res = s[:sblock] + s[eblock + len("*/"):]
            while '/*' in res:
                sblock = res.find("/*")
                eblock = s.find("*/", sblock)
                if eblock >= 0:
                    commentOpen = False
                    res = res = res[:sblock] + res[eblock+len("*/"):]
                else:
                    commentOpen = True
                    res = res[:sblock]
                    break
        else:
            commentOpen = True
            res = s[:sblock]
            return res, commentOpen
    else:
        commentOpen = True
        if '*/' not in s:
            return "", commentOpen

        eblock = s.find("*/")
        res = s[eblock+len("*/"):]
        commentOpen = False

        #usuwamy komentarze
        while '/*' in res:
            sblock = res.find("/*")
            eblock = res.find("*/", sblock)
            if eblock >= 0:
                commentOpen = False
                res = res[:sblock] + res[eblock+len("*/"):]
            else:
                commentOpen = True
                res = res[:sblock]
                break
        return res, commentOpen

#analizuje plik C/C++ i zapisuje dyrektywy OpenACC do słownika ACCconstruct
# (nie biorąc pod uwagę tych w zakomentowanych blokach)
def parseFile(inputfile):
    ACCconstructs = dict()
    lines = []
    try:
        with open(inputfile, "r") as f:
            lines = f.readlines()
            print("lines read")
    except IOError:
        print(f"Error! File {inputfile} is not accessible for reading.")
        sys.exit(-1)

    curline = 0
    isCommentLeftOpen = False

    while curline < len(lines):
        construct = ""

        # Czyta następujący blok kodu
        # usuwamy spacje oraz białe znaki
        original = lines[curline].strip()
        #zwracana wartość true lub false jezeli koniec linii konczy sie ukosnikiem \
        multiline = lines[curline].strip().endswith("\\")
        bline = curline
        while multiline:
            curline = curline + 1
            original = original[:-1] + lines[curline].strip() #pominiecie znaku koncowego \
            # zwracana wartość true lub false jezeli koniec linii konczy sie ukosnikiem \
            multiline = lines[curline].strip().endswith("\\")
        eline = curline
        # zamiana wielokrotnych spacji oraz tabulacji na pojedynczą spację
        original = re.sub('[\\s\\t]+',' ', original)
        #usuwa dowolny biały znak przed nawiasem otwierającym
        original = re.sub('\\s\\(', '(', original)

        print('original: ' , original)
        #proces blokowania komentarzy, jezeli są
        statements, isCommentLeftOpen = blockComments(original, isCommentLeftOpen)

        #sprawdzanie pojedynczych komentarzy, jezeli są to pracyjemy z do tego indeksu
        if '//' in statements:
            statements = statements[:statements.find("//")]

        print('statements: ', statements)

      
        # check OpenACC directives
        if '#' in statements:
            tmp = statements[statements.find("#")+len("#"):].strip()
            if 'pragma' in tmp:
                tmp = tmp[tmp.find("pragma")+len("pragma"):].strip()
                if 'acc' in tmp:
                    construct = tmp[tmp.find("acc")+len("acc"):].strip()
                    ACCconstructs[eline] = convertOpenACCtoOpenMP.AccConstruct(original, construct, bline + 1, eline + 1)

        curline = curline+1

    for key, value in ACCconstructs.items():
        print(f'Klucz: {key}, Wartość: {value.construct}\n')
    return lines, ACCconstructs

