import streamlit as st
import base64

# covert the logo to base64
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

img_base64 = get_base64_image("assets/logo.png")


st.set_page_config(layout='wide')
# desgin css

st.markdown("""
<style>body {
    background-color: #0e1117;
    color: white;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #0b0f14;
    padding: 15px 25px;
    border-radius: 10px;
    margin-bottom: 10px;
    line-height:1.2;
}

.logo {
    font_family:'Cal Sans', sans-serif;
    font-size: 22px;
    font-weight: 600;
    color: white;
    letter-spacing:1.5px;
}

.run-btn {
    background-color: #7b6572;
    padding: 10px 20px;
    border-radius: 10px;
    color: white;
}

.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.result-box {
    background-color: #0f2e24;
    border: 1px solid #00c781;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: #00ff9c;
    font-size: 22px;
    font-weight: bold;
}

.sidebar .sidebar-content {
    background-color: #11161d;
}</style>
""", unsafe_allow_html=True)

# top nav bar
st.markdown(f"""
<div class="topbar">
    <div style="display:flex; align-items:center; gap:20px;">
        <img src="data:image/jpg;base64,{img_base64}" width="50">
        <div class="logo" >AUTOMETA<br>LAB</div>
    </div>
    <button class="run-btn">▶ Run Simulation</button>
</div>
""", unsafe_allow_html=True)

