import xlrd
import xlsxwriter
# 文件名以及路径，前面加一个r防止生成不必要的转义。
filename = r'.vscode\export\组织导入模板.xlsx'
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
filename2 = r'.vscode\export\组织导入模板--5W.xlsx'
# 如果数据量非常大，可以启用constant_memory，这是一种顺序写入模式，得到一行数据就立刻写入一行，而不会把所有的数据都保持在内存中。
# 如果不启用此模式，当数据量巨大时，程序很大概率地卡死
workbook = xlsxwriter.Workbook(filename2, {'constant_memory': True})
# 创建新的sheet页
worksheet = workbook.add_worksheet()
# startNum表示从第几行开始写，这里的数字是从1开始，因为后面要和字母组合对应在excel中，如A1代表第1行第A列
startNum = 1
# 初始值，后面的数字在它们的基础上依次增加
startValues = [
    '0000001', '0000001', '0000001', '0000001', '1000001', '1000001'
]
# 初始值对应的列
col = ['A', 'B', 'C', 'D']
indexs = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
    'P', 'Q'
]
# 先将表头写入文件
worksheet.write_row('A' + str(startNum), header)


# 补齐N位
def getRealVal(prefix, content, length):
    if length != 0:
        content = str(content)
        content = '0' * (length - len(content)) + content
        content = prefix + content
    return content


start_index = 0
mydate = list(data1)
one_org = []
two_org = []
three_org = []
four_org = []
five_org = []
six_org = []


def roundVal(i, sub, div, mod):
    return int((i - sub) / div) % mod


# 正式开始写入数据
for i in range(50000):

    if i < 100:
        print(int(i / 2) % 100)
    mydate[0] = getRealVal("", i + 1, 0)
    # 小于500为二级组织
    if (i < 500):
        mydate[1] = getRealVal("二级组织", i + 1, 5)
        mydate[2] = getRealVal("zz_BA2f_", i + 1, 5)
        two_org.append(mydate[2])
    elif i < 1500:
        # 三级1000
        mydate[1] = getRealVal("三级组织", i - 499, 5)
        mydate[2] = getRealVal("zz_BA3f_", i - 499, 5)
        mydate[3] = two_org[roundVal(i, 500, 2, 500)]
        three_org.append(mydate[2])
    elif i < 2500:
        # 四级1000
        mydate[1] = getRealVal("四级组织", i - 1499, 5)
        mydate[2] = getRealVal("zz_BA4f_", i - 1499, 5)
        mydate[3] = three_org[roundVal(i, 1500, 1, 1000)]
        four_org.append(mydate[2])
    elif i < 22500:
        # 5级2W
        mydate[1] = getRealVal("五级组织", i - 2499, 5)
        mydate[2] = getRealVal("zz_BA5f_", i - 2499, 5)
        mydate[3] = four_org[roundVal(i, 2500, 20, 1000)]
        five_org.append(mydate[2])
    elif i < 42500:
        # 6级 2W
        mydate[1] = getRealVal("六级组织", i - 22499, 5)
        mydate[2] = getRealVal("zz_BA6f_", i - 22499, 5)
        mydate[3] = five_org[roundVal(i, 22500, 1, 20000)]
        six_org.append(mydate[2])
    else:
        # 7级7500
        mydate[1] = getRealVal("七级组织", i - 42499, 5)
        mydate[2] = getRealVal("zz_BA7f_", i - 42499, 5)
        mydate[3] = six_org[roundVal(i, 42500, 1, 20000)]

    worksheet.write_row('A' + str(startNum + i + 1), tuple(mydate))
    # 写完之后关闭workbook，否则会报错
workbook.close()
