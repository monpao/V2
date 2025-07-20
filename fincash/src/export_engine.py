import os
import io
import base64
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# Configuration pour les graphiques
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
pio.templates.default = "plotly_white"

class FinancialExportEngine:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configuration des styles personnalisés pour les rapports"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79')
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2e75b6')
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Style pour les recommandations IA
        self.styles.add(ParagraphStyle(
            name='AIRecommendation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20,
            borderColor=colors.HexColor('#4CAF50'),
            borderWidth=1,
            borderPadding=10,
            backColor=colors.HexColor('#E8F5E8')
        ))

    def create_financial_charts(self, model_data, model_type):
        """Génère des graphiques financiers selon le type de modèle"""
        charts = []
        
        if model_type == 'dcf':
            charts.extend(self._create_dcf_charts(model_data))
        elif model_type == 'investment_budgeting':
            charts.extend(self._create_investment_charts(model_data))
        elif model_type == 'financial_ratios':
            charts.extend(self._create_ratios_charts(model_data))
        elif model_type == 'loan_amortization':
            charts.extend(self._create_loan_charts(model_data))
        else:
            charts.extend(self._create_generic_charts(model_data))
        
        return charts

    def _create_dcf_charts(self, data):
        """Crée des graphiques spécifiques au DCF"""
        charts = []
        
        # Graphique des flux de trésorerie
        if 'cash_flows' in data:
            fig = go.Figure()
            years = list(range(len(data['cash_flows'])))
            
            fig.add_trace(go.Bar(
                x=years,
                y=data['cash_flows'],
                name='Flux de trésorerie',
                marker_color='#2E86AB'
            ))
            
            fig.update_layout(
                title='Évolution des Flux de Trésorerie',
                xaxis_title='Années',
                yaxis_title='Flux (FCFA)',
                template='plotly_white',
                height=400
            )
            
            charts.append({
                'title': 'Flux de Trésorerie DCF',
                'chart': fig,
                'description': 'Projection des flux de trésorerie futurs actualisés'
            })
        
        # Graphique de sensibilité
        if 'sensitivity_analysis' in data:
            fig = go.Figure()
            
            scenarios = ['Pessimiste', 'Base', 'Optimiste']
            values = data['sensitivity_analysis']
            
            fig.add_trace(go.Bar(
                x=scenarios,
                y=values,
                marker_color=['#E74C3C', '#F39C12', '#27AE60']
            ))
            
            fig.update_layout(
                title='Analyse de Sensibilité - Valeur Actuelle Nette',
                xaxis_title='Scénarios',
                yaxis_title='VAN (FCFA)',
                template='plotly_white',
                height=400
            )
            
            charts.append({
                'title': 'Analyse de Sensibilité',
                'chart': fig,
                'description': 'Impact des variations des hypothèses sur la VAN'
            })
        
        return charts

    def _create_investment_charts(self, data):
        """Crée des graphiques pour l'analyse d'investissement"""
        charts = []
        
        # Graphique VAN vs TRI
        if 'npv' in data and 'irr' in data:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=[data['irr']],
                y=[data['npv']],
                mode='markers',
                marker=dict(size=15, color='#3498DB'),
                name='Projet'
            ))
            
            # Ligne de référence VAN = 0
            fig.add_hline(y=0, line_dash="dash", line_color="red", 
                         annotation_text="Seuil de rentabilité")
            
            fig.update_layout(
                title='Positionnement VAN vs TRI',
                xaxis_title='TRI (%)',
                yaxis_title='VAN (FCFA)',
                template='plotly_white',
                height=400
            )
            
            charts.append({
                'title': 'Analyse VAN-TRI',
                'chart': fig,
                'description': 'Évaluation de la rentabilité du projet'
            })
        
        return charts

    def _create_ratios_charts(self, data):
        """Crée des graphiques pour les ratios financiers"""
        charts = []
        
        # Radar chart des ratios
        if 'ratios' in data:
            categories = list(data['ratios'].keys())
            values = list(data['ratios'].values())
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Ratios Actuels',
                line_color='#2E86AB'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(values) * 1.2]
                    )),
                title='Tableau de Bord des Ratios Financiers',
                template='plotly_white',
                height=500
            )
            
            charts.append({
                'title': 'Ratios Financiers',
                'chart': fig,
                'description': 'Vue d\'ensemble de la performance financière'
            })
        
        return charts

    def _create_loan_charts(self, data):
        """Crée des graphiques pour l'amortissement de prêt"""
        charts = []
        
        # Graphique d'amortissement
        if 'amortization_schedule' in data:
            schedule = data['amortization_schedule']
            periods = [row['period'] for row in schedule]
            principal = [row['principal_payment'] for row in schedule]
            interest = [row['interest_payment'] for row in schedule]
            balance = [row['remaining_balance'] for row in schedule]
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Répartition Capital/Intérêts', 'Solde Restant Dû'),
                vertical_spacing=0.1
            )
            
            # Graphique empilé capital/intérêts
            fig.add_trace(go.Bar(
                x=periods,
                y=principal,
                name='Capital',
                marker_color='#27AE60'
            ), row=1, col=1)
            
            fig.add_trace(go.Bar(
                x=periods,
                y=interest,
                name='Intérêts',
                marker_color='#E74C3C'
            ), row=1, col=1)
            
            # Courbe du solde
            fig.add_trace(go.Scatter(
                x=periods,
                y=balance,
                name='Solde',
                line=dict(color='#3498DB', width=3)
            ), row=2, col=1)
            
            fig.update_layout(
                title='Tableau d\'Amortissement du Prêt',
                height=600,
                template='plotly_white'
            )
            
            charts.append({
                'title': 'Amortissement du Prêt',
                'chart': fig,
                'description': 'Évolution du remboursement sur la durée du prêt'
            })
        
        return charts

    def _create_generic_charts(self, data):
        """Crée des graphiques génériques"""
        charts = []
        
        # Graphique des résultats principaux
        if 'results' in data:
            results = data['results']
            labels = list(results.keys())
            values = list(results.values())
            
            fig = go.Figure(data=[
                go.Bar(x=labels, y=values, marker_color='#2E86AB')
            ])
            
            fig.update_layout(
                title='Résultats de l\'Analyse Financière',
                xaxis_title='Indicateurs',
                yaxis_title='Valeurs',
                template='plotly_white',
                height=400
            )
            
            charts.append({
                'title': 'Résultats Principaux',
                'chart': fig,
                'description': 'Synthèse des indicateurs calculés'
            })
        
        return charts

    def export_to_pdf(self, model_data, model_type, ai_analysis, filename):
        """Exporte les résultats en PDF professionnel"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # En-tête du rapport
        story.append(Paragraph("FINCASH", self.styles['CustomTitle']))
        story.append(Paragraph("Rapport d'Analyse Financière", self.styles['CustomHeading']))
        story.append(Paragraph(f"Type d'analyse: {model_type.upper()}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Résumé exécutif
        story.append(Paragraph("RÉSUMÉ EXÉCUTIF", self.styles['CustomHeading']))
        if 'summary' in model_data:
            story.append(Paragraph(model_data['summary'], self.styles['CustomNormal']))
        story.append(Spacer(1, 15))
        
        # Résultats principaux
        story.append(Paragraph("RÉSULTATS PRINCIPAUX", self.styles['CustomHeading']))
        if 'results' in model_data:
            # Création d'un tableau des résultats
            table_data = [['Indicateur', 'Valeur', 'Unité']]
            for key, value in model_data['results'].items():
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                    unit = "FCFA" if "montant" in key.lower() or "valeur" in key.lower() else ""
                    table_data.append([key, formatted_value, unit])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        story.append(Spacer(1, 20))
        
        # Graphiques
        charts = self.create_financial_charts(model_data, model_type)
        if charts:
            story.append(Paragraph("ANALYSES GRAPHIQUES", self.styles['CustomHeading']))
            for chart_info in charts:
                story.append(Paragraph(chart_info['title'], self.styles['CustomHeading']))
                
                # Conversion du graphique Plotly en image
                img_bytes = pio.to_image(chart_info['chart'], format='png', width=600, height=400)
                img_buffer = io.BytesIO(img_bytes)
                img = Image(img_buffer, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Paragraph(chart_info['description'], self.styles['CustomNormal']))
                story.append(Spacer(1, 15))
        
        # Analyse IA
        if ai_analysis:
            story.append(PageBreak())
            story.append(Paragraph("ANALYSE ET RECOMMANDATIONS IA", self.styles['CustomHeading']))
            
            if 'analysis' in ai_analysis:
                story.append(Paragraph("Analyse:", self.styles['CustomHeading']))
                story.append(Paragraph(ai_analysis['analysis'], self.styles['CustomNormal']))
                story.append(Spacer(1, 10))
            
            if 'recommendations' in ai_analysis:
                story.append(Paragraph("Recommandations:", self.styles['CustomHeading']))
                for i, rec in enumerate(ai_analysis['recommendations'], 1):
                    story.append(Paragraph(f"{i}. {rec}", self.styles['AIRecommendation']))
                story.append(Spacer(1, 10))
            
            if 'risks' in ai_analysis:
                story.append(Paragraph("Risques identifiés:", self.styles['CustomHeading']))
                for risk in ai_analysis['risks']:
                    story.append(Paragraph(f"• {risk}", self.styles['CustomNormal']))
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph("Ce rapport a été généré par Fincash - Plateforme de Modélisation Financière", 
                              self.styles['CustomNormal']))
        story.append(Paragraph("Contact: fincashinfos@gmail.com | +229 01 43 20 21 21", 
                              self.styles['CustomNormal']))
        
        # Construction du PDF
        doc.build(story)
        return filename

    def export_to_excel(self, model_data, model_type, ai_analysis, filename):
        """Exporte les résultats en Excel avec formatage professionnel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Feuille de résumé
            summary_data = {
                'Indicateur': [],
                'Valeur': [],
                'Description': []
            }
            
            if 'results' in model_data:
                for key, value in model_data['results'].items():
                    summary_data['Indicateur'].append(key)
                    summary_data['Valeur'].append(value)
                    summary_data['Description'].append(f"Résultat calculé pour {key}")
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Résumé', index=False)
            
            # Feuille de données détaillées
            if 'detailed_data' in model_data:
                df_details = pd.DataFrame(model_data['detailed_data'])
                df_details.to_excel(writer, sheet_name='Données Détaillées', index=False)
            
            # Feuille d'analyse IA
            if ai_analysis:
                ai_data = {
                    'Type': ['Analyse', 'Recommandations', 'Risques'],
                    'Contenu': [
                        ai_analysis.get('analysis', ''),
                        '; '.join(ai_analysis.get('recommendations', [])),
                        '; '.join(ai_analysis.get('risks', []))
                    ]
                }
                df_ai = pd.DataFrame(ai_data)
                df_ai.to_excel(writer, sheet_name='Analyse IA', index=False)
            
            # Formatage des feuilles
            workbook = writer.book
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                
                # Formatage des en-têtes
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.fill = cell.fill.copy(fgColor="366092")
                
                # Ajustement automatique des colonnes
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filename

    def generate_comprehensive_report(self, model_data, model_type, ai_analysis, base_filename):
        """Génère un rapport complet en PDF et Excel"""
        pdf_filename = f"{base_filename}.pdf"
        excel_filename = f"{base_filename}.xlsx"
        
        # Génération des fichiers
        pdf_path = self.export_to_pdf(model_data, model_type, ai_analysis, pdf_filename)
        excel_path = self.export_to_excel(model_data, model_type, ai_analysis, excel_filename)
        
        return {
            'pdf_path': pdf_path,
            'excel_path': excel_path,
            'generated_at': datetime.now().isoformat()
        }

