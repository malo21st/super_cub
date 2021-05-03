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

data = get_data()

# side_bar
sanc = "牧原交差点"
with st.sidebar:
    sanc = st.sidebar.selectbox("聖地：", list(data["anime"]))
    d = data.query(f'anime == "{sanc}"')
    idx = d["id"].values[0]
    lat, lon = d["lat"].values[0], d["lon"].values[0]
    loc = f'{lat:.1f}, {lon:.1f}'
    anime, pos, dsp, url = d["anime"].values[0], d["pos"].values[0], d["dsp"].values[0], d["url"].values[0]

    memo = dsp.replace("<br>", "  ")
    pos_info = f"""
### {pos}
{memo}  

緯度, 経度：{loc}
### [ストリートビュー]({url})
    """
    st.markdown("## **聖地の情報**")
    st.info(pos_info)

# center on Liberty Bell
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

# layout
st.markdown("# アニメ「スーパーカブ」聖地巡礼マップ")
folium_static(m)
