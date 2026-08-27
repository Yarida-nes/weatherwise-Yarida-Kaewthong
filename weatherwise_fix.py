"""WeatherWise fix module.

Two problems this solves:

1. `create_weather_summary` was referenced by the menu but never written.
2. `get_weather_data` returns OpenWeather's format (3-hourly readings under
   the "list" key) while the chart functions were written for wttr.in's
   format ("daily" records with "maxtempC"). `to_daily` adapts one to the
   other, so the charts work without being rewritten.

Load it in Colab with:
    !wget -q https://raw.githubusercontent.com/Yarida-nes/weatherwise-Yarida-Kaewthong/main/weatherwise_fix.py
    %run weatherwise_fix.py
"""

from collections import defaultdict
import matplotlib.pyplot as plt


def to_daily(weather_data):
    """Group OpenWeather's 3-hourly readings into one record per day."""
    if not weather_data or not weather_data.get("list"):
        return []

    buckets = defaultdict(list)
    for entry in weather_data["list"]:
        day = entry.get("dt_txt", "")[:10]          # '2026-08-27'
        if day:
            buckets[day].append(entry)

    daily = []
    for day in sorted(buckets):
        entries = [e for e in buckets[day] if "main" in e]
        if not entries:
            continue
        temps = [e["main"]["temp"] for e in entries]
        hourly = [{
            "time": e.get("dt_txt", "")[11:16],
            "tempC": e["main"]["temp"],
            "precipMM": e.get("rain", {}).get("3h", 0.0),
            "chanceofrain": int(e.get("pop", 0) * 100),
            "description": (e.get("weather") or [{}])[0].get("description", ""),
        } for e in entries]

        daily.append({
            "date": day,
            "maxtempC": round(max(temps)),
            "mintempC": round(min(temps)),
            "avgtempC": round(sum(temps) / len(temps)),
            "totalPrecipMM": round(sum(h["precipMM"] for h in hourly), 1),
            "hourly": hourly,
        })
    return daily


def create_temperature_visualisation(weather_data, output_type="display"):
    daily = to_daily(weather_data)
    if not daily:
        print("No forecast data available to plot temperatures.")
        return None

    labels = [d["date"][5:] for d in daily]
    max_t = [d["maxtempC"] for d in daily]
    min_t = [d["mintempC"] for d in daily]

    fig, ax = plt.subplots()
    ax.plot(labels, max_t, marker="o", label="Max °C")
    ax.plot(labels, min_t, marker="o", label="Min °C")
    ax.fill_between(labels, min_t, max_t, alpha=0.15)
    ax.set_title("Daily temperature range")
    ax.set_xlabel("Day")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    plt.tight_layout()

    if output_type == "figure":
        return fig
    plt.show()
    return None


def create_precipitation_visualisation(weather_data, output_type="display"):
    daily = to_daily(weather_data)
    if not daily:
        print("No forecast data available to plot precipitation.")
        return None

    labels = [d["date"][5:] for d in daily]
    totals = [d["totalPrecipMM"] for d in daily]

    fig, ax = plt.subplots()
    ax.bar(labels, totals, color="#4e79a7")
    ax.set_title("Daily total precipitation")
    ax.set_xlabel("Day")
    ax.set_ylabel("Precipitation (mm)")
    plt.tight_layout()

    if output_type == "figure":
        return fig
    plt.show()
    return None


def create_weather_summary(weather_data, output_type="display"):
    """Print a plain-text 5-day summary. This is the function the menu
    called but which had never been implemented."""
    daily = to_daily(weather_data)
    if not daily:
        print("No forecast data available to summarise.")
        return None

    city = (weather_data.get("city") or {}).get("name", "your location")
    lines = [f"\nWeather summary for {city}", "-" * 38]
    for d in daily:
        wet = "dry" if d["totalPrecipMM"] < 0.2 else f"{d['totalPrecipMM']} mm rain"
        lines.append(f"{d['date']}   {d['mintempC']:>3} to {d['maxtempC']:<3} °C   {wet}")

    highs = [d["maxtempC"] for d in daily]
    lows = [d["mintempC"] for d in daily]
    lines += [
        "-" * 38,
        f"Warmest day:   {max(highs)}°C",
        f"Coolest night: {min(lows)}°C",
        f"Total rain over {len(daily)} days: "
        f"{round(sum(d['totalPrecipMM'] for d in daily), 1)} mm",
    ]

    summary = "\n".join(lines)
    if output_type == "figure":
        return summary
    print(summary)
    return None


def show_today_weather(weather_data):
    daily = to_daily(weather_data)
    if not daily:
        print("No forecast data available.")
        return

    today = daily[0]
    now = today["hourly"][0] if today["hourly"] else {}
    city = (weather_data.get("city") or {}).get("name", "your location")

    print(f"\nToday's weather in {city}")
    print("-" * 30)
    print(f"Temperature now: {now.get('tempC', 'N/A')}°C")
    print(f"Conditions:      {now.get('description', 'Unknown')}")
    print(f"Max temp:        {today['maxtempC']}°C")
    print(f"Min temp:        {today['mintempC']}°C")
    print(f"Chance of rain:  "
          f"{max((h['chanceofrain'] for h in today['hourly']), default=0)}%")


print("WeatherWise fix loaded: to_daily, create_temperature_visualisation, "
      "create_precipitation_visualisation, create_weather_summary, "
      "show_today_weather")
