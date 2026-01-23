import google.generativeai as genai
import pandas as pd
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from dotenv import load_dotenv

load_dotenv()

class CodeGeneratorAgent:
    """Agent 3 : Génère le code Plotly pour la visualisation choisie"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-flash-latest")

    async def generate_visualization(self, proposal: dict, csv_data: str) -> dict:
        """
        Génère le code Plotly et retourne le JSON du graphique
        """

        # Lecture du CSV
        df = pd.read_csv(StringIO(csv_data))

        # Sécurité : forcer les colonnes numériques quand possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        prompt = f"""
Tu es un expert Plotly.

VISUALISATION DEMANDÉE :
- Titre : {proposal['title']}
- Type : {proposal['chart_type']}
- Variables : {proposal['variables']}

COLONNES DISPONIBLES : {list(df.columns)}
PREMIÈRES LIGNES :
{df.head().to_string()}

CONSIGNES STRICTES :
1. Utilise plotly.express ou plotly.graph_objects
2. Le DataFrame s'appelle EXACTEMENT 'df'
3. Le code DOIT créer une variable 'fig'
4. Ne fais PAS de calculs inutiles
5. Si price et sales existent, calcule revenue = price * sales
6. Titre, axes et légendes propres
7. Aucune impression texte

Réponds UNIQUEMENT avec du code Python exécutable.
"""

        response = self.model.generate_content(prompt)
        code = response.text.strip()

        # Nettoyage du markdown si présent
        if "```" in code:
            code = code.split("```")[1].strip()

        try:
            # Exécution sécurisée du code généré
            local_scope = {
                "df": df,
                "px": px,
                "go": go,
                "pd": pd
            }

            exec(code, local_scope)
            fig = local_scope.get("fig")

            # Validation forte du graphique
            if fig is None or not hasattr(fig, "data") or len(fig.data) == 0:
                raise ValueError("Figure Plotly vide ou invalide")

            return {
                "plotly_json": json.loads(fig.to_json()),
                "code": code
            }

        except Exception as e:
            # 🔥 FALLBACK INTELLIGENT ET PROPRE
            if "price" in df.columns and "sales" in df.columns:
                df["revenue"] = df["price"] * df["sales"]
                fig = px.bar(
                    df,
                    x="product" if "product" in df.columns else df.columns[0],
                    y="revenue",
                    title="Chiffre d'affaires par produit",
                    labels={"revenue": "Revenue"}
                )
            else:
                fig = px.bar(
                    df,
                    x=df.columns[0],
                    y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
                    title=proposal["title"]
                )

            return {
                "plotly_json": json.loads(fig.to_json()),
                "code": f"# Fallback utilisé\n# Erreur : {str(e)}\n{code}"
            }
