import markdown2
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    import weasyprint
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False
    logger.warning("WeasyPrint not found or missing system dependencies (common on Windows). Falling back to HTML generation.")

def generate_pdf(brief_markdown: str) -> bytes:
    html_content = markdown2.markdown(brief_markdown)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>JanSetu AI - Policy Brief</title>
        <style>
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background-color: #030712; 
                color: #e2e8f0; 
                line-height: 1.7; 
                padding: 40px 60px; 
            }}
            h1 {{ 
                color: #ffffff; 
                border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
                padding-bottom: 20px; 
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            h2 {{ 
                color: #818cf8; 
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 40px;
            }}
            h3 {{ 
                color: #34d399; 
                font-weight: 700;
            }}
            .header {{ 
                text-align: center; 
                margin-bottom: 50px; 
                background: rgba(255, 255, 255, 0.03);
                padding: 30px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            .header h1 {{ border: none; padding: 0; margin: 0 0 10px 0; }}
            .header p {{ margin: 0; color: #94a3b8; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; }}
            strong {{ color: #ffffff; font-weight: 700; }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 30px; 
                margin-bottom: 30px; 
                background: rgba(0, 0, 0, 0.4);
                border-radius: 12px;
                overflow: hidden;
            }}
            th, td {{ 
                border: 1px solid rgba(255, 255, 255, 0.05); 
                padding: 16px 20px; 
                text-align: left; 
            }}
            th {{ 
                background-color: rgba(255, 255, 255, 0.05); 
                color: #94a3b8; 
                font-weight: 800; 
                text-transform: uppercase; 
                font-size: 12px;
                letter-spacing: 1px;
            }}
            td {{ color: #cbd5e1; }}
            ul, ol {{ padding-left: 20px; margin-bottom: 20px; }}
            li {{ margin-bottom: 10px; }}
            .footer {{ 
                margin-top: 60px;
                text-align: center; 
                font-size: 11px; 
                color: #475569; 
                padding-top: 20px; 
                border-top: 1px solid rgba(255, 255, 255, 0.05);
                font-family: monospace;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: #030712; }}
            ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>JanSetu AI — Infrastructure Priority Brief</h1>
            <p><strong>Generated on:</strong> {current_date}</p>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>Generated automatically by JanSetu AI System.</p>
        </div>
    </body>
    </html>
    """
    
    if HAS_WEASYPRINT:
        try:
            return weasyprint.HTML(string=full_html).write_pdf()
        except Exception as e:
            logger.error(f"WeasyPrint error during generation: {e}")
            return full_html.encode('utf-8')
    else:
        # If no WeasyPrint, just return the raw HTML file.
        # The frontend iframe will render it perfectly anyway.
        return full_html.encode('utf-8')
