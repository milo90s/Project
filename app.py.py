import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Business Radar Österreich", page_icon="📈", layout="wide")
st.title("🔥 Reddit Business-Lead-Radar")

# Begriffe, nach denen wir im "Problem-Modus" suchen
search_terms = ["Webseite", "IT Support", "Automatisierung", "Marketing", "Photovoltaik"]

def get_reddit_leads(terms):
    leads = []
    # Wir nutzen eine Google-Suche, um Reddit nach diesen Begriffen in Österreich zu durchsuchen
    # Das umgeht die komplizierte API-Registrierung für den Anfang
    for term in terms:
        url = f"https://www.google.com/search?q=site:reddit.com/r/Austria+{term}+suche+hilfe"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and 'reddit.com' in href and '/comments/' in href:
                    leads.append({"Begriff": term, "Reddit-Link": href})
                    break # Nur den ersten relevanten Link pro Begriff
        except:
            pass
    return pd.DataFrame(leads)

if st.button("🔍 Reddit-Schmerzpunkte scannen"):
    with st.spinner("Durchsuche Reddit nach Leads..."):
        df_leads = get_reddit_leads(search_terms)
        if not df_leads.empty:
            st.success("Gefundene Diskussionen mit potenziellen Leads:")
            st.dataframe(df_leads, column_config={"Reddit-Link": st.column_config.LinkColumn()}, use_container_width=True)
            st.write("💡 **Tipp:** Klicke auf die Links, lies die Kommentare und schaue, ob du eine Lösung für das Problem hast!")
        else:
            st.info("Aktuell keine passenden Diskussionen gefunden.")
