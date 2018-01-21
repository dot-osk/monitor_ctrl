#!python3
# coding = utf-8

import os
import sys
import logging
import argparse
import vcp

try:
    import tkinter
    from tkinter import ttk
    TK_IMPORTED = True
except ImportError:
    TK_IMPORTED = False


__VERSION__ = '1.0'
__APP_NAME__ = 'monitor_ctrl'
__LOGGING_FORMAT = "%(levelname)s:[%(filename)s:%(lineno)s-%(funcName)s()] %(message)s"

DEFAULT_LOGFILE_PATH = os.path.join(os.environ.get('TEMP', './'), __APP_NAME__, 'log.txt')
_LOGGER = logging.getLogger(__name__)

# -s 参数的分隔符，设置RGB_GAIN的地方需要 eval() 用户输入，使用 [](),等作为分割符会出错
ARG_SPLITTER = ':'

# Application config
APP_OPTIONS = {
    'console': False,
    'setting_values': {},
    'log_file': DEFAULT_LOGFILE_PATH
}

# Win32 _PhysicalMonitorStructure
ALL_MONITORS = []
# vcp.PhyMonitor() instance(s)
ALL_PHY_MONITORS = []


def parse_arg():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='通过DDC/CI设置显示器参数.')
    parser.add_argument('-m', action='store', type=str, default='*', help='指定要应用到的Monitor Model，'
                                                                          '不指定则应用到所有可操作的显示器')
    parser.add_argument('-s', action='store', type=str, help='property1=value1{}property2="value 2" 应用多项设置'
                        .format(ARG_SPLITTER))
    parser.add_argument('-r', action='store_true', default=False, help='将显示器恢复出厂设置')
    parser.add_argument('-t', action='store_true', default=False, help='对输入执行自动调整（仅VGA输入需要）')
    parser.add_argument('-c', action='store_true', default=False, help='不启用GUI')
    parser.add_argument('-l', action='store_true', help='显示可操作的显示器model')
    parser.add_argument('-v', action='store_true', help='Verbose logging')
    opts = parser.parse_args()
    
    global APP_OPTIONS
    APP_OPTIONS['apply_to_model'] = opts.m
    APP_OPTIONS['list_monitors'] = opts.l
    APP_OPTIONS['setting_value_string'] = opts.s
    APP_OPTIONS['restore_factory'] = opts.r
    APP_OPTIONS['perform_auto_setup'] = opts.t
    
    # if specified -c argument or tkinter not imported
    if opts.c or (not TK_IMPORTED):
        APP_OPTIONS['console'] = True
        # log to console
        APP_OPTIONS['log_file'] = None
    else:
        APP_OPTIONS['console'] = False
        # log to file
        APP_OPTIONS['log_file'] = DEFAULT_LOGFILE_PATH
    
    # logging level
    if opts.v:
        APP_OPTIONS['log_level'] = logging.DEBUG
    else:
        APP_OPTIONS['log_level'] = logging.INFO


def set_monitor_attr(object_, attr_name, value) -> bool:
    """
    set attribute of an instance.
    :param object_:
    :param attr_name:
    :param value:
    :return:
    """
    try:
        # convert value type.
        value_type = type(getattr(object_, attr_name))
        if value_type in (list, tuple):
            _LOGGER.debug('eval(): ' + value)
            value = eval(value)
        if value_type in (str, int):
            value = value_type(value)
        
        setattr(object_, attr_name, value)
        _LOGGER.info('OK: {}={}'.format(attr_name, value))
        return True
    except Exception as err:
        _LOGGER.error('Failed: {}={}'.format(attr_name, value))
        _LOGGER.error(err)
        return False


def enum_monitors():
    """
    enumerate all monitor. append to ALL_PHY_MONITORS list
    :return:
    """
    global ALL_PHY_MONITORS
    global ALL_MONITORS
    ALL_MONITORS = vcp.enumerate_monitors()
    for i in ALL_MONITORS:
        try:
            monitor = vcp.PhyMonitor(i)
        except OSError as err:
            _LOGGER.error(err)
            # ignore this monitor
            continue
        _LOGGER.info('Found monitor: ' + monitor.model)
        ALL_PHY_MONITORS.append(monitor)


def parse_settings():
    """
    parse argument passed to "-s"
    format: property=value:property2=value2
    :return:
    """
    settings_str = APP_OPTIONS.get('setting_value_string', '')
    
    settings_dict = {}
    for setting in settings_str.split(ARG_SPLITTER):
        try:
            property_, value = setting.strip().split('=')
            settings_dict[property_] = value
        except ValueError:
            _LOGGER.error('Failed to parse setting: ' + setting)
            continue
    APP_OPTIONS['setting_values'] = settings_dict
    _LOGGER.debug('setting properties: {}'.format(APP_OPTIONS.get('setting_values')))


def apply_all_settings():
    """
    应用命令行指定的操作.
    :return:
    """
    # 过滤不需要操作的显示器
    target_monitor = []
    target_model = APP_OPTIONS.get('apply_to_model', '*').upper()
    
    if target_model == '*':
        target_monitor = ALL_PHY_MONITORS
    else:
        for i in ALL_PHY_MONITORS:
            if i.model.upper() == target_model:
                target_monitor.append(i)
            else:
                _LOGGER.debug('Will NOT apply settings to model: ' + i.model)
    
    for monitor in target_monitor:
        if APP_OPTIONS.get('restore_factory'):
            _LOGGER.info('{}: Reset monitor to factory settings.'.format(monitor.model))
            monitor.reset_factory()
        
        if APP_OPTIONS.get('perform_auto_setup'):
            _LOGGER.info('{}: Perform video auto-setup.'.format(monitor.model))
            monitor.auto_setup_perform()
        
        _LOGGER.info('apply settings to: ' + monitor.model)
        settings = APP_OPTIONS.get('setting_values')
        for i in settings.keys():
            set_monitor_attr(monitor, i, settings.get(i))


def start_gui():
    import tkui
    import threading
    
    app = tkui.TkApp()
    app.title(__APP_NAME__)
    app.status_text_var.set('正在检测显示器...')
    app.add_logfile_button(APP_OPTIONS.get('log_file'))
    
    def background_task():
        enum_monitors()
        _LOGGER.info('start GUI, ignore command line actions.')
        app.status_text_var.set('')
        app.add_monitors_to_tab(ALL_PHY_MONITORS)
    
    threading.Thread(target=background_task, daemon=True).start()
    app.mainloop()


def start_cli():
    enum_monitors()
    
    if APP_OPTIONS.get('list_monitors'):
        for i in ALL_PHY_MONITORS:
            print(i.model)
        sys.exit(0)
    
    apply_all_settings()


if __name__ == '__main__':
    # 接卸命令行参数
    parse_arg()
    
    if APP_OPTIONS.get('log_file'):
        os.makedirs(os.path.dirname(APP_OPTIONS.get('log_file')), exist_ok=True)
    
    logging.basicConfig(filename=APP_OPTIONS['log_file'],
                        level=APP_OPTIONS['log_level'],
                        format=__LOGGING_FORMAT)
    
    if not TK_IMPORTED:
        _LOGGER.warning('Failed to import tkinter, force console mode.')
    
    _LOGGER.debug('parse args done. current config:')
    _LOGGER.debug(APP_OPTIONS)
    
    if APP_OPTIONS.get('console') and \
            (APP_OPTIONS.get('setting_value_string') is None) \
            and (not APP_OPTIONS.get('restore_factory')) \
            and (not APP_OPTIONS.get('list_monitors')) \
            and (not APP_OPTIONS.get('perform_auto_setup')):
        # Nothing to do.
        _LOGGER.warning('Nothing todo. exit.')
        sys.exit(0)
    
    # 解析 -s 参数的值
    if APP_OPTIONS.get('setting_value_string'):
        parse_settings()
    
    if APP_OPTIONS.get('console'):
        start_cli()
    else:
        start_gui()
