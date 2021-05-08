import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import sqlite3

DB = "scub_map.db"

# RDBとのコネクションを確立
@st.cache(allow_output_mutation=True)
def done_connection():
    return sqlite3.connect(DB, check_same_thread=False)

conn = done_connection()

# RDB
def get_data():
    SQL = "SELECT * FROM master;"
    df_data = pd.read_sql(SQL, conn)
    return df_data

def update_db(idx, lat, lon, anime, pos, dsp, url):
    if idx:
        SQL = f'UPDATE master SET lat={lat}, lon={lon}, anime="{anime}", pos="{pos}", dsp="{dsp}", url="{url}" WHERE id={idx}'
    else:
        SQL = f'INSERT INTO master (lat, lon, anime, pos, dsp, url) VALUES ("{lat}", "{lon}", "{anime}", "{pos}", "{dsp}", "{url}");'
    try:  
        conn.execute(SQL)
    except Exception as e:
        st.text("異常終了")
        st.text(e)
    conn.commit()

data = get_data()

# side_bar
sanc = st.sidebar.selectbox("聖地：", ["【新規登録】"] + list(data["anime"]))
if sanc == "【新規登録】":
    idx = 0
    loc, anime, pos, dsp, url = "", "", "", "", ""
else:
    d = data.query(f'anime == "{sanc}"')
    idx = d["id"].values[0]
    lat, lon = d["lat"].values[0], d["lon"].values[0]
    loc = f'{lat}, {lon}'
    anime, pos, dsp, url = d["anime"].values[0], d["pos"].values[0], d["dsp"].values[0], d["url"].values[0]

st.sidebar.markdown("## 登録・編集")
loc = st.sidebar.text_input('緯度, 経度：', value=loc)
anime = st.sidebar.text_input('アニメの場所：', value=anime)
pos = st.sidebar.text_input('実際の場所：', value=pos)
dsp = st.sidebar.text_area('メモ：', value=dsp)
url = st.sidebar.text_input('ストリートビューのURL：', value=url)
btn = st.sidebar.button('実行')

# center on Liberty Bell
if sanc == "【新規登録】":
    selected = data.query(f'anime == "牧原交差点"')
else:
    selected = data.query(f'anime == "{sanc}"')

m = folium.Map(location=[selected["lat"], selected["lon"]], zoom_start=15)

# add marker for Liberty Bell
def add_marker(map, lat, lon, anime, pos, dsp, url, sanc):
    if url:
        ph = f'<B>{anime}</B><br><B>( {pos} )</B><p>{dsp}<p><a href="{url}" target="_blank">ビュー</a>'
    else:
        ph = f'<B>{anime}</B><br><B>( {pos} )</B><p>{dsp}'
    pp = folium.Html(ph, script=True)
    popup = folium.Popup(pp, max_width=160)
    tooltip = f"<B>{anime}</B><br>( {pos} )"
    color = "red" if anime == sanc else "blue"
    folium.Marker(
        [lat, lon], popup=popup, tooltip=tooltip, icon=folium.Icon(color=color)
    ).add_to(map)
    return map

for _, d in data.iterrows():
    m = add_marker(m, d["lat"], d["lon"], d["anime"], d["pos"], d["dsp"], d["url"], sanc)

if btn:
    if loc:
        lat_lon = [float(l) for l in loc.split(",")]
        m = add_marker(m, lat_lon[0], lat_lon[1], anime, pos, dsp, url, anime)
        update_db(idx, lat_lon[0], lat_lon[1], anime, pos, dsp, url)
        data = get_data()

# layout
st.markdown("# アニメ「スーパーカブ」聖地巡礼マップ")
folium_static(m)
