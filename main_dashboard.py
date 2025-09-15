import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from services_analyzer import ServiceManager, PostAnalyzer
from config_keywords import KEYWORDS, DESIRED_SHEET_HEADERS, RELEVANCE_THRESHOLD, API_RATE_LIMIT_DELAY

class DashboardGenerator:
    """Generates a data dashboard from sheet data."""
    @staticmethod
    def generate(sheets_service, output_filename: str = "gtm_dashboard.png"):
        data = sheets_service.get_all_records()
        if not data:
            print("No data available to generate a dashboard.")
            return

        df = pd.DataFrame(data)
        df['Relevance'] = pd.to_numeric(df['Relevance'], errors='coerce')
        sns.set_style("whitegrid", {'axes.grid': False})
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        fig.suptitle('GTM Automation Bot - Data Analysis Dashboard', fontsize=24, weight='bold')
        palette = "viridis"

        # Plot functions
        sns.countplot(ax=axes[0,0], data=df, y='Intent', hue='Intent', legend=False, palette=palette)
        axes[0,0].set_title('Post Intent Analysis')
        sns.countplot(ax=axes[0,1], data=df, x='Sentiment', hue='Sentiment', legend=False, palette=palette)
        axes[0,1].set_title('Overall Sentiment Breakdown')
        sns.boxplot(ax=axes[1,0], data=df, x='Relevance', y='Intent', hue='Intent', legend=False, palette=palette)
        axes[1,0].set_title('Relevance Score Distribution by Intent')

        if df['Keyword'].nunique() > 1:
            keyword_sentiment = df.groupby(['Keyword','Sentiment']).size().unstack(fill_value=0)
            keyword_sentiment.plot(kind='bar', stacked=True, ax=axes[1,1], color=sns.color_palette(palette, n_colors=df['Sentiment'].nunique()))
            axes[1,1].set_title('Sentiment Breakdown by Keyword')
        else:
            axes[1,1].text(0.5,0.5,'Requires more than one keyword for comparative chart.', horizontalalignment='center', verticalalignment='center')

        plt.tight_layout(rect=[0,0.03,1,0.95])
        plt.savefig(output_filename, dpi=300)
        print(f"Dashboard saved as '{output_filename}'")

def main():
    service_manager = ServiceManager()
    sheets_service = service_manager.sheets
    sheets_service.update('A1:L1', [DESIRED_SHEET_HEADERS])

    for keyword in KEYWORDS:
        for submission in service_manager.reddit.subreddit("all").search(keyword, limit=5):
            analysis = PostAnalyzer.get_analysis(submission.title + " " + submission.selftext, service_manager)
            if analysis and analysis.get("relevance",0) > RELEVANCE_THRESHOLD:
                row = [
                    keyword,
                    submission.title,
                    submission.url,
                    str(submission.author),
                    str(submission.subreddit),
                    time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc)),
                    analysis.get("relevance"),
                    analysis.get("intent"),
                    analysis.get("sentiment"),
                    analysis.get("summary"),
                    analysis.get("suggestion"),
                    ""
                ]
                sheets_service.append_row(row)

                # Slack alert
                message = {
                    "text": f"Highly Relevant Post Found! (Relevance {analysis.get('relevance',0):.2f})",
                    "blocks":[
                        {"type":"header","text":{"type":"plain_text","text":":rotating_light: Highly Relevant Post Found!"}},
                        {"type":"section","fields":[
                            {"type":"mrkdwn","text":f"*Title:*\n<{submission.url}|{submission.title}>"},
                            {"type":"mrkdwn","text":f"*Relevance Score:*\n{analysis.get('relevance',0):.2f}"},
                            {"type":"mrkdwn","text":f"*Sentiment:*\n{analysis.get('sentiment','neutral').capitalize()}"}
                        ]},
                        {"type":"divider"},
                        {"type":"section","text":{"type":"mrkdwn","text":f"*Summary:*\n{analysis.get('summary','No summary available.')}"}},
                        {"type":"section","text":{"type":"mrkdwn","text":f"*Suggested Reply:*\n>{analysis.get('suggestion','Could not analyze.')}"}}
                    ]
                }
                requests.post(service_manager.slack["webhook"], json=message)
            time.sleep(API_RATE_LIMIT_DELAY)

    DashboardGenerator.generate(sheets_service)

if __name__ == '__main__':
    main()
