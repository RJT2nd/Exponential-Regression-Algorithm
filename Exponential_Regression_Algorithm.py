from scipy import stats
import math as math
import pandas as pa
import numpy as np

def initialize(context):
    
    context.lev = 1.0;
    
    context.securities = [sid(24),
                          sid(5061),
                          sid(8347),
                          sid(4151),
                          sid(3149),
                          sid(11100),
                          sid(6653),
                          sid(16841),
                          sid(8151),
                          sid(5938),
                          sid(26578),
                          sid(21839),
                          sid(5923),
                          sid(23112),
                          sid(4283),
                          sid(3496),
                          sid(5029),
                          sid(700),
                          sid(2190),
                          sid(1637)]
    
    context.securities_length = len(context.securities)
    context.security_weights = np.zeros(context.securities_length)+1/context.securities_length
    context.xcoords = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    context.xcoords1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80])
    context.x = np.ndarray((context.securities_length, 5))
    context.MA80 = np.zeros((context.securities_length,), dtype=np.float64)
    context.MA20 = np.zeros((context.securities_length,), dtype=np.float64)
    context.MA5 = np.zeros((context.securities_length,), dtype=np.float64)
    context.price = np.zeros(context.securities_length)+0.0
    
    context.condition1=0
    context.condition2=0
    context.condition3=0
    context.condition4=0
    
    schedule_function(rec_vars, date_rules.every_day(), time_rules.market_open())
    schedule_function(regression_80day, date_rules.every_day(), time_rules.market_open())
    schedule_function(trade, date_rules.every_day(), time_rules.market_open(hours=0, minutes=1))
    
def rec_vars(context, data):
    record(b=context.x[1][0], a=context.x[1][1])
    
def trade(context, data):
    for i, stock in enumerate(context.securities):
        context.MA80[i] = data.history(stock, 'price', 81, '1d')[:-1].mean()
        context.MA20[i] = data.history(stock, 'price', 21, '1d')[:-1].mean()
        context.MA5[i] = data.history(stock, 'price', 6, '1d')[:-1].mean()
        context.price[i] = data.current(stock, 'price')
    exp_regr = context.x
    rebalance_portfolio(context, exp_regr)
    
# y = a e^bx, ln y = ln a + bx ------------- 0:b 1: a 2: r 3: p 4: stderr
def regression_20day(context, data):
    for i in range(0, context.securities_length):
        yc = np.log(data.history(context.securities[i], 'price', 21, '1d')[:-1])
        context.x[i][0], context.x[i][1], context.x[i][2], context.x[i][3], context.x[i][4] = stats.linregress(context.xcoords, yc)
        context.x[i][1] = math.e**context.x[i][1]
    return context.x

def regression_80day(context, data):
    for i in range(0, context.securities_length):
        yc = np.log(data.history(context.securities[i], 'price', 81, '1d')[:-1])
        context.x[i][0], context.x[i][1], context.x[i][2], context.x[i][3], context.x[i][4] = stats.linregress(context.xcoords1, yc)
        context.x[i][1] = math.e**context.x[i][1]
    return context.x
                    
def rebalance_portfolio(context, regression):
    
    desired_weights = np.zeros((context.securities_length,), dtype=np.float64)
    
    for i in range(0, context.securities_length):
        if(context.MA20[i]>=context.MA80[i]):
            if(regression[i][1]>50):
                desired_weights[i]=math.e**5.0
                print (desired_weights[i])
            elif(regression[i][1]>45):
                desired_weights[i]=math.e**4.0
                print (desired_weights[i])
            elif(regression[i][1]>40):
                desired_weights[i]=math.e**3.0
                print (desired_weights[i])
            elif(regression[i][1]>35):
                desired_weights[i]=math.e**2.0
                print (desired_weights[i])
            elif(regression[i][1]>30):
                desired_weights[i]=math.e**1.0
                print (desired_weights[i])
            else:
                desired_weights[i]=math.e**0.0
                print (desired_weights[i])
        else:
            if(context.MA5[i]>=context.MA20[i]):
                desired_weights[i]=math.e**-2.0
            else:
                desired_weights[i]=math.e**-4.0
    
    weights_sum = np.sum(desired_weights)*1.0
    
    if weights_sum != 0:
        desired_weights = desired_weights*1.0/weights_sum
            
    for i in range(0, context.securities_length):
            order_target_percent(context.securities[i], context.lev * desired_weights[i])