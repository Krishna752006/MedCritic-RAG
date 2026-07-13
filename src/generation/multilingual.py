class MultilingualService:
    def __init__(self):
        # High fidelity vocabulary translations dictionary containing common medical headings
        self.glossary = {
            "hi": {  # Hindi
                "CLINICAL INTERPRETATION REPORT": "नैदानिक व्याख्या रिपोर्ट (चिकित्सक रजिस्टर)",
                "Active Findings Count": "सक्रिय निष्कर्षों की संख्या",
                "Extracted Clinical Values": "निष्कर्षित नैदानिक मूल्य",
                "Reference Guidelines Retained": "संबद्ध चिकित्सा दिशानिर्देश",
                "Recommended Physician Action Plan": "अनुशंसित चिकित्सक कार्य योजना",
                "PATIENT GLOSSARY & PERSONAL HEALTH INSIGHTS": "सुलभ शब्दावली और स्वास्थ्य संबंधी दृष्टिकोण",
                "HEALTH ACTIONS TO DISCUSS": "स्वास्थ्य संबंधी कदम जिन पर चर्चा करें"
            },
            "es": {  # Spanish
                "CLINICAL INTERPRETATION REPORT": "INFORME DE INTERPRETACIÓN CLÍNICA (REGISTRO MÉDICO)",
                "Active Findings Count": "Recuento de hallazgos activos",
                "Extracted Clinical Values": "Valores clínicos y ontologías extraídos",
                "Reference Guidelines Retained": "Directrices de referencia conservadas",
                "Recommended Physician Action Plan": "Plan de acción médico recomendado",
                "PATIENT GLOSSARY & PERSONAL HEALTH INSIGHTS": "GLOSARIO PARA EL PACIENTE E INFORMACIÓN DE SALUD PERSONAL",
                "HEALTH ACTIONS TO DISCUSS": "MEDIDAS DE SALUD A DISCUTIR"
            },
            "te": {  # Telugu
                "CLINICAL INTERPRETATION REPORT": "క్లినికల్ ఇంటర్‌ప్రెటేషన్ నివేదిక (వైద్యుల రిజిస్టర్)",
                "Active Findings Count": "క్రియాశీల పరిశీలనల సంఖ్య",
                "Extracted Clinical Values": "సేకరించిన క్లినికల్ విలువలు",
                "Reference Guidelines Retained": "సూచించిన క్లినికల్ మార్గదర్శకాలు",
                "Recommended Physician Action Plan": "వైద్యుల కార్యాచరణ ప్రణాళిక",
                "PATIENT GLOSSARY & PERSONAL HEALTH INSIGHTS": "రోగి గ్లోసరీ మరియు వ్యక్తిగత ఆరోగ్య సమాచారం",
                "HEALTH ACTIONS TO DISCUSS": "చర్చించాల్సిన ఆరోగ్య చర్యలు"
            }
        }

    def translate_report(self, text: str, target_lang: str) -> str:
        """
        Translates major sections of target text.
        Falls back to original text if language code is 'en' or unsupported.
        """
        lang = target_lang.lower().strip()
        if lang == "en" or lang not in self.glossary:
            return text

        dict_map = self.glossary[lang]
        translated = text
        for english_phrase, val in dict_map.items():
            translated = translated.replace(english_phrase, val)
            
        return translated
