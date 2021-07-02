def aggregate_result(old_result):

    result = []
    result_copy = []
    for t in old_result:
        t = list(t)
        result.append(t)
        result_copy.append(t.copy())

    height = len(result)
    width = len(result[0])

    i=width-2
    while i >= 0:
        j=0
        while j < height:
            if j+1==height:
                break
            edited = False
            k=j+1
            while result[j][i] == result[k][i]:
                edited = True
                del result_copy[k][i]
                k+=1
                if k==height:
                    break
            k-=1
            if edited:
                result_copy[j][i] = (result[j][i], k-j+1)
            j = k + 1
        i-=1
    return result_copy
