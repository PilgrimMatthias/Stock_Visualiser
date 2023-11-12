import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template, request

sns.set_style("whitegrid")

# Connection to sqlite db
conn = sqlite3.connect("stock_prices.db")
c = conn.cursor()

# Selecting data with sql statement
df = c.execute(
    """select instrument_name, currency_name, date, interval, last_price, open_price ,max_price, min_price, volume, change
from stock 
left join instrument on instrument.instrument_id = stock.instrument_id
left join currency on currency.currency_id  = stock.currency_id;"""
).fetchall()

# Creating dataframe
df = pd.DataFrame(df, columns=[col[0] for col in c.description])
df["date"] = df["date"].apply(lambda x: datetime.strptime(x, "%d.%m.%Y"))

# Closing database connections
conn.commit()
conn.close()

# Creating Flask App
app = Flask(__name__)


def create_plot(stock_name, start_date, end_date, interval, df):
    """
    Method responsible for creating plot with declaration:
    - Name of stock
    - Lower date
    - Upper date
    - Interval (daily, weekly or yearly)
    - Df <- data frame
    """
    # Getting data from selection
    temp_df = df[
        (df["instrument_name"] == stock_name)
        & (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["interval"] == interval)
    ]

    # Setting size of plot figure
    fig = plt.figure(figsize=(15, 7.5))

    # Creating line plot for current selection
    plt.plot(temp_df["date"], temp_df["last_price"])

    # Title of plot
    plt.title(
        "{0}, period: {1} - {2}".format(stock_name.upper(), start_date, end_date),
        fontsize=16,
        loc="left",
        pad=20,
        color="#595959",
    )

    # Y axis label
    plt.ylabel(
        "Value in {0}".format(temp_df["currency_name"].unique()[0]),
        fontsize=14,
        labelpad=20,
        color="#A6A6A6",
    )

    # X axis label
    plt.xlabel(
        "Interval: {0}".format(interval), fontsize=14, labelpad=20, color="#A6A6A6"
    )

    # Changing font and color of y and x axis values
    plt.tick_params(colors="#595959", which="both")
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Changing rotation of x axis values for Daily and Weekly interal
    if interval == "Daily" or interval == "Weekly":
        plt.xticks(rotation=45)

    return plt


@app.route("/")
def main_site():
    """
    Method reponsible for generating base site
    """
    return render_template("main.html")


@app.route("/", methods=["POST"])
def generate_plot():
    """
    Method reponsible for generating plot on site from user selections
    """
    if request.method == "POST":
        stock_name = request.form["stockname"]
        start_date = request.form["startdate"]
        end_date = request.form["enddate"]
        interval = request.form["interval"]

        # Crearting plot
        plot = create_plot(
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            df=df,
        )

        if not os.path.exists("static/images"):
            os.makedirs("static/images")

        # Saving plot to static/images
        plot.savefig(os.path.join("static", "images", "plot.png"))

        # Closing the figure to avoid overwriting
        plot.close()

        # Opening site with plot
        return render_template(
            "main.html", plot_img=os.path.join("static", "images", "plot.png")
        )


if __name__ == "__main__":
    app.run(debug=True)
