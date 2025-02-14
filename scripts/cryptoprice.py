import io
from decimal import Decimal
from typing import Tuple

import requests as requests
from PIL import Image, ImageDraw

try:
    from libs import *
except ImportError as e:
    from ..libs import *

coingecko = CoingeckoApi()


class Script(iScriptImageGenerator):

    def __init__(self):
        super().__init__()
        self.cryptos = self.config.cryptos
        self.show_logo = self.config.get_bool("SHOW_LOGO", 'n')

    def _round_price(self, price: float) -> str:
        if price is None:
            return " - "
        d = Decimal(price)
        if d % 1 == 0:
            s = f"{d:,.0f}"
        elif d > 1000:
            s = f"{d:,.0f}"
        elif d > 100:
            s = f"{d:,.4f}"
        elif d > 1:
            s = f"{d:,.6f}"
        else:
            s = f"{d:,.8f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s

    def getpriceinfo(self, ticker):
        coin = coingecko.get_coin_by_symbol(ticker)
        response = coingecko.get_coin(coin_id=coin['id'], market_data=True)

        return {
            'name': response['name'],
            'price': self._round_price(response['market_data']['current_price']['usd']),
            'last': self._round_price(response['market_data']['current_price']['usd']),
            'high': self._round_price(response['market_data']['high_24h']['usd']),
            'low': self._round_price(response['market_data']['low_24h']['usd']),
            'percentage': round(response['market_data']['price_change_percentage_24h'], 2),
            # thumb, small, large
            'image': Image.open(io.BytesIO(requests.get(response['image']['small']).content), 'r').convert('RGBA')
        }

    def createimage(self, ticker, screen_size: Tuple[int, int]):
        pi = self.getpriceinfo(ticker)
        width, height = screen_size
        # satw = int(math.floor(width / 87))
        # padleft = int(math.floor((width - (87 * satw)) / 2))
        padtop = 40
        im = Image.new(mode="RGB", size=(width, height))
        draw = ImageDraw.Draw(im)
        self.drawcenteredtext(draw, pi['last'], 128, int(width / 2), int(height / 2), self.color("#D9D9D9"))
        self.drawcenteredtext(draw, pi['last'], 128, int(width / 2) - 2, int(height / 2) - 2, self.color("#FFFFFF"))
        self.drawcenteredtext(draw, f"{pi['name']} price:", 24, int(width / 2), int(padtop))
        if self.show_logo:
            logo_image: Image = pi['image']
            im.paste(logo_image, (int(width * 0.05), int((padtop - logo_image.size[1] / 2) / 2)))
        perc_color = self.color("green") if pi['percentage'] >= 0 else self.color("red")
        self.drawcenteredtext(draw, f"24h: {pi['percentage']:.2f} %", 20, int(width / 8 * 4), height - padtop,
                              perc_color)
        self.drawcenteredtext(draw, s=f"H: {pi['high']}", fontsize=25, x=int(width / 8 * 7), y=height - padtop)
        self.drawcenteredtext(draw, s=f"L: {pi['low']}", fontsize=25, x=int(width / 8 * 1), y=height - padtop)
        self.drawbottomlefttext(
            draw,
            s="Market data by coingecko",
            fontsize=16,
            x=0,
            y=height,
            textcolor=self.color("#40FF40")
        )
        self.drawbottomrighttext(draw, f"as of {self.getdateandtime()}", fontsize=12, x=width, y=height)
        return im

    def generate_all_images(self, screen_size: Tuple[int, int]):
        for ticker in self.cryptos:
            yield self.createimage(ticker, screen_size)
