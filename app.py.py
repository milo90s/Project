import streamlit as st
import requests
import pandas as pd
import time

# Streamlit UI Setup
st.set_page_config(page_title="Lead-Maschine für pb.socialhouse", page_icon="🚀", layout="wide")

st.title("🚀 pb.socialhouse – B2B Lead-Generator Oberösterreich")
st.subheader("Echte Live-Daten: KMUs ohne eigene Website")
st.write("---")

# Eingabemaske für die Suche
col1, col2 = st.columns(2)
with col1:
    # Optimiert auf konkrete Städte in OÖ für echte, blitzschnelle Treffer
    region = st.selectbox(
        "Stadt / Gemeinde in OÖ wählen:",
        [
            "Linz", "Leonding", "Wels", "Steyr", "Traun", "Enns", 
            "Vöcklabruck", "Gmunden", "Braunau am Inn", "Ried im Innkreis", 
            "Schärding", "Grieskirchen", "Freistadt", "Perg", "Ansfelden", "Bad Ischl"
        ]
    )
with col2:
    branche = st.selectbox(
        "Branche wählen:",
        ["craftsman", "restaurant", "hairdresser", "car_repair"],
        format_func=lambda x: {
            "craftsman": "Handwerker (Tischler, Fliesenleger etc.)",
            "restaurant": "Gastronomie / Restaurants",
            "hairdresser": "Friseure / Beauty",
            "car_repair": "KFZ-Werkstätten"
        }[x]
    )

if st.button("🔍 Region live scannen", type="primary"):
    with st.spinner(f"Suche echte Betriebe in {region}..."):
        
        # Overpass API Query - Jetzt absolut präzise auf Stadtgrenzen geschärft
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:20];
        area[name="{region}"][boundary=administrative]->.searchArea;
        (
          node["shop"="{branche}"](area.searchArea);
          way["shop"="{branche}"](area.searchArea);
          node["amenity"="{branche}"](area.searchArea);
          way["amenity"="{branche}"](area.searchArea);
        );
        out tags;
        """
        
        leads = []
        api_failed = False
        
        try:
            response = requests.post(overpass_url, data={'data': overpass_query}, timeout=18)
            data = response.json()
            
            if "elements" in data:
                for element in data["elements"]:
                    tags = element.get("tags", {})
                    # FILTER: Nur Betriebe OHNE Website
                    if "website" not in tags and "contact:website" not in tags:
                        name = tags.get("name")
                        if name: # Nur hinzufügen, wenn ein echter Name existiert
                            phone = tags.get("phone", tags.get("contact:phone", "Nicht hinterlegt"))
                            street = tags.get("addr:street", "")
                            hnr = tags.get("addr:housenumber", "")
                            address = f"{street} {hnr}, {region}".strip() if street else f"Bereich {region}"
                            
                            leads.append({
                                "Firmenname": name,
                                "Branche": {
                                    "craftsman": "Handwerk",
                                    "restaurant": "Gastronomie",
                                    "hairdresser": "Friseur / Beauty",
                                    "car_repair": "KFZ-Werkstatt"
                                }.get(branche, branch.capitalize()),
                                "Telefonnummer": phone,
                                "Adresse": address,
                                "Status": "❌ Keine Website"
                            })
        except Exception:
            api_failed = True

        # Falls wirklich mal gar nichts gefunden wird oder die API blockiert
        if api_failed:
            st.error("Der Live-Server ist gerade überlastet. Bitte versuche es in wenigen Sekunden noch einmal.")
        elif len(leads) == 0:
            st.info(f"In {region} wurden aktuell alle Betriebe dieser Branche mit einer Website gefunden – oder OpenStreetMap hat für diese Nische dort keine Daten.")
        else:
            # Daten anzeigen
            df = pd.DataFrame(leads)
            st.success(f"Erfolg! {len(df)} ECHTE Leads ohne Website in {region} gefunden.")
            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Echte Liste für {region} exportieren",
                data=csv,
                file_name=f"echte_leads_{region}.csv",
                mime='text/csv',
            )
