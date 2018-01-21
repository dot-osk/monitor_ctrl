
通过显示器的 DDC/CI 来直接操作显示器，拯救可怜的显示器按键。

支持的操作：

    - 调整亮度
    
    - 调整对比度
    
    - 设置色温 / 颜色预设
    
    - 设置RGB颜色的比例
    
    - OSD语言
    
    - 开关机
    
    - 切换输入源
    
    - 自动调整图像 (VGA输入需要)
    
    - 恢复出厂设置


注意：我只在自己平时使用的几个辣鸡显示器上测试全部OK，不一定对所有显示器支持良好。

HDMI/DP音量调整等更多功能由于显示器不支持没法测试就没加进来，有需要的可以自行添加进去。

由于我对 VESA 的 MCCS 文档只是粗浅的读了一下然后复制指令到代码中，可能有些指令使用方式不正确，欢迎指正。


![GUI](https://github.com/dot-osk/monitor_ctrl/raw/master/doc/img/Capture.JPG)



# 系统需求

```text
Windows Vista +
Python3 (建议安装时选上Python Launcher)
支持DDC/CI的外接显示器，不支持笔记本内置显示器
```


# 使用参考

## GUI 模式

不附加参数启动 `monitor_ctrl.py` 即可启动GUI，直接拖动滑条设置显示器的参数。

由于显示器应用VCP指令可能需要一定时间，为避免出错，GUI模式将忽略命令行指定的操作。

GUI中显示的配置不会自动刷新，要查看新的配置目前需要重启应用程序。

*将文件后缀修改为 .pyw, 直接双击打开，可以避免显示conhost黑窗口*

## 命令行模式

当指定 `-c` 选项或者 tkinter import失败就会使用CLI模式。

```
py monitor_ctrl.py [-h] [-m Model_string] [-s Settings_string] [-r] [-t] [-c] [-l] [-v]
  -h          显示帮助
  -m          指定要应用到的Monitor Model，不指定则应用到所有可操作的显示器
  -s          property1=value1:property2="value 2" 应用多项设置
  -r          将显示器恢复出厂设置
  -t          对输入执行自动调整（仅VGA输入需要）
  -c          不启用GUI
  -l          显示可操作的显示器model
  -v          Verbose logging
```


example：

- 列出可操作的显示器

`monitor_ctrl.py -c -l`

- 降低显示器的亮度和蓝色亮度：

`monitor_ctrl.py -c -s brightness=10:rgb_gain="(100, 100, 80)"`

- 设置显示器颜色预设为 sRGB ：

`monitor_ctrl.py -c -s color_preset=sRGB`

- 恢复出厂设置：

`monitor_ctrl.py -c -r`

- VGA输入自动调整

`monitor_ctrl.py -c -t`

- 仅设置某个特定型号的显示器：

`monitor_ctrl.py -c -m p2401 -s power_mode=on`

### -s 接受的属性

参见后面 PhyMonitor() 类的常用属性。

# TODO

- 添加HDMI/DP输入时音频音量的调节 (显示器不支持音频输出暂时没法测试)


# 参考资料

[MSDN: High-Level Monitor API](https://msdn.microsoft.com/en-us/library/vs/alm/dd692964(v=vs.85).aspx)

[MSDN: Low-Level Monitor Configuration](https://msdn.microsoft.com/en-us/library/windows/desktop/dd692982(v=vs.85).aspx)

[Wiki: Monitor Control Command Set](https://en.wikipedia.org/wiki/Monitor_Control_Command_Set)

[PDF: VESA Monitor Control Command Set](https://milek7.pl/ddcbacklight/mccs.pdf)



# 其它使用方法(vcp.py)

1. 调用 `enumerate_monitors()` 函数获得一个可操作的物理显示器对象列表

```python
from vcp import *

try:
    monitors = enumerate_monitors()
except OSError as err:
    exit(1)
```

2. 迭代列表中的对象并尝试创建每个显示器对应的 `PhyMonitor()` 实例，需要处理可能抛出的异常，如显示器不支持 DDC/CI 或者I2C通讯失败等异常
```python
phy_monitors = []
for i in monitors:
    try:
        monitor = PhyMonitor(i)
    except OSError as err:
        logging.error(err)
        # 忽略这个显示器并继续
        continue
    phy_monitors.append(monitor)
    
# 选一个显示器测试
pm = phy_monitors[0]
# 显示型号
pm.model 
```

3. 对每个 `PhyMonitor()` 实例进行期望的操作



# PhyMonitor() class

## 常用属性的操作

注意：大部分属性操作过程中如出现异常，只会有 logging.error 日志，不会抛出异常

包装后的属性：

```text
color_temperature

brightness
brightness_max

contrast
contrast_max

color_preset
color_preset_list

rgb_gain
rgb_gain_max

osd_language
osd_languages_list

power_mode
power_mode_list

input_src
input_src_list
```


### `color_temperature` : 设置屏幕的色温(K)

显示器可能并不支持你设定的色温值，而且可能在显示器面板上设定的色温值不一定和这个属性报告的一样。
色温越高，屏幕颜色越冷，反之屏幕偏暖。 不建议操作这个属性来设置色温，使用 `color_preset` 属性。

```python
# 读取当前色温设置
pm.color_temperature
>>> 7200
# 设置色温
pm.color_temperature = 6500
```

### `brightness` 设置亮度
读取/设置显示器的亮度，允许值： 0 - `pm.brightness_max`

```python
# 允许设置的最大亮度
pm.brightness_max
>>> 100
# 读取当前亮度
pm.brightness
>>> 50
# 设置亮度
pm.brightness = 60
```

### `contrast` 设置对比度

读取设置显示器的对比度，允许值： 0 - `pm.contrast_max`
使用方法同亮度属性

### `color_preset` 色温/颜色预设

读取/设置当前的颜色预设，列表中的可用值你的显示器不一定都支持。

```python
# 查看VCP标准中可用的预设
pm.color_preset_list
>>> ['sRGB', 'Display Native', '4000K', '5000K', '6500K', '7500K',
'8200K', '9300K', '10000K', '11500K', 'User Mode 1', 'User Mode 2', 'User Mode 3']
# 读取当前使用的预设
pm.color_preset
# 设置新的预设
pm.color_preset = 'sRGB'
```

### `rgb_gain` RGB颜色均衡

设置 RGB 三基色的均衡，注意：有些显示器只有使用用户模式(`'User Mode 1'`)的 `color_preset` 才能调整RGB均衡。

```python
# 允许设置的最大值
pm.rgb_gain_max
>>> 100
# 当前的RGB 均衡
pm.rgb_gain
>>> (100, 100, 100)
# 设置新的RGB均衡
pm.rgb_gain =  100, 100, 80     # "降低蓝光"
pm.rgb_gain =  [90, 90, 100]    # 加强蓝光
``` 

### `osd_language` 菜单语言

在我自己的显示器上测试有一点Bug，不支持设置土耳其和另外两个我不知道是什么的语言( 囧 )，其它显示器支持的语言OK。

```python
# 查看VCP 标准中支持设置的语言，不是显示器支持的语言
pm.osd_languages_list
# 查看当前的OSD语言
pm.osd_language
>>> 'Chinese-traditional'
# 设置OSD语言
pm.osd_language = 'English'
```

### `power_mode` 电源开关

设置为 'off' 相当于按下显示器面板上的电源键关机。
设置为 'on' 相当于按下显示器面板上的电源键开机。

```python
pm.power_mode
>>> 'on'
# 关闭显示器电源
pm.power_mode = 'off'
pm.power_mode
>>> 'off'
# 再次打开显示器电源
pm.power_mode = 'on'
>>> 'on'
```

### `input_src` 输入信号选择

可以设置 `input_src_list` 里面的输入源

```python
# VCP 标准中的 输入源
pm.input_src_list
>>> ['Analog video (R/G/B) 1', 'Analog video (R/G/B) 2', 'Digital video (TMDS) 1 DVI 1', ...]
# 当前的输入源, VGA
pm.input_src
>>> 'Analog video (R/G/B) 1'
# 切换输入源为 DVI 1
pm.input_src = 'Digital video (TMDS) 1 DVI 1'
```



## 常用方法

### `reset_factory()` 恢复出厂设置

恢复显示器的出厂设置

### `auto_setup_perform()` 自动调整

只有使用VGA时才需要自动调节


### `close()` 

调用 Windows 的 `DestroyPhysicalMonitor()` API 来销毁HANDLE


## 显示器信息属性

`info_poweron_hours` 开机小时数

`info_pannel_type` 面板子像素排列信息

`model` 显示器型号


## 发送其它命令, 添加其它功能

1. 参考VCP指令列表，使用

`set_vcp_value_by_name()` 和 `get_vcp_value_by_name()` 来发送 `vcp_code.VCP_CODE` 中已定义的功能。

`vcp_code.VCP_CODE` 里面的代码并不完整，可以根据需要执行添加code到这个字典中。


2. 或者使用

`send_vcp_code()` 和 `read_vcp_code()` 来发送指令代码(数字)


# Todo

找台支持HDMI音频的显示器测试设置HDMI声音输出音量

