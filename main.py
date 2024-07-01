import sys
import os
import parserACC
import convertOpenACCtoOpenMP
import generateResultFile


if __name__ == "__main__":

    #plik źródłowy
    #inputfile = "test/exampleACC.cpp"
    
    inputfile = "test/exampleACCparallel.cpp"
    
    #plik wyjścowy
    outputfile = inputfile + str(".translated.cpp")

    # sprawdza , czy plik z tak ą nazw ą istnieje
    if os.path.exists(inputfile):
        if os.path.isfile(inputfile):
            if not os.access(inputfile, os.R_OK):
                print("Error! File {inputfile} is not accessible for reading.")
                sys.exit(-1)
        else:
            print("Error! Path {inputfile} does not refer to a file.")
            sys.exit(-1)
    else:
        print("Error! Path {inputfile} does not exist.")
        sys.exit(-1)

    #funkcja analizy kodu
    lines, ACCconstructs = parserACC.parseFile(inputfile)

    # funkcja tłumaczenia dyrektywy
    convertOpenACCtoOpenMP.convertACCtoOMP(lines, ACCconstructs)

    # funkcja generowania pliku wyj ś ciowego
    generateResultFile.generateTranslatedFile(lines, ACCconstructs, outputfile)

    print(f"File {inputfile} translated. Name fale is {outputfile}")
