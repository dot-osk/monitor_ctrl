
VCP_CODE = {
    # ######################### Preset Operation #######################
    # 0: ignore, non-zero: reset factory
    
    # Restore factory defaults for color settings.
    'Restore Factory Color Defaults': 0x08,
    
    # Restore all factory presets including luminance / contrast, geometry, color and TV defaults.
    'Restore Factory Defaults': 0x04,
    
    # Restore factory defaults for geometry adjustments.
    'Restore Factory Geometry Defaults': 0x06,
    
    # Restores factory defaults for luminance and contrast adjustments.
    'Restore Factory Luminance / Contrast Defaults': 0x05,
    
    # Restore factory defaults for TV functions.
    'Restore Factory TV Defaults': 0x0A,
    
    # Store/Restore the user saved values for current mode.
    # Byte: SL, 0x01: store current setting, 0x02: Restore factory defaults for current mode.
    'Save / Restore Settings': 0xB0,
    
    'VCP Code Page': 0x00,
    
    # ######################  Image Adjustment VCP Codes ############
    # RO,
    'User Color Temperature Increment': 0x0B,
    
    # RW, read: 3000K + 'User Color Temperature Increment' * 'User Color Temperature'
    'User Color Temperature': 0x0C,
    
    # RW, control brightness level
    'Luminance': 0x10,
    
    # RW, video sampling clock frequency
    'Clock': 0x0E,
    
    'Flesh Tone Enhancement': 0x11,
    
    # Contrast of the image
    'Contrast': 0x12,
    
    # deprecated, It must NOT be implemented in new designs!
    # 'Backlight Control': 0x13,
    
    # ref: COLOR_PRESET_*
    # read: current color preset
    'Select Color Preset': 0x14,
    
    # RGB: Red, test: 0k
    'Video Gain Red': 0x16,
    # RGB：Green, test: ok
    'Video Gain Green': 0x18,
    # RGB: Blue, test: ok
    'Video Gain Blue': 0x1A,
    
    # 'User Color Vision Compensation': 0x17,
    # 'Focus': 0x1C,
    
    # send: AUTO_SETUP_*
    'Auto Setup': 0x1E,
    
    # send: AUTO_SETUP_*
    'Auto Color Setup': 0x1F,
    
    'Gray Scale Expansion': 0x2E,
    
    # test: ok, 但不知道做什么
    'Video Black Level: Red': 0x6C,
    'Video Black Level: Green': 0x6E,
    'Video Black Level: Blue': 0x70,
    
    'Gamma': 0x72,
    
    'Adjust Zoom': 0x7C,
    'Sharpness': 0x87,
    
    # #############################  Display Control VCP Code Cross-Reference
    # unit: Hour
    'Display Usage Time': 0xC0,
    'Display Controller ID': 0xC8,
    'Display Firmware Level': 0xC9,
    
    # see OSD_LANG_CODE
    'OSD Language': 0xCC,
    
    #
    'Power Mode': 0xD6,
    # two bytes: H: MCCS version number, L: MCCS revision number
    'VCP  Version': 0xDF,
    
    # ######################## Geometry VCP Codes
    'Bottom Corner Flare': 0x4A,
    'Bottom Corner Hook': 0x4C,
    'Display Scaling': 0x86,
    'Horizontal Convergence M / G': 0x29,
    'Horizontal Convergence R / B': 0x28,
    'Horizontal Keystone': 0x42,
    'Horizontal linearity': 0x2A,
    'Horizontal Linearity Balance': 0x2C,
    'Horizontal Mirror (Flip)': 0x82,
    'Horizontal Parallelogram': 0x40,
    'Horizontal Pincushion': 0x24,
    'Horizontal Pincushion Balance': 0x26,
    'Horizontal Position (Phase)': 0x20,
    'Horizontal Size': 0x22,
    'Rotation': 0x44,
    'Scan Mode': 0xDA,
    'Top Corner Flare': 0x46,
    'Top Corner Hook': 0x48,
    'Vertical Convergence M / G': 0x39,
    'Vertical Convergence R / B': 0x38,
    'Vertical Keystone': 0x43,
    'Vertical Linearity': 0x3A,
    'Vertical Linearity Balance': 0x3C,
    'Vertical Mirror (Flip)': 0x84,
    'Vertical Parallelogram': 0x41,
    'Vertical Pincushion': 0x34,
    'Vertical Pincushion Balance': 0x36,
    'Vertical Position (Phase)': 0x30,
    'Vertical Size': 0x32,
    'Window Position (BR_X)': 0x97,
    'Window Position (BR_Y)': 0x98,
    'Window Position (TL_X)': 0x95,
    'Window Position (TL_Y)': 0x96,

    # ############### Miscellaneous Functions VCP Codes
    'Active Control': 0x52,
    
    # 0x01: disable, 0x02: enable
    'Ambient Light Sensor': 0x66,
    'Application Enable Key': 0xC6,
    'Asset Tag': 0xD2,
    'Auxiliary Display Data ': 0xCF,
    'Auxiliary Display Size': 0xCE,
    'Auxiliary Power Output': 0xD7,
    # only for CRT, >= 0x01 perform degauss
    'Degauss': 0x01,
    'Display Descriptor Length': 0xC2,
    'Display Identification Data Operation': 0x78,
    # DISPLAY_TECH_TYPE
    'Display Technology Type': 0xB6,
    'Enable Display of ‘Display Descriptor’': 0xC4,
    # FLAT_PANEL_SUB_PIXEL_LAYOUT_CODE
    'Flat Panel Sub-Pixel Layout': 0xB2,
    # Input source control
    'Input Source': 0x60,
    'New Control Value': 0x02,
    'Output Select': 0xD0,
    'Performance Preservation': 0x54,
    'Remote Procedure Call': 0x76,
    'Scratch Pad': 0xDE,
    'Soft Controls': 0x03,
    'Status Indicators (Host)': 0xCD,
    'Transmit Display Descriptor': 0xC3,
    'TV-Channel Up / Down': 0x8B,

    # ############################### Audio Function VCP Code Cross-reference
    # Control Volume
    'Audio: Balance L/R': 0x93,
    'Audio: Bass': 0x91,
    'Audio: Jack Connection Status': 0x65,
    'Audio: Microphone Volume': 0x64,
    'Audio: Mute (screen blank)': 0x8D,
    'Audio: Processor Mode': 0x94,
    'Audio: Speaker Select': 0x63,
    'Audio: Speaker Volume': 0x62,
    'Audio: Treble': 0x8F,
    
    # ############################### DPVL Support Cross-reference
    
}


# 0x14, Select Color Preset
# 显示器不一定支持所有模式
COLOR_PRESET_CODE = {
    'sRGB': 0x01,
    'Display Native': 0x02,
    '4000K': 0x03,
    '5000K': 0x04,
    '6500K': 0x05,
    '7500K': 0x06,
    '8200K': 0x07,
    '9300K': 0x08,
    '10000K': 0x09,
    '11500K': 0x0A,
    'User Mode 1': 0x0B,
    'User Mode 2': 0x0C,
    'User Mode 3': 0x0D
}

AUTO_SETUP_CODE = {
    'off': 0x00,
    'Manual Perform': 0x01,
    'Continuous': 0x02
}

POWER_MODE_CODE = {
    'on': 0x01,
    # 相当于按电源键待机
    'off': 0x05,
}

# OSD 菜单语言列表
OSD_LANG_CODE = {
    'Reserved/ignored': 0x00,
    'Chinese-traditional': 0x01,
    'English': 0x02,
    'French': 0x03,
    'German': 0x04,
    'Italian': 0x05,
    'Japanese': 0x06,
    'Korean': 0x07,
    'Portuguese-Portugal': 0x08,
    'Russian': 0x09,
    'Spanish': 0x0A,
    'Swedish': 0x0B,
    'Turkish': 0x0C,
    'Chinese-simplified': 0x0D,
    'Portuguese-Brazil': 0x0E,
    'Arabic': 0x0F,
    'Bulgarian': 0x10,
    'Croatian': 0x11,
    'Czech': 0x12,
    'Danish': 0x13,
    'Dutch': 0x14,
    'Estonian': 0x15,
    'Finnish': 0x16,
    'Greek': 0x17,
    'Hebrew': 0x18,
    'Hindi': 0x19,
    'Hungarian': 0x1A,
    'Latvian': 0x1B,
    'Lithuanian': 0x1C,
    'Norwegian': 0x1D,
    'Polish': 0x1E,
    'Romanian': 0x1F,
    'Serbian': 0x20,
    'Slovak': 0x21,
    'Slovenian': 0x22,
    'Thai': 0x23,
    'Ukrainian': 0x24,
    'Vietnamese': 0x25
}

# 输入源设置
INPUT_SRC_CODE = {
    'Analog video (R/G/B) 1': 0x01,
    'Analog video (R/G/B) 2': 0x02,
    'Digital video (TMDS) 1 DVI 1': 0x03,
    'Digital video (TMDS) 2 DVI 2': 0x04,
    'Composite video 1': 0x05,
    'Composite video 2': 0x06,
    'S-video 1': 0x07,
    'S-video 2': 0x08,
    'Tuner 1': 0x09,
    'Tuner 2': 0x0A,
    'Tuner 3': 0x0B,
    'Component video (YPbPr / YCbCr) 1': 0x0C,
    'Component video (YPbPr / YCbCr) 2': 0x0D,
    'Component video (YPbPr / YCbCr) 3': 0x0E,
    'DisplayPort 1': 0x0F,
    'DisplayPort 2': 0x10,
    'Digital Video (TMDS) 3 HDMI 1': 0x11,
    'Digital Video (TMDS) 4 HDMI 2': 0x12
}

# 面板子像素排列方式
FLAT_PANEL_SUB_PIXEL_LAYOUT_CODE = {
    0x00: 'Sub-pixel layout is not defined',
    0x01: 'Red / Green / Blue vertical stripe',
    0x02: 'Red / Green / Blue horizontal stripe',
    0x03: 'Blue / Green / Red vertical stripe',
    0x04: 'Blue/ Green / Red horizontal stripe',
    0x05: 'Quad-pixel, a 2 x 2 sub-pixel structure with red at top left, blue at bottom right and green at top right and bottom left',
    0x06: 'Quad-pixel, a 2 x 2 sub-pixel structure with red at bottom left, blue at top right and green at top left and bottom right',
    0x07: 'Delta (triad)',
    0x08: 'Mosaic with interleaved sub-pixels of different colors'
}
