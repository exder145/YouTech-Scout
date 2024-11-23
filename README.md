# YouTube 视频爬虫工具

这是一个用于爬取 YouTube 视频信息的 Python 工具，专注于 AI 和科技相关内容的采集与分析。

## 🚀 快速开始

### 三步上手

1. **安装依赖**

```bash
pip install yt-dlp jieba requests
```

2. **准备 cookies**

   - 登录 YouTube
   - 导出 cookies.txt 文件
   - 放入项目根目录

3. **运行程序**

```bash
python youtube-crawler.py
```

## 📖 文档指南

- [配置指南](配置指南.md) - 详细的代码配置说明，包括：
  - 搜索类别配置
  - 评分系统自定义
  - 视频筛选条件调整
  - 搜索结果数量设置
  - 更多高级配置选项

## 功能特点

- 自动搜索并获取 YouTube 视频信息
- 支持多语言搜索（中文和英文）
- 自动下载视频缩略图
- 多维度评分系统
- 结果导出为 CSV 格式
- 支持 cookies 认证
- 自动过滤不符合条件的视频

### 评分系统说明

视频内容通过五个维度进行评分（可在[配置指南](配置指南.md#2-评分系统配置)中自定义）：

1. **AI 技术**：关键词包括 ai、人工智能、机器学习等
2. **云计算**：关键词包括 云计算、云服务、云平台等
3. **数字化**：关键词包括 数字化、数字转型、智能化等
4. **创新**：关键词包括 创新、革新、突破等
5. **解决方案**：关键词包括 解决方案、应用、落地等

每个维度的得分计算方式：

- 匹配关键词数量 / 该维度总关键词数量 \* 权重
- 最终得分会归一化处理，确保不超过 1

### 常见问题

Q: 为什么搜索结果数量较少？
A: 为了避免频繁请求，当前每个关键词只获取 2 个搜索结果。可以参考[配置指南](配置指南.md#4-搜索结果数量配置)增加数量。

Q: 如何扩展搜索类别？
A: 请参考[配置指南](配置指南.md#1-搜索类别配置)中的说明进行修改。

Q: 缩略图下载失败怎么办？
A: 程序会自动尝试多种缩略图格式，如果全部失败会跳过并继续处理其他视频。

### 常见 Cookies 问题

#### 如何获取 cookies 文件？

##### 方法 1：使用浏览器扩展（推荐）

1. Chrome 浏览器

   - 安装"Get cookies.txt"扩展
   - 访问 [Chrome 网上应用店](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid)
   - 点击"添加至 Chrome"

2. 导出步骤
   - 登录 YouTube
   - 点击扩展图标
   - 选择"导出 cookies"
   - 将文件重命名为`cookies.txt`

##### 方法 2：使用 Firefox 浏览器

1. 安装"Cookie Quick Manager"扩展
2. 登录 YouTube
3. 点击扩展图标
4. 选择"Export"
5. 格式选择"Netscape HTTP Cookie File"
6. 保存为`cookies.txt`

##### 方法 3：手动获取（开发者工具）

1. 打开 Chrome 浏览器
2. 登录 YouTube
3. 按 F12 打开开发者工具
4. 选择"Network"标签
5. 刷新页面
6. 找到任意请求
7. 在 Headers 中找到"Cookie"
8. 复制内容并按 Netscape 格式保存

#### cookies 文件格式示例

Q: cookies 文件无效怎么办？
A: 重新登录 YouTube 并重新导出 cookies 文件

Q: 程序提示"未找到 cookies 文件"？
A: 确保 cookies.txt 文件位于与 youtube-crawler.py 相同的目录下

Q: cookies 过期了怎么办？
A: 需要重新登录 YouTube 并更新 cookies 文件
