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

def get_ga4_report(start_date, end_date, dimensions, metrics, order_by_metric=None, limit=100000):
    """
    Google Analytics 4 のレポートを取得する関数。

    :param start_date: レポートの開始日 (例: "2023-01-01")
    :param end_date: レポートの終了日 (例: "today")
    :param dimensions: 取得したいディメンションのリスト (例: ["pagePath", "pageTitle"])
    :param metrics: 取得したいメトリクスのリスト (例: ["screenPageViews"])
    :param order_by_metric: 並び替えに使用するメトリクス名 (例: "screenPageViews")
    :param limit: 結果の制限数 (デフォルト: 100000)
    :return: レポート結果
    """
    # クライアントの初期化
    client = BetaAnalyticsDataClient.from_service_account_file(KEY_FILE_LOCATION)

    # ディメンションとメトリクスをオブジェクト化
    dimension_objects = [Dimension(name=dim) for dim in dimensions]
    metric_objects = [Metric(name=metric) for metric in metrics]

    # 並び替えの設定
    order_by = None
    if order_by_metric:
        order_by = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True)]

    # レポートリクエストの設定
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=dimension_objects,
        metrics=metric_objects,
        order_bys=order_by,
        limit=limit,
    )

    # レポートの取得
    response = client.run_report(request)
    return response

def format_response_as_json(response):
    """
    レポート結果をJSON形式に整形

    :param response: レポート結果
    :return: JSON形式の文字列
    """
    result = []
    for row in response.rows:
        data = {
            "dimensions": {dim_name: dim_value.value for dim_name, dim_value in zip([dim.name for dim in response.dimension_headers], row.dimension_values)},
            "metrics": {metric_name: metric_value.value for metric_name, metric_value in zip([metric.name for metric in response.metric_headers], row.metric_values)}
        }
        result.append(data)
    return json.dumps(result, indent=4, ensure_ascii=False)

def main():
    # 任意の引数を指定してレポートを取得
    start_date = "2023-01-01"
    end_date = "today"
    dimensions = ["pagePath", "pageTitle", "city", "country", "browser", "operatingSystem", "deviceCategory"]
    metrics = ["screenPageViews", "sessions", "totalUsers", "newUsers", "bounceRate", "averageSessionDuration"]
    order_by_metric = "screenPageViews"
    limit = 100000

    response = get_ga4_report(start_date, end_date, dimensions, metrics, order_by_metric, limit)
    json_result = format_response_as_json(response)
    print(json_result)

if __name__ == "__main__":
    main()
