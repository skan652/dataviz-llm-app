import json
import pandas as pd
import google.generativeai as genai


class DataAnalystAgent:
    def __init__(self, model_name: str = "models/gemini-flash-latest"):
        genai.configure(api_key=None)  # clé déjà gérée ailleurs si besoin
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, df: pd.DataFrame, user_question: str) -> dict:
        """
        Analyse le dataset et retourne :
        - insights
        - relevant_columns
        - recommended_approach
        """

        # -----------------------------
        # 1️⃣ Préparer le prompt
        # -----------------------------
        prompt = f"""
Tu es un data analyst expert.
Analyse le dataset CSV suivant et réponds à la question utilisateur.

QUESTION UTILISATEUR :
{user_question}

COLONNES DISPONIBLES :
{list(df.columns)}

TYPES DE DONNÉES :
{df.dtypes.to_dict()}

STATISTIQUES NUMÉRIQUES :
{df.describe(include='number').to_dict()}

CONTRAINTES IMPORTANTES :
- Réponds UNIQUEMENT en JSON valide
- Ne mets AUCUN texte hors JSON
- Structure attendue EXACTE :

{{
  "insights": "texte synthétique",
  "relevant_columns": ["col1", "col2"],
  "recommended_approach": "description de l'approche analytique"
}}
"""

        # -----------------------------
        # 2️⃣ Appel Gemini
        # -----------------------------
        response = self.model.generate_content(prompt)

        print("=== GEMINI RAW RESPONSE (DataAnalystAgent) ===")
        print(response.text)
        print("============================================")

        # -----------------------------
        # 3️⃣ Sécurisation de la réponse
        # -----------------------------
        text = response.text

        if not text:
            print("❌ Gemini returned empty response")
            return self._fallback(df, "Réponse vide du modèle.")

        text = text.strip()

        # Nettoyage : garder uniquement le bloc JSON
        if "{" in text and "}" in text:
            text = text[text.find("{"): text.rfind("}") + 1]

        # -----------------------------
        # 4️⃣ Parsing JSON sécurisé
        # -----------------------------
        try:
            analysis = json.loads(text)

            # Validation minimale
            if not isinstance(analysis, dict):
                raise ValueError("JSON n'est pas un objet")

            analysis.setdefault("insights", "")
            analysis.setdefault("relevant_columns", list(df.columns))
            analysis.setdefault("recommended_approach", "Analyse exploratoire")

            print("✅ DataAnalystAgent parsing OK")
            return analysis

        except Exception as e:
            print("❌ DataAnalystAgent JSON parsing error:", e)
            print("RAW TEXT AFTER CLEANING:")
            print(text)

            return self._fallback(df, response.text)

    # -----------------------------
    # 5️⃣ Fallback sécurisé
    # -----------------------------
    def _fallback(self, df: pd.DataFrame, raw_text: str) -> dict:
        return {
            "insights": raw_text[:1000] if raw_text else "Analyse non disponible.",
            "relevant_columns": list(df.columns),
            "recommended_approach": (
                "Analyse exploratoire : agrégations, visualisations simples "
                "et inspection des relations entre variables clés."
            )
        }
