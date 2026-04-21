import streamlit as st
import pandas as pd

# 1. 頁面設定
st.set_page_config(page_title="惇裕小學 5月報更管理", layout="wide")
st.title("🏫 惇裕小學 - 5月導師報更看板")

# 這裡只需要 ID，不要完整網址
SHEET_ID = "1uqDMMCinyvsSdXAYE1Dh0EZ36qVvrzhKftNHf_-vw7w"
GID = "997998162" 
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
@st.cache_data(ttl=60)
def load_data():
    # 加入這行來確保能正確下載 CSV
    df = pd.read_csv(csv_url)
    return df
try:
    df = load_data()
    
    # 提取日期欄位 (排除前面的基本資訊)
    # 假設前三欄是 時間戳記、請提供中文姓名 及 英文稱呼 Please provide your name：、電話號碼
    date_columns = [col for col in df.columns if '2026' in col]

    # --- 側邊欄：自動識別姓名欄位 ---
    st.sidebar.header("管理功能")
    
    # 自動尋找名稱包含 '姓名' 或 'name' 的欄位
    name_col = next((col for col in df.columns if '姓名' in col or 'name' in col.lower()), df.columns[1])
    
    all_tutors = df[name_col].dropna().unique()
    selected_tutor = st.sidebar.selectbox("🔍 搜尋導師紀錄", all_tutors)

    # --- 主畫面：兩種檢視模式 ---
    tab1, tab2 = st.tabs(["🗓️ 每日報更概覽", "👤 導師個人統計"])

    with tab1:
        st.subheader("選擇日期查看當天導師")
        target_date = st.selectbox("請選擇日期", date_columns)
        
        # 篩選當天有填寫內容的導師
        # 這裡的 '電話號碼' 如果也報錯，可以改成 df.columns[2] (即 C 欄)
        phone_col = next((col for col in df.columns if '電話' in col or 'Phone' in col), df.columns[2])
        
        daily_attending = df[df[target_date].notna()][[name_col, phone_col, target_date]]
        daily_attending.columns = ['導師姓名', '電話', '報更時段/備註']
        
        if not daily_attending.empty:
            st.success(f"{target_date} 共有 {len(daily_attending)} 位導師")
            st.dataframe(daily_attending, use_container_width=True)
        
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
