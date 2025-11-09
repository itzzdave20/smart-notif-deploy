from typing import Dict
import string

# Centralized design tokens
PRIMARY_COLOR = "#FF6B6B"
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F0F2F6"
TEXT_COLOR = "#262730"

GLOBAL_CSS = string.Template("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  
  :root {
    --primary-color: $PRIMARY_COLOR;
    --primary-dark: #e85b5b;
    --primary-light: #ff8a8a;
    --bg-color: $BACKGROUND_COLOR;
    --bg-alt: $SECONDARY_BACKGROUND_COLOR;
    --text-color: $TEXT_COLOR;
    --text-light: #6b7280;
    --border-color: #e5e7eb;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --gradient-primary: linear-gradient(135deg, $PRIMARY_COLOR 0%, #ff8a8a 100%);
    --gradient-bg: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  }
  
  * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }

  .main-header {
    font-size: 2.8rem;
    font-weight: 800;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 1.6rem;
    letter-spacing: -0.02em;
    text-shadow: 0 2px 4px rgba(255, 107, 107, 0.1);
    animation: fadeInDown 0.6s ease-out;
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

  .metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    padding: 1.5rem;
    border-radius: 16px;
    border-left: 4px solid var(--primary-color);
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out;
  }
  
  .metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-left-width: 6px;
  }

  .notification-card {
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
    animation: slideInRight 0.4s ease-out;
  }
  
  .notification-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateX(4px);
    border-color: var(--primary-light);
  }

  /* App background and sidebar colors */
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--gradient-bg) !important;
    background-attachment: fixed;
  }
  
  [data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-sm);
    border-bottom: 1px solid var(--border-color);
  }
  
  [data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
    backdrop-filter: blur(10px);
  }
  
  .block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    animation: fadeIn 0.6s ease-out;
  }

  .success-message {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    color: #155724;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #b8e0c5;
    box-shadow: var(--shadow-sm);
    animation: slideInRight 0.4s ease-out;
  }

  .error-message {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    color: #721c24;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #f1aeb5;
    box-shadow: var(--shadow-sm);
    animation: slideInRight 0.4s ease-out;
  }
  
  .info-message {
    background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
    color: #0c5460;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #abdde5;
    box-shadow: var(--shadow-sm);
    animation: slideInRight 0.4s ease-out;
  }
  
  .warning-message {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    color: #856404;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #ffe082;
    box-shadow: var(--shadow-sm);
    animation: slideInRight 0.4s ease-out;
  }

  /* Touch-friendly controls */
  .stButton>button {
    padding: 0.9rem 1.8rem;
    font-size: 1rem;
    font-weight: 600;
    background: var(--gradient-primary) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.3px;
  }
  
  .stButton>button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }
  
  .stButton>button:hover::before {
    left: 100%;
  }
  
  .stButton>button:hover {
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%) !important;
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  .stButton>button:active {
    transform: translateY(0);
    box-shadow: var(--shadow-sm);
  }
  
  .stButton>button:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.3);
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
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
    outline: none;
  }
  
  .stTextInput>div>div>input:hover,
  .stPassword>div>div>input:hover,
  .stTextArea>div>div>textarea:hover {
    border-color: var(--primary-light);
  }

  /* Links and accents */
  a, .stMarkdown a {
    color: var(--primary-color);
  }
  a:hover, .stMarkdown a:hover {
    color: #e85b5b;
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
    box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.15) !important;
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
    BACKGROUND_COLOR=BACKGROUND_COLOR,
    SECONDARY_BACKGROUND_COLOR=SECONDARY_BACKGROUND_COLOR,
    TEXT_COLOR=TEXT_COLOR,
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

