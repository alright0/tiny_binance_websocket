import websockets
import asyncio
import json
from datetime import datetime
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd

open_list, close_list, high_list, low_list, time_list = [], [], [], [], []

fig = mpf.figure()


# визаульное форматирование
ax = fig.add_subplot(1, 1, 1, style="yahoo")
ax.set_facecolor("xkcd:charcoal")
ax.grid(alpha=0.05)


def update_graph(data):
    """здесь строится график"""

    ax.clear()
    mpf.plot(data, type="candle", ax=ax, block=False)
    plt.pause(0.1)


async def main():
    url = "wss://stream.binance.com:9443/stream?streams=btcusdt@kline_1m"

    async with websockets.connect(url) as client:
        while True:
            data = json.loads(await client.recv())["data"]
            # Получение информации о котировках, на основании которой можно
            # постироить японскиек свечи требует четырех параметров:
            # Стоимость на момент открытия, Стоимость на момент закрытия
            # Минимальная стоимость за период, Максимальная стоимость за период

            open_list.append(float(data["k"]["o"]))
            close_list.append(float(data["k"]["c"]))
            high_list.append(float(data["k"]["h"]))
            low_list.append(float(data["k"]["l"]))
            time_list.append(
                datetime.fromtimestamp(data["E"] / 1000).strftime("%Y-%m-%d %H:%M")
            )

            # mplfinance принимает на вход dataframe
            data = pd.DataFrame(
                list(zip(open_list, close_list, high_list, low_list, time_list)),
                columns=["Open", "Close", "High", "Low", "Date"],
            )

            # мы хотим получать переменное значение в течение периода, поэтому нам
            # надо рисовать не несколько значений за один и тот же период, а оставлять
            # только самое последнее
            data = (
                data.groupby(["Date"])
                .agg(
                    {
                        "Open": lambda x: x.iloc[-1],
                        "Close": lambda x: x.iloc[-1],
                        "High": lambda x: x.iloc[-1],
                        "Low": lambda x: x.iloc[-1],
                    }
                )
                .reset_index()
            )

            data["Date"] = pd.to_datetime(data["Date"])

            # mplfinance использует индекс в качестве оси Х и ожидает увидеть там дату
            data = data.set_index(["Date"])

            update_graph(data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
