#generuje wyjciowy plik z przetlumaczonymi dyrektywami
def generateTranslatedFile(lines, ACCconstructs, outputFile):
    try:
        with open(outputFile, 'w') as f:
            for i in range(0, len(lines)):

                if i in ACCconstructs and ACCconstructs[i].openmp != None and len(ACCconstructs[i].openmp) > 0:
                    for construct in ACCconstructs[i].openmp:
                        beginpragma = ""
                        if ACCconstructs[i].needsOMPprefix:
                            beginpragma = "#pragma omp "
                        f.write(beginpragma + construct + "\n")
                        i = i + 1
                else:
                    f.write(lines[i])
    except IOError:
        print(f"Error! File {outputFile} is not accessible for writing.")