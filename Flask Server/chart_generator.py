import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os
import uuid
from llm_service import LLMService

class ChartGenerator:
    def __init__(self):
        self.llm_service = LLMService()
        self.charts_folder = 'generated_charts'
        os.makedirs(self.charts_folder, exist_ok=True)
    
    def generate_chart(self, user_query: str, context: str) -> dict:
        """
        Generate a chart based on user query and context data
        Returns: {'filename': str, 'chart_type': str, 'title': str}
        """
        try:
            # Use LLM to extract data and chart specifications from context
            chart_spec = self._get_chart_specifications(user_query, context)
            
            # Parse the data
            data = self._parse_data_from_spec(chart_spec)
            
            # Generate the chart
            filename = self._create_chart(data, chart_spec)
            
            return {
                'filename': filename,
                'chart_type': chart_spec.get('chart_type', 'line'),
                'title': chart_spec.get('title', 'Data Visualization')
            }
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            raise
    
    def _get_chart_specifications(self, user_query: str, context: str) -> dict:
        """
        Use LLM to extract chart specifications from user query and context
        """
        prompt = f"""You are a data visualization expert. Extract data from the context and create chart specifications.

User Query: {user_query}

Context Data:
{context[:5000]}

IMPORTANT INSTRUCTIONS:
1. Carefully extract ALL relevant numerical data from the context
2. For time-based data, include ALL time periods (months, quarters, etc.), not just one
3. Match the chart type to the user's request (bar, line, pie, etc.)
4. Ensure x_values, y_values, and labels arrays are the SAME length
5. For monthly data, use month names as labels (e.g., ["Jan 2024", "Feb 2024", ...])
6. Sort data chronologically if it's time-based

Respond ONLY with a JSON object in this exact format:
{{
    "chart_type": "bar",
    "title": "Descriptive Title",
    "x_label": "X Axis Label",
    "y_label": "Y Axis Label",
    "x_values": [0, 1, 2, 3],
    "y_values": [100, 200, 300, 400],
    "labels": ["Label1", "Label2", "Label3", "Label4"]
}}

EXAMPLE - If data shows spend across months:
{{
    "chart_type": "bar",
    "title": "Total Media Spend Across 2024",
    "x_label": "Month",
    "y_label": "Spend ($)",
    "x_values": [0, 1, 2, 3, 4, 5],
    "y_values": [50000, 60000, 55000, 70000, 65000, 80000],
    "labels": ["Jan 2024", "Feb 2024", "Mar 2024", "Apr 2024", "May 2024", "Jun 2024"]
}}"""

        response = self.llm_service.openai_client.chat.completions.create(
            model="gpt-5-2025-08-07",
            messages=[
                {"role": "system", "content": "You are a data visualization expert. Extract chart specifications from the provided data and return them in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )
        
        import json
        spec_text = response.choices[0].message.content.strip()
        
        print(f"Chart spec response from LLM:\n{spec_text}\n")
        
        # Extract JSON from response (handle code blocks)
        if '```json' in spec_text:
            spec_text = spec_text.split('```json')[1].split('```')[0].strip()
        elif '```' in spec_text:
            spec_text = spec_text.split('```')[1].split('```')[0].strip()
        
        spec = json.loads(spec_text)
        
        # Validate that arrays have the same length
        if spec.get('labels') and spec.get('y_values'):
            if len(spec['labels']) != len(spec['y_values']):
                print(f"WARNING: Label count ({len(spec['labels'])}) doesn't match y_values count ({len(spec['y_values'])})")
                # Truncate to shorter length
                min_len = min(len(spec['labels']), len(spec['y_values']))
                spec['labels'] = spec['labels'][:min_len]
                spec['y_values'] = spec['y_values'][:min_len]
                if spec.get('x_values'):
                    spec['x_values'] = spec['x_values'][:min_len]
        
        print(f"Final spec: {spec}\n")
        return spec
    
    def _parse_data_from_spec(self, spec: dict) -> dict:
        """
        Parse and validate data from chart specification
        """
        return {
            'x_values': spec.get('x_values', []),
            'y_values': spec.get('y_values', []),
            'labels': spec.get('labels', []),
            'chart_type': spec.get('chart_type', 'line'),
            'title': spec.get('title', 'Data Visualization'),
            'x_label': spec.get('x_label', 'X Axis'),
            'y_label': spec.get('y_label', 'Y Axis')
        }
    
    def _create_chart(self, data: dict, spec: dict) -> str:
        """
        Create the actual chart using matplotlib
        """
        # Set default style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Create figure with appropriate size
        fig, ax = plt.subplots(figsize=(12, 7))
        
        chart_type = data['chart_type'].lower()
        
        # Determine if we should use labels or x_values
        use_labels = data.get('labels') and len(data['labels']) > 0
        
        if chart_type == 'line':
            if use_labels:
                x_positions = range(len(data['labels']))
                ax.plot(x_positions, data['y_values'], marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
                ax.set_xticks(x_positions)
                ax.set_xticklabels(data['labels'], rotation=45, ha='right')
            else:
                ax.plot(data.get('x_values', range(len(data['y_values']))), data['y_values'], 
                       marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
        
        elif chart_type == 'bar':
            if use_labels:
                x_positions = range(len(data['labels']))
                bars = ax.bar(x_positions, data['y_values'], color='#2E86AB', alpha=0.8, edgecolor='#1A5276')
                ax.set_xticks(x_positions)
                ax.set_xticklabels(data['labels'], rotation=45, ha='right')
                
                # Add value labels on top of bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:,.0f}',
                           ha='center', va='bottom', fontsize=9)
            else:
                bars = ax.bar(data.get('x_values', range(len(data['y_values']))), data['y_values'], 
                      color='#2E86AB', alpha=0.8, edgecolor='#1A5276')
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:,.0f}',
                           ha='center', va='bottom', fontsize=9)
        
        elif chart_type == 'pie':
            colors = plt.cm.Set3(range(len(data['y_values'])))
            ax.pie(data['y_values'], labels=data.get('labels', None), autopct='%1.1f%%', 
                   startangle=90, colors=colors, textprops={'fontsize': 10})
            ax.axis('equal')
        
        elif chart_type == 'scatter':
            if data.get('x_values') and data.get('y_values'):
                ax.scatter(data['x_values'], data['y_values'], s=100, alpha=0.6, c='#2E86AB', edgecolors='#1A5276')
        
        elif chart_type == 'histogram':
            ax.hist(data['y_values'], bins=min(20, max(5, len(data['y_values'])//2)), 
                   color='#2E86AB', alpha=0.7, edgecolor='#1A5276')
        
        # Set labels and title
        if chart_type != 'pie':
            ax.set_xlabel(data['x_label'], fontsize=13, fontweight='bold', labelpad=10)
            ax.set_ylabel(data['y_label'], fontsize=13, fontweight='bold', labelpad=10)
            
            # Format y-axis with commas for large numbers
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        ax.set_title(data['title'], fontsize=16, fontweight='bold', pad=20)
        
        # Add grid for better readability (except pie charts)
        if chart_type != 'pie':
            ax.grid(True, alpha=0.3, linestyle='--')
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save chart
        filename = f"chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join(self.charts_folder, filename)
        plt.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        
        return filename

