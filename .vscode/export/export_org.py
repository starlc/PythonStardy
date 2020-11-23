import xlrd
import xlsxwriter
# 文件名以及路径，前面加一个r防止生成不必要的转义。
filename = r'D:\Python\workspace\组织导入模板.xlsx'
data = xlrd.open_workbook(filename)
# 获取第1个sheet页
table = data.sheets()[0]
# 获取第2行（第1条）数据
content = table.row(1)
print('第1条示例数据为：', content)
# 通过上面print内容可以看到，直接读出的内容，虽然是list，但每条数据前加了
# text:字样，不能直接强转成tuple为我们所用，于是自定义一个转换方法将其转换为可以用的list以便后面强转成tuple


def convertRowToTuple(rowNum):
    data = []
    # len(content)是上面获取到的该行的数据列数
    for i in range(len(content)):
        data.append(table.cell_value(rowNum, i))
    # 将每个单元格中的数据读取出来加到data这个list中并强转成元组返回
    return tuple(data)


# 将第0行（即excel中的第1行表头）数据读取并转成元组赋给header
header = convertRowToTuple(0)
# 将第1行（即excel中的第2行）示例数据读取并转成元组赋给data1
data1 = convertRowToTuple(1)
# print(header)
# print(data1)
# 即将写入数据的文件名
filename2 = r'D:\Python\workspace\组织导入模板--5W.xlsx'
# 如果数据量非常大，可以启用constant_memory，这是一种顺序写入模式，得到一行数据就立刻写入一行，而不会把所有的数据都保持在内存中。
# 如果不启用此模式，当数据量巨大时，程序很大概率地卡死
workbook = xlsxwriter.Workbook(filename2, {'constant_memory': True})
# 创建新的sheet页
worksheet = workbook.add_worksheet()
# startNum表示从第几行开始写，这里的数字是从1开始，因为后面要和字母组合对应在excel中，如A1代表第1行第A列
startNum = 1
# 初始值，后面的数字在它们的基础上依次增加
startValues = ['0000001', '0000001',
               '0000001', '0000001', '1000001', '1000001']
# 初始值对应的列
col = ['A', 'B', 'C', 'D']
indexs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
          'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
# 先将表头写入文件
worksheet.write_row('A'+str(startNum), header)


# 补齐N位
def getRealVal(prefix, content, length):
    if length != 0:
        content = str(content)
        content = '0'*(length-len(content))+content
        content = prefix+content
    return content

start_index = 0
mydate = list(data1)
# 正式开始写入数据
for i in range(50000):

    mydate[0] = getRealVal("", i+1, 0)
    # 小于5000为二级组织
    if(i < 5000 ):
        mydate[1] = getRealVal("二级组织", i+1, 5)
        mydate[2] = getRealVal("zz_BA2f_", i+1, 5)
        

    elif i < 10000:
        mydate[1] = getRealVal("三级组织", i-4999, 5)
        mydate[2] = getRealVal("zz_BA3f_", i-4999, 5)
        mydate[3] = getRealVal("zz_BA2f_", (i-4999)%5000, 5)
    elif i < 20000:
        mydate[1] = getRealVal("四级组织", i-9999, 5)
        mydate[2] = getRealVal("zz_BA4f_", i-9999, 5)
        mydate[3] = getRealVal("zz_BA3f_", (i-9999)%10000, 5)
    elif i < 30000:
        mydate[1] = getRealVal("五级组织", i-19999, 5)
        mydate[2] = getRealVal("zz_BA5f_", i-19999, 5)
        mydate[3] = getRealVal("zz_BA4f_", (i-19999)%10000, 5)
    elif i < 40000:
        mydate[1] = getRealVal("六级组织", i-29999, 5)
        mydate[2] = getRealVal("zz_BA6f_", i-29999, 5)
        mydate[3] = getRealVal("zz_BA5f_", (i-29999)%10000, 5)
    else:
        mydate[1] = getRealVal("七级组织", i-39999, 5)
        mydate[2] = getRealVal("zz_BA7f_", i-39999, 5)
        mydate[3] = getRealVal("zz_BA6f_", (i-39999)%20000, 5)

    worksheet.write_row('A'+str(startNum+i+1), tuple(mydate))
        # 写完之后关闭workbook，否则会报错
workbook.close()
