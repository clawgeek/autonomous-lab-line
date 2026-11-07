# -*- coding: utf-8 -*-
"""
自主实验室产线 · 项目介绍视频 —— 解说文案
==========================================
结构：SHOT（镜头，对应一段相机运动）→ CUE（一句话，对应一条字幕）
每句独立合成 TTS，因此字幕时间码 = 音频真实时长，不需要按字数估算。
"""

TTS_SPEED = 1.02
INSTRUCTION = (
    '女声讲解，语速适中偏快、节奏紧凑，声音温柔沉稳、专业清晰，吐字干净。'
    '像在现场给一位工程师讲解，不要念稿感，句尾不要上扬。'
)
VOICE = 'wenrounvsheng'

#: 镜头 → 句子（中英）
SHOTS = [
    dict(id='S1', name='开篇', cues=[
        ('这是一条真实的自主实验室产线。',
         'This is a real autonomous laboratory production line.'),
        ('十台移液工站沿两侧一字排开，中间留出三点二米的通道。',
         'Ten liquid-handling stations line both sides, with a 3.2-metre aisle down the middle.'),
        ('这条通道的宽度，来自两台移动机器人双向交会所需的距离。',
         'That width comes from what two mobile robots need to pass each other.'),
        ('从物料进厂到成品出库，整条线只有一个控制输入。',
         'From incoming material to finished goods, the whole line runs on a single input.'),
        ('它不是动画，是一个可以用参数重算的数字样机。',
         'This is not an animation. It is a digital mock-up you can recompute from parameters.'),
    ]),

    dict(id='S2', name='布局', cues=[
        ('从上方看，布局的逻辑很直接。',
         'From above, the logic of the layout is straightforward.'),
        ('左侧五台，右侧五台，交错镜像。',
         'Five on the left, five on the right, mirrored and staggered.'),
        ('每一台都是独立的自动化单元，故障可以单点隔离，不会拖垮全线。',
         'Each is an independent cell, so a fault can be isolated instead of taking down the line.'),
        ('物料从东端进来，成品从东端出去，人和车在空间上彻底分开。',
         'Material enters at the east end and leaves there too, keeping people and vehicles apart.'),
        ('两台车共用一套路线，一台送料，一台回收，车速一点二米每秒。',
         'Two vehicles share one route, one feeding and one collecting, at 1.2 metres per second.'),
    ]),

    dict(id='S3', name='工位', cues=[
        ('打开一台工位。',
         'Open one station.'),
        ('七轴协作臂的正前方，有三个位置。',
         'Directly in front of the seven-axis arm are three positions.'),
        ('左边是毛坯垛，中间是工作位，右边是成品垛。',
         'Raw trays on the left, the work position in the middle, finished trays on the right.'),
        ('机械臂夹的不是板，是托盘。',
         'The arm does not grip the plate. It grips a tray.'),
        ('一百五十毫米宽的标准托盘，侧壁五毫米，那正好是夹爪唯一能咬住的地方。',
         'A standard 150-millimetre tray, with a five-millimetre wall that is the only thing a gripper can hold.'),
    ]),

    dict(id='S4', name='节拍', cues=[
        ('一个循环六秒。',
         'One cycle takes six seconds.'),
        ('先把成品从工作位取走，送进成品垛。',
         'First it takes the finished tray out of the work position and stacks it.'),
        ('再回到毛坯垛，取下一盘，放进工作位。',
         'Then it returns to the raw stack, picks the next tray and loads the work position.'),
        ('先取后放，这是单臂单工位唯一讲得通的顺序。',
         'Unload before you load. With one arm and one fixture, that is the only order that works.'),
        ('整段动作由十四个关键帧定义。',
         'The whole motion is defined by fourteen keyframes.'),
        ('帧间最大位移六十四毫米，没有一帧是手拉的。',
         'Peak travel between frames is 64 millimetres. Not a single frame is hand-animated.'),
    ]),

    dict(id='S5', name='天轨', cues=[
        ('工位上方是一条龙门天轨。',
         'Above the stations runs a gantry.'),
        ('它从移动机器人的料架上取托盘，升到二点六米，横移到工位顶部的投料口，再放下去。',
         'It lifts a tray off the mobile robot, rises to 2.6 metres, crosses to the hatch on top of the station and lowers it in.'),
        ('横梁为什么会压得这么低。',
         'Why is the crossbeam set so low.'),
        ('因为顶上两条风管的底面在二点八一，横梁只能走在它下面。',
         'Because the ducts overhead bottom out at 2.81 metres, the beam has nowhere else to go.'),
        ('这是几何约束，不是审美选择。',
         'That is a geometric constraint, not an aesthetic choice.'),
        ('天轨、工位臂、复合机器人的动作窗口，是互相锁死的。',
         'The motion envelopes of gantry, station arm and mobile manipulator are interlocked.'),
    ]),

    dict(id='S6', name='接驳', cues=[
        ('车和工位之间，还有一层接驳。',
         'Between the vehicle and the station sits one more layer.'),
        ('复合机器人停在工位前，从伸出的接料台上取走成品托盘。',
         'The mobile manipulator parks in front, takes a finished tray from the transfer shelf.'),
        ('转身，放到自己的台面上。',
         'Turns and sets it on its own deck.'),
        ('它不负责搬运，只负责把东西从柜子里接出来，剩下的一段路由移动机器人完成。',
         'It does not haul cargo. It hands off from the cabinet, and the base vehicle carries the rest.'),
    ]),

    dict(id='S7', name='安全', cues=[
        ('天轨下探的时候，工位臂会自动让位，实测最小间隙零点八二米。',
         'When the gantry descends, the station arm yields. Measured minimum clearance: 0.82 metres.'),
        ('臂还停在窗口区域时，滑窗禁止关闭。',
         'While the arm is still in the window zone, the sash is locked open.'),
        ('天轨作业时，窗口强制关合，这一条防的不是机器人，是人。',
         'While the gantry works overhead, the sash is forced shut. That rule is not for the robot, it is for people.'),
        ('外围是安全围栏、入口光幕，和四路吸顶监控。',
         'Around it: perimeter fencing, an entry light curtain and four ceiling cameras.'),
        ('光幕只装在人员入口，不装在车道上，否则每过一台车就会停机。',
         'The curtain guards the personnel door, not the vehicle lane, where every pass would trip it.'),
    ]),

    dict(id='S8', name='料区', cues=[
        ('线体东端是两个料区。',
         'At the east end of the line sit two material zones.'),
        ('蓝色是毛坯，绿色是成品。',
         'Blue for raw, green for finished.'),
        ('托盘本体色、前脸标签条、是否封膜，三层信息同时成立。',
         'Tray colour, face label and whether the plate is sealed: three layers of the same signal.'),
        ('站在任何一个距离，至少有一种能读出来。',
         'At any distance, at least one of them still reads.'),
    ]),

    dict(id='S9', name='界面', cues=[
        ('点开任意一台工站，右侧会展开这一台的物料清单。',
         'Click any station and its bill of materials opens on the right.'),
        ('滑块往下拉，整台设备逐层散开。',
         'Drag the slider and the enclosure comes apart layer by layer.'),
        ('切到剖面，钣金变成半透明，内部结构一目了然。',
         'Switch to section and the sheet metal turns translucent, exposing what is inside.'),
        ('所有视角、所有读数，都挂在同一条时间轴上。',
         'Every view and every readout hangs off the same timeline.'),
        ('时间轴可以拖动，拖到哪一秒，画面就停在哪一秒。',
         'Drag the timeline and the picture stops on exactly that second.'),
        ('五个机位，三档剖切，都是真按钮，不是示意图。',
         'Five camera presets and three cut modes. Real controls, not illustrations.'),
    ]),

    dict(id='S10', name='数据', cues=[
        ('屏幕上每一个数字都是算出来的，不是写死的。',
         'Every number on screen is computed, not typed in.'),
        ('台面横梁跨中挠度零点五四毫米，一阶固有频率十六点八赫兹。',
         'Mid-span deflection of the deck beam is 0.54 millimetres, first natural frequency 16.8 hertz.'),
        ('这个值低于精密台面二十五赫兹的门槛，所以标了警示色。',
         'That sits below the 25-hertz floor for a precision deck, so it is flagged.'),
        ('真正的改法是缩跨距，不是加厚型材。',
         'The fix is a shorter span, not a thicker profile.'),
        ('基座螺栓拉力零点七九千牛，对十五点三千牛的预紧，只占百分之五。',
         'Base bolt load is 0.79 kilonewtons against 15.3 of preload, only five percent.'),
        ('整机抗倾覆系数十二点五，安全余量在刚度上，不在强度上。',
         'Tipping resistance is 12.5. The margin lives in stiffness, not in strength.'),
        ('改一个参数，模型和读数一起重算，不需要重新做一遍。',
         'Change one parameter and model and readouts recompute together, with no rebuild.'),
    ]),

    dict(id='S11', name='收束', cues=[
        ('这是一个可以被拆开、被复算、被质疑的模型。',
         'This is a model you can take apart, recompute and argue with.'),
        ('它也不完美。',
         'It is not perfect.'),
        ('频率不够，臂展偏紧，我都标在了面板上。',
         'The frequency is low and the reach is tight, and both are flagged on the panel.'),
        ('完整工程档案在右边，可以逐条对着看。',
         'The full engineering dossier is on the right, item by item.'),
    ]),
]

#: 句间停顿（秒）——句末已有 TTS 的自然收尾，这里只补一点呼吸
GAP_SENTENCE = 0.16
#: 镜头间停顿
GAP_SHOT = 0.55
