# 图像匹配方法比较工具

本目录包含用于比较不同图像匹配算法性能的工具。

## 可用工具

1. `run_comparison.bat` - 批量比较所有图片
2. `compare_single_file.bat` - 对单个图片文件进行比较
3. `compare_matching_methods.py` - 底层比较脚本

## 比较的算法

这些工具比较了两种不同的图像匹配算法：

1. **test_template_matching.py中的calculate_similarity方法** - 使用模板匹配算法计算两个图像的相似度，输出相似度百分比
2. **ImageProcessor中的image_similarity_opencv方法** - 可以使用两种算法：
   - ORB特征点匹配（默认）
   - 模板匹配（通过`--toggle`参数启用）

## 使用方法

### 批量比较所有图片

```
run_comparison.bat
```

这将会：
- 使用ORB特征点匹配算法比较所有图片，并将结果保存到`comparison_orb.md`
- 使用模板匹配算法比较所有图片，并将结果保存到`comparison_template.md`

### 比较单个图片

```
compare_single_file.bat 图片文件名
```

例如：
```
compare_single_file.bat test_image.png
```

这将会：
- 使用ORB特征点匹配算法比较指定图片，并将结果保存到`comparison_single_orb.md`
- 使用模板匹配算法比较指定图片，并将结果保存到`comparison_single_template.md`

### 自定义比较参数

如果需要更多自定义选项，可以直接使用Python脚本：

```
python compare_matching_methods.py [参数]
```

可用参数：
- `--file FILENAME` - 指定要匹配的文件名
- `--output FILENAME` - 指定输出结果文件名（默认：comparison_results.md）
- `--toggle` - 切换为模板匹配算法（默认使用ORB特征点匹配）

## 输出结果

输出的Markdown文件包含：
- 每个图片的详细匹配结果
- 两种方法的最佳匹配比较
- 两种方法结果是否一致
- 总体一致率统计
- 不一致结果的详细列表

## 注意事项

1. 测试前请确保`resources/25601440`和`resources/temp2313`目录存在并包含测试所需的图片
2. ORB特征点匹配返回的是匹配点数量，程序会自动将其转换为相似度百分比（以40点为基准100%）
3. 模板匹配直接返回0-100的相似度百分比 