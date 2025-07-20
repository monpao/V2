"""
Module IA pour les recommandations et analyses financières avancées
Utilise l'API OpenAI pour générer des commentaires et recommandations intelligents
"""

import openai
import json
from typing import Dict, List, Optional
import os

class AIFinancialAdvisor:
    """Conseiller financier IA pour Fincash"""
    
    def __init__(self):
        # Les variables d'environnement sont déjà configurées dans le sandbox
        self.client = openai.OpenAI()
    
    def generate_dcf_analysis(self, dcf_results: Dict, company_context: Optional[Dict] = None) -> Dict:
        """Génère une analyse IA approfondie des résultats DCF"""
        try:
            context = f"""
            Vous êtes un expert en évaluation d'entreprises. Analysez les résultats DCF suivants et fournissez des recommandations professionnelles.
            
            Résultats DCF:
            - Valeur de l'entreprise: {dcf_results.get('valeur_entreprise', 0):,.0f} FCFA
            - Valeur actuelle des flux: {dcf_results.get('valeur_actuelle_flux', 0):,.0f} FCFA
            - Valeur terminale: {dcf_results.get('valeur_terminale', 0):,.0f} FCFA
            - Part de la valeur terminale: {dcf_results.get('ratios_cles', {}).get('part_valeur_terminale', 0):.1f}%
            
            Projections:
            {json.dumps(dcf_results.get('projections', [])[:3], indent=2)}
            
            Contexte entreprise: {json.dumps(company_context or {}, indent=2)}
            
            Fournissez une analyse structurée avec:
            1. Évaluation de la cohérence des hypothèses
            2. Points forts et risques identifiés
            3. Recommandations d'amélioration du modèle
            4. Comparaison avec les standards du secteur
            5. Recommandations stratégiques
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert financier spécialisé en évaluation d'entreprises. Répondez en français avec un ton professionnel et des recommandations concrètes."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'analyse_ia': analysis,
                'score_confiance': self._calculate_confidence_score(dcf_results),
                'alertes': self._generate_dcf_alerts(dcf_results),
                'recommandations_prioritaires': self._extract_key_recommendations(analysis)
            }
            
        except Exception as e:
            return {
                'analyse_ia': f"Erreur lors de l'analyse IA: {str(e)}",
                'score_confiance': 50,
                'alertes': [],
                'recommandations_prioritaires': ["Vérifiez les paramètres d'entrée du modèle"]
            }
    
    def generate_investment_analysis(self, investment_results: Dict, project_context: Optional[Dict] = None) -> Dict:
        """Génère une analyse IA pour les projets d'investissement"""
        try:
            context = f"""
            Analysez ce projet d'investissement et fournissez des recommandations d'expert.
            
            Résultats financiers:
            - VAN: {investment_results.get('van', 0):,.0f} FCFA
            - TIR: {investment_results.get('tir', 0):.2f}%
            - Délai de récupération: {investment_results.get('delai_recuperation', 0):.1f} années
            - Indice de profitabilité: {investment_results.get('indice_profitabilite', 0):.2f}
            
            Flux de trésorerie:
            {json.dumps(investment_results.get('flux_actualises', [])[:5], indent=2)}
            
            Contexte projet: {json.dumps(project_context or {}, indent=2)}
            
            Analysez:
            1. Attractivité financière du projet
            2. Risques et opportunités
            3. Recommandations pour l'amélioration
            4. Stratégie de financement optimale
            5. Facteurs critiques de succès
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en analyse d'investissements. Fournissez des conseils pratiques et actionnables en français."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'analyse_ia': analysis,
                'recommandation_decision': self._get_investment_recommendation(investment_results),
                'facteurs_risque': self._identify_investment_risks(investment_results),
                'optimisations_suggerees': self._suggest_optimizations(analysis)
            }
            
        except Exception as e:
            return {
                'analyse_ia': f"Erreur lors de l'analyse IA: {str(e)}",
                'recommandation_decision': 'À analyser manuellement',
                'facteurs_risque': [],
                'optimisations_suggerees': []
            }
    
    def generate_financial_health_report(self, ratios_results: Dict, company_info: Optional[Dict] = None) -> Dict:
        """Génère un rapport de santé financière avec IA"""
        try:
            context = f"""
            Évaluez la santé financière de cette entreprise basée sur ses ratios financiers.
            
            Ratios de liquidité:
            {json.dumps(ratios_results.get('ratios', {}).get('liquidite', {}), indent=2)}
            
            Ratios d'endettement:
            {json.dumps(ratios_results.get('ratios', {}).get('endettement', {}), indent=2)}
            
            Ratios de rentabilité:
            {json.dumps(ratios_results.get('ratios', {}).get('rentabilite', {}), indent=2)}
            
            Ratios d'activité:
            {json.dumps(ratios_results.get('ratios', {}).get('activite', {}), indent=2)}
            
            Score global: {ratios_results.get('score_global', 0)}/100
            
            Informations entreprise: {json.dumps(company_info or {}, indent=2)}
            
            Fournissez:
            1. Diagnostic de santé financière
            2. Comparaison avec les standards sectoriels
            3. Tendances et évolutions recommandées
            4. Plan d'action prioritaire
            5. Indicateurs à surveiller
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un analyste financier senior. Fournissez un diagnostic précis et des recommandations concrètes en français."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'diagnostic_ia': analysis,
                'niveau_risque': self._assess_risk_level(ratios_results),
                'actions_prioritaires': self._extract_priority_actions(analysis),
                'indicateurs_surveillance': self._get_monitoring_indicators(ratios_results)
            }
            
        except Exception as e:
            return {
                'diagnostic_ia': f"Erreur lors de l'analyse IA: {str(e)}",
                'niveau_risque': 'Moyen',
                'actions_prioritaires': [],
                'indicateurs_surveillance': []
            }
    
    def analyze_financial_statements_anomalies(self, statements_data: Dict, anomalies: List[Dict]) -> Dict:
        """Analyse les anomalies des états financiers avec IA"""
        try:
            context = f"""
            Analysez les anomalies détectées dans ces états financiers et proposez des corrections.
            
            États financiers:
            - Bilan: {json.dumps(statements_data.get('balance_sheet', {}), indent=2)[:1000]}...
            - Compte de résultat: {json.dumps(statements_data.get('income_statement', {}), indent=2)[:1000]}...
            
            Anomalies détectées:
            {json.dumps(anomalies, indent=2)}
            
            Pour chaque anomalie:
            1. Expliquez les causes possibles
            2. Évaluez la gravité
            3. Proposez des corrections
            4. Suggérez des contrôles préventifs
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert-comptable spécialisé dans l'audit. Analysez les anomalies et proposez des solutions en français."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1200,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'analyse_anomalies': analysis,
                'corrections_suggerees': self._extract_corrections(analysis),
                'controles_preventifs': self._extract_preventive_controls(analysis),
                'impact_evaluation': self._evaluate_anomaly_impact(anomalies)
            }
            
        except Exception as e:
            return {
                'analyse_anomalies': f"Erreur lors de l'analyse IA: {str(e)}",
                'corrections_suggerees': [],
                'controles_preventifs': [],
                'impact_evaluation': 'À évaluer manuellement'
            }
    
    def generate_market_insights(self, model_results: Dict, market_context: Optional[Dict] = None) -> Dict:
        """Génère des insights marché avec IA"""
        try:
            context = f"""
            Fournissez des insights marché basés sur cette analyse financière.
            
            Résultats du modèle:
            {json.dumps(model_results, indent=2)[:1500]}...
            
            Contexte marché: {json.dumps(market_context or {}, indent=2)}
            
            Analysez:
            1. Positionnement concurrentiel
            2. Opportunités de marché
            3. Risques sectoriels
            4. Tendances macroéconomiques
            5. Recommandations stratégiques
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Vous êtes un analyste de marché senior. Fournissez des insights stratégiques en français."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            insights = response.choices[0].message.content
            
            return {
                'insights_marche': insights,
                'opportunites_identifiees': self._extract_opportunities(insights),
                'risques_sectoriels': self._extract_sector_risks(insights),
                'recommandations_strategiques': self._extract_strategic_recommendations(insights)
            }
            
        except Exception as e:
            return {
                'insights_marche': f"Erreur lors de l'analyse IA: {str(e)}",
                'opportunites_identifiees': [],
                'risques_sectoriels': [],
                'recommandations_strategiques': []
            }
    
    # Méthodes utilitaires privées
    
    def _calculate_confidence_score(self, dcf_results: Dict) -> int:
        """Calcule un score de confiance pour l'analyse DCF"""
        score = 70  # Score de base
        
        # Ajustements basés sur les résultats
        terminal_pct = dcf_results.get('ratios_cles', {}).get('part_valeur_terminale', 50)
        if terminal_pct > 80:
            score -= 20
        elif terminal_pct < 50:
            score += 10
        
        # Vérification de la cohérence des projections
        projections = dcf_results.get('projections', [])
        if len(projections) >= 2:
            growth_consistency = True
            for i in range(1, len(projections)):
                if projections[i]['fcf'] < 0:
                    score -= 15
                    break
        
        return max(0, min(100, score))
    
    def _generate_dcf_alerts(self, dcf_results: Dict) -> List[str]:
        """Génère des alertes pour l'analyse DCF"""
        alerts = []
        
        terminal_pct = dcf_results.get('ratios_cles', {}).get('part_valeur_terminale', 0)
        if terminal_pct > 75:
            alerts.append("⚠️ Forte dépendance à la valeur terminale")
        
        projections = dcf_results.get('projections', [])
        for proj in projections:
            if proj.get('fcf', 0) < 0:
                alerts.append(f"⚠️ Flux de trésorerie négatif en année {proj.get('annee', 0)}")
        
        return alerts
    
    def _extract_key_recommendations(self, analysis: str) -> List[str]:
        """Extrait les recommandations clés de l'analyse IA"""
        # Logique simplifiée pour extraire les recommandations
        lines = analysis.split('\n')
        recommendations = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommand', 'conseil', 'suggér', 'devrait']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Limiter à 5 recommandations
    
    def _get_investment_recommendation(self, investment_results: Dict) -> str:
        """Détermine la recommandation d'investissement"""
        van = investment_results.get('van', 0)
        tir = investment_results.get('tir', 0)
        pi = investment_results.get('indice_profitabilite', 0)
        
        if van > 0 and tir > 10 and pi > 1.2:
            return "FORTEMENT RECOMMANDÉ"
        elif van > 0 and tir > 5 and pi > 1:
            return "RECOMMANDÉ"
        elif van > 0:
            return "ACCEPTABLE"
        else:
            return "NON RECOMMANDÉ"
    
    def _identify_investment_risks(self, investment_results: Dict) -> List[str]:
        """Identifie les facteurs de risque de l'investissement"""
        risks = []
        
        payback = investment_results.get('delai_recuperation', 0)
        if payback > 5:
            risks.append("Délai de récupération long")
        
        tir = investment_results.get('tir', 0)
        if tir < 8:
            risks.append("TIR faible par rapport aux standards")
        
        return risks
    
    def _suggest_optimizations(self, analysis: str) -> List[str]:
        """Suggère des optimisations basées sur l'analyse"""
        optimizations = []
        
        if 'flux de trésorerie' in analysis.lower():
            optimizations.append("Optimiser la gestion des flux de trésorerie")
        
        if 'coût' in analysis.lower():
            optimizations.append("Réduire les coûts opérationnels")
        
        return optimizations
    
    def _assess_risk_level(self, ratios_results: Dict) -> str:
        """Évalue le niveau de risque financier"""
        score = ratios_results.get('score_global', 50)
        
        if score >= 80:
            return "FAIBLE"
        elif score >= 60:
            return "MODÉRÉ"
        elif score >= 40:
            return "ÉLEVÉ"
        else:
            return "TRÈS ÉLEVÉ"
    
    def _extract_priority_actions(self, analysis: str) -> List[str]:
        """Extrait les actions prioritaires de l'analyse"""
        actions = []
        
        lines = analysis.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['action', 'priorité', 'urgent', 'immédiat']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    actions.append(clean_line)
        
        return actions[:3]
    
    def _get_monitoring_indicators(self, ratios_results: Dict) -> List[str]:
        """Détermine les indicateurs à surveiller"""
        indicators = []
        
        ratios = ratios_results.get('ratios', {})
        
        # Liquidité
        current_ratio = ratios.get('liquidite', {}).get('ratio_liquidite_generale', 0)
        if current_ratio < 1.2:
            indicators.append("Ratio de liquidité générale")
        
        # Endettement
        debt_ratio = ratios.get('endettement', {}).get('ratio_endettement', 0)
        if debt_ratio > 0.6:
            indicators.append("Ratio d'endettement")
        
        # Rentabilité
        roe = ratios.get('rentabilite', {}).get('rentabilite_capitaux', 0)
        if roe < 10:
            indicators.append("Rentabilité des capitaux propres")
        
        return indicators
    
    def _extract_corrections(self, analysis: str) -> List[str]:
        """Extrait les corrections suggérées"""
        corrections = []
        
        lines = analysis.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['corriger', 'ajuster', 'modifier', 'rectifier']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    corrections.append(clean_line)
        
        return corrections
    
    def _extract_preventive_controls(self, analysis: str) -> List[str]:
        """Extrait les contrôles préventifs suggérés"""
        controls = []
        
        lines = analysis.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['contrôle', 'vérif', 'prévent', 'surveill']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    controls.append(clean_line)
        
        return controls
    
    def _evaluate_anomaly_impact(self, anomalies: List[Dict]) -> str:
        """Évalue l'impact global des anomalies"""
        high_severity = sum(1 for a in anomalies if a.get('severity') == 'high')
        medium_severity = sum(1 for a in anomalies if a.get('severity') == 'medium')
        
        if high_severity > 0:
            return "IMPACT ÉLEVÉ"
        elif medium_severity > 2:
            return "IMPACT MODÉRÉ"
        else:
            return "IMPACT FAIBLE"
    
    def _extract_opportunities(self, insights: str) -> List[str]:
        """Extrait les opportunités identifiées"""
        opportunities = []
        
        lines = insights.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['opportunité', 'potentiel', 'croissance', 'développ']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    opportunities.append(clean_line)
        
        return opportunities[:3]
    
    def _extract_sector_risks(self, insights: str) -> List[str]:
        """Extrait les risques sectoriels"""
        risks = []
        
        lines = insights.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['risque', 'menace', 'défi', 'vulnérab']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    risks.append(clean_line)
        
        return risks[:3]
    
    def _extract_strategic_recommendations(self, insights: str) -> List[str]:
        """Extrait les recommandations stratégiques"""
        recommendations = []
        
        lines = insights.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['stratég', 'recommand', 'orient', 'focus']):
                clean_line = line.strip('- •').strip()
                if len(clean_line) > 10:
                    recommendations.append(clean_line)
        
        return recommendations[:3]

