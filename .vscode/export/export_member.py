import xlrd
import xlsxwriter
# 文件名以及路径，前面加一个r防止生成不必要的转义。
filename = r'.vscode\export\人员导入模板 --新增100W.xlsx'
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
filename2 = r'.vscode\export\人员导入模板 --新增50W.xlsx'
# 如果数据量非常大，可以启用constant_memory，这是一种顺序写入模式，得到一行数据就立刻写入一行，而不会把所有的数据都保持在内存中。
# 如果不启用此模式，当数据量巨大时，程序很大概率地卡死
workbook = xlsxwriter.Workbook(filename2, {'constant_memory': True})
# 创建新的sheet页
worksheet = workbook.add_worksheet()
# startNum表示从第几行开始写，这里的数字是从1开始，因为后面要和字母组合对应在excel中，如A1代表第1行第A列
startNum = 1
# 初始值，后面的数字在它们的基础上依次增加
startValues = [
    '0000001', '0000001', '0000001', '0000001', '0000001', '0000001'
]
# 初始值对应的列
col = ['A', 'B', 'C', 'E', 'F', 'H']
indexs = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
    'P', 'Q'
]

#先将表头写入文件
worksheet.write_row('A' + str(startNum), header)


# 补齐N位
def getRealVal(prefix, content, length):
    if length != 0:
        content = str(content)
        content = '0' * (length - len(content)) + content
        content = prefix + content
    return content


def roundVal(i, sub, div, mod):
    return int((i - sub) / div) % mod


# 定义顺序
mydate = []
for i in range(500000):
    strDate = 'zz_BA2f_'
    j = int(i / 10)
    if (j < 5000):
        strDate = getRealVal("zz_BA2f_", j + 1, 5)
    elif j < 10000:
        strDate = getRealVal("zz_BA3f_", j - 4999, 5)
    elif j < 20000:
        strDate = getRealVal("zz_BA4f_", j - 9999, 5)
    elif j < 30000:
        strDate = getRealVal("zz_BA5f_", j - 19999, 5)
    elif j < 40000:
        strDate = getRealVal("zz_BA6f_", j - 29999, 5)
    else:
        strDate = getRealVal("zz_BA7f_", j - 39999, 5)

    if j % 1000 == 0:
        print(strDate)
    mydate.append(strDate)

# 正式开始写入数据
for i in range(500000):
    # 为了不让生成过程无聊，加此打印信息以便查看进度
    if (i % 50000 == 0):
        print('正创建第', i + 1, '条数据')
    # 表头占据了第1行，所以首条数据从第2行开始，当i=0时，写入的数据从A2开始
    # 将data1中的数据依次写入A2、B2、C2……
    worksheet.write_row('A' + str(startNum + i + 1), data1)
    # 前面相当于复制了第一条数据的所有内容，但是A、I、L三列内容需要依次往下排，因此我们将重写每行中A I L单元格中的值
    for m in col:
        #print('m值为',m)
        length = len(startValues[col.index(m)])
        #print('length值为',data1[indexs.index(m)])
        # 数字用初始值加上i
        content = str(int(startValues[col.index(m)]) + i)
        # 因为像000001这样的数字在计算中会丢失前面的0，为了保持位数，将失去的0再给它补回来
        if (m != 'A' and len(content) < length + 1):
            content = '0' * (length - len(content)) + content
            content = data1[indexs.index(m)] + content
        # 将计算好的值写入到对应的单元格中
        worksheet.write(m + str(startNum + i + 1), content)

    content = mydate[i]
    worksheet.write('D' + str(startNum + i + 1), content)
# 写完之后关闭workbook，否则会报错
workbook.close()