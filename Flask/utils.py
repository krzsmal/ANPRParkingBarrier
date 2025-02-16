import sqlite3
from datetime import timedelta, datetime
import pandas as pd
import plotly.graph_objects as go
import plotly
import json

database = '../Barrier/database.db'


def generate_plot():
    conn = sqlite3.connect(database)
    query = """
    SELECT DATE(data) AS dzien,
           SUM(CASE WHEN wjazd = 1 THEN 1 ELSE 0 END) AS liczba_wjazdow,
           SUM(CASE WHEN wjazd = 0 THEN 1 ELSE 0 END) AS liczba_wyjazdow
    FROM przejazdy
    GROUP BY dzien
    ORDER BY dzien;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['dzien'], 
        y=df['liczba_wjazdow'], 
        mode='lines+markers', 
        name='Wjazdy',
        line=dict(color='royalblue', width=3),
        marker=dict(size=8, symbol='circle', color='royalblue'),
        hoverinfo='x+y'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['dzien'], 
        y=df['liczba_wyjazdow'], 
        mode='lines+markers', 
        name='Wyjazdy',
        line=dict(color='firebrick', width=3, dash='dot'), 
        marker=dict(size=8, symbol='circle', color='firebrick'),
        hoverinfo='x+y'
    ))

    fig.update_layout(
        title={
            'text': 'Liczba wjazdów i wyjazdów w czasie',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Dzień',
        yaxis_title='Liczba',
        font=dict(
            family="Arial, sans-serif",
            size=20,
            color="black"
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            tickangle=45,
            title_font=dict(size=16),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            title_font=dict(size=16),
            tickfont=dict(size=12),
            range=[-1, max(df['liczba_wjazdow'].max(), df['liczba_wyjazdow'].max()) + 1],
            fixedrange=True,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1
        ),
        plot_bgcolor='white',
        hovermode='x',
        dragmode='pan'
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def generate_stats():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Count of distinct vehicles
    cursor.execute("SELECT COUNT(*) FROM (SELECT * FROM przejazdy group by nr_rejestracyjny)")
    cars_count = cursor.fetchall()[0]

    # Number of entries to parking
    cursor.execute("SELECT COUNT(*) FROM przejazdy WHERE wjazd = 1")
    entries_count = cursor.fetchall()[0]

    # Number of exits from the parking lot
    cursor.execute("SELECT COUNT(*) FROM przejazdy WHERE wjazd = 0")
    exits_count = cursor.fetchall()[0]

    # Car registrations at the parking lot
    cursor.execute("SELECT nr_rejestracyjny, ostatnia_data FROM (SELECT nr_rejestracyjny, wjazd, MAX(data) AS ostatnia_data FROM przejazdy GROUP BY nr_rejestracyjny) WHERE wjazd = 1")
    cars_on_parking_registrations = cursor.fetchall()
    cars_on_parking_registrations = [(car[0], datetime.strptime(car[1], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S %d-%m-%y')) for car in cars_on_parking_registrations]

    # Current number of cars in the parking lot
    cars_on_parking = len(cars_on_parking_registrations)

    # Number of cars in the parking lot in the last 24 hours
    cursor.execute("""
    SELECT COUNT(*) 
    FROM (
        SELECT nr_rejestracyjny, MAX(data) AS ostatnia_data 
        FROM przejazdy 
        WHERE data > datetime('now', '-1 day', '+1 hour') AND wjazd = 1
        GROUP BY nr_rejestracyjny
    ) AS podzapytanie;
    """)
    cars_on_parking_last_24h = cursor.fetchall()[0]
    
    # Total duration of cars stay in the parking lot
    cursor.execute("""
        WITH
            Wjazdy AS (
                SELECT nr_rejestracyjny, data AS czas_wjazdu
                FROM przejazdy
                WHERE wjazd = 1
            ),
            Wyjazdy AS (
                SELECT nr_rejestracyjny, data AS czas_wyjazdu
                FROM przejazdy
                WHERE wjazd = 0
            ),
            Pary AS (
                SELECT
                    Wjazdy.nr_rejestracyjny,
                    Wjazdy.czas_wjazdu,
                    MIN(Wyjazdy.czas_wyjazdu) AS czas_wyjazdu
                FROM Wjazdy
                LEFT JOIN Wyjazdy
                ON Wjazdy.nr_rejestracyjny = Wyjazdy.nr_rejestracyjny
                AND strftime('%s', Wyjazdy.czas_wyjazdu) > strftime('%s', Wjazdy.czas_wjazdu)
                GROUP BY Wjazdy.nr_rejestracyjny, Wjazdy.czas_wjazdu
            )
        SELECT
            SUM(
                CASE
                    WHEN czas_wyjazdu IS NOT NULL THEN
                        strftime('%s', czas_wyjazdu) - strftime('%s', czas_wjazdu)
                    ELSE
                        strftime('%s', 'now') - strftime('%s', czas_wjazdu)
                END
            ) AS calkowity_czas_sekundy
        FROM Pary;
    """)
    result = cursor.fetchone()
    total_seconds = int(result[0])
    total_duration = timedelta(seconds=total_seconds)
    conn.close()
    return {'cars_count': cars_count[0], 'entries_count': entries_count[0], 'exits_count': exits_count[0], 'cars_on_parking_registrations': cars_on_parking_registrations, 'cars_on_parking': cars_on_parking, 'cars_on_parking_last_24h': cars_on_parking_last_24h[0], 'total_duration': str(total_duration)}