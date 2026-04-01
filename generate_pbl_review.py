"""
UniverBot PBL Review PDF Generator
Generates a comprehensive Project-Based Learning review for the UniverBot project.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import (
    HexColor, white, black, Color
)
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import Flowable
import datetime

# -------------------------------------------------------------------
# Color Palette (matching UniverBot brand)
# -------------------------------------------------------------------
CYAN        = HexColor("#00E5FF")
DARK_BG     = HexColor("#030617")
MID_BG      = HexColor("#0a0f1a")
LIGHT_TEXT  = HexColor("#94a3b8")
WHITE       = HexColor("#ffffff")
BORDER      = HexColor("#1e293b")
GREEN       = HexColor("#22c55e")
PURPLE      = HexColor("#a855f7")
ORANGE      = HexColor("#f97316")
RED         = HexColor("#ef4444")
YELLOW      = HexColor("#eab308")
BLUE        = HexColor("#3b82f6")

OUTPUT_PATH = r"c:\Users\gowth\Desktop\univerbot\UniverBot_PBL_Review.pdf"

# -------------------------------------------------------------------
# Custom Flowables
# -------------------------------------------------------------------
class ColoredHR(Flowable):
    def __init__(self, color=CYAN, width=None, thickness=1.5, spaceAfter=8):
        Flowable.__init__(self)
        self.color = color
        self.line_width = width
        self.thickness = thickness
        self.spaceAfter = spaceAfter
        self.height = thickness + spaceAfter

    def draw(self):
        w = self.line_width or self.canv._pagesize[0] - 4 * cm
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.thickness / 2, w, self.thickness / 2)


class SectionTag(Flowable):
    """Colored pill badge used as section labels."""
    def __init__(self, text, bg_color=CYAN, text_color=DARK_BG, font_size=9):
        Flowable.__init__(self)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.width = len(text) * font_size * 0.62 + 18
        self.height = font_size + 10

    def draw(self):
        c = self.canv
        r = self.height / 2
        c.setFillColor(self.bg_color)
        c.roundRect(0, 0, self.width, self.height, r, fill=1, stroke=0)
        c.setFillColor(self.text_color)
        c.setFont("Helvetica-Bold", self.font_size)
        c.drawCentredString(self.width / 2, 3, self.text)


# -------------------------------------------------------------------
# Style definitions
# -------------------------------------------------------------------
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontSize=36,
            fontName="Helvetica-Bold",
            textColor=CYAN,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=42,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontSize=16,
            fontName="Helvetica",
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta",
            fontSize=11,
            fontName="Helvetica",
            textColor=LIGHT_TEXT,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "chapter": ParagraphStyle(
            "chapter",
            fontSize=22,
            fontName="Helvetica-Bold",
            textColor=CYAN,
            spaceBefore=18,
            spaceAfter=4,
            leading=28,
        ),
        "section": ParagraphStyle(
            "section",
            fontSize=15,
            fontName="Helvetica-Bold",
            textColor=WHITE,
            spaceBefore=14,
            spaceAfter=4,
            leading=20,
        ),
        "subsection": ParagraphStyle(
            "subsection",
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=CYAN,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontSize=10,
            fontName="Helvetica",
            textColor=LIGHT_TEXT,
            spaceBefore=3,
            spaceAfter=5,
            alignment=TA_JUSTIFY,
            leading=16,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontSize=10,
            fontName="Helvetica",
            textColor=LIGHT_TEXT,
            leftIndent=14,
            spaceBefore=2,
            spaceAfter=2,
            bulletIndent=4,
            leading=15,
        ),
        "code": ParagraphStyle(
            "code",
            fontSize=8.5,
            fontName="Courier",
            textColor=GREEN,
            backColor=MID_BG,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=4,
            leading=13,
            borderPadding=(6, 8, 6, 8),
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=DARK_BG,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontSize=9,
            fontName="Helvetica",
            textColor=LIGHT_TEXT,
            leading=13,
        ),
        "highlight": ParagraphStyle(
            "highlight",
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=CYAN,
            spaceBefore=3,
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontSize=9,
            fontName="Helvetica-Oblique",
            textColor=LIGHT_TEXT,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "score": ParagraphStyle(
            "score",
            fontSize=28,
            fontName="Helvetica-Bold",
            textColor=GREEN,
            alignment=TA_CENTER,
        ),
        "label": ParagraphStyle(
            "label",
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=CYAN,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "toc_entry": ParagraphStyle(
            "toc_entry",
            fontSize=11,
            fontName="Helvetica",
            textColor=LIGHT_TEXT,
            leftIndent=0,
            spaceBefore=4,
            spaceAfter=4,
        ),
    }
    return styles


# -------------------------------------------------------------------
# Helper builders
# -------------------------------------------------------------------
def dark_table(data, col_widths, header_bg=CYAN):
    """Build a styled dark-theme table."""
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  DARK_BG),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        ("BACKGROUND",   (0, 1), (-1, -1), MID_BG),
        ("TEXTCOLOR",    (0, 1), (-1, -1), LIGHT_TEXT),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MID_BG, HexColor("#0d1424")]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ])
    t.setStyle(style)
    return t


def score_card(label, score, max_score, color=GREEN, styles=None):
    """Build a mini score card table."""
    percent = int((score / max_score) * 100)
    bar_filled = int(percent / 5)   # out of 20 blocks
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    data = [
        [Paragraph(f"<b>{label}</b>", styles["table_cell"]),
         Paragraph(f"<font color='#{color.hexval()[2:]}' size='13'><b>{score}/{max_score}</b></font>", styles["table_cell"]),
         Paragraph(f"<font color='#00E5FF'>{bar}</font>  {percent}%", styles["code"])],
    ]
    t = Table(data, colWidths=[5.5 * cm, 2.5 * cm, 9.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BG),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def info_box(title, content_lines, color=CYAN, styles=None):
    """Colored callout box."""
    title_para = Paragraph(f"<b>{title}</b>", ParagraphStyle(
        "ib_title", fontSize=10, fontName="Helvetica-Bold",
        textColor=color, spaceBefore=0, spaceAfter=3))
    body_paras = [Paragraph(f"• {l}", styles["bullet"]) for l in content_lines]
    cells = [[title_para]] + [[p] for p in body_paras]
    t = Table(cells, colWidths=[17.2 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BG),
        ("LINEAFTER",     (0, 0), (0, -1),  0, DARK_BG),
        ("LINEBEFORE",    (0, 0), (0, -1),  3, color),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return t


# -------------------------------------------------------------------
# PDF Page template (dark background)
# -------------------------------------------------------------------
def add_page_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)

    # Subtle top gradient bar
    canvas.setFillColor(CYAN)
    canvas.rect(0, A4[1] - 3, A4[0], 3, fill=1, stroke=0)

    # Footer
    canvas.setFillColor(MID_BG)
    canvas.rect(0, 0, A4[0], 1.1 * cm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(0, 1.1 * cm, A4[0], 1.1 * cm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(LIGHT_TEXT)
    canvas.drawString(2 * cm, 0.4 * cm, "UniverBot — AI Chatbot Builder SaaS Platform")
    canvas.drawRightString(A4[0] - 2 * cm, 0.4 * cm, f"Page {doc.page}")
    canvas.restoreState()


# -------------------------------------------------------------------
# Main builder
# -------------------------------------------------------------------
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=1.6 * cm,
        title="UniverBot — PBL Project Review",
        author="UniverBot Team",
    )

    S = build_styles()
    story = []

    page_w = A4[0] - 4 * cm   # usable width

    # ================================================================
    # COVER PAGE
    # ================================================================
    story.append(Spacer(1, 2.5 * cm))
    story.append(Paragraph("UniverBot", S["cover_title"]))
    story.append(Paragraph("AI Chatbot Builder SaaS Platform", S["cover_sub"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(ColoredHR(CYAN, page_w, 2))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("PROJECT-BASED LEARNING (PBL) REVIEW", ParagraphStyle(
        "pbl_label", fontSize=13, fontName="Helvetica-Bold",
        textColor=LIGHT_TEXT, alignment=TA_CENTER, spaceAfter=6)))
    story.append(Spacer(1, 1.5 * cm))

    # Cover info card
    cover_data = [
        ["Project Title",  "UniverBot — AI Chatbot Builder SaaS"],
        ["Review Date",    datetime.datetime.now().strftime("%B %d, %Y")],
        ["Domain",         "Full-Stack SaaS / AI / NLP / Cloud"],
        ["Architecture",   "Monorepo: Next.js Frontend · FastAPI Backend · Embedding Microservice"],
        ["Database",       "Supabase PostgreSQL + pgvector (RAG)"],
        ["Primary AI",     "Cerebras (LLM) · Gemini (fallback) · all-MiniLM-L6-v2 (Embeddings)"],
        ["Deployment",     "Frontend → Vercel  |  Backend → Koyeb  |  Embeddings → Fly.io"],
        ["Status",         "Production-Ready  ✔"],
    ]
    cover_table = Table(
        [[Paragraph(f"<b>{r[0]}</b>", S["label"]),
          Paragraph(r[1], S["table_cell"])] for r in cover_data],
        colWidths=[4 * cm, 13.2 * cm]
    )
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BG),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [MID_BG, HexColor("#0d1424")]),
    ]))
    story.append(cover_table)

    story.append(Spacer(1, 1.5 * cm))

    # Executive score box on cover
    exec_scores = [
        ["Category", "Score", "Max", "Grade"],
        ["Problem Definition & Relevance", "18", "20", "A"],
        ["Technical Architecture",         "23", "25", "A"],
        ["AI / ML Integration",            "17", "20", "A-"],
        ["Code Quality & Security",        "14", "15", "A"],
        ["Deployment & DevOps",            "9",  "10", "A"],
        ["UI/UX & Usability",              "9",  "10", "A"],
        ["TOTAL",                          "90", "100", "A"],
    ]
    grade_colors = [BORDER, None, None, None, None, None, None, GREEN]
    exec_table = Table(
        [[Paragraph(f"<b>{r[0]}</b>" if i == 0 or i == 6 else r[0], S["table_cell"]),
          Paragraph(f"<b>{r[1]}</b>" if i == 6 else r[1], S["table_cell"]),
          Paragraph(r[2], S["table_cell"]),
          Paragraph(f"<b><font color='#22c55e'>{r[3]}</font></b>" if i == 6
                    else f"<font color='#00E5FF'>{r[3]}</font>", S["table_cell"])]
         for i, r in enumerate(exec_scores)],
        colWidths=[9.5 * cm, 2.5 * cm, 2.5 * cm, 2.7 * cm]
    )
    exec_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  CYAN),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  DARK_BG),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("BACKGROUND",     (0, 1), (-1, -2), MID_BG),
        ("BACKGROUND",     (0, -1),(-1, -1), HexColor("#0d1424")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MID_BG, HexColor("#0d1424")]),
        ("GRID",           (0, 0), (-1, -1), 0.4, BORDER),
        ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",     (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(exec_table)

    story.append(PageBreak())

    # ================================================================
    # TABLE OF CONTENTS
    # ================================================================
    story.append(Paragraph("Table of Contents", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Spacer(1, 0.3 * cm))

    toc = [
        ("1.", "Executive Summary"),
        ("2.", "Problem Statement & Project Motivation"),
        ("3.", "System Architecture Overview"),
        ("4.", "Frontend — Next.js Application"),
        ("5.", "Backend — FastAPI Service"),
        ("6.", "AI & Machine Learning Pipeline"),
        ("7.", "Database Design & Schema"),
        ("8.", "Embedding Microservice"),
        ("9.", "Embeddable Chat Widget"),
        ("10.", "Flow Builder System"),
        ("11.", "Security Implementation"),
        ("12.", "Deployment & DevOps"),
        ("13.", "Free-Tier Resource Limits"),
        ("14.", "Strengths & Achievements"),
        ("15.", "Areas for Improvement"),
        ("16.", "Detailed Scoring Rubric"),
        ("17.", "Conclusion & Recommendations"),
    ]
    for num, title in toc:
        story.append(Paragraph(
            f'<font color="#00E5FF"><b>{num}</b></font>  {title}',
            S["toc_entry"]
        ))
    story.append(PageBreak())

    # ================================================================
    # 1. EXECUTIVE SUMMARY
    # ================================================================
    story.append(Paragraph("1. Executive Summary", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "UniverBot is a fully functional, production-ready SaaS platform that enables users to "
        "create, train, and deploy custom AI chatbots powered by their own knowledge bases. "
        "The project demonstrates mastery of modern full-stack development, integrating cutting-edge "
        "AI technologies including Retrieval-Augmented Generation (RAG), multi-provider LLM cascades, "
        "and real-time embedding microservices.",
        S["body"]
    ))
    story.append(Paragraph(
        "Built as a monorepo containing three distinct services — a Next.js 14 frontend, a FastAPI "
        "Python backend, and a standalone sentence-transformer embedding microservice — UniverBot "
        "achieves enterprise-level separation of concerns while remaining deployable on free-tier "
        "cloud infrastructure. The platform supports PDF/DOCX/TXT document ingestion, intelligent "
        "multi-page website crawling with Crawl4AI, a visual no-code flow builder, and pixel-perfect "
        "widget customisation with real-time preview.",
        S["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(info_box("Key Achievements", [
        "End-to-end RAG pipeline: document ingestion -&gt; chunking -&gt; embedding -&gt; vector similarity search -&gt; LLM generation",
        "Three-provider LLM cascade: Cerebras (primary) -&gt; Gemini 1.5-flash (fallback 1) -&gt; Groq LLaMA3 (fallback 2)",
        "Visual drag-and-drop Flow Builder using React Flow with 5 custom node types",
        "Embeddable JavaScript widget requiring only a single &lt;script&gt; tag",
        "Comprehensive free-tier limit enforcement across storage, bots, documents, and API usage",
        "Row-Level Security via Supabase Auth with JWT-based API key authentication",
        "Crawl4AI + Playwright integration for JavaScript-rendered website scraping",
    ], CYAN, S))
    story.append(PageBreak())

    # ================================================================
    # 2. PROBLEM STATEMENT
    # ================================================================
    story.append(Paragraph("2. Problem Statement & Project Motivation", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The rapid rise of conversational AI has created a significant gap: while large enterprises "
        "can afford bespoke AI chatbot solutions, small businesses, developers, and content creators "
        "lack accessible tools to build knowledge-grounded chatbots without deep ML expertise or "
        "expensive infrastructure.",
        S["body"]
    ))
    story.append(Paragraph("<b>Core Problems Addressed:</b>", S["subsection"]))
    problems = [
        ("Knowledge Grounding",
         "Generic LLMs hallucinate and answer from general training data instead of a business's specific content."),
        ("Integration Complexity",
         "Embedding chatbots into existing websites typically requires custom backend infrastructure and weeks of work."),
        ("Cost Barrier",
         "Proprietary chatbot platforms charge high monthly fees, locking out indie developers and small teams."),
        ("No-Code Gap",
         "Technical RAG pipeline setup requires ML expertise unavailable to most small business owners."),
        ("Customisation",
         "Off-the-shelf chatbots cannot match brand colors, fonts, or conversational flow requirements."),
    ]
    prob_rows = [["Problem", "Description"]] + [[p, d] for p, d in problems]
    story.append(dark_table(
        [[Paragraph(f"<b>{r[0]}</b>", S["table_header"] if i == 0 else S["highlight"]),
          Paragraph(r[1], S["table_cell"])]
         for i, r in enumerate(prob_rows)],
        [4.5 * cm, 12.7 * cm]
    ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("<b>Proposed Solution:</b>", S["subsection"]))
    story.append(Paragraph(
        "UniverBot solves each of these problems with a multi-layered SaaS architecture: "
        "RAG grounds every response in uploaded documents or crawled websites; "
        "the embeddable widget reduces integration to one line of HTML; "
        "free-tier cloud deployment makes the platform cost-free to operate at small scale; "
        "the visual flow builder removes ML friction; "
        "and the appearance editor provides full brand customisation.",
        S["body"]
    ))
    story.append(PageBreak())

    # ================================================================
    # 3. SYSTEM ARCHITECTURE
    # ================================================================
    story.append(Paragraph("3. System Architecture Overview", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "UniverBot follows a microservices-inspired monorepo pattern with three independently "
        "deployable services communicating over HTTP. The database layer is fully managed by "
        "Supabase, providing PostgreSQL with the pgvector extension for vector operations.",
        S["body"]
    ))

    story.append(Paragraph("<b>Service Inventory</b>", S["subsection"]))
    svc_data = [
        ["Service", "Technology", "Deployment", "Role"],
        ["Frontend",            "Next.js 14, TypeScript, TailwindCSS", "Vercel",  "SPA dashboard, flow builder, widget code gen"],
        ["Backend API",         "FastAPI (Python 3.12), Pydantic v2",  "Koyeb",   "REST API, auth, RAG orchestration, LLM proxy"],
        ["Embedding Service",   "FastAPI, sentence-transformers",       "Fly.io",  "all-MiniLM-L6-v2 (384-dim) inference endpoint"],
        ["Database",            "Supabase (PostgreSQL + pgvector)",     "Supabase","Auth, vector store, chat history, bot metadata"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(svc_data)],
        [3.5 * cm, 5 * cm, 3 * cm, 5.7 * cm]
    ))

    story.append(Paragraph("<b>Request Flow (Chat)</b>", S["subsection"]))
    flow_steps = [
        ("1", "User sends a message via the embeddable widget (univerbot.js)"),
        ("2", "Widget POSTs to  POST /chat/{bot_id}  with Bearer API key in header"),
        ("3", "FastAPI verifies the API key against Supabase  bots  table"),
        ("4", "Session state is loaded from  chat_sessions  table (for flow continuity)"),
        ("5", "If Flow Builder data exists, FlowExecutor routes through nodes"),
        ("6", "For AI-response nodes: query embedding generated via embedding microservice"),
        ("7", "Vector similarity search executed via  match_documents  RPC (pgvector IVFFlat index)"),
        ("8", "Low-similarity fallback triggers keyword BM25-style search"),
        ("9", "Assembled context + conversation history + system prompt sent to LLM cascade"),
        ("10","Response stored in  chat_messages  table; session state updated; response returned"),
    ]
    flow_data = [["Step", "Description"]] + [[s, d] for s, d in flow_steps]
    story.append(dark_table(
        [[Paragraph(f"<b>{r[0]}</b>", S["table_header"] if i == 0 else S["highlight"]),
          Paragraph(r[1], S["table_cell"])]
         for i, r in enumerate(flow_data)],
        [1.8 * cm, 15.4 * cm]
    ))
    story.append(PageBreak())

    # ================================================================
    # 4. FRONTEND
    # ================================================================
    story.append(Paragraph("4. Frontend — Next.js Application", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The frontend is built with Next.js 14 using the App Router, fully typed with TypeScript, "
        "and styled with TailwindCSS using a custom dark cyberpunk palette (#030617 background, "
        "#00E5FF cyan accent). UI primitives are provided by Radix UI via the ShadCN component library. "
        "State is managed with Zustand and server state is handled with TanStack React Query.",
        S["body"]
    ))

    story.append(Paragraph("<b>Application Routes</b>", S["subsection"]))
    routes = [
        ["/",                           "Landing page with feature highlights and embed code preview"],
        ["/login, /register",           "Supabase Auth authentication flows"],
        ["/auth/callback",              "OAuth redirect handler"],
        ["/dashboard",                  "Overview stats: bots, messages, documents"],
        ["/dashboard/bots",             "Bot listing with status and quick-access links"],
        ["/dashboard/bots/create",      "Bot creation form (name, description, system prompt)"],
        ["/dashboard/bots/[id]",        "Full bot management: tabs for Flow Builder, Knowledge Base, Appearance, Settings"],
        ["/dashboard/settings",         "User profile and account settings"],
    ]
    route_data = [["Route", "Purpose"]] + routes
    story.append(dark_table(
        [[Paragraph(f"<b>{r[0]}</b>", S["table_header"] if i == 0 else S["code"]),
          Paragraph(r[1], S["table_cell"])]
         for i, r in enumerate(route_data)],
        [6 * cm, 11.2 * cm]
    ))

    story.append(Paragraph("<b>Key Frontend Libraries</b>", S["subsection"]))
    libs = [
        ["Library",           "Version",  "Purpose"],
        ["Next.js",           "14.0.4",   "App Router, SSR, file-based routing"],
        ["React Flow",        "11.11.4",  "Visual flow builder canvas with drag-and-drop nodes"],
        ["Supabase JS",       "2.98.0",   "Auth helpers, real-time client, database queries"],
        ["Zustand",           "4.5.7",    "Lightweight global state for auth and bot data"],
        ["TanStack Query",    "5.17.0",   "Server-state caching and async data fetching"],
        ["Radix UI / ShadCN", "multiple", "Accessible headless UI components"],
        ["TailwindCSS",       "3.4.0",    "Utility-first CSS with custom dark theme config"],
        ["Lucide React",      "0.303.0",  "Icon library (300+ icons)"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(libs)],
        [4.5 * cm, 2.5 * cm, 10.2 * cm]
    ))

    story.append(Paragraph("<b>State Management Pattern</b>", S["subsection"]))
    story.append(Paragraph(
        "Two Zustand stores are used: useAuthStore (user profile, loading) and useBotStore "
        "(bot list, selected bot, CRUD operations). Both stores are consumed directly in page "
        "components with selector hooks, avoiding prop drilling. Supabase's real-time subscription "
        "capabilities are available but not yet utilised for live chat updates.",
        S["body"]
    ))
    story.append(PageBreak())

    # ================================================================
    # 5. BACKEND
    # ================================================================
    story.append(Paragraph("5. Backend — FastAPI Service", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The backend is a FastAPI application structured with clear separation between API routes, "
        "service logic, database access, and configuration. It exposes three router groups under "
        "/bot, /chat, and /health, with Pydantic v2 models for full request/response validation.",
        S["body"]
    ))

    story.append(Paragraph("<b>API Endpoints Summary</b>", S["subsection"]))
    endpoints = [
        ["Method", "Endpoint",                        "Auth",      "Description"],
        ["GET",    "/health",                         "None",      "Service health check"],
        ["POST",   "/bot/create",                     "JWT",       "Create a new bot"],
        ["GET",    "/bot/list",                       "JWT",       "List all bots for current user"],
        ["GET",    "/bot/{bot_id}",                   "JWT",       "Get specific bot details"],
        ["PATCH",  "/bot/{bot_id}",                   "JWT",       "Update bot (name, prompt, flow, appearance)"],
        ["DELETE", "/bot/{bot_id}",                   "JWT",       "Delete bot and all associated data"],
        ["POST",   "/bot/{bot_id}/upload",            "JWT",       "Upload PDF/DOCX/TXT for training"],
        ["POST",   "/bot/{bot_id}/scrape",            "JWT",       "Scrape a single URL"],
        ["POST",   "/bot/{bot_id}/crawl",             "JWT",       "Crawl an entire website (sitemap + links)"],
        ["GET",    "/bot/{bot_id}/documents",         "JWT",       "List training documents"],
        ["DELETE", "/bot/{bot_id}/documents/{doc_id}","JWT",       "Delete a document and its chunks"],
        ["POST",   "/bot/{bot_id}/train",             "JWT",       "Re-generate embeddings for all chunks"],
        ["GET",    "/bot/{bot_id}/storage",           "JWT",       "Storage stats and limit usage"],
        ["GET",    "/chat/{bot_id}/info",             "API Key",   "Get bot name and appearance config"],
        ["POST",   "/chat/{bot_id}",                  "API Key",   "Send a chat message, get AI response"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else
                    (S["highlight"] if c in ["POST","GET","PATCH","DELETE"] else S["code"] if j == 1 else S["table_cell"]))
          for j, c in enumerate(row)] for i, row in enumerate(endpoints)],
        [1.8 * cm, 6.5 * cm, 2.2 * cm, 6.7 * cm]
    ))

    story.append(Paragraph("<b>Service Modules</b>", S["subsection"]))
    services = [
        ["Module",               "File",                    "Responsibility"],
        ["Document Processor",   "document_processor.py",   "PDF (pypdf), DOCX (python-docx), TXT/MD extraction; token-aware chunking (tiktoken)"],
        ["Embeddings",           "embeddings.py",            "HTTP client to embedding microservice; chunk storage to Supabase"],
        ["RAG Engine",           "rag.py",                   "pgvector RPC call; cosine similarity fallback; keyword BM25 fallback"],
        ["LLM Provider",         "llm.py",                   "Cerebras → Gemini → Groq cascade; prompt construction; conversation history"],
        ["Flow Executor",        "flow_executor.py",         "Node-by-node flow traversal; session state management; XSS input sanitisation"],
        ["Site Crawler",         "site_crawler.py",          "Sitemap.xml discovery, robots.txt respect, multi-page Crawl4AI+Playwright crawl"],
        ["Web Scraper",          "web_scraper.py",           "Single-URL Crawl4AI scraping with JS rendering fallback"],
        ["Simple Responses",     "simple_responses.py",      "Pattern matching for greetings, farewells, and trivial queries"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(services)],
        [3.5 * cm, 4.5 * cm, 9.2 * cm]
    ))
    story.append(PageBreak())

    # ================================================================
    # 6. AI / ML PIPELINE
    # ================================================================
    story.append(Paragraph("6. AI & Machine Learning Pipeline", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    story.append(Paragraph("<b>6.1 Document Ingestion Pipeline</b>", S["section"]))
    steps_ingest = [
        "File uploaded via /bot/{id}/upload (PDF, DOCX, TXT, MD — max 2 MB, max 5 per bot)",
        "File extension-based MIME detection (more reliable than browser content-type header)",
        "Text extraction: pypdf for PDF, python-docx for DOCX (incl. tables), UTF-8/Latin-1 decode for text",
        "Text cleaned (CRLF normalised, lines stripped)",
        "Token-aware chunking: splits on paragraphs first, then sentences; 500-token chunks with 50-token overlap",
        "Chunks stored in document_chunks table (content + chunk_index + bot_id + document_id)",
        "Embedding microservice called per chunk → 384-dim vector stored in embedding column",
    ]
    for s in steps_ingest:
        story.append(Paragraph(f"→  {s}", S["bullet"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("<b>6.2 RAG Query Pipeline</b>", S["section"]))
    steps_rag = [
        "User query submitted to /chat/{bot_id}",
        "Query passed to embedding microservice → 384-dim query vector",
        "match_documents RPC called (IVFFlat index, cosine distance, top_k=7)",
        "If RPC fails: manual cosine similarity over all chunks in Python (numpy)",
        "Chunks below 0.25 similarity pruned",
        "If best similarity < 0.3: hybrid keyword search (stop-word removal, partial matching, fuzzy scoring)",
        "Top-k results merged from vector + keyword results",
        "Context assembled and injected into LLM prompt",
    ]
    for s in steps_rag:
        story.append(Paragraph(f"→  {s}", S["bullet"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("<b>6.3 LLM Provider Cascade</b>", S["section"]))
    llm_data = [
        ["Priority", "Provider",  "Model",               "Why"],
        ["1 (Primary)",  "Cerebras", "llama-4-scout / llama3-70b",  "Free, fast (low latency via hardware), high quality"],
        ["2 (Fallback)", "Google Gemini", "gemini-1.5-flash",  "1500 RPD free, reliable, multimodal capability"],
        ["3 (Fallback)", "Groq",     "llama3-70b-8192",    "14,400 RPD free, very fast inference"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(llm_data)],
        [3 * cm, 3.5 * cm, 4.5 * cm, 6.2 * cm]
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "The prompt engineering is thorough: it passes system instructions, last-10-message "
        "conversation history, retrieved RAG context, topic continuity tag (for follow-up handling), "
        "and explicit anti-hallucination rules. The LLM is instructed to respond only from the "
        "knowledge base and to produce clean plain-text (no markdown, no HTML).",
        S["body"]
    ))

    story.append(Paragraph("<b>6.4 Embedding Microservice</b>", S["section"]))
    story.append(Paragraph(
        "A separate FastAPI service runs sentence-transformers' all-MiniLM-L6-v2 model, "
        "producing 384-dimensional L2-normalised vectors. The model is loaded once at startup "
        "using @lru_cache and shared across requests. The service exposes /embed (single) and "
        "/embed/batch (up to 100 texts) endpoints. The main backend communicates with it via "
        "HTTPX async client, keeping ML dependencies isolated from the API service.",
        S["body"]
    ))
    story.append(PageBreak())

    # ================================================================
    # 7. DATABASE DESIGN
    # ================================================================
    story.append(Paragraph("7. Database Design & Schema", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The database is a Supabase-managed PostgreSQL instance with the pgvector extension enabled. "
        "Six core tables form the schema, with cascading deletes and Row Level Security policies.",
        S["body"]
    ))

    tables = [
        ["Table",             "Key Columns",                                     "Notes"],
        ["profiles",          "id (FK→auth.users), email, full_name",            "Extends Supabase Auth users"],
        ["bots",              "id, user_id, name, api_key (UNIQUE), flow_data (JSONB), appearance (JSONB)", "api_key indexed for O(1) lookup"],
        ["documents",         "id, bot_id, filename, file_type, file_size, chunk_count", "Metadata only; content in chunks"],
        ["document_chunks",   "id, document_id, bot_id, content, embedding VECTOR(1024), chunk_index", "pgvector IVFFlat index (lists=100)"],
        ["chat_messages",     "id, bot_id, session_id, role (user|assistant), content", "Session-scoped history, limit 10 for context"],
        ["chat_sessions",     "id, session_id, bot_id, state JSONB",             "UNIQUE(session_id, bot_id) for flow state isolation"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else
                    (S["code"] if j == 0 else S["table_cell"]))
          for j, c in enumerate(row)] for i, row in enumerate(tables)],
        [3.5 * cm, 8 * cm, 5.7 * cm]
    ))

    story.append(Paragraph("<b>Indexes & Performance</b>", S["subsection"]))
    indexes = [
        "idx_bots_user_id — B-Tree on bots.user_id (fast user bot listing)",
        "idx_bots_api_key — B-Tree on bots.api_key (O(1) API key auth)",
        "idx_document_chunks_bot_id — B-Tree on document_chunks.bot_id",
        "idx_document_chunks_embedding — IVFFlat on embedding (cosine_ops, lists=100)",
        "idx_chat_messages_session_id — B-Tree on session_id",
        "idx_chat_sessions_session_bot — Composite on (session_id, bot_id) — matches UNIQUE constraint",
    ]
    for ix in indexes:
        story.append(Paragraph(f"• {ix}", S["bullet"]))

    story.append(Paragraph("<b>match_documents RPC</b>", S["subsection"]))
    story.append(Paragraph(
        "A plpgsql function match_documents(query_embedding, match_count, filter_bot_id) "
        "performs bot-scoped vector similarity search entirely in SQL, returning (id, content, similarity) "
        "triples. This avoids transferring raw embedding vectors to the application layer, "
        "greatly reducing network overhead.",
        S["body"]
    ))
    story.append(PageBreak())

    # ================================================================
    # 8. EMBEDDING MICROSERVICE
    # ================================================================
    story.append(Paragraph("8. Embedding Microservice", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The embedding service is a standalone FastAPI application deployed separately from "
        "the main backend. This design choice decouples heavy ML model loading (sentence-transformers "
        "requires ~100 MB of model weights) from the API logic, enabling independent scaling and "
        "technology replacement.",
        S["body"]
    ))

    emb_data = [
        ["Property",        "Value"],
        ["Model",           "all-MiniLM-L6-v2 (sentence-transformers)"],
        ["Output Dimension","384"],
        ["Inference Time",  "~25 ms per text (CPU)"],
        ["Max Batch Size",  "100 texts per /embed/batch call"],
        ["Model Loading",   "Eager at startup via @lru_cache (single instance)"],
        ["Endpoints",       "GET /health  |  POST /embed  |  POST /embed/batch"],
        ["Deployment",      "Fly.io / Koyeb (Dockerfile + Procfile)"],
        ["CORS",            "Allow all origins (internal microservice, no auth needed)"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{r[0]}</b>", S["table_header"] if i == 0 else S["highlight"]),
          Paragraph(r[1], S["table_cell"])]
         for i, r in enumerate(emb_data)],
        [4.5 * cm, 12.7 * cm]
    ))
    story.append(PageBreak())

    # ================================================================
    # 9. EMBEDDABLE WIDGET
    # ================================================================
    story.append(Paragraph("9. Embeddable Chat Widget", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "univerbot.js is a self-contained vanilla JavaScript IIFE that renders a fully functional "
        "chat interface on any third-party website. It requires zero dependencies — no React, no jQuery.",
        S["body"]
    ))
    story.append(Paragraph("<b>Integration</b>", S["subsection"]))
    story.append(Paragraph(
        '&lt;script src="https://app.univerbot.ai/univerbot.js" data-bot-id="YOUR_BOT_ID" data-api-key="YOUR_API_KEY"&gt;&lt;/script&gt;',
        S["code"]
    ))
    story.append(Paragraph("<b>Widget Features</b>", S["subsection"]))
    widget_features = [
        "Fetches bot appearance config from /chat/{bot_id}/info on load",
        "Dynamically injects CSS using computed appearance values (colors, button radius, position)",
        "Session ID persisted in localStorage per bot (unique conversation isolation)",
        "Sends empty message on first open to trigger welcome message / flow start",
        "Skeleton loading animation while awaiting response",
        "Configurable position (bottom-right / bottom-left)",
        "Custom widget icon URL, avatar URL/initials, and loading GIF support",
        "Responsive: 380×520 px, mobile-friendly",
        "XSS-safe: messages rendered as text nodes, no innerHTML injection from API responses",
    ]
    for f in widget_features:
        story.append(Paragraph(f"• {f}", S["bullet"]))
    story.append(PageBreak())

    # ================================================================
    # 10. FLOW BUILDER
    # ================================================================
    story.append(Paragraph("10. Flow Builder System", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "The Flow Builder is a visual, no-code tool built with React Flow (reactflow library). "
        "It allows users to design conversational flows by dragging and connecting nodes on an "
        "infinite canvas. The flow JSON is stored in bots.flow_data (JSONB) and executed server-side "
        "by FlowExecutor.",
        S["body"]
    ))

    story.append(Paragraph("<b>Node Types</b>", S["subsection"]))
    nodes = [
        ["Node Type",  "Frontend Component",  "Backend Behaviour"],
        ["start",      "StartNode.tsx",        "Entry point; triggers welcome message sequence; exactly one required"],
        ["message",    "MessageNode.tsx",      "Displays static text; supports multi-line; used for welcome messages"],
        ["chatInput",  "ChatInputNode.tsx",    "Captures user input; stores in variableName (default: user_message)"],
        ["aiResponse", "AIResponseNode.tsx",   "Generates LLM response; optionally uses RAG (useKnowledgeBase flag); custom system prompt override"],
        ["condition",  "ConditionNode.tsx",    "Keyword-match routing; true/false handles for branching; case-insensitive"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else
                    (S["code"] if j < 2 else S["table_cell"]))
          for j, c in enumerate(row)] for i, row in enumerate(nodes)],
        [2.5 * cm, 4 * cm, 10.7 * cm]
    ))

    story.append(Paragraph("<b>Default Flow Template</b>", S["subsection"]))
    story.append(Paragraph(
        "New bots start with a pre-built default flow: Start → Message (Welcome) → ChatInput → "
        "AIResponse (with RAG enabled) → back to ChatInput (loop). "
        "This default is production-ready and requires no configuration beyond the system prompt.",
        S["body"]
    ))

    story.append(Paragraph("<b>Flow Execution (Server-Side)</b>", S["subsection"]))
    story.append(Paragraph(
        "FlowExecutor.execute_flow() traverses nodes in order, persisting current_node_id in "
        "chat_sessions.state. Session state validation detects stale node IDs from edited flows "
        "and resets the session transparently. Input sanitisation strips control characters and "
        "blocks XSS patterns before any node processing.",
        S["body"]
    ))
    story.append(PageBreak())

    # ================================================================
    # 11. SECURITY
    # ================================================================
    story.append(Paragraph("11. Security Implementation", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    security_items = [
        ("Authentication",
         "JWT-based auth via Supabase Auth. Backend verifies tokens with supabase.auth.get_user(token). "
         "API key auth uses Bearer scheme with database lookup against indexed api_key column."),
        ("Authorisation",
         "All bot operations verify ownership (verify_bot_ownership) before any data access or mutation. "
         "Supabase Row Level Security policies restrict database access by user_id."),
        ("Input Validation",
         "All request bodies validated by Pydantic v2 models with field constraints (min_length, max_length). "
         "File uploads validated by extension and size (max 2 MB). Text inputs capped at 1000 chars."),
        ("Injection Prevention",
         "FlowExecutor checks for &lt;script, javascript:, onerror=, onclick=, eval(, exec( patterns. "
         "SQL injection not possible — all DB access via Supabase client SDK (parameterised)."),
        ("File Security",
         "Only .pdf, .txt, .md, .docx extensions accepted. MIME type checked via file extension, not browser header. "
         "No files stored on disk — processed in-memory as bytes."),
        ("Rate Limiting / Abuse",
         "Free-tier hard limits enforced in code: 2 bots, 5 docs, 200 chunks, 500 messages/month. "
         "Chunk limit checked before processing to prevent resource exhaustion."),
        ("CORS",
         "Origins configurable via environment variable. Defaults to * in dev; production restricts to frontend domain."),
        ("Secrets Management",
         "All API keys, DB credentials, and JWT secrets loaded from environment variables / .env file. "
         "Pydantic-settings used for type-safe configuration loading."),
    ]
    for title, desc in security_items:
        story.append(KeepTogether([
            Paragraph(f"<b>{title}</b>", S["subsection"]),
            Paragraph(desc, S["body"]),
        ]))
    story.append(PageBreak())

    # ================================================================
    # 12. DEPLOYMENT & DEVOPS
    # ================================================================
    story.append(Paragraph("12. Deployment & DevOps", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    story.append(Paragraph("<b>Deployment Targets</b>", S["subsection"]))
    deploy_data = [
        ["Service",           "Platform",  "Config Files",                         "Notes"],
        ["Frontend",          "Vercel",    "vercel.json, next.config.js",           "Zero-config Next.js deployment, auto HTTPS"],
        ["Backend API",       "Koyeb",     "koyeb.yaml, Procfile, runtime.txt",     "Python 3.12, uvicorn, auto-restart on crash"],
        ["Embedding Service", "Fly.io",    "fly.toml, Dockerfile, Procfile",        "Containerised, persistent model caching"],
        ["Database",          "Supabase",  "schema.sql, migrate_to_384_dimensions.sql", "Managed Postgres + Auth + Storage"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(deploy_data)],
        [3.5 * cm, 2.8 * cm, 5.5 * cm, 5.4 * cm]
    ))

    story.append(Paragraph("<b>Environment Configuration</b>", S["subsection"]))
    env_vars = [
        ["Variable",                  "Service",    "Purpose"],
        ["SUPABASE_URL",              "Backend",    "Supabase project URL"],
        ["SUPABASE_KEY",              "Backend",    "Supabase anon key (public)"],
        ["SUPABASE_SERVICE_ROLE_KEY", "Backend",    "Service role key (admin DB access)"],
        ["JWT_SECRET",                "Backend",    "Supabase JWT secret for token verification"],
        ["GEMINI_API_KEY",            "Backend",    "Google Gemini API key"],
        ["CEREBRAS_API_KEY",          "Backend",    "Cerebras cloud API key"],
        ["GROQ_API_KEY",              "Backend",    "Groq API key (optional fallback)"],
        ["EMBEDDING_SERVICE_URL",     "Backend",    "URL of embedding microservice"],
        ["NEXT_PUBLIC_SUPABASE_URL",  "Frontend",   "Supabase URL (client-side)"],
        ["NEXT_PUBLIC_SUPABASE_ANON_KEY", "Frontend","Supabase anon key (client-side)"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["code"] if j == 0 else S["table_cell"])
          for j, c in enumerate(row)] for i, row in enumerate(env_vars)],
        [5.5 * cm, 2.8 * cm, 8.9 * cm]
    ))
    story.append(PageBreak())

    # ================================================================
    # 13. FREE TIER LIMITS
    # ================================================================
    story.append(Paragraph("13. Free-Tier Resource Limits", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "UniverBot is engineered to operate entirely within free-tier constraints across all "
        "external services. Limits are defined centrally in backend/app/limits.py and enforced "
        "at the API layer before any resource-intensive operation.",
        S["body"]
    ))

    limits_data = [
        ["Resource",                "Limit",     "Rationale"],
        ["Bots per user",           "2",          "Supabase 500 MB DB constraint"],
        ["Documents per bot",       "5",          "Max 5 PDFs/DOCX/TXT per bot"],
        ["Max document size",       "2 MB",       "In-memory processing safety"],
        ["Chunks per bot",          "200",        "~6 KB/chunk → 1.2 MB vector storage"],
        ["Storage per bot",         "25 MB",      "Text + vector combined"],
        ["Websites per bot",        "3",          "Crawled/scraped site limit"],
        ["Pages per website crawl", "10",         "Crawl4AI session limit"],
        ["Messages per bot/month",  "500",        "Gemini 1500 RPD limit with headroom"],
        ["File upload size",        "2 MB",       "Memory safety for serverless platform"],
        ["Total users (platform)",  "50",         "500 MB Supabase + API rate limits"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{c}</b>", S["table_header"] if i == 0 else S["table_cell"])
          for c in row] for i, row in enumerate(limits_data)],
        [5.5 * cm, 2.5 * cm, 9.2 * cm]
    ))
    story.append(PageBreak())

    # ================================================================
    # 14. STRENGTHS
    # ================================================================
    story.append(Paragraph("14. Strengths & Achievements", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    strengths = [
        ("Complete Full-Stack Delivery",
         "The project delivers a working SaaS product from landing page to embeddable widget, "
         "with authentication, database persistence, and cloud deployment — not a prototype."),
        ("Production-Grade RAG Pipeline",
         "The combination of pgvector vector search, cosine similarity fallback, and keyword search "
         "ensures robust retrieval even for short or ambiguous queries."),
        ("Intelligent LLM Cascade",
         "Automatic fallback across three LLM providers (Cerebras → Gemini → Groq) ensures "
         "near-100% uptime even when individual provider APIs are down or rate-limited."),
        ("Visual Flow Builder",
         "The React Flow based drag-and-drop builder with 5 custom node types enables non-technical "
         "users to design complex conditional conversation paths without any coding."),
        ("Microservice Embedding Architecture",
         "Separating embedding inference into its own service allows independent scaling, "
         "technology upgrades (e.g., switching models), and smaller memory footprint on the main API."),
        ("Rich Widget Customisation",
         "The appearance system with 15+ properties (colors, avatar, loading style, button shape, "
         "position) enables per-bot brand matching without any widget code changes."),
        ("Security Depth",
         "Multi-layer security: JWT + API key auth, ownership verification on every mutation, "
         "Pydantic validation, input sanitisation, XSS pattern detection, file type whitelisting."),
        ("Thorough Cost Engineering",
         "Every external service budget is documented with precise RPM/RPD/storage numbers, and "
         "limits.py enforces them in code — preventing surprise bill overruns."),
    ]
    for title, desc in strengths:
        story.append(KeepTogether([
            info_box(f"✓  {title}", [desc], GREEN, S),
            Spacer(1, 0.2 * cm),
        ]))
    story.append(PageBreak())

    # ================================================================
    # 15. AREAS FOR IMPROVEMENT
    # ================================================================
    story.append(Paragraph("15. Areas for Improvement", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    improvements = [
        ("Test Coverage",
         "No automated unit or integration tests were found in the frontend or backend codebases. "
         "Adding pytest tests for service modules (especially RAG, document_processor, flow_executor) "
         "and Jest/React Testing Library tests for UI components is the highest-priority gap."),
        ("Streaming LLM Responses",
         "Chat responses are returned as a single JSON object. Streaming (Server-Sent Events) would "
         "dramatically improve perceived latency for longer LLM outputs."),
        ("Embedding Dimension Mismatch",
         "The schema.sql defines VECTOR(1024) while the embedding microservice produces 384-dimensional "
         "vectors. The migration file migrate_to_384_dimensions.sql exists but having a mismatch in the "
         "canon schema is a maintenance risk."),
        ("Session Security",
         "Session IDs are generated client-side in JavaScript using Math.random(), which is not "
         "cryptographically secure. Server-side session generation or signed tokens would be safer."),
        ("Real-Time Updates",
         "The dashboard stats (messages, documents) are fetched on mount only. Supabase real-time "
         "subscriptions could enable live stat updates without manual refresh."),
        ("Error Handling UX",
         "Backend errors surfaced to the client are raw exception message strings. A structured "
         "error response schema with user-friendly messages would improve UX."),
        ("Logging & Observability",
         "Extensive print() debugging statements remain in production code paths (auth.py, chat.py, "
         "flow_executor.py). These should be replaced with structured logging (Python logging module) "
         "and integrated with a monitoring platform (e.g., Sentry, Logflare)."),
        ("CORS Security",
         "cors_origins defaults to '*' in production configuration. This should be locked down to "
         "the specific frontend domain in the production .env file."),
    ]
    for title, desc in improvements:
        story.append(KeepTogether([
            info_box(f"△  {title}", [desc], ORANGE, S),
            Spacer(1, 0.2 * cm),
        ]))
    story.append(PageBreak())

    # ================================================================
    # 16. SCORING RUBRIC
    # ================================================================
    story.append(Paragraph("16. Detailed Scoring Rubric", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))

    rubric = [
        # (Category, Max, Score, Criteria, Comments)
        ("Problem Definition & Relevance", 20, 18,
         "Clear real-world problem, target audience, unique value prop",
         "Problem is well-defined (5 distinct pain points) with a complete solution mapping. "
         "-2: Limited formal market research or competitive analysis documented."),
        ("Technical Architecture", 25, 23,
         "System design, separation of concerns, scalability, tech choices",
         "Excellent microservices separation, appropriate tech stack, well-documented APIs. "
         "-2: IVFFlat index lists=100 may be over-indexed for < 200 chunks; vector dim mismatch in schema."),
        ("AI / ML Integration", 20, 17,
         "RAG effectiveness, embedding quality, LLM usage, prompt engineering",
         "Strong RAG with vector+keyword hybrid, sophisticated prompt with 7 query-type handlers, "
         "3-provider cascade. -3: No evaluation metrics, no fine-tuning, Math.random session IDs risk."),
        ("Code Quality & Security", 15, 14,
         "Readability, modularity, security, validation, error handling",
         "Well-structured modules, Pydantic validation, XSS checks, ownership guards. "
         "-1: print() debugging in prod paths; no test suite."),
        ("Deployment & DevOps", 10, 9,
         "CI/CD, environment config, cloud deployment, reproducibility",
         "Three independent cloud deployments with all config files present. "
         "-1: No CI/CD pipeline (GitHub Actions); no Docker for backend."),
        ("UI/UX & Usability", 10, 9,
         "Design quality, responsiveness, user flows, accessibility",
         "Polished dark design, consistent brand, smooth animations, collapsible sidebar. "
         "-1: No keyboard accessibility audit; no mobile flow builder support."),
    ]

    totals = (100, sum(r[2] for r in rubric))

    for cat, max_s, score, criteria, comment in rubric:
        story.append(Paragraph(f"<b>{cat}</b>", S["subsection"]))
        story.append(score_card(cat, score, max_s, GREEN if score >= max_s * 0.9 else (YELLOW if score >= max_s * 0.75 else RED), S))
        story.append(Paragraph(f"<i>Criteria: {criteria}</i>", S["caption"]))
        story.append(Paragraph(comment, S["body"]))
        story.append(Spacer(1, 0.25 * cm))

    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        f"<b>FINAL SCORE:  {totals[1]} / {totals[0]}  (Grade: A)</b>",
        ParagraphStyle("final_score", fontSize=16, fontName="Helvetica-Bold",
                       textColor=GREEN, alignment=TA_CENTER, spaceBefore=8, spaceAfter=8)
    ))
    story.append(PageBreak())

    # ================================================================
    # 17. CONCLUSION
    # ================================================================
    story.append(Paragraph("17. Conclusion & Recommendations", S["chapter"]))
    story.append(ColoredHR(CYAN, page_w))
    story.append(Paragraph(
        "UniverBot is an impressive, production-quality project that successfully integrates "
        "modern full-stack engineering with practical AI/ML techniques. The project demonstrates "
        "a deep understanding of SaaS architecture patterns, RAG systems, LLM orchestration, "
        "and cloud deployment — all achieved within zero-cost free-tier infrastructure.",
        S["body"]
    ))
    story.append(Paragraph(
        "The visual flow builder, embeddable widget system, and multi-provider LLM cascade "
        "are particularly standout features that go well beyond typical PBL project scope. "
        "The attention to cost engineering and free-tier limit management shows real-world "
        "product thinking.",
        S["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(info_box("Top 5 Recommendations (Priority Order)", [
        "Add automated tests: pytest for backend services, Jest for React components. Target 60%+ coverage.",
        "Fix embedding dimension: Align schema.sql VECTOR dimension to 384 to match all-MiniLM-L6-v2.",
        "Implement SSE streaming: Add streaming LLM responses using FastAPI StreamingResponse for better UX.",
        "Replace print() with structured logging: Use Python logging module and integrate Sentry for error monitoring.",
        "Lock CORS in production: Set cors_origins to the specific Vercel frontend URL in production environment.",
    ], CYAN, S))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "With the improvements listed above — especially test coverage and the embedding dimension fix — "
        "this project would be a strong candidate for a 95+/100 score and is well-positioned as a "
        "portfolio piece or early-stage startup product.",
        S["body"]
    ))

    story.append(Spacer(1, 1.5 * cm))
    story.append(ColoredHR(CYAN, page_w, 1))
    story.append(Paragraph(
        f"Report generated on {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}  |  "
        "UniverBot PBL Review  |  Confidential",
        S["caption"]
    ))

    # ================================================================
    # BUILD
    # ================================================================
    doc.build(story, onFirstPage=add_page_background, onLaterPages=add_page_background)
    print(f"✅ PDF generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
