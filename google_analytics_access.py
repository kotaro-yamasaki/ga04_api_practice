import json
import os
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, OrderBy

# .envファイルをロード
load_dotenv()

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_path:
    # 環境変数の値を使用
    print(f"Google Cloud Credentials Path: {credentials_path}")
else:
    print("環境変数 'GOOGLE_APPLICATION_CREDENTIALS' が設定されていません。")
# サービスアカウントJSONファイルのパス
KEY_FILE_LOCATION = "phasealterbooth-testblog-c1de7f239fe4.json"
# GA4のプロパティID
PROPERTY_ID = "469101596"

def get_ga4_report():
    # クライアントの初期化
    client = BetaAnalyticsDataClient.from_service_account_file(KEY_FILE_LOCATION)

    # レポートリクエストの設定
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=10,
    )

    # レポートの取得
    response = client.run_report(request)
    return response

def format_response_as_json(response):
    # レポート結果をJSON形式に整形
    result = []
    for row in response.rows:
        data = {
            "dimensions": {dim_name: dim_value.value for dim_name, dim_value in zip(["pagePath", "pageTitle"], row.dimension_values)},
            "metrics": {metric_name: metric_value.value for metric_name, metric_value in zip(["screenPageViews"], row.metric_values)}
        }
        result.append(data)
    return json.dumps(result, indent=4, ensure_ascii=False)


def main():
    response = get_ga4_report()
    json_result = format_response_as_json(response)
    print(json_result)

if __name__ == "__main__":
    main()
