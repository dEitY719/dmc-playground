import dash_mantine_components as dmc


def DashboardLayout():
    return dmc.Container(
        [dmc.Title("대시보드", order=2), dmc.Text("대시보드 페이지입니다."), dmc.Button("대시보드 버튼")]
    )
