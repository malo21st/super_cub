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

# RDB
def get_data():
    SQL = "SELECT * FROM master;"
    df_data = pd.read_sql(SQL, conn)
    return df_data

conn = done_connection()
data = get_data()

# side_bar
sanc = "牧原交差点"
with st.sidebar:
    sanc = st.sidebar.selectbox("聖地：", list(data["anime"]))
    d = data.query(f'anime == "{sanc}"')
    idx = d["id"].values[0]
    lat, lon = d["lat"].values[0], d["lon"].values[0]
    loc = f'{lat:.3f}, {lon:.3f}'
    anime, pos, dsp, url = d["anime"].values[0], d["pos"].values[0], d["dsp"].values[0], d["url"].values[0]

    memo = dsp.replace("<br>", "  ")
    st.info(
        f"### {pos}  \n"
        f"{memo}  \n"
        f"- 緯度, 経度：{loc}  \n"
        f"- [ビュー（画像）]({url})  \n"
    )

selected = data.query(f'anime == "{sanc}"')

# map
m = folium.Map(location=[selected["lat"], selected["lon"]], zoom_start=15)

# marker 
def add_marker(map, lat, lon, anime, pos, dsp, url, sanc):
    if url:
        ph = f'<B>{anime}</B><br><B>( {pos} )</B><p>{dsp}<p><a href="{url}" target="_blank">ビュー（画像）</a>'
    else:
        ph = f'<B>{anime}</B><br><B>( {pos} )</B><p>{dsp}'
    pp = folium.Html(ph, script=True)
    popup = folium.Popup(pp, max_width=200)
    tooltip = f"<B>{anime}</B><br>( {pos} )"
    color = "red" if anime == sanc else "blue"
    folium.Marker(
        [lat, lon], popup=popup, tooltip=tooltip, icon=folium.Icon(color=color)
    ).add_to(map)
    return map

for _, d in data.iterrows():
    m = add_marker(m, d["lat"], d["lon"], d["anime"], d["pos"], d["dsp"], d["url"], sanc)

# layout
st.title("アニメ「スーパーカブ」聖地巡礼マップ")
folium_static(m)
with st.beta_expander("お願い・お知らせ"):
    st.warning(
    	"- 聖地巡礼の際は、学校、お店、近隣住民の方にご迷惑とならないように**節度ある行動とマナー**に十分心がけて下さい。  \n"
    	"- [アニメ「スーパーカブ」公式サイト](https://supercub-anime.com/)  \n"
        "- アニメの場面と写真を見比べることができます。  \n"
        "  [【聖地巡礼】スーパーカブ（週末ひとり旅）](http://blog.livedoor.jp/nadukari/archives/28700950.html)  \n"
    	"- このサイトの作者のTwitter：[@malo21st](https://twitter.com/malo21st)  \n"
    )
