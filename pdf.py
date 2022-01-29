from fpdf import FPDF
import time
import data


class PDF(FPDF):
    ticker = ""
    WIDTH = 216
    HEIGHT = 280

    def __init__(self, ticker):
        super().__init__()
        PDF.ticker = ticker.upper()

    # Page header
    def header(self):
        # Logo
        self.image(f"rif-header-icon.png", 10, 8, 33)
        # Times bold 15
        self.set_font("Times", "", 18)

        # Title
        self.cell(80)
        self.cell(30, 10, f"{self.ticker}: Stock Report", align="C", border=0, ln=1)

        # Date
        self.set_font("Times", "I", 12)
        self.cell(80)
        date = time.ctime().split(" ")
        date = " ".join([*date[1:-2], date[-1]])
        self.cell(30, 10, f"{date}", 0, 0, "C")

        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Times italic 8
        self.set_font("Times", "I", 8)
        # Page number
        self.cell(0, 10, "Page " + str(self.page_no()) + "/{nb}", 0, 0, "C")

    def _heading(self, text):
        self.set_font("Times", "B", 15)
        self.cell(0, 10, text, border=0, ln=1)

    def _text(self, text):
        self.set_font("Times", "", 12)
        self.cell(0, 10, txt=text, border=0, ln=1, align="L")

    def _link(self, text, link):
        self.set_font("Times", "U", 12)
        self.set_text_color(0, 0, 150)
        self.cell(0, 10, txt=text, border=0, ln=1, align="L", link=link)
        self.set_text_color(0, 0, 0)

    def _ctext(self, text):
        self.set_font("Times", "", 12)
        self.cell(0, 10, txt=text, border=0, ln=1, align="C")

    def _body(self, text):
        self.set_font("Times", "", 12)
        self.multi_cell(
            w=0,
            h=6,
            txt=text,
            border=0,
            align="J",
        )

    def _cimage(self, *, path, y, w):
        x = (self.WIDTH - w) / 2
        self.image(path, x=x, y=y, w=w)

    def _grid(self, *, grid: list, y_init):
        num_rows = len(grid) % 2 + len(grid) / 2

        height = int((self.HEIGHT - 1.1 * y_init) // num_rows)
        width = height  # assume square
        width = (self.WIDTH - 10) // 2 if width * 2 > self.WIDTH else width
        height = width

        mid = self.WIDTH / 2
        x = [int(mid - width if grid.index(path) % 2 == 0 else mid) for path in grid]
        y = [y_init + height * (grid.index(path) // 2) for path in grid]

        for xi, yi, path in zip(x, y, grid):
            if len(grid) % 2 and grid.index(path) == len(grid) - 1:
                # last item in odd list
                xi = (self.WIDTH - width) / 2
                self.image(path, x=xi, y=yi, w=width, h=height)
                break

            self.image(path, x=xi, y=yi, w=width, h=height)


def generate_report(ticker):
    '''given a stock ticker, generates a pdf report'''

    # init
    pdf = PDF(ticker)

    pdf.set_author("RIF")
    pdf.set_title("Stock Report")
    pdf.alias_nb_pages()

    # page 1
    pdf.add_page()
    pdf._heading("Market Profile")

    pdf.line(10, 50, 200, 50)
    pdf.line(10, 60, 200, 60)
    pdf.line(10, 80, 200, 80)

    pdf._ctext(f"{ticker} Profile")
    keys, values = data.get_profile(ticker)
    profile = [f'{k}: {v}' for k, v in zip(keys, values)]
    pdf._ctext('    '.join(profile[:4]))
    pdf._ctext('    '.join(profile[4:]))

    data.get_graphs(ticker)
    pdf._cimage(path=f"{ticker}-price-chart.png", y=85, w=150)

    # page 2
    pdf.add_page()
    pdf._heading("Financials")
    pdf._grid(
        grid=[
            f"{ticker}-debt_long.png",
            f"{ticker}-debt_short.png",
            f"{ticker}-ebit.png",
            f"{ticker}-fcf.png",
            f"{ticker}-gross-profit.png",
            f"{ticker}-revenue_earnings.png",
        ],
        y_init=50,
    )

    # page 3
    pdf.add_page()

    summary = data.get_summary(ticker)
    pdf._heading("Company Summary")
    pdf._body(summary)

    news = data.get_news(ticker)
    pdf._heading("Recent News")
    for i in range(4):
        pdf._text(f'{news[i][0]} ')
        pdf._link(
            f"{news[i][1][:75]}{'...' if len(news[i][1])>75 else ''}",
            link=news[i][2],
        )

    # page 4
    pdf.add_page()
    pdf._heading("Sources")

    pdf._text('Market Profile and News')
    pdf._link('Finviz', 'https://finviz.com/')
    pdf._text('Company Summary and Chart Data')
    pdf._link('Yahoo! Finance', 'https: // finance.yahoo.com/')

    pdf.output(f"{ticker}-report.pdf", "F")


def main():
    ticker = input("input stock ticker: ").upper()
    [print("no ticker"), quit()] if not ticker else None
    generate_report(ticker)


if __name__ == "__main__":
    main()
