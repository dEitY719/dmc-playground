#!/bin/bash

source ~/.bashrc

log_info "Start create dmc project structure..."
# 안내 메시지
log_dim "[1/3] 현재 디렉토리 하위에 Dash DMC 프로젝트 폴더 구조를 생성합니다."

# 폴더 구조 생성
mkdir -p backend
mkdir -p frontend/config
mkdir -p frontend/assets/css
mkdir -p frontend/assets/js
mkdir -p frontend/assets/images
mkdir -p frontend/components/theming
mkdir -p frontend/components/layout
mkdir -p frontend/components/inputs
mkdir -p frontend/components/combobox
mkdir -p frontend/components/buttons
mkdir -p frontend/components/navigation
mkdir -p frontend/components/feedback
mkdir -p frontend/components/overlay
mkdir -p frontend/components/data-display
mkdir -p frontend/components/typography
mkdir -p frontend/components/miscellaneous
mkdir -p frontend/components/date-pickers
mkdir -p frontend/components/charts
mkdir -p frontend/pages/home
mkdir -p frontend/pages/dashboard
mkdir -p frontend/themes
mkdir -p frontend/utils
mkdir -p frontend/services
mkdir -p tests/backend
mkdir -p tests/frontend
mkdir -p tests/integration

# 세부 컴포넌트 폴더 추가 생성
log_dim "[2/3] components 디렉토리 하위에 {inputs, combobox, buttons, ...} 폴더들을 생성합니다."
mkdir -p frontend/components/theming/{mantine-provider,theme-object,css-variables,colors,typography,styles-api,style-props,responsive-styles,theme-switch-components,plotly-figure-templates}
mkdir -p frontend/components/layout/{app-shell,aspect-ratio,center,container,flex,grid,group,simple-grid,space,stack}
mkdir -p frontend/components/inputs/{check-box,chip,color-input,color-picker,fieldset,input-wrapper,json-input,number-input,password-input,pin-input,radio-group,rating,rich-text-editor,segmented-control,slider,switch,text-input,text-area}
mkdir -p frontend/components/combobox/{multi-select,select,tags-input}
mkdir -p frontend/components/buttons/{action-icon,button}
mkdir -p frontend/components/navigation/{anchor,breadcrumbs,burger,navlink,pagination,stepper,tabs,tree}
mkdir -p frontend/components/feedback/{alert,loader,loading-overlay,notification,progress,ring-progress,semi-circle-progress,skeleton}
mkdir -p frontend/components/overlay/{affix,drawer,hover-card,menu,modal,popover,tooltip}
mkdir -p frontend/components/data-display/{accordion,avatar,badge,card,carousel,image,indicator,kbd,number-formatter,spoiler,theme-icon,timeline}
mkdir -p frontend/components/typography/{blockquote,code,code-highlight,list,mark,table,text,title,typography-styles-provider}
mkdir -p frontend/components/miscellaneous/{box,collapse,divider,paper,scroll-area,visually-hidden}
mkdir -p frontend/components/date-pickers/{date-input,date-picker,date-picker-input,date-time-picker,date-provider,month-picker-input,time-grid,time-input,time-picker,year-picker-input}
mkdir -p frontend/components/charts/{area-chart,bar-chart,bubble-chart,composite-chart,donut-chart,line-chart,pie-chart,radar-chart,scatter-chart,sparkline}

# 기본 .py 파일 생성 및 예제 코드 삽입
log_dim "[3/3] 기본 .py 파일 생성 및 예제 코드를 삽입합니다."
touch frontend/components/theming/__init__.py
cat <<EOF >frontend/components/theming/theme_provider.py
import dash_mantine_components as dmc

def ThemeProviderExample():
    return dmc.Text('ThemeProvider 예시')
EOF

touch frontend/components/layout/__init__.py
cat <<EOF >frontend/components/layout/app_shell.py
import dash_mantine_components as dmc

def AppShellExample():
    return dmc.Title('AppShell 예시', order=2)
EOF

touch frontend/components/inputs/__init__.py
cat <<EOF >frontend/components/inputs/text_input.py
import dash_mantine_components as dmc

def TextInputExample():
    return dmc.Text('TextInput 예시')
EOF

touch frontend/components/combobox/__init__.py
cat <<EOF >frontend/components/combobox/select_box.py
import dash_mantine_components as dmc

def SelectBoxExample():
    return dmc.Text('SelectBox 예시')
EOF

touch frontend/components/buttons/__init__.py
cat <<EOF >frontend/components/buttons/custom_button.py
import dash_mantine_components as dmc

def CustomButtonExample():
    return dmc.Button('커스텀 버튼')
EOF

touch frontend/components/navigation/__init__.py
cat <<EOF >frontend/components/navigation/sidebar.py
import dash_mantine_components as dmc

def SidebarExample():
    return dmc.Text('Sidebar 예시')
EOF

touch frontend/components/feedback/__init__.py
cat <<EOF >frontend/components/feedback/notification_banner.py
import dash_mantine_components as dmc

def NotificationBannerExample():
    return dmc.Alert('알림 배너 예시', color='blue', title='알림')
EOF

touch frontend/components/overlay/__init__.py
cat <<EOF >frontend/components/overlay/modal.py
import dash_mantine_components as dmc

def ModalExample():
    return dmc.Text('Modal 예시')
EOF

touch frontend/components/data-display/__init__.py
cat <<EOF >frontend/components/data-display/custom_table.py
import dash_mantine_components as dmc

def CustomTableExample():
    return dmc.Text('CustomTable 예시')
EOF

touch frontend/components/typography/__init__.py
cat <<EOF >frontend/components/typography/title_text.py
import dash_mantine_components as dmc

def TitleTextExample():
    return dmc.Title('TitleText 예시', order=3)
EOF

touch frontend/components/miscellaneous/__init__.py
cat <<EOF >frontend/components/miscellaneous/color_swatch.py
import dash_mantine_components as dmc

def ColorSwatchExample():
    return dmc.Text('ColorSwatch 예시')
EOF

touch frontend/components/date-pickers/__init__.py
cat <<EOF >frontend/components/date-pickers/date_picker.py
import dash_mantine_components as dmc

def DatePickerExample():
    return dmc.Text('DatePicker 예시')
EOF

touch frontend/components/charts/__init__.py
cat <<EOF >frontend/components/charts/bar_chart.py
import dash_mantine_components as dmc

def BarChartExample():
    return dmc.Text('BarChart 예시')
EOF

cat <<EOF >frontend/app.py
import dash
import dash_mantine_components as dmc
from dash import html

app = dash.Dash(__name__)
app.layout = dmc.MantineProvider(
    children=dmc.Container([
        dmc.Title('Hello DMC world', order=1),
        dmc.Text('Dash Mantine Components 프로젝트 기본 구조'),
        dmc.Button('확인', color='blue')
    ])
)

if __name__ == "__main__":
    app.run_server(debug=True)
EOF

cat <<EOF >frontend/index.py
# index.py - 엔트리 포인트 예시
from .app import app

if __name__ == "__main__":
    app.run_server(debug=True)
EOF

cat <<EOF >frontend/config/settings.py
# 환경설정 예시
DEBUG = True
EOF

touch frontend/config/__init__.py

touch frontend/assets/css/.gitkeep
mkdir -p frontend/assets/js
mkdir -p frontend/assets/images

cat <<EOF >frontend/pages/home/layout.py
import dash_mantine_components as dmc

def HomeLayout():
    return dmc.Container([
        dmc.Title('홈', order=2),
        dmc.Text('홈페이지에 오신 것을 환영합니다.'),
        dmc.Button('홈 버튼')
    ])
EOF

touch frontend/pages/home/__init__.py

touch frontend/pages/home/callbacks.py

cat <<EOF >frontend/pages/dashboard/layout.py
import dash_mantine_components as dmc

def DashboardLayout():
    return dmc.Container([
        dmc.Title('대시보드', order=2),
        dmc.Text('대시보드 페이지입니다.'),
        dmc.Button('대시보드 버튼')
    ])
EOF

touch frontend/pages/dashboard/__init__.py

touch frontend/pages/dashboard/callbacks.py

cat <<EOF >frontend/themes/main_theme.py
# DMC 테마 예시
theme = {
    "primaryColor": "blue",
    "fontFamily": "Inter, sans-serif"
}
EOF

touch frontend/themes/__init__.py

cat <<EOF >frontend/utils/data_utils.py
# 데이터 유틸리티 예시
def get_data():
    return [1, 2, 3]
EOF

cat <<EOF >frontend/utils/validation_utils.py
# 검증 유틸리티 예시
def is_valid(x):
    return x is not None
EOF

touch frontend/utils/__init__.py

cat <<EOF >frontend/services/data_service.py
# 데이터 서비스 예시
def fetch_data():
    return {"result": "ok"}
EOF

touch frontend/services/__init__.py

cat <<EOF >frontend/requirements.txt
dash
dash-mantine-components
EOF

touch frontend/Dockerfile

touch frontend/.env

touch frontend/.pylintrc

touch frontend/pyproject.toml

touch frontend/README.md

log_info "완료! 현재 디렉토리 하위에 DMC 폴더 구조가 생성되었습니다."
