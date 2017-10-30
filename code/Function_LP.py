import numpy as np
from gurobipy import *


def d2d_lp_s(n_user_pr, BS_num, max_Delay, BS_task_new_total, BS_task_t_new_total, BS_task_o_new_total,BS_task_d_new_total,
			 BS_peak_x_total, BS_peak_y_total,
			 user_con_Delay, user_object_Delay, user_con_Delay_n_acc,user_con_Delay_end,user_con_Delay_n_end,user_object_Delay_end,
			 user_R, user_R_B):

	d2d_s = Model('d2d_s')
	#i = 0
	Vars = [
		[[] for i in xrange(len(BS_task_new_total[j]))]
		for j in xrange(BS_num)]

	for i in xrange(BS_num):
		#basic = i * n_user_pr - 1
		temp_own = [[] for j in range(n_user_pr)]

		for j in xrange(len(BS_task_o_new_total[i])):
			temp_own[BS_task_o_new_total[i][j]-i*n_user_pr].append(j)

		for j in xrange(n_user_pr):
			basic = i * n_user_pr +j
			if len(temp_own[j]):
				Delay_flag = np.zeros(max_Delay,dtype=np.int)

				for m in temp_own[j]:
					Delay_flag[BS_task_d_new_total[i][m]-1] += 1

				temp_flow_Delay = []
				for Delay in xrange(1,max_Delay+1):
					if Delay == 1 and Delay_flag[0] > 0:
						temp_flow_Delay.append([user_R_B[basic]])
					elif Delay_flag[Delay-1] > 0:
						temp_flow = []
						flag = -1
						user_con_n = np.hstack((user_con_Delay_n_acc[basic,0:Delay],user_con_Delay_n_end[basic,Delay-1]))
						user_con = user_con_Delay[basic][0:user_con_Delay_n_acc[basic,Delay-1]]+user_con_Delay_end[basic][Delay-1]
						user_object = user_object_Delay[basic][0:user_con_Delay_n_acc[basic,Delay-1]]+user_object_Delay_end[basic][Delay-1]
						temp = np.array(range(user_con_n[Delay]))

						for m in xrange(Delay-1):
							for k in xrange(user_con_n[m], user_con_n[m + 1]):
								if temp[k] >= 0 and user_con[k] >= 0:
									temp[k] = -1
									temp_flow.append([0] * user_con_n[Delay])
									flag += 1
									temp_o = user_con[k]
									temp_flow[flag][k] = user_R[temp_o, user_object[k]]
									for n in range(k + 1, user_con_n[m + 1]):
										if temp_o == user_con[n]:
											temp_flow[flag][n] = user_R[temp_o, user_object[n]]
											temp[n] = -1
									for n in range(user_con_n[m + 1], user_con_n[m + 2]):
										if temp_o == user_object[n]:
											if user_con[n] >= 0:
												temp_flow[flag][n] = -user_R[temp_o, user_con[n]]
											else:
												temp_flow[flag][n] = -user_R_B[temp_o]

						flag += 1
						temp_flow.append([0]*user_con_n[Delay])
						temp_flow[flag][0:user_con_n[1]] = [user_R[basic,m] if m >= 0  else user_R_B[basic] for m in user_con[0:user_con_n[1]]]

						flag += 1
						temp_flow.append([0]*user_con_n[Delay])
						temp_flow[flag] = [user_R_B[user_object[m]] if user_con[m]<0 else 0 for m in range(user_con_n[Delay])]

						temp_flow_Delay.append(temp_flow)
					else:
						temp_flow_Delay.append([])

				for m in temp_own[j]:
					Delay = BS_task_d_new_total[i][m]

					for k in range(user_con_Delay_n_end[basic, Delay-1]):
						Vars[i][m].append(d2d_s.addVar(lb=0))

					if Delay > 1:
						for k in range(len(temp_flow_Delay[Delay-1])-2):
							d2d_s.addConstr(sum(Vars[i][m][n] * temp_flow_Delay[Delay-1][k][n]
							                    for n in range(user_con_Delay_n_end[basic][Delay-1])) == 0)

						for k in range(len(temp_flow_Delay[Delay-1])-2,len(temp_flow_Delay[Delay-1])):
							d2d_s.addConstr(sum(Vars[i][m][n] * temp_flow_Delay[Delay-1][k][n]
							                    for n in range(user_con_Delay_n_end[basic][Delay-1])) == BS_task_new_total[i][m])

					else:
						d2d_s.addConstr(temp_flow_Delay[0][0]*Vars[i][m][0] == BS_task_new_total[i][m])


	P_b = []

	for i in xrange(BS_num):
		temp = 0
		if len(BS_peak_y_total[i]):
			temp = max(BS_peak_y_total[i])
		P_b.append(d2d_s.addVar(lb=temp))

	BS_task_len = [len(BS_task_new_total[i]) for i in range(BS_num)]
	BS_task_t_full = []
	for i in xrange(BS_num):
		BS_task_t_full.append([])
		for j in xrange(BS_task_len[i]):
			BS_task_t_full[i] += range(BS_task_t_new_total[i][j],BS_task_t_new_total[i][j]+BS_task_d_new_total[i][j])


	for i in xrange(BS_num):
		task_acc = -1
		for j in xrange(BS_task_len[i]):
			Delay = BS_task_d_new_total[i][j]
			for m in xrange(Delay):
				task_acc += 1
				if BS_task_t_full[i][task_acc] >= 0:

					temp = BS_task_t_full[i][task_acc]
					temp_t = temp
					temp_vars = []
					temp_object = []
					temp_con = []

					BS_task_t_full[i][task_acc] = -1
					temp_o = BS_task_o_new_total[i][j]
					if m == Delay-1:
						temp_r1 = user_con_Delay_n_acc[temp_o, Delay-1]
						temp_r2 = user_con_Delay_n_end[temp_o, Delay-1]
						temp_vars += Vars[i][j][temp_r1:temp_r2]
						temp_object += user_object_Delay_end[temp_o][Delay-1]
						temp_con += user_con_Delay_end[temp_o][Delay-1]
					else:
						temp_r1 = user_con_Delay_n_acc[temp_o, m]
						temp_r2 = user_con_Delay_n_acc[temp_o, m+1]
						temp_vars += Vars[i][j][temp_r1:temp_r2]
						temp_object += user_object_Delay[temp_o][temp_r1:temp_r2]
						temp_con += user_con_Delay[temp_o][temp_r1:temp_r2]


					k = j+1
					k_acc = task_acc - m + BS_task_d_new_total[i][j]
					while k < BS_task_len[i] and BS_task_t_new_total[i][k] <= temp:
						#if BS_task_t_full[i][k_acc] != -1 and BS_task_t_full[i][k_acc] != BS_task_t_new_total[i][k]:
						#	print  BS_task_t_new_total[i][k]
						if BS_task_t_new_total[i][k] + BS_task_d_new_total[i][k]-1 >= temp:

							mark = temp - BS_task_t_new_total[i][k]+1
							BS_task_t_full[i][k_acc + mark-1] = -1
							temp_o = BS_task_o_new_total[i][k]
							if mark == BS_task_d_new_total[i][k]:
								temp_r1 = user_con_Delay_n_acc[temp_o, mark-1]
								temp_r2 = user_con_Delay_n_end[temp_o, mark-1]
								temp_vars += Vars[i][k][temp_r1:temp_r2]
								temp_object += user_object_Delay_end[temp_o][mark-1]
								temp_con += user_con_Delay_end[temp_o][mark-1]
							else:
								temp_r1 = user_con_Delay_n_acc[temp_o, mark-1]
								temp_r2 = user_con_Delay_n_acc[temp_o, mark]
								temp_vars += Vars[i][k][temp_r1:temp_r2]
								temp_object += user_object_Delay[temp_o][temp_r1:temp_r2]
								temp_con += user_con_Delay[temp_o][temp_r1:temp_r2]

						k_acc += BS_task_d_new_total[i][k]
						k += 1


					for k in xrange(i + 1, BS_num):
						m = 0
						m_acc = 0
						while m < BS_task_len[k] and BS_task_t_new_total[k][m] <= temp:
							#if BS_task_t_full[k][m_acc] != -1 and BS_task_t_full[k][m_acc] != BS_task_t_new_total[k][m]:
							#	print BS_task_t_full[k][m_acc]
							if BS_task_t_new_total[k][m] + BS_task_d_new_total[k][m] - 1 >= temp:
								mark = temp - BS_task_t_new_total[k][m] + 1
								BS_task_t_full[k][m_acc + mark-1] = -1
								temp_o = BS_task_o_new_total[k][m]
								if mark == BS_task_d_new_total[k][m]:
									temp_r1 = user_con_Delay_n_acc[temp_o,mark-1]
									temp_r2 = user_con_Delay_n_end[temp_o,mark-1]
									temp_vars += Vars[k][m][temp_r1:temp_r2]
									temp_object += user_object_Delay_end[temp_o][mark-1]
									temp_con += user_con_Delay_end[temp_o][mark-1]
								else:
									temp_r1 = user_con_Delay_n_acc[temp_o,mark-1]
									temp_r2 = user_con_Delay_n_acc[temp_o,mark]
									temp_vars += Vars[k][m][temp_r1:temp_r2]
									temp_object += user_object_Delay[temp_o][temp_r1:temp_r2]
									temp_con += user_con_Delay[temp_o][temp_r1:temp_r2]

							m_acc += BS_task_d_new_total[k][m]
							m += 1

					temp_len = len(temp_object)
					temp_flag = [0] * temp_len
					temp_eq = []
					flag = -1
					temp_bs = []
					for k in range(temp_len):
						if not temp_flag[k]:
							if temp_con[k] >= 0 and temp_con[k] != temp_object[k]:
								temp = temp_con[k] / n_user_pr
							elif temp_con[k] < 0:
								temp = -(temp_con[k] + 1)
							else:
								continue

							flag += 1
							temp_eq.append([0] * temp_len)

							temp_flag[k] = 1
							temp_eq[flag][k] = 1

							for m in range(k + 1, temp_len):
								if temp_con[m] >= 0 and temp_con[m] / n_user_pr == temp and temp_con[m] != temp_object[m]:
									temp_flag[m] = 1
									temp_eq[flag][m] = 1
								elif temp_con[m] < 0 and -(temp_con[m] + 1) == temp:
									temp_flag[m] = 1
									temp_eq[flag][m] = 1

							temp_bs += [temp]

					for k in range(flag + 1):
						temp_B = int(temp_bs[k])

						temp = 0
						if temp_t in BS_peak_x_total[temp_B]:
							temp = BS_peak_y_total[temp_B][BS_peak_x_total[temp_B].index(temp_t)]
							#print [temp_B,temp_t,temp]

						d2d_s.addConstr(
							sum(temp_vars[m] * temp_eq[k][m] for m in range(temp_len)) + temp <= P_b[temp_B] )
					#print('end')

	d2d_s.setObjective(sum(P_b[i] for i in range(BS_num)), GRB.MINIMIZE)
	d2d_s.optimize()

	#P_B = d2d_s.getAttr('x', P_b)
	#Vars_s = []
	#for i in range(len(Vars)):
	#	Vars_s.append([])
	#	for j in range(len(Vars[i])):
	#		Vars_s[i].append(d2d_s.getAttr('x',Vars[i][j]))
	return d2d_s.objVal  #[Vars_s,P_B,d2d_s.objVal]




