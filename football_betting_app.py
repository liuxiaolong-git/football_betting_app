import streamlit as st
import requests
import pandas as pd
import numpy as np
import pytz
from datetime import datetime, timedelta, date
import json
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="足球体彩投注计算器",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .match-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    .odds-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    }
    .calculator-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .profit-positive {
        color: #00b894;
        font-weight: bold;
    }
    .profit-negative {
        color: #d63031;
        font-weight: bold;
    }
    .status-live {
        color: #e74c3c;
        font-weight: bold;
    }
    .status-finished {
        color: #27ae60;
        font-weight: bold;
    }
    .status-scheduled {
        color: #3498db;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'bet_slip' not in st.session_state:
    st.session_state.bet_slip = []
    
if 'selected_matches' not in st.session_state:
    st.session_state.selected_matches = {}

if 'calculation_history' not in st.session_state:
    st.session_state.calculation_history = []

# 北京时区
beijing_tz = pytz.timezone('Asia/Shanghai')
now_beijing = datetime.now(beijing_tz)

# ====== 加载配置数据 ======
@st.cache_data(ttl=3600)  # 1小时缓存
def load_config_data():
    """加载配置数据"""
    try:
        # 联赛信息
        leagues = {
            "英超": {"id": "premier_league", "color": "#3D195B"},
            "西甲": {"id": "la_liga", "color": "#FF6B35"},
            "意甲": {"id": "serie_a", "color": "#00A8E8"},
            "德甲": {"id": "bundesliga", "color": "#D10000"},
            "法甲": {"id": "ligue_1", "color": "#0055A4"},
            "欧冠": {"id": "champions_league", "color": "#004D98"},
            "欧联": {"id": "europa_league", "color": "#FF6B6B"},
            "中超": {"id": "csl", "color": "#FFD700"},
            "亚冠": {"id": "afc_cl", "color": "#2E8B57"}
        }
        
        # 球队信息（简化的中英文对照）
        teams_translation = {
            # 英超
            "Manchester United": "曼联",
            "Manchester City": "曼城",
            "Liverpool": "利物浦",
            "Chelsea": "切尔西",
            "Arsenal": "阿森纳",
            "Tottenham": "热刺",
            # 西甲
            "Real Madrid": "皇家马德里",
            "Barcelona": "巴塞罗那",
            "Atletico Madrid": "马德里竞技",
            "Sevilla": "塞维利亚",
            # 意甲
            "Juventus": "尤文图斯",
            "AC Milan": "AC米兰",
            "Inter Milan": "国际米兰",
            "Roma": "罗马",
            "Napoli": "那不勒斯",
            # 德甲
            "Bayern Munich": "拜仁慕尼黑",
            "Borussia Dortmund": "多特蒙德",
            "RB Leipzig": "RB莱比锡",
            # 法甲
            "PSG": "巴黎圣日耳曼",
            "Marseille": "马赛",
            "Lyon": "里昂",
            # 中超
            "广州队": "广州队",
            "上海海港": "上海海港",
            "北京国安": "北京国安",
            "山东泰山": "山东泰山"
        }
        
        return leagues, teams_translation
    except Exception as e:
        st.error(f"加载配置失败: {str(e)}")
        return {}, {}

# 加载配置
leagues, teams_translation = load_config_data()

def translate_team_name(name):
    """翻译球队名称"""
    return teams_translation.get(name, name)

# ====== API数据获取函数 ======
@st.cache_data(ttl=60)  # 1分钟缓存，赛事数据实时性较高
def fetch_live_matches():
    """获取实时比赛数据（模拟数据，实际应用中替换为真实API）"""
    try:
        # 这里使用模拟数据，实际应用中应该调用真实的足球API
        # 例如：football-data.org, api-football.com等
        
        # 生成模拟比赛数据
        today = now_beijing.date()
        matches = []
        
        # 英超比赛
        if today.weekday() in [5, 6]:  # 周末有更多比赛
            matches.extend([
                {
                    "id": 1,
                    "league": "英超",
                    "home_team": "Manchester United",
                    "away_team": "Manchester City",
                    "home_team_cn": "曼联",
                    "away_team_cn": "曼城",
                    "start_time": (now_beijing + timedelta(hours=2)).strftime("%H:%M"),
                    "status": "未开始",
                    "home_score": None,
                    "away_score": None,
                    "odds": {
                        "win": 3.80,
                        "draw": 3.60,
                        "lose": 1.85,
                        "handicap": {
                            "home": 2.10,
                            "draw": 3.30,
                            "away": 2.80
                        }
                    }
                },
                {
                    "id": 2,
                    "league": "英超",
                    "home_team": "Liverpool",
                    "away_team": "Arsenal",
                    "home_team_cn": "利物浦",
                    "away_team_cn": "阿森纳",
                    "start_time": (now_beijing + timedelta(hours=1)).strftime("%H:%M"),
                    "status": "未开始",
                    "home_score": None,
                    "away_score": None,
                    "odds": {
                        "win": 2.20,
                        "draw": 3.40,
                        "lose": 2.90,
                        "handicap": {
                            "home": 1.85,
                            "draw": 3.60,
                            "away": 3.20
                        }
                    }
                }
            ])
        
        # 西甲比赛
        matches.append({
            "id": 3,
            "league": "西甲",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "home_team_cn": "皇家马德里",
            "away_team_cn": "巴塞罗那",
            "start_time": (now_beijing + timedelta(hours=3)).strftime("%H:%M"),
            "status": "未开始",
            "home_score": None,
            "away_score": None,
            "odds": {
                "win": 2.10,
                "draw": 3.50,
                "lose": 3.00,
                "handicap": {
                    "home": 1.95,
                    "draw": 3.40,
                    "away": 3.10
                }
            }
        })
        
        # 正在进行中的比赛
        matches.append({
            "id": 4,
            "league": "意甲",
            "home_team": "AC Milan",
            "away_team": "Inter Milan",
            "home_team_cn": "AC米兰",
            "away_team_cn": "国际米兰",
            "start_time": now_beijing.strftime("%H:%M"),
            "status": "进行中",
            "home_score": 1,
            "away_score": 1,
            "odds": {
                "win": 2.80,
                "draw": 3.20,
                "lose": 2.40,
                "handicap": {
                    "home": 2.30,
                    "draw": 3.30,
                    "away": 2.60
                }
            }
        })
        
        # 已结束的比赛
        matches.append({
            "id": 5,
            "league": "德甲",
            "home_team": "Bayern Munich",
            "away_team": "Borussia Dortmund",
            "home_team_cn": "拜仁慕尼黑",
            "away_team_cn": "多特蒙德",
            "start_time": (now_beijing - timedelta(hours=2)).strftime("%H:%M"),
            "status": "已结束",
            "home_score": 3,
            "away_score": 2,
            "odds": {
                "win": 1.60,
                "draw": 4.00,
                "lose": 5.00,
                "handicap": {
                    "home": 2.00,
                    "draw": 3.50,
                    "away": 3.00
                }
            }
        })
        
        return matches
        
    except Exception as e:
        st.error(f"获取比赛数据失败: {str(e)}")
        return []

@st.cache_data(ttl=3600)  # 1小时缓存
def fetch_historical_data(team_name: str, days: int = 30):
    """获取球队历史数据（模拟数据）"""
    try:
        # 生成模拟历史数据
        today = date.today()
        dates = [(today - timedelta(days=i)).strftime("%m-%d") for i in range(days, 0, -1)]
        
        # 模拟比赛结果
        results = []
        for i in range(days):
            # 随机生成比赛结果
            rand = np.random.rand()
            if rand < 0.4:
                results.append("胜")
            elif rand < 0.7:
                results.append("平")
            else:
                results.append("负")
        
        # 模拟赔率变化
        odds_trend = np.random.normal(2.0, 0.3, days)
        odds_trend = np.clip(odds_trend, 1.1, 5.0)
        
        # 模拟进球数
        goals_scored = np.random.poisson(1.5, days)
        goals_conceded = np.random.poisson(1.2, days)
        
        return {
            "dates": dates,
            "results": results,
            "odds_trend": odds_trend.tolist(),
            "goals_scored": goals_scored.tolist(),
            "goals_conceded": goals_conceded.tolist()
        }
        
    except Exception as e:
        st.error(f"获取历史数据失败: {str(e)}")
        return None

# ====== 投注计算函数 ======
def calculate_bet_return(bet_type: str, matches: List[Dict], stake: float) -> Dict:
    """
    计算投注回报
    
    参数:
        bet_type: 投注类型 - 'single', 'multiple', 'system'
        matches: 比赛列表
        stake: 投注金额
        
    返回:
        计算结果字典
    """
    try:
        if not matches:
            return {"total_odds": 0, "potential_return": 0, "potential_profit": -stake}
        
        if bet_type == "single":
            # 单关计算
            match = matches[0]
            odds = match["odds"]["win"] if match["selection"] == "主胜" else \
                   match["odds"]["draw"] if match["selection"] == "平局" else \
                   match["odds"]["lose"]
            
            total_odds = odds
            potential_return = stake * odds
            potential_profit = potential_return - stake
            
        elif bet_type == "multiple":
            # 串关计算
            total_odds = 1.0
            for match in matches:
                odds = match["odds"]["win"] if match["selection"] == "主胜" else \
                       match["odds"]["draw"] if match["selection"] == "平局" else \
                       match["lose"]
                total_odds *= odds
            
            potential_return = stake * total_odds
            potential_profit = potential_return - stake
            
        elif bet_type == "system":
            # 系统投注计算（例如2串1、3串4等）
            # 这里简化处理，实际应用需要更复杂的组合计算
            n = len(matches)
            if n < 2:
                return {"total_odds": 0, "potential_return": 0, "potential_profit": -stake}
            
            # 计算所有可能的2串1组合
            combinations = []
            for i in range(n):
                for j in range(i+1, n):
                    combo_odds = 1.0
                    for k in [i, j]:
                        match = matches[k]
                        odds = match["odds"]["win"] if match["selection"] == "主胜" else \
                               match["odds"]["draw"] if match["selection"] == "平局" else \
                               match["lose"]
                        combo_odds *= odds
                    combinations.append(combo_odds)
            
            # 平均赔率
            avg_odds = sum(combinations) / len(combinations) if combinations else 0
            
            # 假设每注金额相等
            num_bets = len(combinations)
            per_bet_stake = stake / num_bets
            potential_return = sum([per_bet_stake * odds for odds in combinations])
            potential_profit = potential_return - stake
            
            total_odds = avg_odds
        
        else:
            return {"total_odds": 0, "potential_return": 0, "potential_profit": -stake}
        
        return {
            "total_odds": round(total_odds, 2),
            "potential_return": round(potential_return, 2),
            "potential_profit": round(potential_profit, 2),
            "matches_count": len(matches)
        }
        
    except Exception as e:
        st.error(f"计算错误: {str(e)}")
        return {"total_odds": 0, "potential_return": 0, "potential_profit": -stake}

def add_to_bet_slip(match_id: int, selection: str, odds: float):
    """添加到投注单"""
    for match in st.session_state.bet_slip:
        if match["match_id"] == match_id:
            match["selection"] = selection
            match["odds"] = odds
            return
    
    # 查找比赛信息
    live_matches = fetch_live_matches()
    match_info = next((m for m in live_matches if m["id"] == match_id), None)
    
    if match_info:
        st.session_state.bet_slip.append({
            "match_id": match_id,
            "league": match_info["league"],
            "home_team": match_info["home_team_cn"],
            "away_team": match_info["away_team_cn"],
            "selection": selection,
            "odds": odds,
            "time": match_info["start_time"]
        })
        st.success(f"已添加到投注单！")

def remove_from_bet_slip(match_id: int):
    """从投注单移除"""
    st.session_state.bet_slip = [m for m in st.session_state.bet_slip if m["match_id"] != match_id]

# ====== 可视化函数 ======
def create_odds_chart(matches_data: List[Dict]):
    """创建赔率变化图表"""
    if not matches_data:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('胜平负赔率分布', '让球赔率分布', '赔率变化趋势', '比赛状态分布'),
        specs=[[{'type': 'pie'}, {'type': 'pie'}],
               [{'type': 'scatter'}, {'type': 'bar'}]]
    )
    
    # 提取数据
    win_odds = []
    draw_odds = []
    lose_odds = []
    status_counts = {}
    
    for match in matches_data:
        win_odds.append(match["odds"]["win"])
        draw_odds.append(match["odds"]["draw"])
        lose_odds.append(match["odds"]["lose"])
        
        status = match["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # 1. 胜平负赔率分布
    avg_win = np.mean(win_odds)
    avg_draw = np.mean(draw_odds)
    avg_lose = np.mean(lose_odds)
    
    fig.add_trace(
        go.Pie(
            labels=['主胜', '平局', '客胜'],
            values=[avg_win, avg_draw, avg_lose],
            hole=0.4,
            marker_colors=['#00b894', '#fdcb6e', '#e17055']
        ),
        row=1, col=1
    )
    
    # 2. 让球赔率分布（示例数据）
    handicap_data = matches_data[0]["odds"]["handicap"]
    fig.add_trace(
        go.Pie(
            labels=['主胜', '平局', '客胜'],
            values=[handicap_data["home"], handicap_data["draw"], handicap_data["away"]],
            hole=0.4,
            marker_colors=['#6c5ce7', '#a29bfe', '#74b9ff']
        ),
        row=1, col=2
    )
    
    # 3. 赔率变化趋势
    fig.add_trace(
        go.Scatter(
            x=list(range(len(win_odds))),
            y=win_odds,
            mode='lines+markers',
            name='主胜赔率',
            line=dict(color='#00b894')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(len(draw_odds))),
            y=draw_odds,
            mode='lines+markers',
            name='平局赔率',
            line=dict(color='#fdcb6e')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(len(lose_odds))),
            y=lose_odds,
            mode='lines+markers',
            name='客胜赔率',
            line=dict(color='#e17055')
        ),
        row=2, col=1
    )
    
    # 4. 比赛状态分布
    fig.add_trace(
        go.Bar(
            x=list(status_counts.keys()),
            y=list(status_counts.values()),
            marker_color=['#e74c3c' if k == '进行中' else 
                         '#27ae60' if k == '已结束' else 
                         '#3498db' for k in status_counts.keys()]
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

def create_team_analysis_chart(historical_data: Dict):
    """创建球队分析图表"""
    if not historical_data:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('近期战绩', '赔率趋势', '进球分布', '得失球对比'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'histogram'}, {'type': 'bar'}]]
    )
    
    dates = historical_data["dates"]
    results = historical_data["results"]
    odds_trend = historical_data["odds_trend"]
    goals_scored = historical_data["goals_scored"]
    goals_conceded = historical_data["goals_conceded"]
    
    # 1. 近期战绩
    result_counts = {"胜": results.count("胜"), "平": results.count("平"), "负": results.count("负")}
    fig.add_trace(
        go.Bar(
            x=list(result_counts.keys()),
            y=list(result_counts.values()),
            marker_color=['#00b894', '#fdcb6e', '#e17055']
        ),
        row=1, col=1
    )
    
    # 2. 赔率趋势
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=odds_trend,
            mode='lines+markers',
            name='赔率趋势',
            line=dict(color='#6c5ce7')
        ),
        row=1, col=2
    )
    
    # 3. 进球分布
    fig.add_trace(
        go.Histogram(
            x=goals_scored,
            nbinsx=10,
            name='进球数分布',
            marker_color='#00b894'
        ),
        row=2, col=1
    )
    
    # 4. 得失球对比
    fig.add_trace(
        go.Bar(
            x=dates[-10:],  # 最近10场
            y=goals_scored[-10:],
            name='进球',
            marker_color='#00b894'
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=dates[-10:],
            y=goals_conceded[-10:],
            name='失球',
            marker_color='#e17055'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig

# ====== Streamlit界面 ======
def main():
    """主应用界面"""
    
    # 页头
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown("# ⚽ 足球体彩投注计算器")
    with col2:
        st.markdown(f"### 📅 {now_beijing.strftime('%Y年%m月%d日 %H:%M')}")
    with col3:
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 🎯 投注设置")
        
        # 投注类型选择
        bet_type = st.selectbox(
            "选择投注类型",
            ["单关", "串关", "系统投注"],
            index=0
        )
        
        # 投注金额
        stake = st.number_input(
            "投注金额 (元)",
            min_value=2.0,
            max_value=10000.0,
            value=100.0,
            step=10.0
        )
        
        # 联赛筛选
        selected_leagues = st.multiselect(
            "筛选联赛",
            list(leagues.keys()),
            default=["英超", "西甲", "意甲"]
        )
        
        st.markdown("---")
        
        # 投注单
        st.markdown("## 📝 当前投注单")
        if st.session_state.bet_slip:
            for i, bet in enumerate(st.session_state.bet_slip):
                with st.expander(f"{bet['home_team']} vs {bet['away_team']}"):
                    st.write(f"**选择:** {bet['selection']}")
                    st.write(f"**赔率:** {bet['odds']}")
                    st.write(f"**联赛:** {bet['league']}")
                    st.write(f"**时间:** {bet['time']}")
                    if st.button(f"移除", key=f"remove_{i}"):
                        remove_from_bet_slip(bet['match_id'])
                        st.rerun()
            
            # 计算按钮
            if st.button("💰 计算奖金", type="primary", use_container_width=True):
                if st.session_state.bet_slip:
                    bet_type_map = {"单关": "single", "串关": "multiple", "系统投注": "system"}
                    result = calculate_bet_return(
                        bet_type_map[bet_type],
                        st.session_state.bet_slip,
                        stake
                    )
                    
                    # 保存到历史记录
                    st.session_state.calculation_history.append({
                        "timestamp": now_beijing.strftime("%Y-%m-%d %H:%M"),
                        "bet_type": bet_type,
                        "matches": len(st.session_state.bet_slip),
                        "stake": stake,
                        "total_odds": result["total_odds"],
                        "potential_return": result["potential_return"],
                        "potential_profit": result["potential_profit"]
                    })
                    
                    st.success("计算完成！")
                else:
                    st.warning("投注单为空！")
        else:
            st.info("投注单为空，请选择比赛添加到投注单")
        
        st.markdown("---")
        
        # 历史计算记录
        if st.session_state.calculation_history:
            st.markdown("## 📊 历史计算")
            for i, record in enumerate(st.session_state.calculation_history[-5:]):  # 显示最近5条
                profit_class = "profit-positive" if record["potential_profit"] > 0 else "profit-negative"
                st.markdown(f"""
                **{record['timestamp']}**
                - 类型: {record['bet_type']}
                - 场次: {record['matches']}
                - 金额: ¥{record['stake']}
                - 总赔率: {record['total_odds']}
                - 预期回报: ¥{record['potential_return']}
                - <span class="{profit_class}">预期盈利: ¥{record['potential_profit']}</span>
                """, unsafe_allow_html=True)
        
        # 清除按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("清空投注单", use_container_width=True):
                st.session_state.bet_slip.clear()
                st.rerun()
        with col2:
            if st.button("清除缓存", use_container_width=True):
                st.cache_data.clear()
                st.success("缓存已清除")
    
    # 主内容区
    # 实时赛事标签页
    tab1, tab2, tab3 = st.tabs(["📺 实时赛事", "📈 数据分析", "💰 投注计算器"])
    
    with tab1:
        st.markdown("## 🏆 今日足球赛事")
        
        # 获取比赛数据
        with st.spinner("加载赛事数据..."):
            matches = fetch_live_matches()
            
            # 按联赛筛选
            if selected_leagues:
                matches = [m for m in matches if m["league"] in selected_leagues]
        
        if not matches:
            st.info("今日暂无赛事")
        else:
            # 显示比赛卡片
            for match in matches:
                with st.container():
                    st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([3, 2, 3])
                    
                    with col1:
                        st.markdown(f"### {match['home_team_cn']}")
                        st.markdown(f"**{match['league']}**")
                    
                    with col2:
                        # 比赛状态和比分
                        status_class = "status-live" if match["status"] == "进行中" else \
                                      "status-finished" if match["status"] == "已结束" else \
                                      "status-scheduled"
                        
                        if match["status"] in ["进行中", "已结束"]:
                            st.markdown(f"<h2 style='text-align: center;'>{match['home_score']} - {match['away_score']}</h2>", 
                                       unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h4 style='text-align: center;'>{match['start_time']}</h4>", 
                                       unsafe_allow_html=True)
                        
                        st.markdown(f"<p class='{status_class}' style='text-align: center;'>{match['status']}</p>", 
                                   unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"### {match['away_team_cn']}")
                        st.markdown(f"**比赛ID: {match['id']}**")
                    
                    st.markdown("---")
                    
                    # 赔率显示
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown('<div class="odds-card">', unsafe_allow_html=True)
                        st.markdown(f"**主胜**")
                        st.markdown(f"### {match['odds']['win']}")
                        if st.button(f"选择主胜", key=f"win_{match['id']}", use_container_width=True):
                            add_to_bet_slip(match['id'], "主胜", match['odds']['win'])
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="odds-card">', unsafe_allow_html=True)
                        st.markdown(f"**平局**")
                        st.markdown(f"### {match['odds']['draw']}")
                        if st.button(f"选择平局", key=f"draw_{match['id']}", use_container_width=True):
                            add_to_bet_slip(match['id'], "平局", match['odds']['draw'])
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="odds-card">', unsafe_allow_html=True)
                        st.markdown(f"**客胜**")
                        st.markdown(f"### {match['odds']['lose']}")
                        if st.button(f"选择客胜", key=f"lose_{match['id']}", use_container_width=True):
                            add_to_bet_slip(match['id'], "客胜", match['odds']['lose'])
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown('<div class="odds-card">', unsafe_allow_html=True)
                        st.markdown(f"**让球**")
                        st.markdown(f"主: {match['odds']['handicap']['home']}")
                        st.markdown(f"平: {match['odds']['handicap']['draw']}")
                        st.markdown(f"客: {match['odds']['handicap']['away']}")
                        if st.button(f"详细", key=f"handicap_{match['id']}", use_container_width=True):
                            st.session_state[f"show_handicap_{match['id']}"] = True
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 显示让球详细赔率
                    if st.session_state.get(f"show_handicap_{match['id']}", False):
                        with st.expander("让球赔率详情"):
                            hc = match['odds']['handicap']
                            st.write(f"主胜: {hc['home']}")
                            st.write(f"平局: {hc['draw']}")
                            st.write(f"客胜: {hc['away']}")
                            if st.button("关闭", key=f"close_hc_{match['id']}"):
                                st.session_state[f"show_handicap_{match['id']}"] = False
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## 📊 数据统计分析")
        
        # 赔率分析图表
        if matches:
            st.markdown("### 📈 赔率数据分析")
            fig = create_odds_chart(matches)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 球队历史数据分析
            st.markdown("### 🏅 球队历史数据")
            selected_team = st.selectbox(
                "选择球队分析",
                list(set([m["home_team_cn"] for m in matches] + [m["away_team_cn"] for m in matches]))
            )
            
            if selected_team:
                with st.spinner(f"加载 {selected_team} 的历史数据..."):
                    historical_data = fetch_historical_data(selected_team)
                    
                    if historical_data:
                        # 显示基本统计
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("近期胜率", f"{historical_data['results'].count('胜')/len(historical_data['results'])*100:.1f}%")
                        with col2:
                            st.metric("平均进球", f"{np.mean(historical_data['goals_scored']):.1f}")
                        with col3:
                            st.metric("平均失球", f"{np.mean(historical_data['goals_conceded']):.1f}")
                        with col4:
                            st.metric("平均赔率", f"{np.mean(historical_data['odds_trend']):.2f}")
                        
                        # 显示图表
                        fig2 = create_team_analysis_chart(historical_data)
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.warning("暂无该球队的历史数据")
        else:
            st.info("暂无赛事数据可供分析")
    
    with tab3:
        st.markdown("## 🧮 高级投注计算器")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
            st.markdown("### 自定义投注组合")
            
            # 动态添加比赛
            num_matches = st.slider("选择比赛场次", 1, 8, 3)
            
            bet_entries = []
            for i in range(num_matches):
                st.markdown(f"#### 比赛 {i+1}")
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    home_team = st.text_input(f"主队 {i+1}", f"球队A_{i+1}")
                
                with col_b:
                    selection = st.selectbox(f"选择 {i+1}", ["主胜", "平局", "客胜"], key=f"sel_{i}")
                
                with col_c:
                    odds = st.number_input(f"赔率 {i+1}", min_value=1.1, max_value=50.0, 
                                          value=2.0 + i*0.2, step=0.1, key=f"odds_{i}")
                
                bet_entries.append({
                    "home_team": home_team,
                    "selection": selection,
                    "odds": odds
                })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="calculator-card">', unsafe_allow_html=True)
            st.markdown("### 计算结果")
            
            if bet_entries and stake > 0:
                # 转换数据格式
                calc_matches = []
                for entry in bet_entries:
                    calc_matches.append({
                        "selection": entry["selection"],
                        "odds": {"win": entry["odds"] if entry["selection"] == "主胜" else 2.0,
                                "draw": entry["odds"] if entry["selection"] == "平局" else 2.0,
                                "lose": entry["odds"] if entry["selection"] == "客胜" else 2.0}
                    })
                
                # 计算不同类型
                bet_type_map = {"单关": "single", "串关": "multiple", "系统投注": "system"}
                result = calculate_bet_return(
                    bet_type_map[bet_type],
                    calc_matches,
                    stake
                )
                
                st.metric("总赔率", f"{result['total_odds']:.2f}")
                st.metric("投注金额", f"¥{stake:.2f}")
                st.metric("预期回报", f"¥{result['potential_return']:.2f}")
                
                profit_color = "profit-positive" if result["potential_profit"] > 0 else "profit-negative"
                st.markdown(f"<h3 class='{profit_color}'>预期盈利: ¥{result['potential_profit']:.2f}</h3>", 
                          unsafe_allow_html=True)
                
                # 预期回报率
                if stake > 0:
                    roi = (result["potential_return"] - stake) / stake * 100
                    st.metric("预期回报率", f"{roi:.1f}%")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 投注策略建议
        st.markdown("## 💡 投注策略建议")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("🏆 热门策略"):
                st.write("""
                1. **价值投注**: 寻找赔率被低估的比赛
                2. **均注策略**: 每次投注固定金额
                3. **跟随趋势**: 关注连胜球队
                """)
        
        with col2:
            with st.expander("📊 数据分析"):
                st.write("""
                1. 分析球队近期状态
                2. 查看历史交锋记录
                3. 关注伤病和停赛情况
                4. 考虑主客场优势
                """)
        
        with col3:
            with st.expander("⚠️ 风险管理"):
                st.write("""
                1. 设置投注上限
                2. 避免情绪化投注
                3. 分散投资多场比赛
                4. 记录投注历史
                """)
    
    # 页脚
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("📱 手机优化 | 实时更新")
    with col2:
        st.caption(f"🔄 最后更新: {now_beijing.strftime('%H:%M:%S')}")
    with col3:
        st.caption("⚽ 数据仅供参考，投注需谨慎")

# 运行应用
if __name__ == "__main__":
    main()