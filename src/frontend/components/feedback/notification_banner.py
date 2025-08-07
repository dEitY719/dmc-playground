import dash_mantine_components as dmc
from dash.development.base_component import Component

def NotificationBannerExample() -> Component:
    return dmc.Alert("알림 배너 예시", color="blue", title="알림")
