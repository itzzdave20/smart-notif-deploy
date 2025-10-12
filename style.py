from typing import Dict
import string

# Centralized design tokens
PRIMARY_COLOR = "#FF6B6B"
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F0F2F6"
TEXT_COLOR = "#262730"

GLOBAL_CSS = string.Template("""
<style>
  :root {
    --primary-color: $PRIMARY_COLOR;
    --bg-color: $BACKGROUND_COLOR;
    --bg-alt: $SECONDARY_BACKGROUND_COLOR;
    --text-color: $TEXT_COLOR;
  }

  .main-header {
    font-size: 2.4rem;
    color: var(--primary-color);
    text-align: center;
    margin-bottom: 1.6rem;
  }

  .metric-card {
    background-color: var(--bg-alt);
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid var(--primary-color);
  }

  .notification-card {
    background-color: #ffffff;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e0e0e0;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  }

  /* App background and sidebar colors */
  html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--bg-color) !important;
  }
  [data-testid="stHeader"] {
    background: transparent !important;
  }
  [data-testid="stSidebar"] > div {
    background-color: var(--bg-alt) !important;
  }

  .success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #c3e6cb;
  }

  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #f5c6cb;
  }

  /* Touch-friendly controls */
  .stButton>button {
    padding: 0.9rem 1.2rem;
    font-size: 1rem;
    background-color: var(--primary-color) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    transition: background-color 0.15s ease, transform 0.02s ease;
  }
  .stButton>button:hover {
    background-color: #e85b5b !important; /* slightly darker */
  }
  .stButton>button:active {
    transform: translateY(1px);
  }
  .stTextInput>div>div>input,
  .stPassword>div>div>input,
  .stSelectbox>div>div>div>div,
  .stNumberInput>div>div>input {
    min-height: 44px;
    font-size: 1rem;
  }

  /* Links and accents */
  a, .stMarkdown a {
    color: var(--primary-color);
  }
  a:hover, .stMarkdown a:hover {
    color: #e85b5b;
  }

  /* Headings and section accents */
  h1, h2, h3, h4, h5, h6 { color: var(--text-color); }
  h2, h3 { border-bottom: 2px solid var(--bg-alt); padding-bottom: 0.25rem; }
  .main-header { letter-spacing: 0.2px; }

  /* Tabs */
  [data-baseweb="tab-highlight"] { background-color: var(--primary-color) !important; }
  [data-baseweb="tab"] { color: var(--text-color) !important; }

  /* Expanders */
  .streamlit-expanderHeader { background-color: var(--bg-alt); border-radius: 8px; }

  /* Tables */
  thead tr th { background-color: var(--bg-alt) !important; color: var(--text-color) !important; }
  tbody tr:hover { background-color: rgba(0,0,0,0.02) !important; }

  /* Inputs focus color */
  input:focus, select:focus, textarea:focus { outline-color: var(--primary-color); box-shadow: 0 0 0 2px rgba(255,107,107,0.25); }

  /* Utility badges */
  .badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }
  .badge-success { background: #e6f4ea; color: #18794e; border: 1px solid #b8e0c5; }
  .badge-warning { background: #fff4e5; color: #8a4b12; border: 1px solid #ffe0b2; }
  .badge-info { background: #e6f3ff; color: #0b5cad; border: 1px solid #c9e2ff; }
  .badge-danger { background: #fde7ea; color: #8a1c24; border: 1px solid #f5b5bd; }

  /* Colored cards */
  .card-primary { border-left: 4px solid var(--primary-color); background: var(--bg-alt); padding: 1rem; border-radius: 8px; }
  .card-success { border-left: 4px solid #2db36c; background: #ecfff3; padding: 1rem; border-radius: 8px; }
  .card-warning { border-left: 4px solid #f4a100; background: #fff9e6; padding: 1rem; border-radius: 8px; }
  .card-danger { border-left: 4px solid #d64545; background: #fff1f3; padding: 1rem; border-radius: 8px; }

  /* Responsive layout tweaks for small screens */
  @media (max-width: 768px) {
    .main-header {
      font-size: 1.8rem;
      margin-bottom: 1.1rem;
    }
    .block-container {
      padding-left: 0.5rem;
      padding-right: 0.5rem;
    }
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

