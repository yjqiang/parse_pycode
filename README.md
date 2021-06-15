
1. 对每个 python 文件进行分析，查看该文件使用了torch 的哪个 api，写成 `['torch.xx.xx.xx", 'torch.xx.xx', ...]`
2. 分析工具，ast，缺点是还有一些额外步骤