# 👨‍⚖️ AI法律顾问团队

一个使用多个AI代理来分析法律文档并提供全面法律见解的Streamlit应用程序。每个代理代表不同的法律专家角色，从研究和合同分析到战略规划，共同协作提供全面的法律分析和建议。

## 功能特点

- **专业法律AI代理团队**
  - **法律研究员**: 配备DuckDuckGo搜索工具，用于查找和引用相关法律案例和判例。提供详细的研究总结，并引用上传文档中的具体章节。
  
  - **合同分析师**: 专注于全面的合同审查，识别关键条款、义务和潜在问题。引用文档中的具体条款进行详细分析。
  
  - **法律策略师**: 专注于制定全面的法律策略，在考虑风险和机遇的同时提供可行的建议。
  
  - **团队负责人**: 协调团队成员之间的分析工作，确保全面的响应，提供有据可依的建议，并引用文档的具体部分。作为所有三个代理的团队协调员。

- **文档分析类型**
  - 合同审查 - 由合同分析师执行
  - 法律研究 - 由法律研究员执行
  - 风险评估 - 由合同分析师和法律策略师执行
  - 合规检查 - 由法律研究员、合同分析师和法律策略师执行
  - 自定义查询 - 由整个代理团队执行

## 运行说明

1. **环境配置**
   ```bash
   # 克隆仓库
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd ai_legal_agent_team
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **API配置**
   - OpenAI API配置
     * API密钥配置位置：
       1. 文件：`legal_agent_team.py`
       2. 函数：`init_session_state`
       3. 当前配置：
          ```python
          def init_session_state():
              if 'openai_api_key' not in st.session_state:
                  st.session_state.openai_api_key = "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"
          ```
     * API密钥使用位置：
       1. 文档处理：用于设置环境变量
       2. 文本嵌入：用于初始化OpenAIEmbedder
       3. AI代理：用于GPT-4模型访问
     * 如需更换API密钥，只需修改`init_session_state`函数中的密钥值即可

   - Qdrant配置
     * API配置位置：
       1. 文件：`legal_agent_team.py`
       2. 函数：`init_qdrant`
       3. 当前配置：
          ```python
          def init_qdrant():
              return Qdrant(          
                  collection="legal_knowledge",
                  path=":memory:",  # 使用内存型存储
                  distance="cosine"
              )
          ```
     * 配置说明：
       1. 使用内存型向量数据库，无需外部服务器
       2. 数据库参数：
          - collection：集合名称，用于存储文档向量
          - path：设置为":memory:"表示使用内存存储
          - distance：向量距离计算方法，使用余弦相似度
       3. 数据生命周期：
          - 向量数据存储在内存中
          - 会话结束后自动清除
          - 每次重启应用需要重新处理文档

3. **启动应用**
   ```bash
   streamlit run legal_agent_team.py
   ```

4. **使用界面**
   - 上传法律文档（支持PDF格式）
   - 选择分析类型
   - 添加自定义查询（如需要）
   - 查看分析结果

## 注意事项

- 仅支持PDF文档
- 使用GPT-4进行分析
- 使用text-embedding-3-small进行文本嵌入
- 需要稳定的网络连接
- 使用API会产生相应费用
- 所有分析结果均为中文输出
