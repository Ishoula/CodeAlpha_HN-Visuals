from __future__ import annotations

from pathlib import Path
from textwrap import shorten
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _short_titles(series: pd.Series, width: int = 45) -> pd.Series:
    """Return abbreviated titles for tidy plotting."""
    return series.apply(lambda title: shorten(str(title), width=width, placeholder="…"))


def _aggregate_top_share(
    df: pd.DataFrame,
    value_col: str,
    label_col: str,
    top_n: int = 5,
    other_label: str = "Other"
) -> tuple[list[str], list[float]]:
    ordered = df.sort_values(value_col, ascending=False)[[label_col, value_col]].copy()
    top = ordered.head(top_n).copy()
    remainder = ordered[value_col].sum() - top[value_col].sum()
    if remainder > 0:
        top = pd.concat(
            [
                top,
                pd.DataFrame({label_col: [other_label], value_col: [remainder]}),
            ],
            ignore_index=True,
        )
    return top[label_col].tolist(), top[value_col].astype(float).tolist()


def _plot_pie(ax: plt.Axes, labels: list[str], sizes: list[float], palette: str, title: str) -> None:
    colors = sns.color_palette(palette, n_colors=len(sizes))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        startangle=90,
        autopct=lambda pct: f"{pct:.1f}%",
        pctdistance=0.75,
        textprops={"fontsize": 9},
        wedgeprops={"edgecolor": "white", "linewidth": 1.0},
    )
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax.set_title(title, fontweight="bold")
    ax.axis("equal")


def load_hackernews(data_path: Path) -> pd.DataFrame:
    df = pd.read_csv(data_path)
    df[["Votes", "Comments"]] = df[["Votes", "Comments"]].apply(
        pd.to_numeric, errors="coerce"
    )
    return df.dropna(subset=["Votes", "Comments"])


def plot_visualizations(df: pd.DataFrame) -> None:
    """Create a dashboard of pie charts summarizing Hacker News engagement."""
    sns.set_theme(style="whitegrid", context="notebook")
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))
    ax_votes, ax_comments, ax_domains, ax_ratio = axes.flatten()

    df = df.copy()
    df["TitleShort"] = _short_titles(df["Title"], width=40)

    # Pie 1: Vote share of top stories
    vote_labels, vote_sizes = _aggregate_top_share(
        df, value_col="Votes", label_col="TitleShort", top_n=5, other_label="Other stories"
    )
    _plot_pie(ax_votes, vote_labels, vote_sizes, palette="crest", title="Vote Share (Top Stories)")

    # Pie 2: Comment share of top stories
    comment_labels, comment_sizes = _aggregate_top_share(
        df, value_col="Comments", label_col="TitleShort", top_n=5, other_label="Other stories"
    )
    _plot_pie(ax_comments, comment_labels, comment_sizes, palette="rocket", title="Comment Share (Top Stories)")

    # Pie 3: Vote share by domain
    df["Domain"] = df["URL"].apply(lambda url: urlparse(str(url)).netloc or "Unknown")
    domain_votes = df.groupby("Domain", as_index=False)["Votes"].sum()
    domain_labels, domain_sizes = _aggregate_top_share(
        domain_votes, value_col="Votes", label_col="Domain", top_n=6, other_label="Other domains"
    )
    _plot_pie(ax_domains, domain_labels, domain_sizes, palette="mako", title="Vote Share by Domain")

    # Pie 4: Engagement levels based on comments per vote
    engagement = df.assign(
        EngagementRatio=df["Comments"] / df["Votes"].replace({0: pd.NA})
    ).dropna(subset=["EngagementRatio"])
    if engagement.empty:
        ax_ratio.text(0.5, 0.5, "No engagement data", ha="center", va="center", fontsize=10)
        ax_ratio.axis("off")
    else:
        engagement_bins = pd.cut(
            engagement["EngagementRatio"],
            bins=[0, 0.5, 1.0, float("inf")],
            labels=["Quiet (<0.5)", "Balanced (0.5-1.0)", "Buzzing (>1.0)"],
            include_lowest=True,
        )
        bucket_counts = engagement_bins.value_counts().sort_index()
        ratio_labels = bucket_counts.index.tolist()
        ratio_sizes = bucket_counts.values.astype(float).tolist()
        _plot_pie(ax_ratio, ratio_labels, ratio_sizes, palette="Spectral", title="Engagement Levels")

    fig.suptitle(
        "Hacker News Engagement Snapshot",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    plt.show()


def main() -> None:
    data_path = Path(__file__).with_name("hackernews.csv")

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = load_hackernews(data_path)

    if df.empty:
        raise ValueError("Dataset contains no valid numeric rows.")

    plot_visualizations(df)


if __name__ == "__main__":
    main()
