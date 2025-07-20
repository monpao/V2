"""
Moteur de calculs financiers avancés pour Fincash
Implémente les modèles financiers professionnels avec précision mathématique
"""

import numpy as np
import pandas as pd
from scipy.optimize import fsolve, minimize_scalar
from scipy.stats import norm
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class FinancialEngine:
    """Moteur principal pour tous les calculs financiers"""
    
    def __init__(self):
        self.precision = 6  # Précision des calculs
    
    def calculate_dcf(self, params: Dict) -> Dict:
        """
        Calcul DCF (Discounted Cash Flow) avancé
        """
        try:
            # Paramètres d'entrée
            initial_revenue = float(params.get('revenus_initiaux', 1000000))
            growth_rate = float(params.get('taux_croissance', 0.05))
            discount_rate = float(params.get('taux_actualisation', 0.10))
            projection_years = int(params.get('duree_projection', 5))
            terminal_growth = float(params.get('croissance_terminale', 0.02))
            
            # Marges et ratios
            ebitda_margin = float(params.get('marge_ebitda', 0.20))
            tax_rate = float(params.get('taux_impot', 0.30))
            capex_rate = float(params.get('taux_capex', 0.05))
            working_capital_rate = float(params.get('taux_bfr', 0.02))
            
            # Projections des flux de trésorerie
            projections = []
            total_pv = 0
            
            for year in range(1, projection_years + 1):
                # Revenus projetés
                revenue = initial_revenue * ((1 + growth_rate) ** year)
                
                # EBITDA
                ebitda = revenue * ebitda_margin
                
                # Amortissements (estimation)
                depreciation = revenue * 0.03
                
                # EBIT
                ebit = ebitda - depreciation
                
                # Impôts
                taxes = ebit * tax_rate if ebit > 0 else 0
                
                # Résultat net opérationnel après impôts (NOPAT)
                nopat = ebit - taxes
                
                # CAPEX
                capex = revenue * capex_rate
                
                # Variation du BFR
                wc_change = revenue * working_capital_rate * growth_rate
                
                # Flux de trésorerie libre
                fcf = nopat + depreciation - capex - wc_change
                
                # Valeur actuelle
                pv_factor = 1 / ((1 + discount_rate) ** year)
                present_value = fcf * pv_factor
                total_pv += present_value
                
                projections.append({
                    'annee': year,
                    'revenus': round(revenue, 0),
                    'ebitda': round(ebitda, 0),
                    'ebit': round(ebit, 0),
                    'nopat': round(nopat, 0),
                    'fcf': round(fcf, 0),
                    'facteur_actualisation': round(pv_factor, 4),
                    'valeur_actuelle': round(present_value, 0)
                })
            
            # Valeur terminale
            terminal_fcf = projections[-1]['fcf'] * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            terminal_pv = terminal_value / ((1 + discount_rate) ** projection_years)
            
            # Valeur de l'entreprise
            enterprise_value = total_pv + terminal_pv
            
            # Analyse de sensibilité
            sensitivity = self._dcf_sensitivity_analysis(params, enterprise_value)
            
            return {
                'projections': projections,
                'valeur_actuelle_flux': round(total_pv, 0),
                'valeur_terminale': round(terminal_value, 0),
                'valeur_actuelle_terminale': round(terminal_pv, 0),
                'valeur_entreprise': round(enterprise_value, 0),
                'analyse_sensibilite': sensitivity,
                'ratios_cles': {
                    'multiple_revenus': round(enterprise_value / initial_revenue, 2),
                    'multiple_ebitda': round(enterprise_value / (initial_revenue * ebitda_margin), 2),
                    'part_valeur_terminale': round((terminal_pv / enterprise_value) * 100, 1)
                },
                'recommandations': self._generate_dcf_recommendations(enterprise_value, projections, terminal_pv)
            }
            
        except Exception as e:
            return {'error': f'Erreur dans le calcul DCF: {str(e)}'}
    
    def calculate_investment_budgeting(self, params: Dict) -> Dict:
        """
        Analyse d'investissement en capital avec méthodes multiples
        """
        try:
            initial_investment = float(params.get('investissement_initial', 1000000))
            annual_cash_flows = params.get('flux_annuels', [])
            discount_rate = float(params.get('taux_actualisation', 0.10))
            project_life = int(params.get('duree_vie', 5))
            
            # Si flux uniformes
            if not annual_cash_flows:
                uniform_flow = float(params.get('flux_uniforme', 200000))
                annual_cash_flows = [uniform_flow] * project_life
            
            # Calcul de la VAN
            npv = -initial_investment
            discounted_flows = []
            
            for year, cash_flow in enumerate(annual_cash_flows, 1):
                pv_factor = 1 / ((1 + discount_rate) ** year)
                present_value = cash_flow * pv_factor
                npv += present_value
                
                discounted_flows.append({
                    'annee': year,
                    'flux_brut': cash_flow,
                    'facteur_actualisation': round(pv_factor, 4),
                    'valeur_actuelle': round(present_value, 0)
                })
            
            # Calcul du TRI (IRR)
            irr = self._calculate_irr(initial_investment, annual_cash_flows)
            
            # Délai de récupération simple
            payback_period = self._calculate_payback_period(initial_investment, annual_cash_flows)
            
            # Délai de récupération actualisé
            discounted_payback = self._calculate_discounted_payback(initial_investment, discounted_flows)
            
            # Indice de profitabilité
            profitability_index = (npv + initial_investment) / initial_investment
            
            # Analyse de sensibilité
            sensitivity = self._investment_sensitivity_analysis(params, npv, irr)
            
            return {
                'investissement_initial': initial_investment,
                'flux_actualises': discounted_flows,
                'van': round(npv, 0),
                'tir': round(irr * 100, 2) if irr else None,
                'delai_recuperation': round(payback_period, 2),
                'delai_recuperation_actualise': round(discounted_payback, 2),
                'indice_profitabilite': round(profitability_index, 3),
                'analyse_sensibilite': sensitivity,
                'decision': {
                    'rentable': npv > 0,
                    'tir_superieur_cout_capital': irr > discount_rate if irr else False,
                    'indice_prof_acceptable': profitability_index > 1
                },
                'recommandations': self._generate_investment_recommendations(npv, irr, payback_period, profitability_index, discount_rate)
            }
            
        except Exception as e:
            return {'error': f'Erreur dans l\'analyse d\'investissement: {str(e)}'}
    
    def calculate_loan_amortization(self, params: Dict) -> Dict:
        """
        Calcul d'amortissement de prêt avec options avancées
        """
        try:
            loan_amount = float(params.get('montant_pret', 1000000))
            annual_rate = float(params.get('taux_interet', 0.05))
            duration_months = int(params.get('duree_mois', 60))
            amortization_type = params.get('type_amortissement', 'constant')  # constant, lineaire, in_fine
            
            monthly_rate = annual_rate / 12
            
            if amortization_type == 'constant':
                # Amortissement à mensualités constantes
                if monthly_rate > 0:
                    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**duration_months) / ((1 + monthly_rate)**duration_months - 1)
                else:
                    monthly_payment = loan_amount / duration_months
                
                schedule = self._generate_constant_amortization_schedule(loan_amount, monthly_rate, duration_months, monthly_payment)
                
            elif amortization_type == 'lineaire':
                # Amortissement linéaire (capital constant)
                schedule = self._generate_linear_amortization_schedule(loan_amount, monthly_rate, duration_months)
                monthly_payment = schedule[0]['mensualite']  # Première mensualité
                
            else:  # in_fine
                # Amortissement in fine
                schedule = self._generate_in_fine_amortization_schedule(loan_amount, monthly_rate, duration_months)
                monthly_payment = schedule[0]['mensualite']  # Mensualité d'intérêts
            
            total_interest = sum(payment['interets'] for payment in schedule)
            total_cost = loan_amount + total_interest
            
            # Analyse comparative
            comparison = self._compare_amortization_types(loan_amount, annual_rate, duration_months)
            
            return {
                'montant_pret': loan_amount,
                'taux_annuel': annual_rate * 100,
                'duree_mois': duration_months,
                'type_amortissement': amortization_type,
                'mensualite_initiale': round(monthly_payment, 0),
                'total_interets': round(total_interest, 0),
                'cout_total': round(total_cost, 0),
                'taux_effectif_global': round(((total_cost / loan_amount) ** (12 / duration_months) - 1) * 100, 2),
                'tableau_amortissement': schedule[:12],  # Première année
                'tableau_complet_disponible': True,
                'comparaison_types': comparison,
                'recommandations': self._generate_loan_recommendations(amortization_type, total_interest, monthly_payment, loan_amount)
            }
            
        except Exception as e:
            return {'error': f'Erreur dans le calcul d\'amortissement: {str(e)}'}
    
    def calculate_black_scholes(self, params: Dict) -> Dict:
        """
        Modèle Black-Scholes pour l'évaluation d'options
        """
        try:
            S = float(params.get('prix_actif', 100))  # Prix de l'actif sous-jacent
            K = float(params.get('prix_exercice', 100))  # Prix d'exercice
            T = float(params.get('temps_echeance', 1))  # Temps jusqu'à l'échéance (années)
            r = float(params.get('taux_sans_risque', 0.05))  # Taux sans risque
            sigma = float(params.get('volatilite', 0.20))  # Volatilité
            option_type = params.get('type_option', 'call')  # call ou put
            
            # Calculs Black-Scholes
            d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if option_type.lower() == 'call':
                option_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
                delta = norm.cdf(d1)
            else:  # put
                option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
                delta = -norm.cdf(-d1)
            
            # Calcul des grecques
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                    r * K * np.exp(-r * T) * norm.cdf(d2 if option_type.lower() == 'call' else -d2))
            vega = S * norm.pdf(d1) * np.sqrt(T)
            rho = (K * T * np.exp(-r * T) * 
                  norm.cdf(d2 if option_type.lower() == 'call' else -d2))
            
            # Analyse de sensibilité
            sensitivity = self._black_scholes_sensitivity(S, K, T, r, sigma, option_type)
            
            return {
                'prix_option': round(option_price, 4),
                'type_option': option_type,
                'parametres': {
                    'prix_actif': S,
                    'prix_exercice': K,
                    'temps_echeance': T,
                    'taux_sans_risque': r * 100,
                    'volatilite': sigma * 100
                },
                'grecques': {
                    'delta': round(delta, 4),
                    'gamma': round(gamma, 6),
                    'theta': round(theta, 4),
                    'vega': round(vega, 4),
                    'rho': round(rho, 4)
                },
                'd1': round(d1, 4),
                'd2': round(d2, 4),
                'analyse_sensibilite': sensitivity,
                'moneyness': 'ITM' if (S > K and option_type == 'call') or (S < K and option_type == 'put') else 'OTM',
                'recommandations': self._generate_option_recommendations(option_price, delta, gamma, theta, S, K)
            }
            
        except Exception as e:
            return {'error': f'Erreur dans le calcul Black-Scholes: {str(e)}'}
    
    def calculate_bond_pricing(self, params: Dict) -> Dict:
        """
        Évaluation d'obligations avec calculs avancés
        """
        try:
            face_value = float(params.get('valeur_nominale', 1000))
            coupon_rate = float(params.get('taux_coupon', 0.05))
            market_rate = float(params.get('taux_marche', 0.06))
            years_to_maturity = float(params.get('echeance', 5))
            frequency = int(params.get('frequence_paiement', 2))  # Semestriel par défaut
            
            # Calcul du prix de l'obligation
            periods = int(years_to_maturity * frequency)
            coupon_payment = (coupon_rate * face_value) / frequency
            period_rate = market_rate / frequency
            
            # Valeur actuelle des coupons
            pv_coupons = 0
            coupon_schedule = []
            
            for period in range(1, periods + 1):
                pv_factor = 1 / ((1 + period_rate) ** period)
                pv_coupon = coupon_payment * pv_factor
                pv_coupons += pv_coupon
                
                if period <= 10:  # Afficher les 10 premiers paiements
                    coupon_schedule.append({
                        'periode': period,
                        'date_relative': round(period / frequency, 2),
                        'coupon': round(coupon_payment, 2),
                        'facteur_actualisation': round(pv_factor, 6),
                        'valeur_actuelle': round(pv_coupon, 2)
                    })
            
            # Valeur actuelle du principal
            pv_principal = face_value / ((1 + period_rate) ** periods)
            
            # Prix de l'obligation
            bond_price = pv_coupons + pv_principal
            
            # Calcul de la duration et de la convexité
            duration = self._calculate_duration(face_value, coupon_rate, market_rate, years_to_maturity, frequency)
            convexity = self._calculate_convexity(face_value, coupon_rate, market_rate, years_to_maturity, frequency)
            
            # Rendement à l'échéance (si prix différent du pair)
            current_price = params.get('prix_actuel', bond_price)
            ytm = self._calculate_ytm(face_value, coupon_rate, years_to_maturity, current_price, frequency)
            
            return {
                'prix_obligation': round(bond_price, 2),
                'valeur_nominale': face_value,
                'valeur_actuelle_coupons': round(pv_coupons, 2),
                'valeur_actuelle_principal': round(pv_principal, 2),
                'taux_coupon': coupon_rate * 100,
                'taux_marche': market_rate * 100,
                'echeance_annees': years_to_maturity,
                'duration': round(duration, 2),
                'duration_modifiee': round(duration / (1 + market_rate / frequency), 2),
                'convexite': round(convexity, 2),
                'rendement_echeance': round(ytm * 100, 2),
                'calendrier_coupons': coupon_schedule,
                'analyse_risque': {
                    'sensibilite_taux': round(-duration * 0.01 * bond_price, 2),  # Pour 1% de variation
                    'risque_credit': 'A évaluer selon la notation',
                    'risque_liquidite': 'Dépend du marché'
                },
                'recommandations': self._generate_bond_recommendations(bond_price, face_value, duration, ytm, market_rate)
            }
            
        except Exception as e:
            return {'error': f'Erreur dans l\'évaluation d\'obligation: {str(e)}'}
    
    def calculate_financial_ratios(self, params: Dict) -> Dict:
        """
        Analyse complète des ratios financiers
        """
        try:
            # Données du bilan
            total_assets = float(params.get('actif_total', 1000000))
            current_assets = float(params.get('actif_circulant', 400000))
            cash = float(params.get('tresorerie', 100000))
            inventory = float(params.get('stocks', 150000))
            receivables = float(params.get('creances', 150000))
            
            total_liabilities = float(params.get('passif_total', 600000))
            current_liabilities = float(params.get('passif_circulant', 200000))
            long_term_debt = float(params.get('dettes_long_terme', 400000))
            
            equity = total_assets - total_liabilities
            
            # Données du compte de résultat
            revenue = float(params.get('chiffre_affaires', 2000000))
            gross_profit = float(params.get('benefice_brut', 800000))
            operating_profit = float(params.get('benefice_exploitation', 200000))
            net_income = float(params.get('benefice_net', 100000))
            interest_expense = float(params.get('charges_financieres', 50000))
            
            # Ratios de liquidité
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
            cash_ratio = cash / current_liabilities if current_liabilities > 0 else 0
            
            # Ratios d'activité
            asset_turnover = revenue / total_assets if total_assets > 0 else 0
            inventory_turnover = (revenue * 0.7) / inventory if inventory > 0 else 0  # Approximation du COGS
            receivables_turnover = revenue / receivables if receivables > 0 else 0
            
            # Ratios d'endettement
            debt_to_assets = total_liabilities / total_assets if total_assets > 0 else 0
            debt_to_equity = total_liabilities / equity if equity > 0 else 0
            equity_ratio = equity / total_assets if total_assets > 0 else 0
            interest_coverage = operating_profit / interest_expense if interest_expense > 0 else 0
            
            # Ratios de rentabilité
            gross_margin = gross_profit / revenue if revenue > 0 else 0
            operating_margin = operating_profit / revenue if revenue > 0 else 0
            net_margin = net_income / revenue if revenue > 0 else 0
            roa = net_income / total_assets if total_assets > 0 else 0
            roe = net_income / equity if equity > 0 else 0
            
            # Analyse DuPont
            dupont_roe = net_margin * asset_turnover * (total_assets / equity) if equity > 0 else 0
            
            ratios = {
                'liquidite': {
                    'ratio_liquidite_generale': round(current_ratio, 2),
                    'ratio_liquidite_reduite': round(quick_ratio, 2),
                    'ratio_liquidite_immediate': round(cash_ratio, 2)
                },
                'activite': {
                    'rotation_actif': round(asset_turnover, 2),
                    'rotation_stocks': round(inventory_turnover, 2),
                    'rotation_creances': round(receivables_turnover, 2),
                    'duree_stocks_jours': round(365 / inventory_turnover, 0) if inventory_turnover > 0 else 0,
                    'duree_creances_jours': round(365 / receivables_turnover, 0) if receivables_turnover > 0 else 0
                },
                'endettement': {
                    'ratio_endettement': round(debt_to_assets, 2),
                    'ratio_dette_capitaux': round(debt_to_equity, 2),
                    'ratio_autonomie': round(equity_ratio, 2),
                    'couverture_interets': round(interest_coverage, 2)
                },
                'rentabilite': {
                    'marge_brute': round(gross_margin * 100, 1),
                    'marge_exploitation': round(operating_margin * 100, 1),
                    'marge_nette': round(net_margin * 100, 1),
                    'rentabilite_actif': round(roa * 100, 1),
                    'rentabilite_capitaux': round(roe * 100, 1),
                    'dupont_roe': round(dupont_roe * 100, 1)
                }
            }
            
            # Analyse et benchmarking
            analysis = self._analyze_financial_ratios(ratios)
            
            return {
                'ratios': ratios,
                'analyse': analysis,
                'forces': analysis['forces'],
                'faiblesses': analysis['faiblesses'],
                'recommandations': analysis['recommandations'],
                'score_global': analysis['score_global']
            }
            
        except Exception as e:
            return {'error': f'Erreur dans l\'analyse des ratios: {str(e)}'}
    
    # Méthodes utilitaires privées
    
    def _calculate_irr(self, initial_investment: float, cash_flows: List[float]) -> Optional[float]:
        """Calcule le taux de rendement interne"""
        def npv_function(rate):
            npv = -initial_investment
            for i, cf in enumerate(cash_flows, 1):
                npv += cf / ((1 + rate) ** i)
            return npv
        
        try:
            # Recherche du TRI entre -99% et 100%
            irr = fsolve(npv_function, 0.1)[0]
            # Vérification que c'est une vraie solution
            if abs(npv_function(irr)) < 1e-6 and -0.99 < irr < 1.0:
                return irr
            return None
        except:
            return None
    
    def _calculate_payback_period(self, initial_investment: float, cash_flows: List[float]) -> float:
        """Calcule le délai de récupération simple"""
        cumulative = 0
        for i, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative >= initial_investment:
                # Interpolation pour plus de précision
                excess = cumulative - initial_investment
                return i + 1 - (excess / cf)
        return len(cash_flows)  # Si pas de récupération
    
    def _calculate_discounted_payback(self, initial_investment: float, discounted_flows: List[Dict]) -> float:
        """Calcule le délai de récupération actualisé"""
        cumulative = 0
        for i, flow in enumerate(discounted_flows):
            cumulative += flow['valeur_actuelle']
            if cumulative >= initial_investment:
                excess = cumulative - initial_investment
                return i + 1 - (excess / flow['valeur_actuelle'])
        return len(discounted_flows)
    
    def _dcf_sensitivity_analysis(self, params: Dict, base_value: float) -> Dict:
        """Analyse de sensibilité pour le DCF"""
        sensitivity = {}
        
        # Test de sensibilité sur le taux de croissance
        growth_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
        growth_results = []
        
        for delta in growth_scenarios:
            new_params = params.copy()
            new_params['taux_croissance'] = float(params.get('taux_croissance', 0.05)) + delta
            result = self.calculate_dcf(new_params)
            if 'valeur_entreprise' in result:
                growth_results.append({
                    'scenario': f"{delta*100:+.0f}%",
                    'valeur': result['valeur_entreprise'],
                    'variation': ((result['valeur_entreprise'] / base_value) - 1) * 100
                })
        
        sensitivity['croissance'] = growth_results
        
        # Test de sensibilité sur le taux d'actualisation
        discount_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
        discount_results = []
        
        for delta in discount_scenarios:
            new_params = params.copy()
            new_params['taux_actualisation'] = float(params.get('taux_actualisation', 0.10)) + delta
            result = self.calculate_dcf(new_params)
            if 'valeur_entreprise' in result:
                discount_results.append({
                    'scenario': f"{delta*100:+.0f}%",
                    'valeur': result['valeur_entreprise'],
                    'variation': ((result['valeur_entreprise'] / base_value) - 1) * 100
                })
        
        sensitivity['actualisation'] = discount_results
        
        return sensitivity
    
    def _generate_dcf_recommendations(self, enterprise_value: float, projections: List[Dict], terminal_pv: float) -> List[str]:
        """Génère des recommandations pour l'analyse DCF"""
        recommendations = []
        
        recommendations.append(f"La valeur de l'entreprise est estimée à {enterprise_value:,.0f} FCFA")
        
        terminal_percentage = (terminal_pv / enterprise_value) * 100
        if terminal_percentage > 70:
            recommendations.append(f"⚠️ La valeur terminale représente {terminal_percentage:.1f}% de la valeur totale, ce qui indique une forte sensibilité aux hypothèses long terme")
        else:
            recommendations.append(f"✓ La valeur terminale représente {terminal_percentage:.1f}% de la valeur totale, répartition équilibrée")
        
        # Analyse de la croissance des FCF
        if len(projections) >= 2:
            fcf_growth = (projections[-1]['fcf'] / projections[0]['fcf']) ** (1/(len(projections)-1)) - 1
            if fcf_growth > 0.15:
                recommendations.append("⚠️ Croissance des flux de trésorerie très optimiste, vérifiez la soutenabilité")
            elif fcf_growth < 0:
                recommendations.append("⚠️ Décroissance des flux de trésorerie projetée, analysez les causes")
        
        recommendations.append("💡 Effectuez une analyse de sensibilité sur les hypothèses clés")
        recommendations.append("💡 Comparez avec des multiples de sociétés comparables")
        
        return recommendations
    
    def _generate_investment_recommendations(self, npv: float, irr: Optional[float], payback: float, pi: float, discount_rate: float) -> List[str]:
        """Génère des recommandations pour l'analyse d'investissement"""
        recommendations = []
        
        if npv > 0:
            recommendations.append(f"✅ VAN positive ({npv:,.0f} FCFA) : projet créateur de valeur")
        else:
            recommendations.append(f"❌ VAN négative ({npv:,.0f} FCFA) : projet destructeur de valeur")
        
        if irr:
            if irr > discount_rate:
                recommendations.append(f"✅ TRI ({irr*100:.1f}%) supérieur au coût du capital ({discount_rate*100:.1f}%)")
            else:
                recommendations.append(f"❌ TRI ({irr*100:.1f}%) inférieur au coût du capital ({discount_rate*100:.1f}%)")
        
        if payback <= 3:
            recommendations.append(f"✅ Délai de récupération court ({payback:.1f} années)")
        elif payback <= 5:
            recommendations.append(f"⚠️ Délai de récupération modéré ({payback:.1f} années)")
        else:
            recommendations.append(f"❌ Délai de récupération long ({payback:.1f} années)")
        
        if pi > 1.2:
            recommendations.append(f"✅ Indice de profitabilité élevé ({pi:.2f})")
        elif pi > 1:
            recommendations.append(f"✅ Indice de profitabilité acceptable ({pi:.2f})")
        else:
            recommendations.append(f"❌ Indice de profitabilité insuffisant ({pi:.2f})")
        
        return recommendations
    
    def _generate_constant_amortization_schedule(self, loan_amount: float, monthly_rate: float, duration: int, monthly_payment: float) -> List[Dict]:
        """Génère le tableau d'amortissement à mensualités constantes"""
        schedule = []
        remaining_balance = loan_amount
        
        for month in range(1, duration + 1):
            interest = remaining_balance * monthly_rate
            principal = monthly_payment - interest
            remaining_balance -= principal
            
            schedule.append({
                'mois': month,
                'mensualite': round(monthly_payment, 0),
                'capital': round(principal, 0),
                'interets': round(interest, 0),
                'capital_restant': round(max(0, remaining_balance), 0)
            })
        
        return schedule
    
    def _generate_linear_amortization_schedule(self, loan_amount: float, monthly_rate: float, duration: int) -> List[Dict]:
        """Génère le tableau d'amortissement linéaire"""
        schedule = []
        monthly_principal = loan_amount / duration
        remaining_balance = loan_amount
        
        for month in range(1, duration + 1):
            interest = remaining_balance * monthly_rate
            monthly_payment = monthly_principal + interest
            remaining_balance -= monthly_principal
            
            schedule.append({
                'mois': month,
                'mensualite': round(monthly_payment, 0),
                'capital': round(monthly_principal, 0),
                'interets': round(interest, 0),
                'capital_restant': round(max(0, remaining_balance), 0)
            })
        
        return schedule
    
    def _generate_in_fine_amortization_schedule(self, loan_amount: float, monthly_rate: float, duration: int) -> List[Dict]:
        """Génère le tableau d'amortissement in fine"""
        schedule = []
        monthly_interest = loan_amount * monthly_rate
        
        for month in range(1, duration + 1):
            if month == duration:
                # Dernier mois : intérêts + capital
                monthly_payment = monthly_interest + loan_amount
                principal = loan_amount
                remaining_balance = 0
            else:
                # Mois intermédiaires : intérêts seulement
                monthly_payment = monthly_interest
                principal = 0
                remaining_balance = loan_amount
            
            schedule.append({
                'mois': month,
                'mensualite': round(monthly_payment, 0),
                'capital': round(principal, 0),
                'interets': round(monthly_interest, 0),
                'capital_restant': round(remaining_balance, 0)
            })
        
        return schedule
    
    def _compare_amortization_types(self, loan_amount: float, annual_rate: float, duration: int) -> Dict:
        """Compare les différents types d'amortissement"""
        monthly_rate = annual_rate / 12
        
        # Amortissement constant
        if monthly_rate > 0:
            constant_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**duration) / ((1 + monthly_rate)**duration - 1)
        else:
            constant_payment = loan_amount / duration
        constant_total_interest = (constant_payment * duration) - loan_amount
        
        # Amortissement linéaire
        linear_total_interest = loan_amount * monthly_rate * (duration + 1) / 2
        linear_first_payment = (loan_amount / duration) + (loan_amount * monthly_rate)
        
        # Amortissement in fine
        in_fine_total_interest = loan_amount * monthly_rate * duration
        in_fine_monthly_interest = loan_amount * monthly_rate
        
        return {
            'constant': {
                'mensualite': round(constant_payment, 0),
                'total_interets': round(constant_total_interest, 0),
                'cout_total': round(loan_amount + constant_total_interest, 0)
            },
            'lineaire': {
                'mensualite_initiale': round(linear_first_payment, 0),
                'total_interets': round(linear_total_interest, 0),
                'cout_total': round(loan_amount + linear_total_interest, 0)
            },
            'in_fine': {
                'mensualite_interets': round(in_fine_monthly_interest, 0),
                'total_interets': round(in_fine_total_interest, 0),
                'cout_total': round(loan_amount + in_fine_total_interest, 0)
            }
        }
    
    def _generate_loan_recommendations(self, amortization_type: str, total_interest: float, monthly_payment: float, loan_amount: float) -> List[str]:
        """Génère des recommandations pour le prêt"""
        recommendations = []
        
        interest_rate_pct = (total_interest / loan_amount) * 100
        
        recommendations.append(f"Type d'amortissement choisi : {amortization_type}")
        recommendations.append(f"Coût total du crédit : {total_interest:,.0f} FCFA ({interest_rate_pct:.1f}% du capital)")
        
        if amortization_type == 'constant':
            recommendations.append("✓ Mensualités constantes, budgétisation facilitée")
        elif amortization_type == 'lineaire':
            recommendations.append("✓ Intérêts dégressifs, économies sur le long terme")
        else:  # in_fine
            recommendations.append("⚠️ Remboursement du capital en fin de période, prévoir la trésorerie")
        
        payment_to_income_ratio = (monthly_payment * 12) / (loan_amount * 0.1)  # Approximation
        if payment_to_income_ratio > 0.33:
            recommendations.append("⚠️ Vérifiez que les mensualités ne dépassent pas 33% des revenus")
        
        return recommendations
    
    def _black_scholes_sensitivity(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> Dict:
        """Analyse de sensibilité pour Black-Scholes"""
        base_params = {'prix_actif': S, 'prix_exercice': K, 'temps_echeance': T, 'taux_sans_risque': r, 'volatilite': sigma, 'type_option': option_type}
        base_result = self.calculate_black_scholes(base_params)
        base_price = base_result['prix_option']
        
        sensitivity = {}
        
        # Sensibilité au prix de l'actif
        price_scenarios = [S * 0.9, S * 0.95, S, S * 1.05, S * 1.1]
        price_results = []
        for price in price_scenarios:
            params = base_params.copy()
            params['prix_actif'] = price
            result = self.calculate_black_scholes(params)
            price_results.append({
                'prix_actif': price,
                'prix_option': result['prix_option'],
                'variation': result['prix_option'] - base_price
            })
        sensitivity['prix_actif'] = price_results
        
        # Sensibilité à la volatilité
        vol_scenarios = [sigma * 0.8, sigma * 0.9, sigma, sigma * 1.1, sigma * 1.2]
        vol_results = []
        for vol in vol_scenarios:
            params = base_params.copy()
            params['volatilite'] = vol
            result = self.calculate_black_scholes(params)
            vol_results.append({
                'volatilite': vol * 100,
                'prix_option': result['prix_option'],
                'variation': result['prix_option'] - base_price
            })
        sensitivity['volatilite'] = vol_results
        
        return sensitivity
    
    def _generate_option_recommendations(self, option_price: float, delta: float, gamma: float, theta: float, S: float, K: float) -> List[str]:
        """Génère des recommandations pour les options"""
        recommendations = []
        
        recommendations.append(f"Prix théorique de l'option : {option_price:.4f}")
        
        if abs(delta) > 0.7:
            recommendations.append(f"✓ Delta élevé ({delta:.3f}) : option très sensible au prix de l'actif")
        elif abs(delta) < 0.3:
            recommendations.append(f"⚠️ Delta faible ({delta:.3f}) : option peu sensible au prix de l'actif")
        
        if gamma > 0.1:
            recommendations.append(f"⚠️ Gamma élevé ({gamma:.4f}) : delta très instable")
        
        if theta < -0.05:
            recommendations.append(f"⚠️ Theta négatif élevé ({theta:.4f}) : décroissance temporelle importante")
        
        moneyness = S / K
        if moneyness > 1.1:
            recommendations.append("Option fortement dans la monnaie")
        elif moneyness < 0.9:
            recommendations.append("Option fortement hors de la monnaie")
        else:
            recommendations.append("Option proche de la monnaie")
        
        return recommendations
    
    def _calculate_duration(self, face_value: float, coupon_rate: float, market_rate: float, years: float, frequency: int) -> float:
        """Calcule la duration de Macaulay"""
        periods = int(years * frequency)
        coupon = (coupon_rate * face_value) / frequency
        period_rate = market_rate / frequency
        
        weighted_time = 0
        bond_price = 0
        
        for period in range(1, periods + 1):
            pv_factor = 1 / ((1 + period_rate) ** period)
            cash_flow = coupon if period < periods else coupon + face_value
            pv_cash_flow = cash_flow * pv_factor
            
            weighted_time += (period / frequency) * pv_cash_flow
            bond_price += pv_cash_flow
        
        return weighted_time / bond_price if bond_price > 0 else 0
    
    def _calculate_convexity(self, face_value: float, coupon_rate: float, market_rate: float, years: float, frequency: int) -> float:
        """Calcule la convexité"""
        periods = int(years * frequency)
        coupon = (coupon_rate * face_value) / frequency
        period_rate = market_rate / frequency
        
        convexity_sum = 0
        bond_price = 0
        
        for period in range(1, periods + 1):
            pv_factor = 1 / ((1 + period_rate) ** period)
            cash_flow = coupon if period < periods else coupon + face_value
            pv_cash_flow = cash_flow * pv_factor
            
            convexity_sum += (period * (period + 1) / (frequency ** 2)) * pv_cash_flow
            bond_price += pv_cash_flow
        
        return convexity_sum / (bond_price * ((1 + period_rate) ** 2)) if bond_price > 0 else 0
    
    def _calculate_ytm(self, face_value: float, coupon_rate: float, years: float, current_price: float, frequency: int) -> float:
        """Calcule le rendement à l'échéance"""
        periods = int(years * frequency)
        coupon = (coupon_rate * face_value) / frequency
        
        def ytm_function(rate):
            price = 0
            period_rate = rate / frequency
            for period in range(1, periods + 1):
                cash_flow = coupon if period < periods else coupon + face_value
                price += cash_flow / ((1 + period_rate) ** period)
            return price - current_price
        
        try:
            ytm = fsolve(ytm_function, coupon_rate)[0]
            return ytm if 0 <= ytm <= 1 else coupon_rate
        except:
            return coupon_rate
    
    def _generate_bond_recommendations(self, bond_price: float, face_value: float, duration: float, ytm: float, market_rate: float) -> List[str]:
        """Génère des recommandations pour les obligations"""
        recommendations = []
        
        premium_discount = (bond_price / face_value - 1) * 100
        
        if premium_discount > 5:
            recommendations.append(f"Obligation à prime ({premium_discount:.1f}%) : taux de coupon > taux de marché")
        elif premium_discount < -5:
            recommendations.append(f"Obligation à escompte ({premium_discount:.1f}%) : taux de coupon < taux de marché")
        else:
            recommendations.append("Obligation proche du pair")
        
        if duration > 7:
            recommendations.append(f"⚠️ Duration élevée ({duration:.1f}) : forte sensibilité aux taux d'intérêt")
        elif duration < 3:
            recommendations.append(f"✓ Duration faible ({duration:.1f}) : faible sensibilité aux taux d'intérêt")
        
        yield_spread = (ytm - market_rate) * 100
        if abs(yield_spread) > 0.5:
            recommendations.append(f"Écart de rendement : {yield_spread:+.1f} points de base vs marché")
        
        recommendations.append(f"Rendement à l'échéance : {ytm*100:.2f}%")
        
        return recommendations
    
    def _analyze_financial_ratios(self, ratios: Dict) -> Dict:
        """Analyse les ratios financiers et génère un score"""
        analysis = {
            'forces': [],
            'faiblesses': [],
            'recommandations': [],
            'score_global': 0
        }
        
        score = 0
        max_score = 0
        
        # Analyse de la liquidité
        current_ratio = ratios['liquidite']['ratio_liquidite_generale']
        max_score += 20
        if current_ratio >= 1.5:
            analysis['forces'].append(f"Excellente liquidité générale ({current_ratio})")
            score += 20
        elif current_ratio >= 1.2:
            analysis['forces'].append(f"Bonne liquidité générale ({current_ratio})")
            score += 15
        elif current_ratio >= 1.0:
            score += 10
        else:
            analysis['faiblesses'].append(f"Liquidité générale insuffisante ({current_ratio})")
            analysis['recommandations'].append("Améliorer la gestion de trésorerie")
        
        # Analyse de l'endettement
        debt_ratio = ratios['endettement']['ratio_endettement']
        max_score += 20
        if debt_ratio <= 0.3:
            analysis['forces'].append(f"Endettement faible ({debt_ratio:.1%})")
            score += 20
        elif debt_ratio <= 0.6:
            score += 15
        elif debt_ratio <= 0.8:
            score += 10
        else:
            analysis['faiblesses'].append(f"Endettement élevé ({debt_ratio:.1%})")
            analysis['recommandations'].append("Réduire l'endettement")
        
        # Analyse de la rentabilité
        roe = ratios['rentabilite']['rentabilite_capitaux'] / 100
        max_score += 20
        if roe >= 0.15:
            analysis['forces'].append(f"Excellente rentabilité des capitaux propres ({roe:.1%})")
            score += 20
        elif roe >= 0.10:
            analysis['forces'].append(f"Bonne rentabilité des capitaux propres ({roe:.1%})")
            score += 15
        elif roe >= 0.05:
            score += 10
        else:
            analysis['faiblesses'].append(f"Rentabilité des capitaux propres faible ({roe:.1%})")
            analysis['recommandations'].append("Améliorer la rentabilité opérationnelle")
        
        # Analyse de l'activité
        asset_turnover = ratios['activite']['rotation_actif']
        max_score += 20
        if asset_turnover >= 1.5:
            analysis['forces'].append(f"Excellente rotation des actifs ({asset_turnover})")
            score += 20
        elif asset_turnover >= 1.0:
            analysis['forces'].append(f"Bonne rotation des actifs ({asset_turnover})")
            score += 15
        elif asset_turnover >= 0.5:
            score += 10
        else:
            analysis['faiblesses'].append(f"Rotation des actifs faible ({asset_turnover})")
            analysis['recommandations'].append("Optimiser l'utilisation des actifs")
        
        # Couverture des intérêts
        interest_coverage = ratios['endettement']['couverture_interets']
        max_score += 20
        if interest_coverage >= 5:
            analysis['forces'].append(f"Excellente couverture des intérêts ({interest_coverage:.1f})")
            score += 20
        elif interest_coverage >= 2.5:
            analysis['forces'].append(f"Bonne couverture des intérêts ({interest_coverage:.1f})")
            score += 15
        elif interest_coverage >= 1.5:
            score += 10
        else:
            analysis['faiblesses'].append(f"Couverture des intérêts insuffisante ({interest_coverage:.1f})")
            analysis['recommandations'].append("Améliorer la capacité de remboursement")
        
        # Recommandations générales
        if not analysis['recommandations']:
            analysis['recommandations'].append("Maintenir les bonnes performances actuelles")
            analysis['recommandations'].append("Surveiller l'évolution des ratios dans le temps")
        
        analysis['score_global'] = round((score / max_score) * 100, 0)
        
        return analysis
    
    def _investment_sensitivity_analysis(self, params: Dict, base_npv: float, base_irr: Optional[float]) -> Dict:
        """Analyse de sensibilité pour l'investissement"""
        sensitivity = {}
        
        # Sensibilité au taux d'actualisation
        discount_scenarios = [-0.02, -0.01, 0, 0.01, 0.02]
        discount_results = []
        
        for delta in discount_scenarios:
            new_params = params.copy()
            new_params['taux_actualisation'] = float(params.get('taux_actualisation', 0.10)) + delta
            result = self.calculate_investment_budgeting(new_params)
            if 'van' in result:
                discount_results.append({
                    'scenario': f"{delta*100:+.0f}%",
                    'van': result['van'],
                    'variation_van': result['van'] - base_npv
                })
        
        sensitivity['taux_actualisation'] = discount_results
        
        return sensitivity

