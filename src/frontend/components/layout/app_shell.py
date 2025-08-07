import dash_mantine_components as dmc
from dash.development.base_component import Component

def AppShellExample() -> Component:
    return dmc.Title("AppShell 예시", order=2)
