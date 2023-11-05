import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template, request

sns.set()

conn = sqlite3.connect("stock_prices.db")
c = conn.cursor()

df = c.execute(
    """select instrument_name, currency_name, date, interval, last_price, open_price ,max_price, min_price, volume, change
from stock 
left join instrument on instrument.instrument_id = stock.instrument_id
left join currency on currency.currency_id  = stock.currency_id;"""
).fetchall()

df = pd.DataFrame(df, columns=[col[0] for col in c.description])
df["date"] = df["date"].apply(lambda x: datetime.strptime(x, "%d.%m.%Y"))

conn.commit()
conn.close()

app = Flask(__name__)


def create_plot(stock_name, start_date, end_date, interval, df):
    temp_df = df[
        (df["instrument_name"] == stock_name)
        & (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["interval"] == interval)
    ]

    plt.plot(temp_df["date"], temp_df["last_price"])

    return plt


@app.route("/")
def main_site():
    return render_template("main.html")


@app.route("/test", methods=["POST"])
def generate_plot():
    if request.method == "POST":
        stock_name = request.form["stockname"]
        start_date = request.form["startdate"]
        end_date = request.form["enddate"]
        interval = request.form["interval"]

        plot = create_plot(
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            df=df,
        )

        if not os.path.exists("static/images"):
            os.makedirs("static/images")

        plot.savefig(os.path.join("static", "images", "plot.png"))

        # Close the figure to avoid overwriting
        plot.close()

        # return "<h1>STOCK_NAME: {0}</h1> <h1>START_DATE: {1}</h1> <h1>END_DATE: {2}</h1> <h1>INTERVAL: {3}</h1> ".format(
        #     stock_name, start_date, end_date, interval
        # )
        return render_template(
            "test_plot.html",
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )


if __name__ == "__main__":
    app.run(debug=True)
