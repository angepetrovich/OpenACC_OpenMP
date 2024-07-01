
class AccConstruct:
    def __init__(self, original, construct, beginline, endline):
        self.original = original  # oryginany kod
        self.construct = construct  # oryginalna dyrektywa / konstrukcja
        self.needsOMPprefix = True  # jezeli potrzebujemy pocztek #pragma omp
        self.bline = beginline  # początkowa linia konstrukcji
        self.eline = endline  # koncowa linia konstrukcji
        self.openmp = None  # tłumaczenie konstrukcji
        self.hasLoop = False  # czy konstrukcja zawiera dyrektywę loop


# Główny punkt tłumaczenia dla dyrektyw OpenACC
def convertACCtoOMP(lines, constructs):
    for line, construct in constructs.items():

        # dyrektywy acc
        if construct.construct.startswith("parallel"):
            translateACCtoOMP_parallel(lines, construct)
        elif construct.construct.startswith("kernels"):
            translateACCtoOMP_parallel(lines, construct)
        elif construct.construct.startswith("loop"):
            translateACCtoOMP_loop(lines, construct)
        elif construct.construct.startswith("data"):
            translateACCtoOMP_data(lines, construct)



def translateACCtoOMP_loop(lines, construct):
    construct.hasLoop = True
    omp_construct = []
    omp_clauses = []
    seq = False

    # acc loop gang -> omp distribute
    if 'gang' in construct.construct:
        omp_construct += ["distribute"]

    # acc loop vector -> omp parallel for
    if 'vector' in construct.construct:
        omp_construct += ["parallel for"]

    # usuwamy cala linijke w kodzie (loop seq)
    if 'seq' in construct.construct:
        seq = True

    if 'worker' in construct.construct:
        omp_construct += ["parallel for"]

    if 'gang' in construct.construct and 'worker' in construct.construct and 'vector' in construct.construct:
        omp_construct += ["distribute parallel for"]

    if not 'gang' in construct.construct and not 'worker' in construct.construct and not 'vector' in construct.construct and not 'seq' in construct.construct:
        omp_construct += ["for"]

    # clauses loop
    # private
    if 'private' in construct.construct:
        var = getVariablesForClause(construct.construct, "private")
        if len(var) > 0:
            omp_clauses.append(f"private({var})")

    # reduction
    if 'reduction' in construct.construct:
        var = getVariablesForClause(construct.construct, "reduction")
        if len(var) > 0:
            omp_clauses.append(f"reduction({var})")

    # collapse
    if 'collapse' in construct.construct:
        collapse_var = getVariablesForClause(construct.construct, "collapse")
        if len(collapse_var) >= 1:
            omp_clauses.append(f"collapse({collapse_var})")

    # zapisujemy omp konstrukcję
    if seq:
        #loop seq -> zwracamy pusta linie
        construct.openmp = [""]
        construct.needsOMPprefix = False
        seq = False
    else:
        construct.openmp = [" ".join(omp_construct + omp_clauses)]


def translateACCtoOMP_parallel(lines, construct):
    omp_construct = []
    omp_clauses = []

    # if loop in construct
    if 'loop' in construct.construct:
        construct.hasLoop = True
        translateACCtoOMP_loop(lines, construct)

        if construct.openmp == ["for"]:
            omp_construct = ["parallel"]
        else:
            omp_construct = ["target teams"]

    elif construct.hasLoop == False:
        omp_construct = ["parallel"]

    # num_gangs(n)
    if "num_gangs" in construct.construct:
        var = getVariablesForClause(construct.construct, "num_gangs")
        if len(var) > 0:
            omp_clauses.append(f"num_teams({var})")

    # vector_length(n)
    if "vector_length" in construct.construct:
        var = getVariablesForClause(construct.construct, "vector_length")
        if len(var) > 0:
            omp_clauses.append(f"thread_limit({var})")

    if "num_workers" in construct.construct:
        var = getVariablesForClause(construct.construct, "num_workers")
        if len(var) > 0:
            omp_clauses.append(f"num_threads({var})")

    # firstprivate
    if "firstprivate" in construct.construct:
        var = getVariablesForClause(construct.construct, "firstprivate")
        if len(var) > 0:
            omp_clauses.append(f"firstprivate({var})")

    # private
    if "private" in construct.construct:
        var = getVariablesForClause(construct.construct, "private")
        if len(var) > 0:
            omp_clauses.append(f"private({var})")

    # reduction
    if 'reduction' in construct.construct:
        var = getVariablesForClause(construct.construct, "reduction")
        if len(var) > 0:
            omp_clauses.append(f"reduction({var})")

    # collapse
    if 'collapse' in construct.construct:
        collapse_var = getVariablesForClause(construct.construct, "collapse")
        if len(collapse_var) >= 1:
            omp_clauses.append(f"collapse({collapse_var})")

    # if(x)
    if "if" in construct.construct:
        var = getVariablesForClause(construct.construct, "if")
        if len(var) > 0:
            omp_clauses.append(f"if({var})")

    construct.openmp = [" ".join(omp_construct + (construct.openmp if construct.hasLoop else []) + omp_clauses)]


def translateACCtoOMP_data(lines, construct):
    omp_construct = ["target data"]
    omp_clauses = []

    # copy, copyin, copyout clauses
    if "copy" in construct.construct:
        var = getVariablesForClause(construct.construct, "copy")
        if len(var) > 0:
            omp_clauses.append(f"map(tofrom:{var})")

    elif "present_or_copy" in construct.construct:
        var = getVariablesForClause(construct.construct, "present_or_copy")
        if len(var) > 0:
            omp_clauses.append(f"map(tofrom:{var})")

    elif "present" in construct.construct:
        var = getVariablesForClause(construct.construct, "present")
        if len(var) > 0:
            omp_clauses.append(f"map(tofrom:{var})")

    elif "copyin" in construct.construct:
        var = getVariablesForClause(construct.construct, "copyin")
        if len(var) > 0:
            omp_clauses.append(f"map(to:{var})")

    elif "present_or_copyin" in construct.construct:
        var = getVariablesForClause(construct.construct, "present_or_copyin")
        if len(var) > 0:
            omp_clauses.append(f"map(to:{var})")

    elif "copyout" in construct.construct:
        var = getVariablesForClause(construct.construct, "copyout")
        if len(var) > 0:
            omp_clauses.append(f"map(from:{var})")

    elif "present_or_copyout" in construct.construct:
        var = getVariablesForClause(construct.construct, "present_or_copyout")
        if len(var) > 0:
            omp_clauses.append(f"map(from:{var})")

    elif "create" in construct.construct:
        var = getVariablesForClause(construct.construct, "create")
        if len(var) > 0:
            omp_clauses.append(f"map(alloc:{var})")

    elif "present_or_create" in construct.construct:
        var = getVariablesForClause(construct.construct, "present_or_create")
        if len(var) > 0:
            omp_clauses.append(f"map(alloc:{var})")

    construct.openmp = [" ".join(omp_construct + (construct.openmp if construct.hasLoop else []) + omp_clauses)]



# przepisujemy wartosci w nawiasach ()
def getVariablesForClause(construct, clause):
    key = clause + str("(")
    result = ""
    pos = construct.find(key)
    if pos >= 0:
        # przyjmuje construct, pos, line, lines
        # return pos, line
        pos_end, line = findClosingParenthesis(construct, pos, None, None)
        if pos_end == -1:
            print("Error! Problem with " + construct)
        else:
            result = construct[pos + len(key):pos_end].replace(" ", "")
    return result


# szukamy pasujący nawias zamykający )
def findClosingParenthesis(construct, pos, line, lines):
    result = -1
    noParenthesis = 0

    for i in range(pos, len(construct)):
        if construct[i] == '(':
            noParenthesis = noParenthesis + 1
        elif construct[i] == ')':
            noParenthesis = noParenthesis - 1
            if noParenthesis == 0:
                result = i
                break

    # szukamy w nastepnych liniach
    if noParenthesis > 0 and line is not None and lines is not None:
        currentline = line + 1
        while currentline < len(lines) and noParenthesis > 0:
            s = lines[line]
            pos = 0
            for i in range(pos, len(s)):
                if s[i] == '(':
                    noParenthesis = noParenthesis + 1
                elif s[i] == ')':
                    noParenthesis = noParenthesis - 1
                    if noParenthesis == 0:
                        result = i
                        break

        if noParenthesis > 0:
            return -1, None
        else:
            return result, currentline

    else:
        if noParenthesis > 0:
            return -1, None
        else:
            return result, line
