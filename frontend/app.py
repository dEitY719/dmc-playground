import dash
import dash_mantine_components as dmc
from dash import html

app = dash.Dash(__name__)
app.layout = dmc.MantineProvider(
    children=dmc.Container(
        [
            dmc.Title("Hello DMC world", order=1),
            dmc.Text("Dash Mantine Components 프로젝트 기본 구조"),
            dmc.Button("확인", color="blue"),
        ]
    )
)

if __name__ == "__main__":
    app.run(debug=True)
