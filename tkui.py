#!python3
# coding = utf-8

import tkinter as tk
from tkinter import ttk
import logging
import os

"""
注意： GUI中显示的配置不会自动刷新，要查看新的配置目前需要重启应用程序
"""

_LOGGER = logging.getLogger(__name__)


def _get_attr(object_, property_name):
    try:
        return getattr(object_, property_name)
    except AttributeError as err:
        _LOGGER.error(err)
        return None


def _set_attr(object_, property_name, value):
        try:
            setattr(object_, property_name, value)
        except AttributeError as err:
            _LOGGER.error(err)
 

class PropertySlider(tk.Scale):
    """
    设置数值的滑条控件
    """
    def __init__(self, parent, phy_monitor, property_name: str, max_value=None, **kwargs):
        super(PropertySlider, self).__init__(parent, **kwargs)
        
        self.phy_monitor = phy_monitor
        self.property_name = property_name
        
        # get Max Value
        if max_value:
            self.max_value = max_value
        else:
            _LOGGER.warning("'max_value' not set, set max_value=100")
            self.max_value = 100
        
        self.var = tk.IntVar()
        self.var.set(_get_attr(self.phy_monitor, self.property_name))
        self.configure(orient=tk.HORIZONTAL, from_=0,
                       to=self.max_value,
                       variable=self.var,
                       length=200,
                       showvalue=1)
        
        # 如果让 Widget 的操作即时响应，可能会导致发送vcp指令太频繁而报错，所以在鼠标放开后才设置新的值
        self.bind('<ButtonRelease-1>',
                  lambda event: _set_attr(self.phy_monitor, self.property_name, self.var.get()))


class RGBSlider(ttk.LabelFrame):
    """
    设置RGB均衡的滑条控件
    """
    def __init__(self, parent, phy_monitor, property_name: str, max_value=None, **kwargs):
        super(RGBSlider, self).__init__(parent, **kwargs)
        self.phy_monitor = phy_monitor
        self.property_name = property_name
        
        self.configure(text='RGB 均衡')
        
        # get Max Value
        if max_value:
            self.max_value = max_value
        else:
            _LOGGER.warning("'max_value' not set, set max_value=100")
            self.max_value = 100

        self.r_var = tk.IntVar()
        self.g_var = tk.IntVar()
        self.b_var = tk.IntVar()
        
        current_rgb = _get_attr(self.phy_monitor, self.property_name)
        self.r_var.set(current_rgb[0])
        self.g_var.set(current_rgb[1])
        self.b_var.set(current_rgb[2])

        # UI Init
        self.r_bar = tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=self.max_value, variable=self.r_var,
                              length=200, showvalue=1)
        self.g_bar = tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=self.max_value, variable=self.g_var,
                              length=200, showvalue=1)
        self.b_bar = tk.Scale(self, orient=tk.HORIZONTAL, from_=0, to=self.max_value, variable=self.b_var,
                              length=200, showvalue=1)

        # layout
        ttk.Label(self, text='R:').grid(row=0, column=0, sticky='SW')
        ttk.Label(self, text='G:').grid(row=1, column=0, sticky='SW')
        ttk.Label(self, text='B:').grid(row=2, column=0, sticky='SW')
        self.r_bar.grid(row=0, column=1, sticky='SW')
        self.g_bar.grid(row=1, column=1, sticky='SW')
        self.b_bar.grid(row=2, column=1, sticky='SW')

        self.r_bar.bind('<ButtonRelease-1>', self.__set_rgb)
        self.g_bar.bind('<ButtonRelease-1>', self.__set_rgb)
        self.b_bar.bind('<ButtonRelease-1>', self.__set_rgb)

    def __set_rgb(self, event):
        # get desired RGB
        rgb = self.r_var.get(), self.g_var.get(), self.b_var.get()
        _set_attr(self.phy_monitor, self.property_name, rgb)


class PowerButtonWidget(ttk.Button):
    """
    电源按钮控件
    """
    def __init__(self, parent, phy_monitor, property_name: str, value_list: list, **kwargs):
        super(PowerButtonWidget, self).__init__(parent, **kwargs)
        self.phy_monitor = phy_monitor
        self.property_name = property_name
        self.value_list = value_list
        self.value = tk.StringVar()

        self.value.set(_get_attr(self.phy_monitor, self.property_name))
        self.__current_value_index = self.value_list.index(self.value.get())
        self.configure(textvariable=self.value, command=self.__click_action)

    def __click_action(self):
        self.__current_value_index += 1
        if self.__current_value_index >= len(self.value_list):
            self.__current_value_index = 0
        
        value = self.value_list[self.__current_value_index]
        _set_attr(self.phy_monitor, self.property_name, value)
        self.value.set(value)
        
        
class OptionListWidget(ttk.OptionMenu):
    """
    下拉列表菜单控件
    TODO: 跟踪StringVar的变化，会执行相应的命令，但是会执行两次。
    通过比较当前设置来避免设置两次，但是无效的设置仍然会被执行两次。担心EEPROM的寿命
    """
    def __init__(self, parent, phy_monitor, property_name: str, options_list: list, **kwargs):
        
        self.phy_monitor = phy_monitor
        self.property_name = property_name
        self.options_list = options_list
        self.var = tk.StringVar()
        self.var.set(_get_attr(self.phy_monitor, self.property_name))
        
        super(OptionListWidget, self).__init__(parent, self.var, self.var.get(), *self.options_list, **kwargs)
        # trace Change Event.
        self.var.trace('w', self.__set_value)

    def __set_value(self, *event):
        value = self.var.get()
        old_value = _get_attr(self.phy_monitor, self.property_name)
        if old_value == value:
            logging.info('ignored: update setting: ' + value)
            return
        _set_attr(self.phy_monitor, self.property_name, value)
        

class MonitorTab(ttk.Frame):
    """
    一个显示器实例的Tab
    """
    def __init__(self, parent, phy_monitor, **kwargs):
        super(MonitorTab, self).__init__(parent, **kwargs)
        self.phy_monitor = phy_monitor
        
        self.__init_widgets()
        self.__init_ui()
    
    def __init_widgets(self):
        """
        initialize UI elements.
        :return:
        """
        self.model_name = self.phy_monitor.model
        self.brightness_bar = PropertySlider(self, self.phy_monitor, 'brightness', self.phy_monitor.brightness_max)
        self.contrast_bar = PropertySlider(self, self.phy_monitor, 'contrast', self.phy_monitor.contrast_max)
        self.rgb_slider = RGBSlider(self, self.phy_monitor, 'rgb_gain', self.phy_monitor.rgb_gain_max)
        self.power_button = PowerButtonWidget(self, self.phy_monitor, 'power_mode', self.phy_monitor.power_mode_list)

        self.color_preset_option = OptionListWidget(self, self.phy_monitor,
                                                    'color_preset', self.phy_monitor.color_preset_list)
        self.osd_lang_option = OptionListWidget(self, self.phy_monitor,
                                                'osd_language', self.phy_monitor.osd_languages_list)
        self.input_select_option = OptionListWidget(self, self.phy_monitor,
                                                    'input_src', self.phy_monitor.input_src_list)
        
        self.buttons_frame = ttk.Frame(self)
        self.reset_factory_button = ttk.Button(self.buttons_frame,
                                               text="恢复出厂设置", command=self.phy_monitor.reset_factory)
        self.auto_setup_button = ttk.Button(self.buttons_frame,
                                            text="自动调整", command=self.phy_monitor.auto_setup_perform)
        self.save_nvram_button = ttk.Button(self.buttons_frame, text="保存NVRAM", command=self.phy_monitor.save_nvram)

    def __init_ui(self):
        ttk.Label(self, text='亮度:').grid(row=0, column=0, sticky='SW')
        ttk.Label(self, text='对比度:').grid(row=1, column=0, sticky='SW')
        ttk.Label(self, text='当前电源状态:').grid(row=3, column=0, sticky='SW')
        ttk.Label(self, text='颜色配置文件:').grid(row=4, column=0, sticky='SW')
        ttk.Label(self, text='当前OSD语言:').grid(row=5, column=0, sticky='SW')
        ttk.Label(self, text='输入信号选择:').grid(row=6, column=0, sticky='SW')
        
        self.brightness_bar.grid(row=0, column=1, sticky='W')
        self.contrast_bar.grid(row=1, column=1, sticky='W')
        self.rgb_slider.grid(row=2, column=0, columnspan=2, sticky='WE')
        self.power_button.grid(row=3, column=1, sticky='W')
        self.color_preset_option.grid(row=4, column=1, sticky='W')
        self.osd_lang_option.grid(row=5, column=1, sticky='W')
        self.input_select_option.grid(row=6, column=1, sticky='W')
        self.buttons_frame.grid(row=7, column=0, sticky='W', columnspan=2)
        self.auto_setup_button.grid(row=0, column=0, sticky='W')
        self.reset_factory_button.grid(row=0, column=1, sticky='W')
        self.save_nvram_button.grid(row=0, column=2, sticky='W')


class TkApp(tk.Tk):
    """
    APP
    """
    def __init__(self, *args, **kwargs):
        super(TkApp, self).__init__(*args, **kwargs)
        self.status_text_var = tk.StringVar()
        self.status_text_bar = ttk.Label(self, textvariable=self.status_text_var)
        self.notebook = ttk.Notebook(self)
    
        self.__init_ui()
        
    def __init_ui(self):
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.status_text_bar.grid(row=1, column=0, sticky='SW')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.geometry('300x400')
    
    def add_monitors_to_tab(self, phy_monitor_list: list):
        """
        将PhyMonitor对象添加到NoteBook widget
        :param phy_monitor_list:
        :return:
        """
        for pm in phy_monitor_list:
            widget = MonitorTab(self.notebook, pm)
            self.notebook.add(widget, text=widget.model_name)
        self.status_text_var.set('{} monitor(s) found.'.format(len(phy_monitor_list)))
        
    def add_logfile_button(self, logfile_path: str):
        ttk.Button(self, text='查看日志文件', command=lambda: os.system('explorer /select, "{}"'.format(logfile_path)))\
            .grid(row=1, column=0, sticky='SE')


if __name__ == '__main__':
    # Test Code
    import vcp
    import threading

    logging.basicConfig(level=logging.DEBUG)

    app = TkApp()
    app.title('DDC/CI APP')
    app.status_text_var.set('正在检测显示器...')
    
    def background_task():
        monitors = []
        for i in vcp.enumerate_monitors():
            try:
                monitors.append(vcp.PhyMonitor(i))
            except OSError:
                pass
        app.status_text_var.set(' ')
        app.add_monitors_to_tab(monitors)
        
    threading.Thread(target=background_task, daemon=True).start()
    app.mainloop()
