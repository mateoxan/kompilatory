import os
import sys
import re
import codecs


def processFile(filepath):
    fp = codecs.open(filepath, 'rU', encoding='iso-8859-2')
    content = fp.read()


    def metaSearch(meta, info):
        def search(line, str):
            regex = r'<META NAME="' + str + r'" CONTENT="'
            found = re.findall(regex, line)
            if len(found) == 0:
                return ""
            else:
                return re.sub(r'">', "", re.sub(found[0], "", line))    #usuwa wszystko z linii poza szukana informacja

        result = ""
        for line in meta:
            tmp = search(line, info)
            if len(tmp) != 0:
                result = result + tmp + ", "

        return result[:-2]       #-2 aby pominac ostatnie ', '

    def ptagsSearch(ptags, regexp):
        result = set()
        new_lines = list()             #lista linii, z ktorych usunieto dopasowane regeksy
        for line in ptags:
            result = result | set(re.findall(regexp, line))  #dodaje do wyniku zbior znalezionych dopasowan
            new_lines.append(re.sub(regexp, '', line))       #usuwa dopasowane czesci z linii
        return len(result), new_lines

    def buildRegexForDates():
        delims = [r'\.', r'-', r'/']
        year = r'\d{4}'
        daysandmonths = [r'(?:(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9]))',
            r'02)|(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9])|30)',
            r'(?:04|06|09|11))|(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9])|30|31)',
            r'(?:01|03|05|07|08|10|12)))']
        result = r'(?:'

        for delim in delims:
            result = result + delim.join(daysandmonths) + delim + year + '|' + year + delim + delim.join(daysandmonths) + '|'

        """
        Przykladowy rezultat (DD.MM.YYYY):
        (?:
		(?:    #dzien i miesiac
		(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9]))\.02)|  #luty
		(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9])|30)\.(?:04|06|09|11))|    #miesiace 30-dniowe
		(?:(?:(?:(?:1|2)[0-9])|(?:0[1-9])|30|31)\.(?:01|03|05|07|08|10|12))    #31 dni
		)
		\.\d{4})   #rok
		"""

        return result[:-1] + r')'

    without_p = re.split(r'<P>', content)[1:]                 #dzieli html na czesci, usuwa naglowki i wszystkie wystapienia <P>
    last_p = re.split(r'</P>', without_p[-1])[0]
    without_endp = [re.sub(r'</P>', '', wp) for wp in without_p]      #usuwa wszystkie wystapienia </P>
    article = [re.sub(r'</B>\s*(</FONT>)?|(</FONT>)?\s*</B>', '', re.sub(r'(?:<B>(<FONT.*?>)?)|(?:(<FONT.*?>)?<B>)', '', wep, flags=re.IGNORECASE), flags=re.IGNORECASE) for wep in without_endp[:-1]]      #usuwa wszystkie wystapienia <Font> i <B>
    last_p = re.sub(r'</B>\s*(</FONT>)?|(</FONT>)?\s*</B>', '', re.sub(r'(?:<B>(<FONT.*?>)?)|(?:(<FONT.*?>)?<B>)', '', last_p, flags=re.IGNORECASE), flags=re.IGNORECASE)
    article.append(last_p)         #for przy tworzeniu article nie uwzglednia ostatniego elementu powstalego w pierwszym splicie, dlatego trzeba go oczyscic i dolaczyc

    int_regex = re.compile(r"""(?:  #int -32768, 32767
        (?:[ ]|-)             #opcjonalny minus
        (?:[1-9]\d{0,3}|    #liczby maksymalnie czterocyfrowe (1-9999)
        [12]\d{4}|          #liczby pieciocyfrowe z 1 lub 2 na poczatku (10000-29999)
        3(?:[01]\d{3}       #liczby pieciocyfrowe z 3 na poczatku (30000-31999)
        |2(?:[0-6]\d{2}|    #liczby pieciocyfrowe z 32 na poczatku (32000-32699)
        7(?:[0-5]\d|        #liczby pieciocyfrowe z 327 na poczatku (32700-32759)
        6[0-7]))))|         #(32760-32767)
        (?:[ ]|-)-32768|      #-32768
        (?:[ ]|--)0)          #zero
        """, re.X)

    shortcut_regex = re.compile(r"""
        (?<=\s|[()-])       #przed skrotem moze wystapic bialy znak, nawias lub myslnik, ta grupa nie wlicza sie do dopasowania (positive lookbehind)
        [a-zA-Z]{1,3}\.        #ciag maksymalnie trzech liter zakonczony kropka
        (?!\s+[A-Z])     #po kropce nie wystepuje bialy znak i wielka litera co oznaczaloby poczatek nowego zdania
        """, re.X)

    emails, without_endp = ptagsSearch(without_endp, r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]')
    dates, article = ptagsSearch(article, buildRegexForDates())
    floats, article = ptagsSearch(article, r'-?\d+[.,]\s?\d+')
    ints, article = ptagsSearch(article, int_regex)
    shortcuts, article = ptagsSearch(article, shortcut_regex)
    sentences, article = ptagsSearch(article, r'[A-Z][^.]*(?:[.?!]+|\n)')    #zdanie rozpoczyna sie od wielkiej litery, nastepnie dowolne znaki oprocz kropki, na koniec ciag kropek, pytajnikow, wykrzyknikow lub znak nowej linii

    meta = without_p[-1].splitlines()     #sekcja meta jest dzielona na linie
    author = metaSearch(meta, r"AUTOR")
    section = metaSearch(meta, r"DZIAL")
    keywords = metaSearch(meta, r"KLUCZOWE_\d+")

    fp.close()
    print("nazwa pliku: ", filepath)
    print("autor: ", author)
    print("dzial: ", section)
    print("slowa kluczowe: ", keywords)
    print("liczba zdan: ", sentences)
    print("liczba skrotow: ", shortcuts)
    print("liczba liczb calkowitych z zakresu int: ", ints)
    print("liczba liczb zmiennoprzecinkowych: ", floats)
    print("liczba dat: ", dates)
    print("liczba adresow email: ", emails)
    print("\n")

    with codecs.open('result.txt', mode='a', encoding='iso-8859-2') as myfile:
        myfile.write('nazwa pliku: ' + filepath)
        myfile.write('\nautor: ' + author)
        myfile.write('\ndzial: ' + section)
        myfile.write('\nliczba zdan: ' + str(sentences))
        myfile.write('\nliczba skrotow: ' + str(shortcuts))
        myfile.write('\nliczba liczb calkowitych z zakresu int: ' + str(ints))
        myfile.write('\nliczba liczb zmiennoprzecinkowych: ' + str(floats))
        myfile.write('\nLiczba dat: ' + str(dates))
        myfile.write('\nliczba adresow email: ' + str(emails) + '\n\n')



try:
    path = sys.argv[1]
except IndexError:
    print("Brak podanej nazwy katalogu")
    sys.exit(0)


tree = os.walk(path)

path1 = os.getcwd()
path1 += ('\\result.txt')
if(os.path.isfile(path1)):
    os.remove(path1)

for root, dirs, files in tree:
    for f in files:
        if f.endswith(".html"):
            filepath = os.path.join(root, f)
            processFile(filepath)



