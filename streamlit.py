import streamlit as st
import pandas as pd
import mysql.connector

# df = pd.read_csv('suara.csv')
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="uastol2"
)

# Membaca data dari tabel dalam database
query = "SELECT * FROM detect"
df = pd.read_sql(query, conn)

option = st.sidebar.selectbox(
    'Silakan pilih:',
    ('Home','Chart')
)

if option == 'Home' or option == '':
    st.write("# Halaman Utama")
    st.write("## Data 3 baris pertama")
    st.write(df.head(3))  # Menampilkan 3 baris pertama

elif option == 'Chart':
    st.write("""## Dataframe""")
    data = df.iloc[:, [1,2]]
    st.write(data)


    st.write("""## GRAFIK""")
    chart = pd.DataFrame(df['jumlah kendaraan'].value_counts())
    st.bar_chart(chart)


#kategori berdasarkan jumlah bukan

# elif option == 'Chart':
#     st.write("""# Draw Charts""")
#     df = pd.DataFrame(
#         df,
#         columns=['jumlah','emosi']
#     )
#     fig, ax = plt.subplots()
#     df.plot.bar(x = 'jumlah', y = ['emosi'], rot = 90, ax = ax)
#     for p in ax.patches: 
#         ax.annotate(np.round(p.get_height(),decimals=2), (p.get_x()+p.get_width()/2., p.get_height()))
#     st.pyplot(fig) #menampilkan chart
#     st.write("""## Dataframe""") #menampilkan judul halaman dataframe
#     df
#     st.line_chart(data)
#     data
conn.close()