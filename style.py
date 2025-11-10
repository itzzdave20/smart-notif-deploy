from typing import Dict
import string

# Centralized design tokens - Enhanced Modern Palette
PRIMARY_COLOR = "#6366F1"  # Indigo - more modern and professional
SECONDARY_COLOR = "#8B5CF6"  # Purple accent
ACCENT_COLOR = "#EC4899"  # Pink accent
SUCCESS_COLOR = "#10B981"  # Green
WARNING_COLOR = "#F59E0B"  # Amber
ERROR_COLOR = "#EF4444"  # Red
INFO_COLOR = "#3B82F6"  # Blue
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F8FAFC"
TEXT_COLOR = "#1E293B"
TEXT_LIGHT = "#64748B"

GLOBAL_CSS = string.Template("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  
  :root {
    --primary-color: $PRIMARY_COLOR;
    --primary-dark: #4F46E5;
    --primary-light: #818CF8;
    --secondary-color: $SECONDARY_COLOR;
    --accent-color: $ACCENT_COLOR;
    --success-color: $SUCCESS_COLOR;
    --warning-color: $WARNING_COLOR;
    --error-color: $ERROR_COLOR;
    --info-color: $INFO_COLOR;
    --bg-color: $BACKGROUND_COLOR;
    --bg-alt: $SECONDARY_BACKGROUND_COLOR;
    --text-color: $TEXT_COLOR;
    --text-light: $TEXT_LIGHT;
    --border-color: #E2E8F0;
    --border-light: #F1F5F9;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --shadow-primary: 0 10px 25px -5px rgba(99, 102, 241, 0.3);
    --gradient-primary: linear-gradient(135deg, $PRIMARY_COLOR 0%, $SECONDARY_COLOR 100%);
    --gradient-accent: linear-gradient(135deg, $ACCENT_COLOR 0%, $SECONDARY_COLOR 100%);
    --gradient-bg: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
    --gradient-card: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    --gradient-success: linear-gradient(135deg, $SUCCESS_COLOR 0%, #34D399 100%);
    --gradient-warning: linear-gradient(135deg, $WARNING_COLOR 0%, #FBBF24 100%);
    --gradient-error: linear-gradient(135deg, $ERROR_COLOR 0%, #F87171 100%);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-2xl: 24px;
  }
  
  * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  .main-header {
    font-size: 3rem;
    font-weight: 800;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 2rem;
    letter-spacing: -0.03em;
    position: relative;
    animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    line-height: 1.2;
  }
  
  .main-header::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 4px;
    background: var(--gradient-primary);
    border-radius: 2px;
    animation: expandWidth 0.8s ease-out 0.3s both;
  }
  
  @keyframes expandWidth {
    from { width: 0; opacity: 0; }
    to { width: 60px; opacity: 1; }
  }
  
  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  
  @keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
  
  @keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
    50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8), 0 0 30px rgba(99, 102, 241, 0.4); }
  }
  
  @keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }

  .metric-card {
    background: var(--gradient-card);
    padding: 2rem;
    border-radius: var(--radius-xl);
    border: 1px solid var(--border-light);
    border-left: 5px solid var(--primary-color);
    box-shadow: var(--shadow-md);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: scaleIn 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
    transition: left 0.5s;
  }
  
  .metric-card:hover::before {
    left: 100%;
  }
  
  .metric-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: var(--shadow-xl), var(--shadow-primary);
    border-left-width: 6px;
    border-color: var(--primary-light);
  }

  .notification-card {
    background: var(--gradient-card);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-light);
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: slideInRight 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .notification-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--gradient-primary);
    transform: scaleY(0);
    transition: transform 0.3s ease;
  }
  
  .notification-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateX(6px) scale(1.01);
    border-color: var(--primary-light);
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  }
  
  .notification-card:hover::after {
    transform: scaleY(1);
  }

  /* App background and sidebar colors */
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--gradient-bg) !important;
    background-attachment: fixed;
    min-height: 100vh;
  }
  
  /* Animated background pattern */
  [data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
      radial-gradient(circle at 20% 50%, rgba(99, 102, 241, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 40% 20%, rgba(236, 72, 153, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }
  
  [data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border-bottom: 1px solid var(--border-light);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  
  [data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid var(--border-light);
  }
  
  .block-container {
    padding-top: 3.5rem;
    padding-bottom: 4rem;
    animation: fadeIn 0.8s ease-out;
    position: relative;
    z-index: 1;
  }

  .success-message {
    background: var(--gradient-success);
    color: #065F46;
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(16, 185, 129, 0.3);
    box-shadow: var(--shadow-md);
    animation: slideInRight 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .success-message::before {
    content: '✓';
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    opacity: 0.3;
  }

  .error-message {
    background: var(--gradient-error);
    color: #991B1B;
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(239, 68, 68, 0.3);
    box-shadow: var(--shadow-md);
    animation: slideInRight 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .error-message::before {
    content: '✕';
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    opacity: 0.3;
  }
  
  .info-message {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
    color: #1E40AF;
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(59, 130, 246, 0.3);
    box-shadow: var(--shadow-md);
    animation: slideInRight 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .info-message::before {
    content: 'ℹ';
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    opacity: 0.3;
  }
  
  .warning-message {
    background: var(--gradient-warning);
    color: #92400E;
    padding: 1.25rem 1.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(245, 158, 11, 0.3);
    box-shadow: var(--shadow-md);
    animation: slideInRight 0.5s ease-out;
    position: relative;
    overflow: hidden;
  }
  
  .warning-message::before {
    content: '⚠';
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    opacity: 0.3;
  }

  /* Touch-friendly controls - Enhanced */
  .stButton>button {
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    background: var(--gradient-primary) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md), var(--shadow-primary);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-size: 0.875rem;
    cursor: pointer;
  }
  
  .stButton>button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.6s;
  }
  
  .stButton>button:hover::before {
    left: 100%;
  }
  
  .stButton>button::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
  }
  
  .stButton>button:active::after {
    width: 300px;
    height: 300px;
  }
  
  .stButton>button:hover {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary-color) 100%) !important;
    transform: translateY(-3px) scale(1.02);
    box-shadow: var(--shadow-xl), var(--shadow-primary);
  }
  
  .stButton>button:active {
    transform: translateY(-1px) scale(0.98);
    box-shadow: var(--shadow-md);
  }
  
  .stButton>button:focus {
    outline: none;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.4), var(--shadow-lg);
  }
  
  /* Primary button variant */
  .stButton>button[kind="primary"] {
    background: var(--gradient-primary) !important;
    box-shadow: var(--shadow-lg), var(--shadow-primary);
  }
  
  /* Secondary button variant */
  .stButton>button[kind="secondary"] {
    background: linear-gradient(135deg, var(--bg-alt) 0%, #FFFFFF 100%) !important;
    color: var(--primary-color) !important;
    border: 2px solid var(--primary-color) !important;
  }
  
  .stButton>button[kind="secondary"]:hover {
    background: var(--gradient-primary) !important;
    color: #FFFFFF !important;
  }
  .stTextInput>div>div>input,
  .stPassword>div>div>input,
  .stSelectbox>div>div>div>div,
  .stNumberInput>div>div>input,
  .stTextArea>div>div>textarea {
    min-height: 44px;
    font-size: 1rem;
    border-radius: 10px;
    border: 2px solid var(--border-color);
    transition: all 0.3s ease;
    padding: 0.75rem 1rem;
  }
  
  .stTextInput>div>div>input:focus,
  .stPassword>div>div>input:focus,
  .stSelectbox>div>div>div>div:focus,
  .stNumberInput>div>div>input:focus,
  .stTextArea>div>div>textarea:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    outline: none;
    background: #FFFFFF;
  }
  
  .stTextInput>div>div>input:hover,
  .stPassword>div>div>input:hover,
  .stTextArea>div>div>textarea:hover {
    border-color: var(--primary-light);
    background: #FAFBFC;
  }
  
  .stTextInput>div>div>input,
  .stPassword>div>div>input,
  .stTextArea>div>div>textarea {
    background: #FFFFFF;
  }

  /* Links and accents */
  a, .stMarkdown a {
    color: var(--primary-color);
    text-decoration: none;
    transition: all 0.3s ease;
    position: relative;
  }
  
  a::after, .stMarkdown a::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--gradient-primary);
    transition: width 0.3s ease;
  }
  
  a:hover::after, .stMarkdown a:hover::after {
    width: 100%;
  }
  
  a:hover, .stMarkdown a:hover {
    color: var(--primary-dark);
  }

  /* Headings and section accents */
  h1, h2, h3, h4, h5, h6 { 
    color: var(--text-color);
    font-weight: 700;
    letter-spacing: -0.01em;
    animation: fadeInDown 0.5s ease-out;
  }
  
  h1 {
    font-size: 2.5rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  h2 {
    font-size: 2rem;
    border-bottom: 3px solid;
    border-image: var(--gradient-primary) 1;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
  }
  
  h3 {
    font-size: 1.5rem;
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.25rem;
    margin-bottom: 1rem;
  }
  
  .main-header { letter-spacing: -0.02em; }

  /* Tabs */
  [data-baseweb="tab-highlight"] { 
    background: var(--gradient-primary) !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0;
  }
  
  [data-baseweb="tab"] { 
    color: var(--text-color) !important;
    font-weight: 500;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
  }
  
  [data-baseweb="tab"]:hover {
    color: var(--primary-color) !important;
    background: rgba(255, 107, 107, 0.05);
  }
  
  [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary-color) !important;
    font-weight: 600;
  }

  /* Expanders */
  .streamlit-expanderHeader { 
    background: linear-gradient(135deg, var(--bg-alt) 0%, #ffffff 100%);
    border-radius: 12px;
    padding: 1rem;
    transition: all 0.3s ease;
    border: 1px solid var(--border-color);
  }
  
  .streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, #ffffff 100%);
    border-color: var(--primary-light);
  }
  
  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  
  ::-webkit-scrollbar-track {
    background: var(--bg-alt);
    border-radius: 10px;
  }
  
  ::-webkit-scrollbar-thumb {
    background: var(--gradient-primary);
    border-radius: 10px;
    border: 2px solid var(--bg-alt);
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
  }
  
  /* Loading spinner enhancement */
  .stSpinner > div {
    border-color: var(--primary-color) transparent transparent transparent !important;
  }
  
  /* File uploader styling */
  .stFileUploader > div {
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
    transition: all 0.3s ease;
  }
  
  .stFileUploader > div:hover {
    border-color: var(--primary-color);
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, #ffffff 100%);
  }
  
  /* Divider styling */
  hr {
    border: none;
    height: 2px;
    background: var(--gradient-primary);
    margin: 2rem 0;
    border-radius: 2px;
  }
  
  /* Code block styling */
  code {
    background: var(--bg-alt);
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-size: 0.9em;
    color: var(--primary-color);
    border: 1px solid var(--border-color);
  }
  
  pre {
    background: var(--bg-alt);
    padding: 1rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    overflow-x: auto;
  }
  
  /* Chat message styling */
  [data-testid="stChatMessage"] {
    animation: slideInRight 0.4s ease-out;
  }
  
  /* Selectbox dropdown */
  [data-baseweb="select"] {
    border-radius: 10px;
  }
  
  /* Date input styling */
  .stDateInput > div > div > input {
    border-radius: 10px;
    border: 2px solid var(--border-color);
  }
  
  /* Time input styling */
  .stTimeInput > div > div > input {
    border-radius: 10px;
    border: 2px solid var(--border-color);
  }

  /* Tables */
  thead tr th { 
    background: var(--gradient-primary) !important;
    color: #ffffff !important;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    padding: 1rem !important;
    border: none !important;
  }
  
  tbody tr {
    transition: all 0.2s ease;
  }
  
  tbody tr:hover { 
    background: linear-gradient(90deg, rgba(255, 107, 107, 0.05) 0%, transparent 100%) !important;
    transform: scale(1.01);
    box-shadow: var(--shadow-sm);
  }
  
  tbody td {
    padding: 0.75rem 1rem !important;
    border-bottom: 1px solid var(--border-color) !important;
  }

  /* Inputs focus color */
  input:focus, select:focus, textarea:focus { 
    outline: none;
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
  }
  
  /* Select dropdown styling */
  .stSelectbox>div>div>div {
    border-radius: 10px;
    border: 2px solid var(--border-color);
    transition: all 0.3s ease;
  }
  
  .stSelectbox>div>div>div:hover {
    border-color: var(--primary-light);
  }
  
  /* Checkbox styling */
  .stCheckbox>div>div>div>label {
    font-weight: 500;
    color: var(--text-color);
  }
  
  /* Radio button styling */
  [role="radiogroup"]>label {
    border-radius: 10px;
    padding: 0.75rem 1rem;
    transition: all 0.3s ease;
    border: 2px solid var(--border-color);
  }
  
  [role="radiogroup"]>label:hover {
    border-color: var(--primary-light);
    background: rgba(255, 107, 107, 0.05);
  }
  
  [role="radiogroup"]>label[data-checked="true"] {
    border-color: var(--primary-color);
    background: rgba(255, 107, 107, 0.1);
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
  }

  /* Utility badges */
  .badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
  .badge-success { background: #e6f4ea; color: #18794e; border: 1px solid #b8e0c5; }
  .badge-warning { background: #fff4e5; color: #8a4b12; border: 1px solid #ffe0b2; }
  .badge-info { background: #e6f3ff; color: #0b5cad; border: 1px solid #c9e2ff; }
  .badge-danger { background: #fde7ea; color: #8a1c24; border: 1px solid #f5b5bd; }

  /* Colored cards */
  .card-primary { 
    border-left: 4px solid var(--primary-color); 
    background: linear-gradient(135deg, #fff5f5 0%, #fff 100%); 
    padding: 1.5rem; 
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
  }
  
  .card-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .card-success { 
    border-left: 4px solid #2db36c; 
    background: linear-gradient(135deg, #ecfff3 0%, #fff 100%); 
    padding: 1.5rem; 
    border-radius: 12px;
    box-shadow: var(--shadow-md);
  }
  
  .card-warning { 
    border-left: 4px solid #f4a100; 
    background: linear-gradient(135deg, #fff9e6 0%, #fff 100%); 
    padding: 1.5rem; 
    border-radius: 12px;
    box-shadow: var(--shadow-md);
  }
  
  .card-danger { 
    border-left: 4px solid #d64545; 
    background: linear-gradient(135deg, #fff1f3 0%, #fff 100%); 
    padding: 1.5rem; 
    border-radius: 12px;
    box-shadow: var(--shadow-md);
  }
  
  /* Glassmorphism effect */
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: var(--shadow-lg);
  }
  
  /* Enhanced metric styling */
  [data-testid="stMetricValue"] {
    font-weight: 700;
    font-size: 2rem;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  [data-testid="stMetricLabel"] {
    color: var(--text-light);
    font-weight: 500;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Mobile-first responsive design */
  @media (max-width: 768px) {
    .main-header {
      font-size: 1.8rem;
      margin-bottom: 1.1rem;
    }
    .block-container {
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }
    
    /* Mobile-specific button improvements */
    .stButton>button {
      min-height: 48px;
      padding: 1rem 1.5rem;
      font-size: 1.1rem;
      touch-action: manipulation;
    }
    
    /* Mobile form improvements */
    .stTextInput>div>div>input,
    .stPassword>div>div>input,
    .stSelectbox>div>div>div>div,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {
      min-height: 48px;
      font-size: 16px; /* Prevents zoom on iOS */
      padding: 12px;
    }
    
    /* Mobile table improvements */
    .stDataFrame {
      font-size: 14px;
      overflow-x: auto;
    }
    
    /* Mobile sidebar improvements */
    [data-testid="stSidebar"] {
      width: 100% !important;
      max-width: 100% !important;
    }
    
    /* Mobile column improvements */
    .stColumn {
      margin-bottom: 1rem;
    }
    
    /* Mobile notification cards */
    .notification-card {
      margin-bottom: 0.5rem;
      padding: 0.75rem;
    }
    
    /* Mobile metric cards */
    .metric-card {
      margin-bottom: 0.5rem;
      padding: 0.75rem;
    }
  }
  
  /* iPhone specific fixes */
  @media (max-width: 414px) {
    .main-header {
      font-size: 1.6rem;
    }
    
    .stButton>button {
      min-height: 44px;
      padding: 0.8rem 1.2rem;
      font-size: 1rem;
    }
    
    .block-container {
      padding-left: 0.25rem;
      padding-right: 0.25rem;
    }
  }
  
  /* Landscape mobile orientation */
  @media (max-width: 896px) and (orientation: landscape) {
    .main-header {
      font-size: 1.4rem;
      margin-bottom: 0.5rem;
    }
    
    .stButton>button {
      min-height: 40px;
      padding: 0.6rem 1rem;
    }
  }
  
  /* Touch device improvements */
  @media (hover: none) and (pointer: coarse) {
    .stButton>button:hover {
      background-color: var(--primary-color) !important;
    }
    
    /* Increase touch targets */
    .stButton>button,
    .stSelectbox>div>div>div,
    .stCheckbox>div>div>div>label {
      min-height: 44px;
    }
  }
  
  /* iOS Safari specific fixes */
  .ios-device {
    -webkit-overflow-scrolling: touch;
  }
  
  .ios-device .stTextInput>div>div>input,
  .ios-device .stPassword>div>div>input,
  .ios-device .stTextArea>div>div>textarea {
    font-size: 16px !important; /* Prevents zoom */
    transform: translateZ(0); /* Hardware acceleration */
  }
  
  /* Android specific fixes */
  .android-device .stButton>button {
    -webkit-tap-highlight-color: transparent;
  }
  
  /* Mobile device specific improvements */
  .mobile-device {
    /* Prevent horizontal scroll */
    overflow-x: hidden;
  }
  
  .mobile-device .stDataFrame {
    font-size: 12px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  
  .mobile-device .stTabs [role="tablist"] {
    flex-wrap: wrap;
  }
  
  .mobile-device .stTabs [role="tab"] {
    min-width: auto;
    flex: 1;
    text-align: center;
  }
  
  /* Fix for mobile sidebar */
  .mobile-device [data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    z-index: 999 !important;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .mobile-device [data-testid="stSidebar"][aria-expanded="true"] {
    transform: translateX(0);
  }
  
  /* Mobile-friendly file uploader */
  .mobile-device .stFileUploader>div {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    background: #f9f9f9;
  }
  
  /* Mobile notification improvements */
  .mobile-device .notification-card {
    margin: 10px 0;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  /* Mobile form improvements */
  .mobile-device .stForm {
    padding: 10px;
  }
  
  .mobile-device .stForm .stButton {
    margin-top: 15px;
  }
  
  /* Mobile table improvements */
  .mobile-device table {
    font-size: 14px;
    width: 100%;
  }
  
  .mobile-device th,
  .mobile-device td {
    padding: 8px 4px;
    word-wrap: break-word;
  }
</style>
""").substitute(
    PRIMARY_COLOR=PRIMARY_COLOR,
    SECONDARY_COLOR=SECONDARY_COLOR,
    ACCENT_COLOR=ACCENT_COLOR,
    SUCCESS_COLOR=SUCCESS_COLOR,
    WARNING_COLOR=WARNING_COLOR,
    ERROR_COLOR=ERROR_COLOR,
    INFO_COLOR=INFO_COLOR,
    BACKGROUND_COLOR=BACKGROUND_COLOR,
    SECONDARY_BACKGROUND_COLOR=SECONDARY_BACKGROUND_COLOR,
    TEXT_COLOR=TEXT_COLOR,
    TEXT_LIGHT=TEXT_LIGHT,
)


def get_plotly_template() -> str:
    """Return a simple Plotly template name that matches our palette."""
    # Users can override per-chart; keep default to 'plotly_white'
    return "plotly_white"


def with_primary_color(fig) -> None:
    """Apply primary color accents to a Plotly figure in-place."""
    fig.update_layout(
        template=get_plotly_template(),
        title_font_color=PRIMARY_COLOR,
        font=dict(color=TEXT_COLOR),
        legend=dict(title_font_color=TEXT_COLOR),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
    )

