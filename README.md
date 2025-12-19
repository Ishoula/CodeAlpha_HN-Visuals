Hacker News Engagement Dashboard
--------------------------------

Overview:
This project visualizes Hacker News front-page data to summarize engagement patterns.
It shows how votes and comments are distributed among top stories, domains, and engagement levels.

Features:
- Top Stories Votes & Comments: Distribution among top 5 stories.
- Vote Share by Domain: Aggregated votes by website domain.
- Engagement Levels: Categorizes stories as Quiet, Balanced, or Buzzing based on comments per vote.

Usage:
1. Place your dataset as 'hackernews.csv' in the project folder.
2. Install dependencies: pandas, matplotlib, seaborn
   Example: pip install pandas matplotlib seaborn
3. Run the script: python visualize_hn.py
4. The dashboard of pie charts will be displayed.

Dataset Requirements:
Columns: Title, URL, Votes, Comments

Notes:
- Long titles are shortened for readability.
- Legends are used to avoid overlapping labels.
- Percentages are shown inside pie slices for clarity.
