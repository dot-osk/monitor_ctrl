# coding = utf-8

import sys
import logging
import ctypes
from ctypes import wintypes
import vcp_code
from typing import Tuple

_LOGGER = logging.getLogger(__name__)

"""

# Reference
[High-Level Monitor API](https://msdn.microsoft.com/en-us/library/vs/alm/dd692964(v=vs.85).aspx)
[Low-Level Monitor Configuration](https://msdn.microsoft.com/en-us/library/windows/desktop/dd692982(v=vs.85).aspx)

[Monitor Control Command Set](https://en.wikipedia.org/wiki/Monitor_Control_Command_Set)
https://milek7.pl/ddcbacklight/mccs.pdf

"""


# #################################### Use Windows API to enumerate monitors
def _get_physical_monitors_from_hmonitor(hmonitor: wintypes.HMONITOR) -> list:
    """
    Retrieves the physical monitors associated with an HMONITOR monitor handle

    https://msdn.microsoft.com/en-us/library/vs/alm/dd692950(v=vs.85).aspx
    BOOL GetPhysicalMonitorsFromHMONITOR(
        _In_   HMONITOR hMonitor,
        _In_   DWORD dwPhysicalMonitorArraySize,
        _Out_  LPPHYSICAL_MONITOR pPhysicalMonitorArray
    );
    
    Retrieves the number of physical monitors associated with an HMONITOR monitor handle.
    Call this function before calling GetPhysicalMonitorsFromHMONITOR.
    https://msdn.microsoft.com/en-us/library/dd692948(v=vs.85).aspx
    BOOL GetNumberOfPhysicalMonitorsFromHMONITOR(
        _In_   HMONITOR hMonitor,
        _Out_  LPDWORD pdwNumberOfPhysicalMonitors
    );

    :param hmonitor:
    :return:

    """
    class _PhysicalMonitorStructure(ctypes.Structure):
        """
        PHYSICAL_MONITOR Structure.
        https://msdn.microsoft.com/en-us/library/vs/alm/dd692967(v=vs.85).aspx
        typedef struct _PHYSICAL_MONITOR {
            HANDLE hPhysicalMonitor;
            WCHAR  szPhysicalMonitorDescription[PHYSICAL_MONITOR_DESCRIPTION_SIZE];
        } PHYSICAL_MONITOR, *LPPHYSICAL_MONITOR;

        PHYSICAL_MONITOR_DESCRIPTION_SIZE = 128
        """
        _fields_ = [
            ("hPhysicalMonitor", wintypes.HANDLE),
            ("szPhysicalMonitorDescription", wintypes.WCHAR * 128)
        ]

    # Retrieves the number of physical monitors
    phy_monitor_number = wintypes.DWORD()
    api_call_get_number = ctypes.windll.Dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR
    if not api_call_get_number(hmonitor, ctypes.byref(phy_monitor_number)):
        _LOGGER.error(ctypes.WinError())
        return []
    
    # Retrieves the physical monitors
    api_call_get_monitor = ctypes.windll.Dxva2.GetPhysicalMonitorsFromHMONITOR
    # create array
    phy_monitor_array = (_PhysicalMonitorStructure * phy_monitor_number.value)()
    if not api_call_get_monitor(hmonitor, phy_monitor_number, phy_monitor_array):
        _LOGGER.error(ctypes.WinError())
        return []
    
    return list(phy_monitor_array)


def enumerate_monitors() -> list:
    """
    enumerate all physical monitor.
    ** 请注意防止返回的 Handle 对象被GC!
    
    https://msdn.microsoft.com/en-us/library/dd162610(v=vs.85).aspx
    BOOL EnumDisplayMonitors(
        _In_ HDC             hdc,
        _In_ LPCRECT         lprcClip,
        _In_ MONITORENUMPROC lpfnEnum,
        _In_ LPARAM          dwData
    );
    
    :return: list contains physical monitor handles
    """
    all_hmonitor = []

    # Factory function of EnumDisplayMonitors callback.
    # 保持引用以防止被GC !
    # https://msdn.microsoft.com/en-us/library/dd145061(v=vs.85).aspx
    _MONITOR_ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL,
                                            wintypes.HMONITOR,
                                            wintypes.HDC,
                                            ctypes.POINTER(wintypes.LPRECT),
                                            wintypes.LPARAM)

    def __monitor_enum_proc_callback(hmonitor_: wintypes.HMONITOR, hdc, lprect, lparam) -> bool:
        """
        EnumDisplayMonitors callback, append HMONITOR to all_hmonitor list.
        :param hmonitor_:
        :param hdc:
        :param lprect:
        :param lparam:
        :return:
        """
        all_hmonitor.append(hmonitor_)
        return True
    
    if not ctypes.windll.user32.EnumDisplayMonitors(None, None,
                                                    _MONITOR_ENUM_PROC(__monitor_enum_proc_callback), None):
            raise ctypes.WinError()
    
    # get physical monitor handle
    handles = []
    for hmonitor in all_hmonitor:
        handles.extend(_get_physical_monitors_from_hmonitor(hmonitor))
    
    return handles


class PhyMonitor(object):
    """
    一个物理显示器的VCP控制class，封装常用操作.
    """
    def __init__(self, phy_monitor):
        self._phy_monitor = phy_monitor
        self._phy_monitor_handle = self._phy_monitor.hPhysicalMonitor
        # VCP Capabilities String
        self._caps_string = ''
        # Monitor model name
        self.model = ''
        self.info_display_type = ''
        
        self._get_monitor_caps()
        if self._caps_string != '':
            self._get_model_info()

    def _get_monitor_caps(self):
        """
        https://msdn.microsoft.com/en-us/library/windows/desktop/dd692938(v=vs.85).aspx
        BOOL GetCapabilitiesStringLength(
            _In_   HANDLE hMonitor,
            _Out_  LPDWORD pdwCapabilitiesStringLengthInCharacters
        );
        
        https://msdn.microsoft.com/en-us/library/windows/desktop/dd692934(v=vs.85).aspx
        BOOL CapabilitiesRequestAndCapabilitiesReply(
            _In_   HANDLE hMonitor,
            _Out_  LPSTR pszASCIICapabilitiesString,
            _In_   DWORD dwCapabilitiesStringLengthInCharacters
        );
        :return:
        """
        
        caps_string_length = wintypes.DWORD()
        if not ctypes.windll.Dxva2.GetCapabilitiesStringLength(self._phy_monitor_handle,
                                                               ctypes.byref(caps_string_length)):
            _LOGGER.error(ctypes.WinError())
            raise ctypes.WinError()
        
        caps_string = (ctypes.c_char * caps_string_length.value)()
        if not ctypes.windll.Dxva2.CapabilitiesRequestAndCapabilitiesReply(
                self._phy_monitor_handle, caps_string, caps_string_length):
                _LOGGER.error(ctypes.WinError())
                return
        
        self._caps_string = caps_string.value.decode('ASCII')
    
    def _get_model_info(self):
        """
        analyze caps string
        :return:
        """
        def find_(src: str, start_: str, end_: str) -> str:
            """
            查找 start_ 和 end_ 之间包围的内容
            :param src: 待寻找的支付串
            :param start_:
            :param end_:
            :return:
            """
            start_index = src.find(start_)
            if start_index == -1:
                # not found
                return ''
            start_index = start_index + len(start_)
            
            end_index = src.find(end_, start_index)
            if end_index == -1:
                return ''
            return src[start_index:end_index]
        
        model = find_(self._caps_string, 'model(', ')')
        if model == '':
            _LOGGER.warning('unable to find model info in vcp caps string: {}'.format(self._caps_string))
        self.model = model

        info_display_type = find_(self._caps_string, 'type(', ')')
        if info_display_type == '':
            _LOGGER.warning('unable to find display type info in vcp caps string: {}'.format(self._caps_string))
        self.info_display_type = info_display_type
        
    def close(self):
        """
        Close WinAPI Handle.
        
        https://msdn.microsoft.com/en-us/library/windows/desktop/dd692936(v=vs.85).aspx
        BOOL DestroyPhysicalMonitor(
            _In_  HANDLE hMonitor
        );
        :return:
        """
        import ctypes
        api_call = ctypes.windll.Dxva2.DestroyPhysicalMonitor
        
        if not api_call(self._phy_monitor_handle):
            _LOGGER.error(ctypes.WinError())
    
    # ########################## 发送/读取 VCP 设置的函数
    
    def send_vcp_code(self, code: int, value: int) -> bool:
        """
        send vcp code to monitor.
        
        https://msdn.microsoft.com/en-us/library/dd692979(v=vs.85).aspx
        BOOL SetVCPFeature(
            _In_  HANDLE hMonitor,
            _In_  BYTE bVCPCode,
            _In_  DWORD dwNewValue
        );
        
        :param code: VCP Code
        :param value: Data
        :return: Win32 API return
        """
        if code is None:
            _LOGGER.error('vcp code to send is None. ignored.')
            return False
        
        api_call = ctypes.windll.Dxva2.SetVCPFeature
        code = wintypes.BYTE(code)
        new_value = wintypes.DWORD(value)
        api_call.restype = ctypes.c_bool
        ret_ = api_call(self._phy_monitor_handle, code, new_value)
        if not ret_:
            _LOGGER.error('send vcp command failed: ' + hex(code))
            _LOGGER.error(ctypes.WinError())
        return ret_
    
    def read_vcp_code(self, code: int) -> Tuple[int, int]:
        """
        send vcp code to monitor, get current value and max value.
        
        https://msdn.microsoft.com/en-us/library/dd692953(v=vs.85).aspx
        BOOL GetVCPFeatureAndVCPFeatureReply(
            _In_   HANDLE hMonitor,
            _In_   BYTE bVCPCode,
            _Out_  LPMC_VCP_CODE_TYPE pvct,
            _Out_  LPDWORD pdwCurrentValue,
            _Out_  LPDWORD pdwMaximumValue
        );
        
        :param code: VCP Code
        :return: current_value, max_value
        """
        if code is None:
            _LOGGER.error('vcp code to send is None. ignored.')
            return 0, 0
        
        api_call = ctypes.windll.Dxva2.GetVCPFeatureAndVCPFeatureReply
        api_in_vcp_code = wintypes.BYTE(code)
        api_out_current_value = wintypes.DWORD()
        api_out_max_value = wintypes.DWORD()
        
        if not api_call(self._phy_monitor_handle, api_in_vcp_code, None,
                        ctypes.byref(api_out_current_value), ctypes.byref(api_out_max_value)):
            _LOGGER.error('get vcp command failed: ' + hex(code))
            _LOGGER.error(ctypes.WinError())
        return api_out_current_value.value, api_out_max_value.value
        
    def set_vcp_value_by_name(self, vcp_code_key: str, value: int) -> bool:
        """
        根据功能名称发送vcp code和数据
        :param vcp_code_key: key name of vcp_code.VCP_CODE dict
        :param value: new value
        :return:
        """
        return self.send_vcp_code(vcp_code.VCP_CODE.get(vcp_code_key), value)
    
    def get_vcp_value_by_name(self, vcp_code_key: str) -> Tuple[int, int]:
        """
        根据功能名称读取vcp code的值和最大值
        :param vcp_code_key: key name of vcp_code.VCP_CODE dict
        :return: current_value, max_value
        """
        return self.read_vcp_code(vcp_code.VCP_CODE.get(vcp_code_key))
    
    # ########################### 经过包装后方便调用的属性/方法
    
    def reset_factory(self):
        """
        Reset monitor to factory defaults
        :return:
        """
        self.set_vcp_value_by_name('Restore Factory Defaults', 1)
    
    @property
    def color_temperature(self):
        increment = self.get_vcp_value_by_name('User Color Temperature Increment')[0]
        current = self.get_vcp_value_by_name('User Color Temperature')[0]
        return 3000 + current * increment
    
    @color_temperature.setter
    def color_temperature(self, value: int):
        increment = self.get_vcp_value_by_name('User Color Temperature Increment')[0]
        new_value = (value - 3000) // increment
        self.set_vcp_value_by_name('User Color Temperature', new_value)
    
    @property
    def brightness_max(self):
        return self.get_vcp_value_by_name('Luminance')[1]
    
    @property
    def brightness(self):
        return self.get_vcp_value_by_name('Luminance')[0]
    
    @brightness.setter
    def brightness(self, value):
        """
        设置亮度
        :param value:
        :return:
        """
        brightness_max = self.brightness_max
        if value < 0 or value > brightness_max:
            _LOGGER.warning('invalid brightness level: {}, allowed: 0-{}'.format(
                value, brightness_max))
            return
        self.set_vcp_value_by_name('Luminance', value)

    @property
    def contrast_max(self):
        return self.get_vcp_value_by_name('Contrast')[1]
    
    @property
    def contrast(self):
        return self.get_vcp_value_by_name('Contrast')[0]
    
    @contrast.setter
    def contrast(self, value):
        contrast_max = self.contrast_max
        if value < 0 or value > contrast_max:
            _LOGGER.warning('invalid contrast level: {}, allowed: 0-{}'.format(
                value, contrast_max))
            return
        self.set_vcp_value_by_name('Contrast', value)
    
    @property
    def color_preset_list(self) -> list:
        """
        可用的color preset, 显示器不一定全部支持
        :return:
        """
        return list(vcp_code.COLOR_PRESET_CODE.keys())
    
    @property
    def color_preset(self) -> str:
        """
        当前的color preset
        :return:
        """
        preset = self.get_vcp_value_by_name('Select Color Preset')[0]
        for i in list(vcp_code.COLOR_PRESET_CODE.keys()):
            if vcp_code.COLOR_PRESET_CODE[i] == preset:
                return i
        return ''
    
    @color_preset.setter
    def color_preset(self, preset: str):
        if preset not in self.color_preset_list:
            _LOGGER.warning('invalid color preset: {}, available:{}'.format(
                preset, self.color_preset_list))
            return
        self.set_vcp_value_by_name('Select Color Preset', vcp_code.COLOR_PRESET_CODE.get(preset))
    
    @property
    def rgb_gain_max(self):
        """
        最大允许设置的RGB值
        ! 只取红色的RGB最大值作为3个颜色的参考
        :return:
        """
        return self.get_vcp_value_by_name('Video Gain Red')[1]
    
    @property
    def rgb_gain(self) -> Tuple[int, int, int]:
        """
        
        :return:  Red, Green, Blue
        """
        rg = self.get_vcp_value_by_name('Video Gain Red')[0]
        gg = self.get_vcp_value_by_name('Video Gain Green')[0]
        bg = self.get_vcp_value_by_name('Video Gain Blue')[0]
        return rg, gg, bg
    
    @rgb_gain.setter
    def rgb_gain(self, value_pack):
        max_ = self.rgb_gain_max
        
        # 检查传入参数
        def check_input(value) -> bool:
            """
            检查传入的RGB gain
            :param value:
            :return:
            """
            if value < 0 or value > max_:
                _LOGGER.warning('invalid RGB value: {}, allowed: 0-{}'.format(
                    value, max_))
                return False
            return True
        try:
            rg = value_pack[0]
            gg = value_pack[1]
            bg = value_pack[2]
        except Exception as err:
            _LOGGER.error(err)
            return
        if not (check_input(rg) and check_input(gg) and check_input(bg)):
            return
        # 设置 RGB Gain
        self.set_vcp_value_by_name('Video Gain Red', rg)
        self.set_vcp_value_by_name('Video Gain Green', gg)
        self.set_vcp_value_by_name('Video Gain Blue', bg)
    
    def auto_setup_perform(self):
        """
        执行自动调整
        :return:
        """
        self.set_vcp_value_by_name('Auto Setup', vcp_code.AUTO_SETUP_CODE.get('Manual Perform'))
    
    @property
    def info_poweron_hours(self):
        """
        返回显示器的开机时间 (Hours)
        :return:
        """
        return self.get_vcp_value_by_name('Display Usage Time')[0]
    
    @property
    def osd_languages_list(self) -> list:
        """
        VCP 中指定的语言列表
        :return:
        """
        return list(vcp_code.OSD_LANG_CODE.keys())
    
    @property
    def osd_language(self):
        language = self.get_vcp_value_by_name('OSD Language')[0]
        for i in list(vcp_code.OSD_LANG_CODE.keys()):
            if vcp_code.OSD_LANG_CODE[i] == language:
                return i
        return ''

    @osd_language.setter
    def osd_language(self, language: str):
        if language not in self.osd_languages_list:
            _LOGGER.warning('invalid OSD Language: {}, available:{}'.format(
                language, self.osd_languages_list))
            return
        self.set_vcp_value_by_name('OSD Language', vcp_code.OSD_LANG_CODE.get(language))

    @property
    def power_mode_list(self) -> list:
        """
        VCP 中指定的电源状态
        :return:
        """
        return list(vcp_code.POWER_MODE_CODE.keys())

    @property
    def power_mode(self):
        power_ = self.get_vcp_value_by_name('Power Mode')[0]
        for i in list(vcp_code.POWER_MODE_CODE.keys()):
            if vcp_code.POWER_MODE_CODE[i] == power_:
                return i
        # return 'off' to fix quirky, example: when power-off, it return 0x02
        return 'off'

    @power_mode.setter
    def power_mode(self, mode: str):
        if mode not in self.power_mode_list:
            _LOGGER.warning('invalid power mode: {}, available:{}'.format(
                mode, self.power_mode_list))
            return
        self.set_vcp_value_by_name('Power Mode', vcp_code.POWER_MODE_CODE.get(mode))

    @property
    def input_src_list(self) -> list:
        """
        VCP 中指定的输入源
        :return:
        """
        return list(vcp_code.INPUT_SRC_CODE.keys())

    @property
    def input_src(self):
        input_ = self.get_vcp_value_by_name('Input Source')[0]
        for i in list(vcp_code.INPUT_SRC_CODE.keys()):
            if vcp_code.INPUT_SRC_CODE[i] == input_:
                return i
        return ''

    @input_src.setter
    def input_src(self, src: str):
        if src not in self.input_src_list:
            _LOGGER.warning('invalid input source: {}, available:{}'.format(
                src, self.input_src_list))
            return
        self.set_vcp_value_by_name('Input Source', vcp_code.INPUT_SRC_CODE.get(src))

    @property
    def info_pannel_type(self) -> str:
        pannel_type = self.get_vcp_value_by_name('Flat Panel Sub-Pixel Layout')[0]
        return vcp_code.FLAT_PANEL_SUB_PIXEL_LAYOUT_CODE.get(pannel_type, '')


if __name__ == '__main__':
    # test code
    
    logging.basicConfig(level=logging.INFO)
    
    # 检查是否在支持的平台上工作
    # os.popen('ver.exe').read()
    if sys.platform != 'win32' or sys.version_info.major != 3:
        _LOGGER.error('不支持的平台，需要 Windows Vista+, Python 3')
        sys.exit(1)

    try:
        monitors = enumerate_monitors()
    except OSError:
        sys.exit(1)

    phy_monitors = []
    for h_monitor in monitors:
        try:
            monitor = PhyMonitor(h_monitor)
        except OSError as os_err:
            _LOGGER.error(os_err)
            # 忽略这个显示器并继续
            continue
        _LOGGER.info('found {}'.format(monitor.model))
        phy_monitors.append(monitor)

    test_monitor = phy_monitors[0]
