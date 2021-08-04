import pandas as pd
#读取第一列、第二列、第四列
df = pd.read_excel('cov19/hubei_move_out.xlsx',sheet_name='Sheet1',usecols=[1,2,3])
data = df.values
HB=[]
for i,j in zip(data,range(0,100)):
    HB.append([{"name":'湖北'},{"name":i[1],"value":int(i[2])}])
print(HB,'\n')
