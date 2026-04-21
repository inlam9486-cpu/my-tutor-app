import streamlit as st
import pandas as pd

# 1. 頁面設定
st.set_page_config(page_title="惇裕小學 5月報更管理", layout="wide")
st.title("🏫 惇裕小學 - 5月導師報更看板")

# 這裡直接使用你提供的試算表 ID 和正確的頁籤 GID
SHEET_ID = "1uqDMMCinyvsSdXAYE1Dh0EZ36qVvrzhKftNHf_-vw7w"
GID = "997998162" # 這是 5月報更 Report (回覆) 的分頁 ID
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=60)
def load_data():
    # 加入這行來確保能正確下載 CSV
    df = pd.read_csv(csv_url)
    return df
try:
    df = load_data()
    
    # 提取日期欄位 (排除前面的基本資訊)
    # 假設前三欄是 時間戳記、中文姓名、電話號碼
    date_columns = [col for col in df.columns if '2026' in col]

    # --- 側邊欄：導師搜尋 ---
    st.sidebar.header("管理功能")
    all_tutors = df['中文姓名'].dropna().unique()
    selected_tutor = st.sidebar.selectbox("🔍 搜尋導師紀錄", all_tutors)

    # --- 主畫面：兩種檢視模式 ---
    tab1, tab2 = st.tabs(["🗓️ 每日報更概覽", "👤 導師個人統計"])

    with tab1:
        st.subheader("選擇日期查看當天導師")
        target_date = st.selectbox("請選擇日期", date_columns)
        
        # 篩選當天有填寫內容（不為空）的導師
        daily_attending = df[df[target_date].notna()][['中文姓名', '電話號碼', target_date]]
        daily_attending.columns = ['導師姓名', '電話', '報更時段/備註']
        
        if not daily_attending.empty:
            st.success(f"{target_date} 共有 {len(daily_attending)} 位導師")
            st.dataframe(daily_attending, use_container_width=True)
        else:
            st.info("當天暫時沒有導師報更。")

    with tab2:
        st.subheader(f"{selected_tutor} 的報更詳情")
        tutor_row = df[df['中文姓名'] == selected_tutor]
        
        # 整理該導師有報更的日期
        tutor_schedule = []
        for date in date_columns:
            status = tutor_row[date].values[0]
            if pd.notna(status):
                tutor_schedule.append({"日期": date, "內容/時段": status})
        
        if tutor_schedule:
            st.metric("本月總報更天數", len(tutor_schedule))
            st.table(pd.DataFrame(tutor_schedule))
        else:
            st.warning("該導師本月尚未有報更紀錄。")

except Exception as e:
    st.error("讀取試算表失敗，請確保該 Google 試算表已開啟「知道連結的人即可檢視」權限。")
