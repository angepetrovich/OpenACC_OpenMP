import sys
import os
import parserACC
import convertOpenACCtoOpenMP
import generateResultFile


if __name__ == "__main__":

    #inputfile = "test/przykładProgram.cpp"
    #processFile.processFile(inputfile)


    #inputfile = "test/example2.cpp"
    #processFile.processFile(inputfile)


    #inputfile = "test/example3.cpp"
    #processFile.processFile(inputfile)
    

    #inputfile = "test/example4.cpp"
    #processFile.processFile(inputfile) '''

    #plik wyjścowy
    inputfile = "test/majaProgram.cpp"
    outputfile = inputfile + str(".translated.cpp")

    # Sprawdzenie istnienia pliku
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

    # metoda analizuje plik C++,w ACCconstructs przechowywamy wszystkie znalezione dyrektywy
    lines, ACCconstructs = parserACC.parseFile(inputfile)

    # funkcja tłumaczy dyrektywy openACC na openMP i przechowuje w ACCconstructs
    convertOpenACCtoOpenMP.convertACCtoOMP(lines, ACCconstructs)

    # generujemy nowy plik z przetłumaczonymi dyryktywami

    generateResultFile.generateTranslatedFile(lines, ACCconstructs, outputfile)

    print(f"File {inputfile} translated. Name fale is {outputfile}")
