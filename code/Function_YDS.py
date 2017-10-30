# YDS achievement
def peak_task(BS_task_t, BS_task, BS_task_o, user_R_B_th, BS_task_t_end):


    result = yds(BS_task_t, BS_task, BS_task_o, user_R_B_th, BS_task_t_end)

    b_begin = min(BS_task_t)
    e_end = max(BS_task_t_end)

    begin = BS_task_t[result[0][0]]
    end = BS_task_t_end[result[0][0]]
    #peak1 = (end-begin+1)*[result[1]]


    for i in xrange(len(result[0])):
        # change the value and remove those tasks
        j = result[0][i]-i
        if BS_task_t_end[j] > end:
            end = BS_task_t_end[j]
        if BS_task_t[j] < begin:
            begin = BS_task_t[j]

        del BS_task_t_end[j]
        del BS_task_t[j]
        del BS_task_o[j]
        del BS_task[j]

    peak1 = (end - begin + 1) * [result[1]]
    if len(BS_task) == 0:
        return [peak1,[result[1]]*len(result[0])]

    #change the arrival time and deadline
    for i in xrange(len(BS_task)):
        if BS_task_t[i] < begin and BS_task_t_end[i] < begin:
            continue

        if BS_task_t[i] < begin and BS_task_t_end[i] > end:
            BS_task_t_end[i] -= (end-begin+1)
        elif BS_task_t[i] < begin and BS_task_t_end[i] <= end:
            BS_task_t_end[i] = begin-1
        elif BS_task_t[i] >= begin and BS_task_t[i] <= end and BS_task_t_end[i] > end:
            BS_task_t[i] = begin
            BS_task_t_end[i] = BS_task_t_end[i]-end-1 + begin
        elif BS_task_t[i] > end:
            BS_task_t[i] -= (end-begin+1)
            BS_task_t_end[i] -= (end-begin+1)

    Res=peak_task(BS_task_t, BS_task, BS_task_o, user_R_B_th, BS_task_t_end)

    peak2 = Res[0]
    peak = peak2[:begin-b_begin]+peak1+peak2[begin-b_begin:]

    peak_list = Res[1]
    for i in result[0]:
        peak_list.insert(i,result[1])

    return [peak, peak_list]



def yds(BS_task_t, BS_task, BS_task_o, user_R_B_th, BS_task_t_end):

    temp_begin = list(set(BS_task_t))
    temp_end = list(set(BS_task_t_end))

    max_peak = 0
    max_list = []

    for be in temp_begin:
        for end in temp_end:
            if be > end:
                continue

            task_acc = 0
            task_list = []
            for i in xrange(len(BS_task)):
                if BS_task_t[i] >= be and BS_task_t_end[i] <= end:
                    task_acc += BS_task[i]/user_R_B_th[BS_task_o[i]]
                    task_list.append(i)

            task_acc /= (end-be+1)
            if task_acc > max_peak:
                max_peak = task_acc
                max_list = task_list

    return [max_list, max_peak]