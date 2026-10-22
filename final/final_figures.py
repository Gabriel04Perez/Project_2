"""DSC 106 Project 2: final versions of the four charts picked at the checkpoint.

Proposition, narrowed after checkpoint feedback:
    "U.S. CO2 emissions from burning fossil fuels are no longer a growing climate problem."

What the feedback asked for, and what changed here:
    - Say which CO2. File 05 counts CO2 from fuel combustion only, so every
      title, subtitle, axis and note on a2/b2 now names it as fossil-fuel CO2,
      and a6/b6 say their subsidies include the climate cost of that CO2.
    - a6 and b6 plot IMF subsidy estimates whose 2023-2030 values are
      projections. Those years are now shaded, labeled and dashed, and every
      headline number rests on actual years or says "projected".

The report (final/index.html) uses a2 (FOR) and b2 (AGAINST), the pair the
feedback called strongest; a6 and b6 are kept as alternates. The combined_*
images stack each side's two charts under one headline, as a single
concatenated visualization (a2 over a6, b2 over b6).

    python final/final_figures.py           # write final/images/*.png
    python final/final_figures.py --show    # ...and also open them in the browser
"""

import base64
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# Reuse the checkpoint module's data loaders and chart chrome.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import (  # noqa: E402
    AXIS, FONT, GRAY, GREEN, GRID, IMF_FFS, INK, INK_2, LAST_ACTUAL, OECD, PAD, PERIODS, RED, SURFACE,
    TOTAL, end_dot, end_label, finish, implied_gdp, line, load_subsidies, load_trade, wash,
)

IMG_DIR = Path(__file__).parent / "images"
PROJECTED_NOTE = f"Values for {LAST_ACTUAL + 1}–2030 are IMF projections."


def minus(text):
    return text.replace("-", "−")


# --------------------------------------------------------------------------
# Projection helpers (a6, b6)
# --------------------------------------------------------------------------
def split(series, color, name, **kw):
    """Two traces for one series: solid through LAST_ACTUAL, dashed over the IMF projections."""
    actual, projected = series.loc[:LAST_ACTUAL], series.loc[LAST_ACTUAL:]
    return (line(actual.index, actual, color, name, **kw),
            line(projected.index, projected, color, f"{name} (IMF projection)", dash="dash", **kw))


def mark_projections(fig, last):
    """Shade and label the projection years so a forecast can't pass as data."""
    fig.add_vrect(x0=LAST_ACTUAL, x1=last + 0.5, fillcolor=wash(GRAY, 0.16), line_width=0, layer="below")
    fig.add_vline(x=LAST_ACTUAL, line=dict(color=AXIS, width=1))
    for text, anchor, shift in (("Actual", "right", -8), ("IMF projections", "left", 8)):
        fig.add_annotation(x=LAST_ACTUAL, xanchor=anchor, xshift=shift, y=1, yref="paper", yanchor="top",
                           yshift=-4, showarrow=False, text=text, font=dict(size=12, color=INK_2))


def hollow_dot(x, y, color):
    """Endpoint marker for a projected value: ring only, unlike the filled actual-data dots."""
    return go.Scatter(x=[x], y=[y], mode="markers", hoverinfo="skip", showlegend=False,
                      marker=dict(size=11, color=SURFACE, line=dict(color=color, width=2.5)))


# --------------------------------------------------------------------------
# A2 final. Peak and decline of fossil-fuel CO2 (report: FOR)
# --------------------------------------------------------------------------
def viz_a2_final(trade, start=2000, end=2017):
    """FOR: U.S. fossil-fuel CO2 peaked in 2005 and has stayed below that peak since.

    Changed from the checkpoint: the title, subtitle, axis and note name the
    CO2 as fossil-fuel combustion CO2, which is exactly what file 05 measures.

    Persuasive choices (score: -2 deceptive ... +2 earnest)
    - Window 2000-2017 (-1.5). The data runs 1995-2018; 2018 rose ~3%, and
      2017 is only 6% below 1995. The window keeps the line falling at its end.
    - Truncated y-axis from 4.4 billion t (-1). A 17% drop fills the plot.
    - "Avoided" area (-1). Sum of (peak - actual) for each year after the
      peak: a counterfactual (emissions frozen at their high) stated as fact.
    - Production-based fossil-fuel CO2, named precisely (+1.5). The standard
      national-inventory measure; the narrowed labels match what is measured.
    - Peak and endpoint annotated, the 2009 recession left unlabeled (-0.5).
    """
    prod = trade["production"].loc[start:end] / 1000  # billion tonnes
    peak_year = int(prod.idxmax())
    peak = prod[peak_year]
    after = prod.loc[peak_year:]
    assert (after.iloc[1:] < peak).all(), "subtitle says every year since the peak is below it"
    avoided = (peak - after).sum()
    drop = (prod[end] / peak - 1) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=after.index, y=[peak] * len(after), mode="lines",
                             line=dict(color=INK_2, width=1.5, dash="dot"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=after.index, y=after, mode="lines", line=dict(width=0),
                             fill="tonexty", fillcolor=wash(GREEN, 0.16), hoverinfo="skip"))
    fig.add_trace(line(prod.index, prod, GREEN, "U.S. fossil-fuel CO₂"))
    fig.add_trace(end_dot(peak_year, peak, GREEN))
    fig.add_trace(end_dot(end, prod[end], GREEN))

    fig.add_annotation(x=peak_year, y=peak, yshift=14, yanchor="bottom", showarrow=False,
                       text=f"{peak_year} peak: <b>{peak:.2f}</b> billion t", font=dict(color=INK))
    fig.add_annotation(x=end, y=peak, xanchor="left", xshift=8, showarrow=False,
                       text=f"{peak_year} level", font=dict(size=12, color=INK_2))
    end_label(fig, end, prod[end], minus(f"{drop:.0f}%"), f"since {peak_year}, to {prod[end]:.2f} bn t", GREEN)
    fig.add_annotation(
        x=(peak_year + end) / 2 + 1.5, y=peak - 0.32, showarrow=False, align="center",
        text=f"<b><span style='font-size:20px;color:{INK}'>{avoided:.1f} billion tonnes</span></b>"
             f"<br>of CO₂ avoided since {peak_year}",
        font=dict(size=14, color=INK_2),
    )
    fig.update_xaxes(range=[start - 0.5, end + 0.5], dtick=2, showgrid=False)
    fig.update_yaxes(title_text="Billion tonnes of fossil-fuel CO₂ per year", range=[4.4, 6.05], dtick=0.25,
                     tickformat=".2f")

    return finish(
        fig,
        title=f"U.S. Fossil-Fuel CO₂ Emissions Have Fallen {abs(drop):.0f}% Since Their {peak_year} Peak",
        subtitle=(f"CO₂ from burning coal, oil and gas inside the United States has stayed below "
                  f"its {peak_year} high every year since"),
        note=f"Source: {OECD}. CO₂ from fuel combustion by producers located in the United States.",
    )


# --------------------------------------------------------------------------
# B2 final. Fossil-fuel CO2 embodied in imports vs. exports (report: AGAINST)
# --------------------------------------------------------------------------
def viz_b2_final(trade):
    """AGAINST: the fossil-fuel CO2 behind U.S. imports keeps climbing.

    Changed from the checkpoint: the title, subtitle, axis and note name the
    CO2 as fossil-fuel combustion CO2, and a new annotation ties the chart back
    to A2: none of this imported CO2 appears in official (territorial) totals.

    Persuasive choices (score: -2 deceptive ... +2 earnest)
    - Consumption-side lens, with exports as the baseline (+1.5). CO2 embodied
      in trade is a recognized measure (OECD TeCO2), and territorial
      inventories really do leave it out.
    - Splicing two methods (-2). 1995-2018 is OECD TeCO2; 2019-2021 is a
      different IMF extension (imports jump 66% in one year). Through 2018 the
      period averages rise ~1.4x, not 2.2x. Both sources are cited; the seam isn't.
    - Five-year bins with a two-year final bin (-1). Binning damps noise, but
      it also smooths the 2019 break into a steady climb.
    - First-period reference line and "x2.2" callout (-0.5). An endpoint
      comparison that skips the 2010-14 dip.
    - Red imports vs. gray exports, and the word "hidden" (-0.5).
    """
    binned = pd.DataFrame({
        label: trade.loc[a:b, ["imports", "exports"]].mean() for label, (a, b) in PERIODS.items()
    }).T
    labels = list(binned.index)
    ratio = binned["imports"].iloc[-1] / binned["imports"].iloc[0]
    assert ratio > 2, "title says 'more than doubled'"

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=binned["exports"], name="Exported", marker_color=GRAY,
                         width=0.32, offset=-0.34,
                         hovertemplate="%{x}: %{y:,.0f} Mt<extra>Exports</extra>"))
    fig.add_trace(go.Bar(x=labels, y=binned["imports"], name="Imported", marker_color=RED,
                         width=0.32, offset=0.02, text=[f"{v:,.0f}" for v in binned["imports"]],
                         textposition="outside", textfont=dict(color=INK, size=13),
                         cliponaxis=False,
                         hovertemplate="%{x}: %{y:,.0f} Mt<extra>Imports</extra>"))
    # Dotted line at the first period's level, so every later bar reads as "more than then".
    base = binned["imports"].iloc[0]
    fig.add_shape(type="line", xref="paper", yref="y", x0=0, x1=1, y0=base, y1=base,
                  line=dict(color=INK_2, width=1.5, dash="dot"), layer="above")
    fig.add_annotation(x=labels[-1], y=binned["imports"].iloc[-1], xshift=18, yshift=48,
                       showarrow=False, text=f"<b><span style='font-size:22px;color:{INK}'>×{ratio:.1f}</span></b>"
                       f"<br><span style='font-size:12px'>vs. {labels[0]}</span>")
    fig.add_annotation(x=labels[0], y=base, xshift=-46, yshift=-12, showarrow=False,
                       text=f"{labels[0]} level", font=dict(size=12, color=INK_2))
    # x=0.5 sits between the first two categories, in the empty space above their bars.
    fig.add_annotation(
        x=0.5, y=2150, showarrow=False, align="left", xanchor="center",
        text=f"<b><span style='color:{INK}'>None of this imported CO₂</span></b>"
             "<br>is counted in official U.S. emissions totals,"
             "<br>which only include what is burned at home",
        font=dict(size=14, color=INK_2),
    )
    fig.update_xaxes(showgrid=False, linecolor=AXIS)
    fig.update_yaxes(title_text="Million tonnes of fossil-fuel CO₂ per year (period average)",
                     range=[0, 2500], dtick=500, tickformat=",")

    finish(
        fig,
        title="The Fossil-Fuel CO₂ Hidden in U.S. Imports Has More Than Doubled",
        subtitle="CO₂ released abroad by burning fossil fuels to make goods the U.S. imports, vs. the CO₂ in its exports",
        note=("Source: OECD Trade in Embodied CO₂ database (2021); IMF Direction of Trade Statistics (2022), "
              "via IMF Climate Change Indicators. CO₂ from fuel combustion."),
        margin={"r": 40},
    )
    # After finish(), which turns the legend off for the single-series line charts.
    fig.update_layout(
        showlegend=True, bargap=0.3,
        legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom",
                    font=dict(size=13, color=INK_2), traceorder="reversed"),
    )
    return fig


# --------------------------------------------------------------------------
# A6 final. Coal subsidies as a share of GDP, projections marked (alternate FOR)
# --------------------------------------------------------------------------
def viz_a6_final(subsidies):
    """FOR: coal's subsidies, climate cost included, are on track to halve.

    Changed from the checkpoint: 2023-2030 are shaded, labeled "IMF
    projections" and dashed, with a hollow end marker; the actual-data drop
    (to 2022) gets its own label; the title says "on track ... by 2030"
    instead of "have been cut"; the subtitle ties the subsidy to coal's CO2.

    Persuasive choices (score: -2 deceptive ... +2 earnest)
    - Projections marked, but still in the headline (+0.5). "Nearly in half"
      needs the 2030 forecast; through 2022 the drop is 35%.
    - Coal alone (-1.5). Natural gas, which largely replaced coal, is left out.
    - Share of GDP (-1). In 2021 dollars the drop through 2022 is 26%.
    - Truncated y-axis from 0.4% (-0.5).
    """
    pct, _ = subsidies
    coal = pct.loc[f"{TOTAL}; Coal"]
    first, last = coal.index.min(), coal.index.max()
    drop_actual = (coal[LAST_ACTUAL] / coal[first] - 1) * 100
    drop_projected = (coal[last] / coal[first] - 1) * 100
    assert 40 <= abs(drop_projected) < 50, "title says 'nearly in half'"

    fig = go.Figure()
    mark_projections(fig, last)
    for trace in split(coal, GREEN, "Coal", fill="tozeroy", fillcolor=wash(GREEN, 0.10)):
        fig.add_trace(trace)
    fig.add_trace(end_dot(first, coal[first], GREEN))
    fig.add_trace(end_dot(LAST_ACTUAL, coal[LAST_ACTUAL], GREEN))
    fig.add_trace(hollow_dot(last, coal[last], GREEN))
    fig.add_annotation(x=first, y=coal[first], xanchor="left", yanchor="bottom", xshift=6, yshift=12,
                       showarrow=False, font=dict(color=INK),
                       text=f"{first}: <b>{coal[first]:.2f}%</b> of GDP")
    fig.add_annotation(
        x=LAST_ACTUAL, y=coal[LAST_ACTUAL], xanchor="right", yanchor="top", xshift=-6, yshift=-12,
        showarrow=False, align="right",
        text=f"<b><span style='font-size:18px;color:{INK}'>{minus(f'{drop_actual:.0f}%')}</span></b>"
             f"<br>by {LAST_ACTUAL}, latest actual year",
        font=dict(color=INK_2),
    )
    end_label(fig, last, coal[last], minus(f"{drop_projected:.0f}%"),
              f"projected for {last},<br>to {coal[last]:.2f}% of GDP", GREEN)
    fig.update_xaxes(title_text="Year", range=[first - 0.5, last + 0.5], tick0=first, dtick=5,
                     showgrid=False)
    fig.update_yaxes(title_text="Coal subsidies (% of U.S. GDP)", range=[0.4, 0.95], dtick=0.1,
                     ticksuffix="%", tickformat=".1f")

    return finish(
        fig,
        title=f"U.S. Coal Subsidies Are on Track to Be Cut Nearly in Half by {last}",
        subtitle="Explicit and implicit coal subsidies, including the unpriced climate cost of coal’s CO₂, "
                 "as a share of U.S. GDP",
        note=f"Source: {IMF_FFS}. {PROJECTED_NOTE}",
        margin={"b": 100, "r": 190},
    )


# --------------------------------------------------------------------------
# B6 final. Natural gas vs. GDP, indexed to 2015, projections marked (alternate AGAINST)
# --------------------------------------------------------------------------
def viz_b6_final(subsidies):
    """AGAINST: natural gas's cost, climate damage included, is on track to double.

    Changed from the checkpoint: 2023-2030 are shaded, labeled and dashed for
    both lines; the "faster than the economy" callout now uses actual years
    only (2015-2022); the end labels say "projected"; the subtitle ties the
    subsidy to gas's CO2.

    Persuasive choices (score: -2 deceptive ... +2 earnest)
    - Projections marked, but still in the headline (+0.5). Gas "doubles"
      only by the 2030 forecast; through 2022 it rose 44%.
    - Coal left out (-1.5). Gas grew mostly by replacing coal; the two
      together cost 4% less in 2022 than in 2015.
    - Index to 2015 = 100 (-0.5). Hides that gas is ~$111B of a $757B total.
    - GDP backed out of the data (+0.5). Subsidies / their share of GDP gives
      GDP, a fair yardstick for "faster than the economy".
    """
    pct, usd = subsidies
    gas = usd.loc[f"{TOTAL}; Natural Gas"]
    gdp = implied_gdp(pct, usd)
    first, last = gas.index.min(), gas.index.max()
    idx_gas = gas / gas[first] * 100
    idx_gdp = gdp / gdp[first] * 100
    ratio = idx_gas[last] / 100
    assert 1.9 <= ratio < 2.1, "title says 'double'"
    gas_chg = idx_gas[LAST_ACTUAL] - 100
    faster = gas_chg / (idx_gdp[LAST_ACTUAL] - 100)

    fig = go.Figure()
    mark_projections(fig, last)
    gdp_actual, gdp_projected = split(idx_gdp, GRAY, "U.S. GDP")
    gas_actual, gas_projected = split(idx_gas, RED, "Natural-gas subsidies",
                                      fill="tonexty", fillcolor=wash(RED, 0.12))
    # Each gas trace fills down to the GDP trace added just before it.
    for trace in (gdp_actual, gas_actual, gdp_projected, gas_projected):
        fig.add_trace(trace)
    fig.add_trace(end_dot(LAST_ACTUAL, idx_gas[LAST_ACTUAL], RED))
    fig.add_trace(end_dot(LAST_ACTUAL, idx_gdp[LAST_ACTUAL], GRAY))
    fig.add_trace(hollow_dot(last, idx_gas[last], RED))
    fig.add_trace(hollow_dot(last, idx_gdp[last], GRAY))
    end_label(fig, last, idx_gas[last], f"×{ratio:.1f}", "Natural-gas subsidies,<br>projected", RED)
    end_label(fig, last, idx_gdp[last], f"{idx_gdp[last] - 100:+.0f}%", "U.S. GDP, projected", GRAY)
    # In the empty space above the actual-years lines, which top out near 150.
    fig.add_annotation(
        x=(first + LAST_ACTUAL) / 2, y=180, showarrow=False, align="center",
        text=f"<b><span style='font-size:18px;color:{INK}'>Up {gas_chg:.0f}% by {LAST_ACTUAL}</span></b>"
             f"<br>{faster:.0f}× faster than the U.S. economy",
        font=dict(size=14, color=INK_2),
    )
    fig.add_hline(y=100, line=dict(color=AXIS, width=1))
    fig.update_xaxes(title_text="Year", range=[first - 0.5, last + 0.5], tick0=first, dtick=5,
                     showgrid=False)
    fig.update_yaxes(title_text=f"Index ({first} = 100)", range=[80, 210], dtick=20)

    return finish(
        fig,
        title=f"Natural Gas’s Hidden Cost Is on Track to Double by {last}",
        subtitle="Explicit and implicit natural-gas subsidies, including the unpriced climate cost of gas’s CO₂, "
                 "vs. U.S. GDP",
        note=(f"Source: {IMF_FFS}.<br>{PROJECTED_NOTE} "
              "GDP = total subsidies ÷ their share of GDP; both series in 2021 dollars."),
        margin={"b": 115},
    )


# --------------------------------------------------------------------------
# Combined. Each side's two charts stacked under one headline
# --------------------------------------------------------------------------
def combine(title, subtitle, panels, header=112):
    """Stack finished charts, each rendered as an image, under one shared headline.

    The headline carries the side's overall claim and says how the emissions
    panel and the subsidy panel connect; each panel keeps its own title,
    labels and source note.
    """
    width = panels[0].layout.width
    height = header + sum(p.layout.height for p in panels)
    fig = go.Figure()
    top = header
    for panel in panels:
        png = base64.b64encode(panel.to_image(format="png", scale=2)).decode()
        fig.add_layout_image(source=f"data:image/png;base64,{png}", xref="paper", yref="paper",
                             x=0, y=1 - top / height, sizex=1, sizey=panel.layout.height / height,
                             xanchor="left", yanchor="top", sizing="stretch", layer="below")
        # Hairline above each panel, inset to the same gutter as the charts' text.
        fig.add_shape(type="line", xref="paper", yref="paper", x0=PAD / width, x1=1 - PAD / width,
                      y0=1 - top / height, y1=1 - top / height, line=dict(color=GRID, width=1.5))
        top += panel.layout.height
    fig.update_layout(
        width=width, height=height, margin=dict(t=0, b=0, l=0, r=0), showlegend=False,
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, font=dict(family=FONT, color=INK_2),
        xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1]),
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=28, color=INK),
            subtitle=dict(text=subtitle, font=dict(size=15, color=INK_2)),
            x=PAD / width, xanchor="left", xref="container",
            y=1 - PAD / height, yanchor="top", yref="container",
        ),
    )
    return fig


COMBINED = {
    "combined_for": (
        "America’s Fossil-Fuel Carbon Problem Is Shrinking",
        "CO₂ from burning fossil fuels has fallen since its 2005 peak, and subsidies for coal, the most "
        "carbon-intensive fuel, are shrinking too",
        ["a2_final", "a6_final"],
    ),
    "combined_against": (
        "America’s Fossil-Fuel Carbon Problem Is Still Growing",
        "The fossil-fuel CO₂ behind U.S. imports has more than doubled, and natural gas’s cost, climate "
        "damage included, is outpacing the economy",
        ["b2_final", "b6_final"],
    ),
}

FINALS = {
    "a2_final": ("trade", viz_a2_final),
    "b2_final": ("trade", viz_b2_final),
    "a6_final": ("subsidies", viz_a6_final),
    "b6_final": ("subsidies", viz_b6_final),
}


def main():
    show = "--show" in sys.argv
    data = {"trade": load_trade(), "subsidies": load_subsidies()}
    IMG_DIR.mkdir(exist_ok=True)
    figs = {name: build(data[source]) for name, (source, build) in FINALS.items()}
    for name, (title, subtitle, panels) in COMBINED.items():
        figs[name] = combine(title, subtitle, [figs[p] for p in panels])
    for name, fig in figs.items():
        fig.write_image(IMG_DIR / f"{name}.png", scale=2)
        print(f"  saved final/images/{name}.png")
        if show:
            fig.show()


if __name__ == "__main__":
    main()
