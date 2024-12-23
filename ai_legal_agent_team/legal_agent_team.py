import streamlit as st
from phi.agent import Agent
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.qdrant import Qdrant
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.openai import OpenAIChat
from phi.embedder.openai import OpenAIEmbedder
import tempfile
import os

#initializing the session state variables
def init_session_state():
    """Initialize session state variables"""
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = "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"
    if 'vector_db' not in st.session_state:
        st.session_state.vector_db = None
    if 'legal_team' not in st.session_state:
        st.session_state.legal_team = None
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = None

def init_qdrant():
    """Initialize Qdrant vector database"""
    return Qdrant(          
        collection="legal_knowledge",
        path=":memory:",  # Use in-memory storage
        distance="cosine"
    )

def process_document(uploaded_file, vector_db: Qdrant):
    """Process document, create embeddings and store in Qdrant vector database"""
    if not st.session_state.openai_api_key:
        raise ValueError("未提供OpenAI API密钥")
        
    os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key
    
    with tempfile.TemporaryDirectory() as temp_dir:
      
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
       
            embedder = OpenAIEmbedder(
                model="text-embedding-3-small",
                api_key=st.session_state.openai_api_key
            )
            
            # Creating knowledge base with explicit Qdrant configuration
            knowledge_base = PDFKnowledgeBase(
                path=temp_dir, 
                vector_db=vector_db, 
                reader=PDFReader(chunk=True),
                embedder=embedder,
                recreate_vector_db=True  
            )
            knowledge_base.load()     
            return knowledge_base      
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")

def main():
    st.set_page_config(page_title="法律文档分析器", layout="wide")
    init_session_state()

    st.title("AI法律顾问团队 👨‍⚖️")

    with st.sidebar:
        st.header("🔑 API配置")
   
        # OpenAI API key is pre-configured
        st.success("OpenAI API密钥已预配置")
        
        # Initialize in-memory Qdrant
        if not st.session_state.vector_db:
            st.session_state.vector_db = init_qdrant()
            st.success("内存数据库初始化成功！")

        st.divider()

        if all([st.session_state.openai_api_key, st.session_state.vector_db]):
            st.header("📄 文档上传")
            uploaded_file = st.file_uploader("上传法律文档", type=['pdf'])
            
            if uploaded_file:
                with st.spinner("正在处理文档..."):
                    try:
                        knowledge_base = process_document(uploaded_file, st.session_state.vector_db)
                        st.session_state.knowledge_base = knowledge_base
                        
                        # Initialize agents
                        legal_researcher = Agent(
                            name="legal_researcher",
                            role="Legal Research Expert",
                            model=OpenAIChat(model="gpt-4"),
                            tools=[DuckDuckGo()],
                            knowledge=st.session_state.knowledge_base,
                            search_knowledge=True,
                            instructions=[
                                "查找并引用相关法律案例和判例",
                                "提供详细的研究总结和来源",
                                "引用上传文档中的具体章节",
                                "始终搜索知识库以获取相关信息"
                            ],
                            show_tool_calls=True,
                            markdown=True
                        )

                        contract_analyst = Agent(
                            name="contract_analyst",
                            role="Contract Analysis Expert",
                            model=OpenAIChat(model="gpt-4"),
                            knowledge=knowledge_base,
                            search_knowledge=True,
                            instructions=[
                                "全面审查合同内容",
                                "识别关键条款和潜在问题",
                                "引用文档中的具体条款"
                            ],
                            markdown=True
                        )

                        legal_strategist = Agent(
                            name="legal_strategist", 
                            role="Legal Strategy Expert",
                            model=OpenAIChat(model="gpt-4"),
                            knowledge=knowledge_base,
                            search_knowledge=True,
                            instructions=[
                                "制定全面的法律策略",
                                "提供可行的建议",
                                "考虑风险和机遇"
                            ],
                            markdown=True
                        )

                        # Legal Agent Team
                        st.session_state.legal_team = Agent(
                            name="legal_team_lead",
                            role="Legal Team Coordinator",
                            model=OpenAIChat(model="gpt-4"),
                            team=[legal_researcher, contract_analyst, legal_strategist],
                            knowledge=st.session_state.knowledge_base,
                            search_knowledge=True,
                            instructions=[
                                "协调团队成员之间的分析工作",
                                "提供全面的响应",
                                "确保所有建议都有适当的来源",
                                "引用文档的具体部分",
                                "在分配任务前始终搜索知识库"
                            ],
                            show_tool_calls=True,
                            markdown=True
                        )
                        
                        st.success("✅ 文档处理完成，团队已初始化！")
                            
                    except Exception as e:
                        st.error(f"文档处理错误: {str(e)}")

            st.divider()
            st.header("🔍 分析选项")
            analysis_type = st.selectbox(
                "选择分析类型",
                [
                    "合同审查",
                    "法律研究",
                    "风险评估",
                    "合规检查",
                    "自定义查询"
                ]
            )
        else:
            st.warning("请配置所有API凭据以继续")

    # Main content area
    if not all([st.session_state.openai_api_key, st.session_state.vector_db]):
        st.info("👈 请在侧边栏配置API凭据以开始")
    elif not uploaded_file:
        st.info("👈 请上传法律文档以开始分析")
    elif st.session_state.legal_team:
        # Create a dictionary for analysis type icons
        analysis_icons = {
            "合同审查": "📑",
            "法律研究": "🔍",
            "风险评估": "⚠️",
            "合规检查": "✅",
            "自定义查询": "💭"
        }

        # Dynamic header with icon
        st.header(f"{analysis_icons[analysis_type]} {analysis_type}分析")
  
        analysis_configs = {
            "合同审查": {
                "query": "请审查本合同并识别关键条款、义务和潜在问题。",
                "agents": ["contract_analyst"],
                "description": "详细的合同分析，重点关注条款和义务"
            },
            "法律研究": {
                "query": "研究与本文档相关的案例和判例。",
                "agents": ["legal_researcher"],
                "description": "相关法律案例和判例研究"
            },
            "风险评估": {
                "query": "分析本文档中的潜在法律风险和责任。",
                "agents": ["contract_analyst", "legal_strategist"],
                "description": "综合风险分析和战略评估"
            },
            "合规检查": {
                "query": "检查本文档的监管合规性问题。",
                "agents": ["legal_researcher", "contract_analyst", "legal_strategist"],
                "description": "全面的合规性分析"
            },
            "自定义查询": {
                "query": None,
                "agents": ["legal_researcher", "contract_analyst", "legal_strategist"],
                "description": "使用所有可用代理进行自定义分析"
            }
        }

        st.info(f"📋 {analysis_configs[analysis_type]['description']}")
        # Agent name mapping
        agent_names = {
            "legal_researcher": "法律研究员",
            "contract_analyst": "合同分析师",
            "legal_strategist": "法律策略师",
            "legal_team_lead": "法律团队负责人"
        }
        
        # Convert agent IDs to display names
        active_agents = [agent_names[agent] for agent in analysis_configs[analysis_type]['agents']]
        st.write(f"🤖 当前活动的法律AI专家: {', '.join(active_agents)}")

        # Replace the existing user_query section with this:
        if analysis_type == "自定义查询":
            user_query = st.text_area(
                "请输入您的具体问题：",
                help="添加您想要分析的具体问题或要点"
            )
        else:
            user_query = None  # Set to None for non-custom queries


        if st.button("开始分析"):
            if analysis_type == "自定义查询" and not user_query:
                st.warning("请输入查询内容")
            else:
                with st.spinner("正在分析文档..."):
                    try:
                        # Ensure OpenAI API key is set
                        os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key
                        
                        # Combine predefined and user queries
                        if analysis_type != "自定义查询":
                            combined_query = f"""
                            使用上传的文档作为参考：
                            
                            主要分析任务：{analysis_configs[analysis_type]['query']}
                            关注领域：{', '.join(analysis_configs[analysis_type]['agents'])}
                            
                            请搜索知识库并提供文档中的具体参考内容。请用中文回复。
                            """
                        else:
                            combined_query = f"""
                            使用上传的文档作为参考：
                            
                            {user_query}
                            
                            请搜索知识库并提供文档中的具体参考内容。
                            关注领域：{', '.join(analysis_configs[analysis_type]['agents'])}
                            请用中文回复。
                            """

                        response = st.session_state.legal_team.run(combined_query)
                        
                        # Display results in tabs
                        tabs = st.tabs(["分析", "要点", "建议"])
                        
                        with tabs[0]:
                            st.markdown("### 详细分析")
                            if response.content:
                                st.markdown(response.content)
                            else:
                                for message in response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)
                        
                        with tabs[1]:
                            st.markdown("### 关键要点")
                            key_points_response = st.session_state.legal_team.run(
                                f"""基于之前的分析：    
                                {response.content}
                                
                                请用要点列表总结关键内容。
                                重点关注来自以下专家的见解：{', '.join([agent_names[agent] for agent in analysis_configs[analysis_type]['agents']])}
                                请用中文回复。"""
                            )
                            if key_points_response.content:
                                st.markdown(key_points_response.content)
                            else:
                                for message in key_points_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)
                        
                        with tabs[2]:
                            st.markdown("### 建议")
                            recommendations_response = st.session_state.legal_team.run(
                                f"""基于之前的分析：
                                {response.content}
                                
                                根据分析结果，您的主要建议和最佳行动方案是什么？
                                请提供来自以下专家的具体建议：{', '.join([agent_names[agent] for agent in analysis_configs[analysis_type]['agents']])}
                                请用中文回复。"""
                            )
                            if recommendations_response.content:
                                st.markdown(recommendations_response.content)
                            else:
                                for message in recommendations_response.messages:
                                    if message.role == 'assistant' and message.content:
                                        st.markdown(message.content)

                    except Exception as e:
                        st.error(f"分析过程中出错: {str(e)}")
    else:
        st.info("请上传法律文档以开始分析")

if __name__ == "__main__":
    main()
