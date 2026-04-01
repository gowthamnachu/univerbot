"""
UniverBot — Project Overview PDF
"What is UniverBot and How It Works"
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import datetime

# ── Brand Colors ──────────────────────────────────────────────────
CYAN      = HexColor("#00E5FF")
DARK_BG   = HexColor("#030617")
MID_BG    = HexColor("#0a0f1a")
CARD_BG   = HexColor("#0d1424")
BORDER    = HexColor("#1e293b")
LIGHT     = HexColor("#94a3b8")
WHITE     = HexColor("#ffffff")
GREEN     = HexColor("#22c55e")
PURPLE    = HexColor("#a855f7")
ORANGE    = HexColor("#f97316")
YELLOW    = HexColor("#eab308")
BLUE      = HexColor("#3b82f6")

OUTPUT    = r"c:\Users\gowth\Desktop\univerbot\UniverBot_Project_Overview.pdf"
PAGE_W    = A4[0] - 4 * cm


# ── Custom Flowables ──────────────────────────────────────────────
class DarkHR(Flowable):
    def __init__(self, color=CYAN, thickness=1.5, space_after=6):
        Flowable.__init__(self)
        self.color = color
        self.thickness = thickness
        self.space_after = space_after
        self.height = thickness + space_after

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.thickness / 2, PAGE_W, self.thickness / 2)


class StepBadge(Flowable):
    """Numbered circle badge for steps."""
    def __init__(self, number, color=CYAN):
        Flowable.__init__(self)
        self.number = str(number)
        self.color = color
        self.width = 28
        self.height = 28

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.circle(14, 14, 14, fill=1, stroke=0)
        c.setFillColor(DARK_BG)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(14, 9, self.number)


# ── Background ────────────────────────────────────────────────────
def page_bg(canvas, doc):
    canvas.saveState()
    # Full dark background
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Top cyan bar
    canvas.setFillColor(CYAN)
    canvas.rect(0, A4[1] - 3, A4[0], 3, fill=1, stroke=0)
    # Footer bar
    canvas.setFillColor(MID_BG)
    canvas.rect(0, 0, A4[0], 1.1 * cm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(0, 1.1 * cm, A4[0], 1.1 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(LIGHT)
    canvas.drawString(2 * cm, 0.38 * cm, "UniverBot — AI Chatbot Builder Platform")
    canvas.drawRightString(A4[0] - 2 * cm, 0.38 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────────
def styles():
    return {
        "h1": ParagraphStyle("h1", fontSize=32, fontName="Helvetica-Bold",
                             textColor=CYAN, alignment=TA_CENTER,
                             spaceBefore=0, spaceAfter=6, leading=38),
        "h1_sub": ParagraphStyle("h1_sub", fontSize=14, fontName="Helvetica",
                                 textColor=LIGHT, alignment=TA_CENTER,
                                 spaceBefore=0, spaceAfter=4),
        "section": ParagraphStyle("section", fontSize=18, fontName="Helvetica-Bold",
                                  textColor=CYAN, spaceBefore=16, spaceAfter=4),
        "step_title": ParagraphStyle("step_title", fontSize=13, fontName="Helvetica-Bold",
                                     textColor=WHITE, spaceBefore=0, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=10.5, fontName="Helvetica",
                               textColor=LIGHT, spaceBefore=0, spaceAfter=6,
                               alignment=TA_JUSTIFY, leading=17),
        "bullet": ParagraphStyle("bullet", fontSize=10, fontName="Helvetica",
                                 textColor=LIGHT, leftIndent=14,
                                 spaceBefore=2, spaceAfter=2, leading=15),
        "code": ParagraphStyle("code", fontSize=9, fontName="Courier",
                               textColor=GREEN, backColor=MID_BG,
                               leftIndent=10, rightIndent=10,
                               spaceBefore=4, spaceAfter=4, leading=14,
                               borderPadding=(6, 8, 6, 8)),
        "flow_label": ParagraphStyle("flow_label", fontSize=10, fontName="Helvetica-Bold",
                                     textColor=WHITE, alignment=TA_CENTER),
        "flow_arrow": ParagraphStyle("flow_arrow", fontSize=14, fontName="Helvetica-Bold",
                                     textColor=CYAN, alignment=TA_CENTER),
        "caption": ParagraphStyle("caption", fontSize=9, fontName="Helvetica-Oblique",
                                  textColor=LIGHT, alignment=TA_CENTER, spaceAfter=6),
        "label": ParagraphStyle("label", fontSize=9, fontName="Helvetica-Bold",
                                textColor=CYAN),
        "cell": ParagraphStyle("cell", fontSize=9.5, fontName="Helvetica",
                               textColor=LIGHT, leading=14),
        "highlight": ParagraphStyle("highlight", fontSize=11, fontName="Helvetica-Bold",
                                    textColor=WHITE, alignment=TA_CENTER,
                                    spaceBefore=4, spaceAfter=4),
        "footer_note": ParagraphStyle("footer_note", fontSize=9,
                                      fontName="Helvetica-Oblique",
                                      textColor=LIGHT, alignment=TA_CENTER),
    }


# ── Helpers ───────────────────────────────────────────────────────
def card(content_rows, col_widths, left_accent=None):
    """Dark card table, optional left color accent."""
    t = Table(content_rows, colWidths=col_widths)
    s = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BG),
        ("GRID",          (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ])
    if left_accent:
        s.add("LINEBEFORE", (0, 0), (0, -1), 3, left_accent)
    t.setStyle(s)
    return t


def step_card(S, number, title, bullets, color=CYAN):
    """One step card: colored number + title + bullet list."""
    title_p  = Paragraph(f"<b>{title}</b>", S["step_title"])
    bullet_p = [Paragraph(f"<font color='#00E5FF'>►</font>  {b}", S["bullet"])
                for b in bullets]
    content  = [[title_p]] + [[p] for p in bullet_p]
    inner    = Table(content, colWidths=[13.8 * cm])
    inner.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    badge_table = Table(
        [[StepBadge(number, color), inner]],
        colWidths=[1.1 * cm, 14.1 * cm]
    )
    badge_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BG),
        ("LINEBEFORE",    (0, 0), (0, -1),  3, color),
        ("GRID",          (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return badge_table


def flow_diagram(S):
    """Visual flow arrow diagram."""
    steps = [
        ("Your Content\n(PDFs / Website)", CYAN),
        ("UniverBot\nTrains It", BLUE),
        ("Visitor Asks\na Question", PURPLE),
        ("System Finds\nRelevant Content", ORANGE),
        ("AI Answers Using\nOnly Your Content", GREEN),
        ("Response in\nYour Widget", YELLOW),
    ]

    cells = []
    header_row = []
    for label, color in steps:
        p = Paragraph(
            f"<font color='#{color.hexval()[2:]}'><b>{label}</b></font>",
            S["flow_label"]
        )
        header_row.append(p)
    cells.append(header_row)

    arrow_row = []
    for i, (_, color) in enumerate(steps):
        if i < len(steps) - 1:
            arrow_row.append(Paragraph(
                f"<font color='#{color.hexval()[2:]}'>&#8594;</font>",
                S["flow_arrow"]
            ))
        else:
            arrow_row.append(Paragraph("", S["flow_arrow"]))

    # Build interleaved label + arrow layout
    col_w = PAGE_W / len(steps)
    label_widths = [col_w] * len(steps)

    t = Table(cells, colWidths=label_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
        ("GRID",          (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ── Main Builder ──────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=1.6 * cm,
        title="UniverBot — Project Overview",
        author="UniverBot"
    )
    S = styles()
    story = []

    # ── COVER ────────────────────────────────────────────────────
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("UniverBot", S["h1"]))
    story.append(Paragraph("AI Chatbot Builder Platform", S["h1_sub"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(DarkHR(CYAN, 2))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("PROJECT OVERVIEW — What It Is &amp; How It Works",
                            ParagraphStyle("cov", fontSize=12, fontName="Helvetica-Bold",
                                           textColor=LIGHT, alignment=TA_CENTER)))
    story.append(Spacer(1, 1.2 * cm))

    # One-liner definition card
    story.append(card(
        [[Paragraph(
            "<font color='#00E5FF'><b>UniverBot</b></font>  is a SaaS platform where anyone can build "
            "their own AI chatbot trained on their own content — PDFs, documents, websites — "
            "and embed that chatbot on any website with a <b>single line of code</b>.",
            S["body"]
        )]],
        [PAGE_W], left_accent=CYAN
    ))

    story.append(Spacer(1, 0.5 * cm))

    # Key idea comparison table
    story.append(Paragraph("<b>The Core Idea</b>", S["step_title"]))
    story.append(Spacer(1, 0.2 * cm))
    compare_data = [
        [Paragraph("<b>Generic ChatGPT</b>", ParagraphStyle("ch", fontSize=10,
            fontName="Helvetica-Bold", textColor=ORANGE, alignment=TA_CENTER)),
         Paragraph("<b>UniverBot</b>", ParagraphStyle("ub", fontSize=10,
            fontName="Helvetica-Bold", textColor=CYAN, alignment=TA_CENTER))],
        [Paragraph("Knows everything in the world", S["cell"]),
         Paragraph("Knows only YOUR content", S["cell"])],
        [Paragraph("Cannot use your documents", S["cell"]),
         Paragraph("Trained on your PDFs, websites, files", S["cell"])],
        [Paragraph("Needs complex custom backend", S["cell"]),
         Paragraph("Embed with one &lt;script&gt; tag", S["cell"])],
        [Paragraph("Answers from general training data", S["cell"]),
         Paragraph("Answers only from your knowledge base", S["cell"])],
        [Paragraph("No brand customisation", S["cell"]),
         Paragraph("Full color, avatar, layout control", S["cell"])],
    ]
    compare_t = Table(compare_data, colWidths=[PAGE_W / 2, PAGE_W / 2])
    compare_t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (0, 0),   HexColor("#1a0f06")),
        ("BACKGROUND",     (1, 0), (1, 0),   HexColor("#061a10")),
        ("BACKGROUND",     (0, 1), (-1, -1), MID_BG),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MID_BG, CARD_BG]),
        ("GRID",           (0, 0), (-1, -1), 0.4, BORDER),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",     (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 8),
        ("LEFTPADDING",    (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 12),
        ("LINEAFTER",      (0, 0), (0, -1),  1, BORDER),
    ]))
    story.append(compare_t)

    story.append(PageBreak())

    # ── HOW IT WORKS ─────────────────────────────────────────────
    story.append(Paragraph("How It Works", S["section"]))
    story.append(DarkHR(CYAN))
    story.append(Spacer(1, 0.2 * cm))

    # Step 1
    story.append(step_card(S, 1, "You Create a Bot", [
        "Sign up and go to your Dashboard",
        "Click 'Create New Bot' — give it a name",
        "Write a personality:  'You are a customer support agent for XYZ company'",
        "Choose colors, avatar, button style to match your brand",
    ], CYAN))
    story.append(Spacer(1, 0.3 * cm))

    # Step 2
    story.append(step_card(S, 2, "You Train It With Your Content", [
        "Upload PDF, DOCX, or TXT files — product manuals, FAQs, policies",
        "Paste a website URL — UniverBot crawls all pages automatically (up to 10 pages)",
        "Works even on JavaScript-rendered websites (Playwright + Crawl4AI)",
        "Behind the scenes: content is split into ~500-token chunks, each chunk is "
        "converted into a 384-number mathematical fingerprint (embedding vector), "
        "and stored in a searchable database",
    ], BLUE))
    story.append(Spacer(1, 0.3 * cm))

    # Step 3
    story.append(step_card(S, 3, "You Design the Conversation Flow", [
        "Use the drag-and-drop Flow Builder — no coding required",
        "Connect nodes:  Start  →  Welcome Message  →  Chat Input  →  AI Response  → (loops back)",
        "Add Condition nodes to branch: if user says 'pricing' → pricing reply, else → AI answer",
        "Default template works immediately — just set your system prompt",
    ], PURPLE))
    story.append(Spacer(1, 0.3 * cm))

    # Step 4
    story.append(step_card(S, 4, "You Embed It on Any Website", [
        "UniverBot gives you one line of HTML code",
        "Paste it into any website — the chat widget appears instantly",
        "No backend or server setup required on your side",
    ], ORANGE))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "&lt;script src=\"univerbot.js\"  data-bot-id=\"YOUR_BOT_ID\"  "
        "data-api-key=\"YOUR_API_KEY\"&gt;&lt;/script&gt;",
        S["code"]
    ))

    story.append(Spacer(1, 0.15 * cm))

    # Step 5
    story.append(step_card(S, 5, "Visitor Chats — The AI Answers From Your Content", [
        "Visitor types a question in the chat widget on your site",
        "The question is converted into a vector and matched against your uploaded content",
        "The most relevant chunks from your documents are retrieved",
        "Those chunks + conversation history are sent to the AI (Cerebras → Gemini → Groq fallback)",
        "The AI generates an answer using only your content — no hallucination, no off-topic replies",
        "Response appears in the chat widget instantly",
    ], GREEN))

    story.append(Spacer(1, 0.4 * cm))

    # ── BIG PICTURE FLOW ─────────────────────────────────────────
    story.append(Paragraph("The Big Picture", S["section"]))
    story.append(DarkHR(CYAN))
    story.append(Spacer(1, 0.3 * cm))
    story.append(flow_diagram(S))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Each arrow represents an automated step — the user only touches Step 1 (create), "
        "Step 2 (train), and Step 4 (embed). Everything else is fully automated.",
        S["caption"]
    ))

    story.append(Spacer(1, 0.4 * cm))

    # ── SUMMARY BOX ──────────────────────────────────────────────
    story.append(card(
        [[Paragraph(
            "<font color='#00E5FF'><b>In Short:</b></font>  UniverBot turns any document or website "
            "into a smart, answerable knowledge base — wrapped in a beautiful, fully customisable "
            "chat widget that embeds anywhere in seconds.",
            S["body"]
        )]],
        [PAGE_W], left_accent=GREEN
    ))

    story.append(Spacer(1, 0.8 * cm))

    # ── TECH STACK QUICK VIEW ────────────────────────────────────
    story.append(Paragraph("Tech Stack at a Glance", S["section"]))
    story.append(DarkHR(CYAN))
    story.append(Spacer(1, 0.2 * cm))

    tech_data = [
        [Paragraph("<b>Layer</b>",       S["label"]),
         Paragraph("<b>Technology</b>",  S["label"]),
         Paragraph("<b>Purpose</b>",     S["label"])],
        [Paragraph("Frontend",    S["cell"]),
         Paragraph("Next.js 14, React, TailwindCSS, React Flow", S["cell"]),
         Paragraph("Dashboard, Flow Builder, Appearance Editor", S["cell"])],
        [Paragraph("Backend",     S["cell"]),
         Paragraph("FastAPI (Python), Pydantic v2", S["cell"]),
         Paragraph("REST API, auth, RAG orchestration, LLM routing", S["cell"])],
        [Paragraph("AI / LLM",    S["cell"]),
         Paragraph("Cerebras → Gemini → Groq (cascade)", S["cell"]),
         Paragraph("Answer generation with fallback for 100% uptime", S["cell"])],
        [Paragraph("Embeddings",  S["cell"]),
         Paragraph("all-MiniLM-L6-v2 (sentence-transformers)", S["cell"]),
         Paragraph("384-dim semantic vectors for document search", S["cell"])],
        [Paragraph("Database",    S["cell"]),
         Paragraph("Supabase PostgreSQL + pgvector", S["cell"]),
         Paragraph("Auth, vector store, chat history, bot metadata", S["cell"])],
        [Paragraph("Widget",      S["cell"]),
         Paragraph("Vanilla JavaScript (zero dependencies)", S["cell"]),
         Paragraph("Embeddable chat UI — one script tag", S["cell"])],
        [Paragraph("Deployment",  S["cell"]),
         Paragraph("Vercel · Koyeb · Fly.io · Supabase", S["cell"]),
         Paragraph("All free-tier — zero infrastructure cost", S["cell"])],
    ]
    tech_t = Table(tech_data, colWidths=[3 * cm, 6.5 * cm, 7.7 * cm])
    tech_t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  CYAN),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  DARK_BG),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MID_BG, CARD_BG]),
        ("GRID",           (0, 0), (-1, -1), 0.4, BORDER),
        ("TOPPADDING",     (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 8),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tech_t)

    story.append(Spacer(1, 0.8 * cm))
    story.append(DarkHR(CYAN, 1))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}  |  UniverBot Project Overview",
        S["footer_note"]
    ))

    doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
    print(f"✅ PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build()
