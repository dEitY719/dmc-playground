import dash_mantine_components as dmc


def HomeLayout():
    return dmc.Container(
        [dmc.Title("홈", order=2), dmc.Text("홈페이지에 오신 것을 환영합니다."), dmc.Button("홈 버튼")]
    )
