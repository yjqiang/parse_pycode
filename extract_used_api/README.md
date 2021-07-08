1. 对每个 python 文件进行分析，查看该文件**使用**了torch 的哪个 api，写成 `['torch.xx.xx.xx", 'torch.xx.xx', ...]`
2. 分析工具，`ast`，缺点是还有一些额外步骤
3. 本代码不针对下面的“特殊”情况，即认为 `import` 都在要分析的代码前面，使用都在后面，且要分析的代码作者脑子比较正常:
    ```py
    import torch

    print(torch)
    
    def torch():
        import ast as torch    
        print(torch)
        
        
    torch()
    torch = 'whwj'
    print(torch)
    ```