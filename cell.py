# test.py  ——  带标题 + 防遮挡的基站查询
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.core.text import LabelBase
from pathlib import Path
import pandas as pd

Window.size = (360, 640)

# 中文字体
font_path = Path(__file__).with_name('NotoSansCJK-Regular.otf')
if not font_path.exists():
    font_path = Path(__file__).with_name('msyh.ttc')
if font_path.exists():
    LabelBase.register(name='CJK', fn_regular=str(font_path))

KV = '''
<RootWidget>:
    BoxLayout:
        orientation: 'vertical'
        padding: 4
        spacing: 2

        # 标题
        Label:
            text: '基站信息查询'
            font_name: 'CJK'
            font_size: 18
            size_hint_y: None
            height: 30
            color: 1, 1, 1, 1
            canvas.before:
                Color:
                    rgba: 0.2, 0.4, 0.7, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        # 搜索框
        TextInput:
            id: search_input
            hint_text: "输入任意列关键字"
            font_name: 'CJK'
            font_size: 14
            height: 36
            size_hint_y: None
            multiline: False
            on_text: root.do_filter(self.text)

        # 内容区（套 ScrollView 防遮挡）
        ScrollView:
            RecycleView:
                id: rv
                viewclass: 'SelectableLabel'
                RecycleBoxLayout:
                    default_size: None, dp(160)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'

<SelectableLabel@Label>:
    markup: True
    color: 0, 0, 0, 1
    font_name: 'CJK'
    font_size: 13
    text_size: self.width - 6, None
    halign: 'left'
    valign: 'top'
    canvas.before:
        Color:
            rgba: 0.96, 0.96, 0.96, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''


class RootWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        csv_path = Path(__file__).with_name('site.csv')
        if not csv_path.exists():
            raise RuntimeError(f"找不到数据文件: {csv_path}")

        try:
            self.df = pd.read_csv(csv_path, dtype=str, encoding='utf-8-sig').fillna('')
        except UnicodeDecodeError:
            self.df = pd.read_csv(csv_path, dtype=str, encoding='gb18030').fillna('')
        self.df.columns = [c.strip().strip('"').strip("'") for c in self.df.columns]

        self.all_data = self.df.to_dict('records')
        self.display_data(self.all_data)

    def display_data(self, records):
        rows = []
        for r in records:
            txt = '\n'.join([f"{k}: {v}" for k, v in r.items()])
            rows.append({'text': txt})
        self.ids.rv.data = rows

    def do_filter(self, text: str):
        text = text.strip().lower()
        if not text:
            filtered = self.all_data
        else:
            filtered = [
                r for r in self.all_data
                if any(text in str(v).lower() for v in r.values())
            ]
        self.display_data(filtered)


class SiteApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()


if __name__ == '__main__':
    SiteApp().run()