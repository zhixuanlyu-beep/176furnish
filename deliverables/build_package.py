"""Generate the editable concept design package. All geometry is schematic."""
from pathlib import Path
import base64
import csv
import html
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SOURCE = ROOT / 'IMG20260907-094631119.jpg'
INK, GREEN, BLUE, AMBER = '#233d36', '#287361', '#427f9a', '#ac6537'

def txt(x, y, s, size=15, fill=INK, anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{html.escape(s)}</text>'

def rect(x,y,w,h,fill='#fff',stroke='#82958c',radius=0,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" {extra}/>'

def line(x1,y1,x2,y2,color=INK,dash='',width=2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'

def badge(x,y,s,color=BLUE):
    return rect(x-25,y-11,50,22,color,color,5)+txt(x,y+5,s,13,'#fff')

def bed(x,y,w,h):
    return rect(x,y,w,h,'#fff','#acb8ad',6)+rect(x+4,y+4,w-8,23,'#e9e8dc','#acb8ad',3)+line(x,y+38,x+w,y+38,'#acb8ad')

def base(mode):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 650 920" role="img" aria-labelledby="title desc"><title id="title">{mode}</title><desc id="desc">依据原图空间上下左右关系绘制的概念示意；不按比例，不用于放线或拆墙。</desc><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="{GREEN}"/></marker></defs><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif">']
    parts += [rect(240,35,360,200,'#f0eddf'),rect(240,35,100,140,'#e5eff0'),rect(85,235,155,135,'#e0eee7'),rect(240,235,60,170,'#faf8f1'),rect(85,370,155,35,'#faf8f1','#faf8f1'),rect(300,235,175,170,'#f0eddf'),rect(228,405,125,85,'#e5eff0'),rect(353,405,122,150,'#e5eff0'),rect(475,405,62,150,'#e9ece6'),rect(270,555,205,150,'#f5e7d3'),rect(270,705,205,165,'#f0eddf'),rect(50,815,170,65,'#e9ece6')]
    parts.append('<path d="M85 405H228V490H353V555H270V815H50V485H85Z" fill="#faf8f1" stroke="#82958c"/>')
    parts += [txt(430,62,'A 主卧套间',19),txt(290,92,'原主卫',16),txt(387,264,'B 次卧',19),txt(160,262,'独立书房',18),txt(271,293,'卧室',13),txt(271,316,'通道',13),txt(290,439,'原公卫',17),txt(414,430,'原中厨',17),txt(506,434,'阳台B',13),txt(375,580,'C 干备餐区',17),txt(375,730,'D 次卧',18),txt(161,554,'客厅',20),txt(130,855,'阳台A · 休闲',16),txt(71,462,'入户 →',15)]
    # R2: source arrow points up/north. A window is on its south-east wall.
    # B/C east and D south have projecting window outlines; sill construction is unknown.
    parts += [line(502,235,580,235,BLUE,'',5),rect(475,278,27,79,'#fffef9',BLUE),line(502,280,502,355,BLUE,'',4),rect(475,590,27,68,'#fffef9',BLUE),line(502,592,502,656,BLUE,'',4),rect(329,870,81,22,'#fffef9',BLUE),line(331,892,408,892,BLUE,'',4),line(537,416,537,545,BLUE,'',5),line(482,405,530,405,BLUE,'',4),line(482,555,530,555,BLUE,'',4),line(66,880,202,880,BLUE,'',5),line(575,355,575,300,INK,'',2),txt(575,290,'N / 北',13)]
    # Existing doorway locations, schematic spans only (not opening dimensions).
    for x1,y1,x2,y2 in [(250,235,286,235),(340,116,340,163),(300,350,300,395),(245,490,285,490),(353,510,353,550),(475,512,475,550),(287,555,331,555),(270,712,270,752)]:
        parts += [line(x1,y1,x2,y2,'#fffef9','',7),line(x1,y1,x2,y2,'#68736b','3 4',1.5)]
    parts += [txt(300,542,'C原门洞',11),txt(299,569,'↓',12)]
    if mode != '拆改核验示意图':
        # R4 final concept: erase the selected west partition span, keeping end portions.
        # The span is schematic; it is not a measured demolition limit.
        parts += [rect(266,575,8,100,'#faf8f1','#faf8f1')]
    return parts

def floorplan(mode):
    p = base(mode)
    if mode == '家具与通行概念图':
        p += [bed(418,93,112,123),rect(556,75,28,131,'#d8decf'),bed(360,310,83,79),rect(311,275,140,22,'#d8decf'),bed(331,759,103,96),rect(444,741,25,112,'#d8decf')]
        p += [rect(99,277,32,75,'#d8decf'),txt(115,321,'桌',14),rect(154,351,72,15,'#d8decf'),txt(190,341,'封闭书柜',12),rect(149,294,24,28,'#fff','#82958c',5)]
        p += [line(240,245,240,320,BLUE,'',4),line(95,370,240,370,BLUE,'',4),line(240,320,240,356,BLUE,'4 3',3),txt(157,395,'入口过渡',12,BLUE)]
        p += [rect(363,440,104,24,'#d8decf'),txt(415,456,'北侧厨台示意',11),rect(363,475,30,28,'#d8decf'),txt(378,493,'洗碗',11),txt(428,497,'灶位待核',11,AMBER)]
        p += [rect(489,461,34,49,'#d8decf'),txt(506,480,'洗',12),txt(506,499,'烘',12),txt(507,540,'条件位',11,AMBER)]
        p += [rect(281,677,123,26,'#d8decf'),rect(405,669,62,34,'#ccd9cc'),txt(340,694,'食品／电器柜',11),txt(436,692,'冰箱',12),rect(446,594,28,66,'#e7d7b7'),txt(427,652,'净台≥1200',12,AMBER)]
        p += [rect(204,602,112,52,'#ead5b7','#ac936d',5),txt(260,632,'餐桌',16),rect(219,582,28,16,'#fff','#ac936d',4),rect(274,582,28,16,'#fff','#ac936d',4),rect(219,658,28,16,'#fff','#ac936d',4),rect(274,658,28,16,'#fff','#ac936d',4),rect(184,616,16,25,'none',AMBER,3,'stroke-dasharray="3 3"'),rect(320,616,16,25,'none',AMBER,3,'stroke-dasharray="3 3"')]
        p += [rect(60,609,45,180,'#d5ddd5','#82958c',10),rect(120,688,49,45,'#ead5b7','#ac936d',9),line(263,767,263,810,INK,'',5),txt(230,792,'TV待量',12)]
        p += [rect(60,505,38,88,'#ead5b7','#ac936d'),txt(79,533,'咖啡',11),txt(79,553,'餐柜',11),txt(79,576,'H03',10)]
        p += [txt(136,579,'R01室内重选',12,AMBER),txt(136,598,'厨房门外留通行',11,AMBER)]
        p += ['<path d="M103 479 H208 V388 H267 V216 M267 351 H330 M177 502 L183 710 L300 741" fill="none" stroke="#287361" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrow)"/>']
        p += [txt(380,608,'宽开口联通',13,GREEN),line(380,555,445,555,BLUE,'5 3',3)]
    elif mode == '拆改核验示意图':
        p += [line(240,240,240,370,BLUE,'',5),line(90,370,240,370,BLUE,'',5),badge(157,313,'M01',BLUE),txt(160,345,'新设玻璃隔断',13,BLUE),txt(157,395,'入口过渡',12,BLUE)]
        p += [line(270,575,270,675,AMBER,'9 6',3),badge(273,634,'M02',AMBER),line(367,555,467,555,AMBER,'9 6',3),badge(416,531,'M03',AMBER),badge(506,485,'M04',AMBER)]
        p += [txt(150,704,'M02 已采用',13,GREEN),txt(150,727,'西侧细墙宽开口',12,GREEN),txt(150,750,'粗线承重墙保留',12),txt(376,697,'C / D 隔墙保留',12)]
        p += [txt(438,142,'保留卧室及原湿区',17),txt(386,322,'保留',17),txt(376,800,'保留',17),txt(144,646,'保留客厅',17),txt(147,678,'家具重排',14),txt(286,471,'不扩大湿区',12),txt(414,497,'水火留中厨',13)]
        p += ['<path d="M110 478H208V388H267V215M267 351H330" fill="none" stroke="#287361" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#arrow)"/>']
    else:
        for x,y,s,c in [(435,453,'K01',BLUE),(383,479,'K02',AMBER),(433,502,'K03',BLUE),(415,540,'K04',AMBER),(503,465,'L01',BLUE),(503,514,'L02',AMBER),(140,610,'R01',AMBER),(433,682,'C01',BLUE),(429,619,'C02',BLUE),(332,683,'C03',AMBER),(164,301,'S01',BLUE),(184,351,'S02',BLUE),(148,510,'H01',BLUE),(198,573,'H02',BLUE)]:
            p.append(badge(x,y,s,c))
        p += [badge(98,535,'H03',BLUE),txt(91,564,'咖啡柜',12),txt(85,585,'仅电源',11,BLUE)]
        p += [txt(402,178,'照明／空调核查保留',15),txt(387,330,'空调与插座复核',13),txt(374,795,'空调与插座复核',13),txt(140,638,'室内重选，非点位',12,AMBER),txt(146,707,'本图仅定位功能区',15),txt(148,739,'无管线或回路走向',14,AMBER)]
    p += [txt(325,908,'非比例图 · C西侧宽开口为采用方案 · 粗墙及C/D隔墙保留',12,AMBER),'</g></svg>']
    return ''.join(p)

EQUIPMENT = [
 ['E01','洗碗机','原中厨水槽旁','600mm宽全尺寸候选','整机宽深高、门全开投影、踢脚避让','进排水与插座置可达邻柜；餐具柜紧邻','门开后可通行且整机可前抽'],
 ['E02','冰箱','C靠D实墙高柜端部','柜深先按约650–750mm研究，非下单尺寸','型号散热间隙、门铰侧余量、抽屉全拉出','电源可达；不封住厂家进出风口','满开门不撞桌椅和窗；可独立搬出'],
 ['E03','蒸烤箱','优先原中厨靠C一端','600mm柜体模块候选','开孔、托板承载、通风及开门投影','专用回路是否需要由铭牌及设计核定','不挤掉必要操作台；不可行则暂不落柜'],
 ['E04','厨余机预留','原中厨水槽柜','不预设整机尺寸，暂不采购','与存水弯、净水器、分类桶三维排布','核实排水及物业要求，预留可达电源','能拆装存水弯、取滤芯与抽垃圾桶'],
 ['E05','洗衣机＋热泵烘干机','阳台B，条件不满足改室内统筹','600mm级整机候选，柜宽深高待定','狭长净宽、门扇/端部窗、叠放件、管线突出与搬出','保温防冻、承载、合规污水排水、阀门电源','原厂连接件；过滤器可达、可分机搬出'],
 ['E06','自动上下水机器人','R01室内重新选址，撤销厨房/C门外交汇处候选位','按基站型号包络留位，不套用统一柜尺寸','坡道、机身高度、托盘/尘袋抽取与侧向余量','独立阀门、合规排污、厂家水压/高差/长度限制','厨房关门仍到达客餐厅及三卧；不占C现门及厨房入口'],
 ['E07','净水器','原中厨水槽柜','待确定型号','滤芯抽取方向、独立阀门与维护包络','按厂家接供水与废水（如有），电源可达','能直接换芯、不需先拆厨余机'],
 ['E08','水箱式咖啡机＋磨豆机','客厅西墙北段、沙发北侧餐边柜H03','柜宽1600–1800、深550–600、高850–900起研','水箱抽取/翻盖、豆仓加豆、废水盘前抽及排汽','只留电源；不接给排水，不设水槽；手动加水倒废水','无需移动整机就能加水、取盘；柜前操作不堵通道'],
 ['E09','漏水探测及可选关水阀','水槽、洗衣区、机器人基站','按传感器与阀门型号','电池更换和阀门操作空间','联动阀须可手动操作；故障仍可关水','分别模拟漏水并核查报警/关阀'],
 ['E10','现有空调与采暖','原位置核查保留；书房专项补足','检验合格保留','室内外机检修、回风与送风路径','封闭书房须有可验证的空气交换方案','书房关门有人办公时验证通风与温度'],
 ['E11','电饭煲／其他小电器','C独立电器位，与备餐净台分开','按同时使用设备的实际包络留位','开盖、排汽与接电，不能在封闭收纳格内运行','普通电饭煲手动加水，无固定上下水；其余按型号','不占≥1200净台，蒸汽不冲吊柜'],
]

POINTS = [
 ['K01','原中厨水槽柜','水槽／净水／厨余预留','冷/热水、独立阀门、净水废水按型号','净水及厨余预留电源、漏水探测','邻柜可达；避开接头下方；滤芯与桶不冲突'],
 ['K02','原中厨灶烟机区','灶具／烟机','燃气和烟道由专业方核查','烟机/点火电源按型号；保留检修','关门排烟与补风；禁止自行改燃气或烟道'],
 ['K03','水槽邻柜','洗碗机','单独可关阀；排水固定/防回流按厂家','按铭牌负荷核回路、保护及可达插座','管线不挡整机前抽；开门核通行'],
 ['K04','中厨靠C端条件位','蒸烤箱候选','是否需供排水依机型；未定不预埋','按铭牌和安装图确定电源与回路','高柜放不下则取消此位；C位须另核用途'],
 ['C01','C高柜端部','冰箱','不默认预留制冰供水','可达电源，回路由电气设计确定','散热与满开门按厂家尺寸'],
 ['C02','C窗侧条件低柜或其他实测可用位置','开放备餐台','无新增水槽及给排水','操作照明、小电器电源按清单','1200mm净面与电器区分开；外凸窗需核窗台高度/开启'],
 ['C03','C靠D实墙柜体','食品／电器收纳','无','收纳柜内不默认配置运行电源','设备取出台面使用；固定运行位须独立核散热'],
 ['L01','阳台B条件位','洗衣／烘干','给水阀、合规污水排水；烘干排水按机型','按两机负荷核算回路/保护、漏水探测','核狭长净宽、门扇/端部窗、保温承载和搬出'],
 ['L02','阳台B原候选位','机器人备选（默认不采用）','保温与合规上下水满足才讨论','独立可达电源、漏水探测','经常关闭厨房门时不能作为全屋清洁基站'],
 ['R01','室内重新选址；图中文字为任务注记而非落位','机器人重新选址任务','核实可合法接入生活污水及独立供水','可达电源、漏水探测','撤销厨房/C现门外交汇处旧点；先保通行再找合法水路'],
 ['S01','书房书桌侧','办公设备','无','桌面插座、网络、独立任务照明','桌下理线；开门和椅后净空复核'],
 ['S02','书房顶/玻璃隔断上部方案位','照明／通风／空调','冷凝水如新增由专业设计落实','照明、控制；通风设备用电按方案','气流路径兼顾隔声；关门通风有测量记录'],
 ['H01','入户墙面可用段','实体场景控制','无','照明/窗帘场景保留实体控制','网络或自动化失效后仍可直接操作'],
 ['H02','客餐厅','餐桌及公共照明','无','餐桌灯位随最终桌位确定；TV位待量','避免为未锁定桌位设地插；不让线缆横穿通道'],
 ['H03','客厅西墙北段、沙发北侧餐边柜','咖啡机＋磨豆机','不设给水、排水和水槽；水箱手动加水、废水盘手倒','按铭牌配固定墙面插座，台面照明；实体控制','不挤玄关/卧室通道；预留取箱、开盖和废水盘抽出'],
]

DIMENSIONS = [
 ['F01','书桌','宽1600–1800；深约650–750','目标家具尺寸','实测书房净宽及椅后使用、门扇开启'],
 ['F02','书柜','深约300–350，封闭为主','研究起点','不挤卧室通道，柜门开启不撞办公椅'],
 ['F03','卧室连续通道','争取净宽1000–1100','通行目标，非实测','按A/B门洞、踢脚、柜门、隔断框测最窄处'],
 ['F04','餐桌','常态1600×800–850；延伸约1800','候选家具尺寸','六人桌椅实物包络、桌腿与椅宽，主通道仍可用'],
 ['F05','主要通道','争取1000–1100','通行目标，非规范判定','有人就座、拉椅及电器开门状态分别校核'],
 ['F06','备餐净台','连续净长至少约1200；柜深约600起研','目标操作面','扣除固定电器及冰箱开门；按窗/暖气/墙长调整'],
 ['F07','A主卧床','床垫1800×2000候选','床垫尺寸非床架','另加床架包络、衣柜开门及床侧走道'],
 ['F08','B次卧床','床垫1200–1500×2000候选','床垫尺寸非床架','根据使用人和净尺寸选窄档优先保通行'],
 ['F09','D次卧床','床垫1500×2000候选','床垫尺寸非床架','另核床尾走道、房门与柜门'],
 ['F10','卧室衣柜','柜深约600，尽量到顶','规划尺寸','床侧通行、门型与梁/空调/检修口'],
 ['F11','直排沙发','宽约2600–3000；深约900–1000','候选家具尺寸','按客厅净宽与餐区借位选型'],
 ['F12','机器人通行及柜底','按所选机身高度＋厂家余量；家具封底或可完整进入','型号决定','不能只按机器人高度忽略宽度、转向及阈值'],
 ['F13','咖啡餐边柜H03','宽1600–1800；深550–600；高850–900','规划目标，型号及实测锁定','西墙北段长度、入户门及沙发一起放样；柜前操作不侵主通道'],
]

CHECKS = [
 ['V01','测绘/设计师','现状净尺寸、门窗开启、梁柱、暖气、检修口、标高','完整测绘图及关键净宽照片','所有落位图','待现场核验'],
 ['V02','设计师/施工及相关专业','已采用M02：C西侧细墙宽开口；M03保留可关闭分隔','标清粗墙/梁柱端部、开口净宽、隐藏管线及门上构造；C/D隔墙保留','落实拆改边界，不再比较是否保留C西侧封闭隔墙','方案已选定，施工边界待核'],
 ['V03','设计师/物业及当地主管要求','C改干备餐/用餐的用途条件','明确可行用途及设备边界的记录','C功能与固定设备清单','待确认'],
 ['V04','燃气专业/设计师','关闭中厨的分隔形式、门及排烟补风','当地燃气要求与方案确认；关门运行测试','M03门及中厨施工','待现场核验'],
 ['V05','给排水/结构/物业','阳台B保温防冻、承载、合规排污、搬运','管道属性及接入、环境、承载核查记录','L01洗烘柜','待现场核验'],
 ['V06','给排水/设备供应方','R01室内重新选址，避厨房/C现门；上下水及前场','接管路径与设备安装图，厨房关门可达演示','机器人柜与管线','旧候选点撤销，待重选'],
 ['V07','电气专业','入户容量、接地及保护、设备同时用电','铭牌清单、负荷表、回路与保护设计','水电施工图','待核算'],
 ['V08','暖通专业','封闭书房照明、通风、温控','送/回/排风或空气交换设计，关门有人测试记录','书房隔断及吊顶','待设计/实测'],
 ['V09','设计师/业主','4/6人就餐、冰箱/洗碗机开门、卧室通行','现场放样和最窄处测量；逐项状态照片','餐桌和柜体下单','待放样'],
 ['V10','柜体商/设备供应方','安装、散热、独立拆出、滤芯和尘袋抽取','型号对应柜图、维护包络及演示','柜体下单与验收','待选型'],
 ['V11','施工/防水专业','湿区防水挡水、干区连续地面','标高图、防水施工与按当地要求验收记录','地面做法','待设计/验收'],
 ['V12','施工/业主','自动上下水、漏水报警、实体控制','机器人完整往返、分点漏水模拟及断网操作记录','交付验收','待安装后验证'],
 ['V13','业主/柜体商/设备供应方','H03水箱咖啡机、磨豆机与餐边柜','柜前站人通行；加水、取盘、加豆和端杯清洗的实操记录','咖啡餐边柜与插座；无固定上下水','配置已确认，尺寸及设备待选'],
]

NEW_AREAS = [
 ['卧室A','23.5','保留主卧；主卫另列'],['卫生间A','4.8','保留原主卫'],
 ['原餐厅','14.4','替换R1正文13.9；先扣通道及入口过渡'],['卧室B','11.5','保留次卧'],
 ['公卫','3.7','保留原湿区'],['厨房','6.4','水火与洗涤留中厨'],
 ['阳台B','3.2','洗烘需另核狭长净宽、窗和门扇'],['客厅','35.2','餐桌借位仍需六人放样'],
 ['卧室C','11.9','已采用西侧宽开口，与客厅共享餐区；边界尺寸待实测'],['卧室D','13.0','保留次卧及C/D隔墙'],
 ['阳台A','3.7','休闲及可收起晾晒'],
]
NEW_SPANS = [
 ['A右侧纵向段','3930','不等于已核定的主卧净进深'],
 ['餐厅/B对应纵向段','3423','书房隔断仍需按A/B门洞净位置落位'],
 ['厨房/阳台B对应纵向段','2844','需扣墙/门框等影响后核设备前场'],
 ['C对应纵向段','2998','与底部3976横向参考段共同用于初排'],
 ['D对应纵向段','3264','衣柜及床架尺寸仍待实测'],
 ['C/D底部对应横向段','3976','不能直接作为定制柜净墙长'],
 ['右侧相邻轮廓横向段','1117','与阳台B狭长形态相关，不能直接认作净宽'],
]

WATER_NEEDS = [
 ['E01 洗碗机','必须；独立可关阀','必须；按厂家防回流','中厨水槽旁；管线经可达邻柜，不放设备正后方妨碍前抽'],
 ['E02 冰箱','普通型无；直连制冰型需要','普通型无；特殊型号核实','C高柜；优先无外接水型，选制冰供水款前先核接水路径'],
 ['E03 水箱式蒸烤','无固定给水，手动加水','通常手动取废水盒；按型号','中厨条件高柜；需留取箱和开盖空间'],
 ['E03 直连式蒸烤备选','需要，水质/水压按厂家','部分机型需要，按安装图','只在水路可达处落位，不能仅凭600宽柜确认安装'],
 ['E04 厨余机预留','使用水槽龙头流水','接原水槽合规排水系统','中厨水槽柜；核存水弯、净水器和分类桶，暂无采购决定'],
 ['E05 洗衣机','必须；独立可关阀','必须；生活污水系统','阳台B条件位；须确认现有管道属性和接入，不能接雨水管'],
 ['E05 热泵烘干机','普通型无；蒸汽护理按机型','有冷凝水：水盒手倒或接管','优先合法直排冷凝水以减少倒水；不能以“无需给水”漏掉排水'],
 ['E06 自动上下水机器人','必须；水压/长度按厂家','必须；高差/距离按厂家','R01先查合法水路再选室内点位；厨房关闭仍可出入'],
 ['E07 净水器','必须','RO型需要废水管；非RO按型号','中厨水槽柜，阀门与滤芯可达；过滤水取用依咖啡机水质要求'],
 ['E08 水箱式咖啡机','不接管，手动加水','不接管，手倒废水盘','H03客厅餐边柜；中厨取水、清洗与倒废水，柜内不存开放废水桶'],
 ['E08 磨豆机','无','无','H03；留豆仓加豆和粉屑清理空间，仅需电源'],
 ['E11 电饭煲','不接管，手动加水','无固定排水','C独立电器位；清洗内胆去中厨水槽，不占备餐净台'],
 ['E10 空调','普通室内机无给水','制冷冷凝水需合规排放','原系统核查保留；新增书房设备须落实冷凝水路径'],
]

def table(headers, rows, cls=''):
    return f'<table class="{cls}"><thead><tr>'+''.join(f'<th>{html.escape(v)}</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{html.escape(v)}</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'

def card(title, body, cls=''):
    return f'<div class="card {cls}"><h3>{title}</h3>{body}</div>'

def page(num,title,subtitle,body):
    return f'<section class="page" id="p{num}"><header><div class="eyebrow">LISHUI JIAYUAN / 丽水嘉园 · 176㎡</div><span>概念深化 · R4 C与客厅联通 · 2026.09.07</span></header><h1><b>{num}</b>{title}</h1><p class="subtitle">{subtitle}</p>{body}<footer><span>依据用户方案、新图及墙体图例｜176㎡为任务提供面积，非净面积测算</span><span>未实测 · 非施工图　/　{num}</span></footer></section>'

def coffee_svg():
    p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 460" role="img" aria-label="H03水箱式咖啡餐边柜概念立面"><g font-family="Microsoft YaHei, sans-serif">']
    p += [txt(425,30,'H03 咖啡餐边柜 · 水箱式 / 仅接电',23),rect(80,220,690,170,'#e4e9db'),line(80,215,770,215,INK,'',6),line(310,222,310,389,'#82958c'),line(540,222,540,389,'#82958c'),txt(195,285,'咖啡耗材抽屉',18),txt(425,285,'杯具封闭收纳',18),txt(655,285,'餐具／备用用品',18)]
    p += [rect(126,118,148,94,'#f0e4cd',INK,5),txt(200,155,'咖啡机',19),txt(200,186,'水箱可取',15),rect(337,144,79,68,'#f0e4cd',INK,5),txt(376,179,'磨豆',16),rect(520,202,175,10,'#f0e4cd'),txt(607,180,'留操作与接水托盘',17)]
    p += [line(200,110,200,67,AMBER,'5 4'),txt(425,70,'上方不做压低吊柜；开盖、取水箱及加豆空间按型号',16,AMBER),badge(678,120,'电源',BLUE),txt(656,151,'避开加水操作区',14,BLUE),line(80,418,770,418,INK),txt(425,446,'宽1600–1800 / 深550–600 / 高850–900 mm，均为研究起点',18)]
    p += [txt(425,357,'不设水槽、给水口、排水口；废水盘取出后到中厨处理',16,AMBER),'</g></svg>']
    return ''.join(p)

def cabinet_svg():
    p=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 450" role="img" aria-label="四组柜体检修关系示意"><g font-family="Microsoft YaHei, sans-serif">']
    for x,title in [(20,'J01 水槽＋洗碗机'),(300,'J02 冰箱／可选蒸烤柜'),(580,'J03 叠放洗烘'),(860,'J04 机器人基站')]:
        p += [txt(x+120,28,title,18),rect(x,48,240,267,'#f9f8f2')]
    p += [rect(30,70,125,147,'#dfe9e0'),txt(92,100,'水槽柜',16),txt(92,134,'阀门／插座可达',13),txt(92,164,'净水＋分类桶',13),txt(92,194,'厨余仅预留',13),rect(164,70,86,147,'#eee4d2'),txt(207,125,'洗碗机',15),txt(207,158,'600级',14),line(164,227,250,227,AMBER,'6 4',3),txt(140,272,'门全开＋整机前抽 ↓',15,AMBER)]
    p += [rect(310,70,105,186,'#dfe9e0'),txt(362,141,'冰箱',17),txt(362,178,'铰链侧余量',12),rect(432,70,97,186,'#eee4d2'),rect(440,119,81,70,'#fff'),txt(480,149,'蒸烤箱',14),txt(480,177,'条件位',12,AMBER),txt(420,289,'两者为模块示意，非指定并排',12,AMBER)]
    p += [rect(630,62,140,113,'#dfe9e0'),rect(630,184,140,113,'#dfe9e0'),'<circle cx="700" cy="118" r="32" fill="white" stroke="#82958c"/><circle cx="700" cy="240" r="32" fill="white" stroke="#82958c"/>',txt(700,124,'烘',17),txt(700,246,'洗',17),line(630,179,770,179,AMBER,'',5),txt(822,113,'阀',13),txt(822,137,'电',13),txt(822,161,'可达',12),txt(700,338,'连接件＋顶部拆机包络',14,AMBER)]
    p += [rect(888,78,181,105,'#dfe9e0'),txt(978,128,'收纳柜',17),rect(911,204,131,94,'#eee4d2'),txt(976,240,'基站',17),txt(976,268,'低位开放',13),line(894,314,1060,314,AMBER,'6 4',3),txt(980,341,'托盘／尘袋抽取方向依型号',13,AMBER)]
    p += [txt(143,371,'邻柜检修；管线不挡抽机',14),txt(420,371,'开孔与通风严格按厂家',14),txt(700,371,'过滤器可取；两机分别搬出',14),txt(978,371,'前场不能兼作固定储物',14),txt(560,423,'图示只表达设备与检修关系；所有宽深高、开孔、散热和维修包络以候选型号安装图＋现场净尺寸锁定。',15,AMBER),'</g></svg>']
    return ''.join(p)

def write_csv(name, headers, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f);writer.writerow(headers);writer.writerows(rows)

def main():
    OUT.mkdir(exist_ok=True)
    drawings = [('01-furniture.svg','家具与通行概念图'),('02-alterations-review.svg','拆改核验示意图'),('03-services.svg','水电功能点位示意图')]
    svgs={}
    for filename, title in drawings:
        svgs[filename]=floorplan(title)
        (OUT/filename).write_text(svgs[filename],encoding='utf-8')
    cabinet=cabinet_svg()
    (OUT/'04-cabinet-access.svg').write_text(cabinet,encoding='utf-8')
    coffee=coffee_svg()
    (OUT/'05-coffee-sideboard.svg').write_text(coffee,encoding='utf-8')
    source_data=base64.b64encode(SOURCE.read_bytes()).decode()
    pages=[]
    pages.append(page('00','三卧保留，让餐厨与家务更顺手','A、B、D三间卧室 · 原餐厅独立书房 · 可关闭中厨＋C开放用餐备餐 · 四人日常、六人偶尔',f'''
    <div class="overview-grid"><div class="source-panel"><img class="source" src="data:image/jpeg;base64,{source_data}" alt="用户新提供的1170×874清晰户型图，包含A/B/C/D、原餐厅、厨房和两个阳台"/><p class="caption">采用清晰图及用户补充图例：粗线为承重墙，细线为非承重墙。粗线承重墙保留；细墙拆改边界与隐藏管线需落图。新旧图数值不混用，图注尺寸仍非实测净尺寸。</p></div><div>
    <div class="statrow"><div><strong>3＋1</strong><span>三卧＋单人书房</span></div><div><strong>4→6</strong><span>可延伸独立餐桌</span></div><div><strong>0</strong><span>新增C区水槽／独立岛台</span></div></div>
    {card('已确定的空间决策','<p>已采用M02：打开C西侧非承重隔墙，与客厅形成宽开口共享餐区。C配置冰箱、食品收纳及干备餐台，餐桌放在两区交界。粗线承重部分、梁柱、C/D隔墙及东侧外墙窗保留；中厨继续可关闭。</p><p>原餐厅部分隔书房，保住A、B通道；三卧两卫不换位。咖啡餐边柜H03仍在客厅西墙北段，水箱咖啡机仅接电。</p>')}
    {card('新图校核后的关键修正','<p>C现门在北侧偏西，厨房现门在其西墙南端，门外是通行交汇区。撤销这里的机器人旧候选点，R01改为室内重新选址任务。阳台B经厨房出入，仍不作为默认全屋清洁基站。</p>','accent')}
    {card('本册如何使用','<p>01 家具 → 02 拆改 → 03 水电 → 04 设备 → 05 柜体 → 06 验收 → 07 待核验 → 08 新图核对 → 09 咖啡柜与上下水。</p><p>R4将C西侧宽开口联通更新为采用方案；家具及水电图表达改后空间，拆改图单独标出拟拆细墙段。实际拆除范围仍须现场放线。</p>')}
    </div></div><div class="notice">当前完成的是可审阅的概念深化包。缺少实测、结构资料和设备型号，不能出具“经核验的拆改图”或可直接施工的水电尺寸图。</div>'''))

    dims_short=[[r[0]+' '+r[1],r[2],r[4]] for r in DIMENSIONS[:6]]
    pages.append(page('01','家具布局与通行','图按原图上下左右关系绘制；家具符号不按比例。尺寸单位：mm。',f'''
    <div class="plan-grid"><div class="drawing">{svgs['01-furniture.svg']}</div><div>
    <div class="legend"><span class="dot green"></span>通行及联通方案 <span class="dot blue"></span>玻璃/窗/中厨分隔；灰虚线为原门洞</div>
    {table(['家具／区域','规划目标','落位条件'],dims_short,'compact')}
    {card('书房先让出通道','<p>新图餐厅14.4㎡，右侧分别通A、B；下侧留绕开公卫的入口过渡。隔断框、门扇、柜门不计入净宽，玻璃平开门优先向书房内开。14.4㎡不能全围作书房；图中未见直接外窗，仍需借光和关门通风。</p>')}
    {card('客厅与三卧','<p>左侧沙发宽约2600–3000；TV只在实测可用墙段落位，避开D房门和餐区。小型可移动茶几；不增加厚地毯及零散落地柜。</p><p>床垫候选：A 1800×2000；B 1200–1500×2000；D 1500×2000。另加床架包络、床侧通道和衣柜开门空间。衣柜深约600、尽量到顶。</p>')}
    {card('H03 咖啡餐边柜','<p>优先客厅西墙北段、沙发北侧，宽1600–1800、深550–600、高850–900起研。柜前站人操作后主通道仍可用；若不够，缩短柜体或调整沙发，不挤厨房/C门厅。仅接电，取水与清洗在中厨。</p>')}
    {card('共享餐区与六人放样','<p>C西侧打开后，餐桌跨两区借位，C的冰箱/备餐台可直接服务餐桌；原C北门保留门洞、取消房门门扇。摆齐六把实际座椅，测试就座、拉椅及端盘经过，再全开冰箱和洗碗机门记录最窄通道。</p>','accent')}
    <p class="caption">本图为已采用宽开口方案，西侧原细墙拆除线另见02图；保留端部仅表达边界原则，不代表实测墙垛尺寸。C/D隔墙及C东窗保留，窗侧低柜须测窗台；R01仍需合法水路与通行共同选址。</p>
    </div></div>'''))

    pages.append(page('02','已采用：C西侧宽开口联通客厅','原图粗线承重、细线非承重。M02作为采用方案；拟拆线仅限非承重段，粗墙、梁柱、C/D隔墙及东侧外墙窗保留。',f'''
    <div class="plan-grid"><div class="drawing">{svgs['02-alterations-review.svg']}</div><div>
    {table(['编号','设计意图','开工前证据'],[
    ['M01','原餐厅部分玻璃围合为单人书房','A/B门洞实测、净通道、门扇包络、固定基层、关门通风和空调方案'],
    ['M02','已采用：打开C西侧非承重隔墙，宽开口联通客厅','现场标定净开口及拆除边界；保留粗墙、梁柱、C/D隔墙和东侧外墙窗；核隐藏管线'],
    ['M03','厨房与C连接处保留可关闭分隔，水火留原中厨','门洞位置、尺寸及门上构造待落图；保留粗墙端部并满足当地燃气分隔要求'],
    ['M04','阳台B家政设备适配','保温防冻、合规污水管、承载、电源、叠放高度与搬出路径']
    ])}
    {card('宽开口边界与原C门处理','<p>设计方向已确定为打开C西侧细墙，无需再比较保留封闭C房的方案。现场根据粗墙端部、梁柱和管线锁定可实施宽度，不将“联通”理解为连结构边界一起拆净。原C北门保留门洞、取消房门门扇，减少通行冲突。</p>')}
    {card('中厨继续可关闭','<p>灶具、烟机、水槽和洗碗机仍在中厨，C不新增水槽或炒菜区。M03若受现场条件限制，保留原中厨入口连接共享餐区；无论采用哪个入口，均落实完整、可关闭的中厨分隔。</p>')}
    {card('若阳台B不满足设备条件','<p>阳台B狭长，需重点核门扇、端部窗及设备前场，不能仅凭3.2㎡确认叠放可行。不满足则在中厨/生活阳台入口附近室内重新统筹，保住烹饪面和通道。R01已撤销门外交汇区旧点，独立重选。</p>','accent')}
    <div class="notice small">图例已确认，粗墙保留。细墙段仍需标清管线、门上构造和施工边界；非承重不等于可以连同相邻粗墙一起整面拆除。</div>
    </div></div>'''))

    points_short=[[r[0]+' '+r[2],r[1],r[3]+'；'+r[4]] for r in POINTS if r[0] not in ['L02','C03','H02']]
    points_short[-1]=['H03 咖啡餐边柜','客厅西墙北段','仅电源与台面照明；不接上下水，手动加水、倒废水']
    pages.append(page('03','水电功能点位与负荷任务','编号对应可编辑《水电点位表.csv》。点位仅定位区域；没有虚构标高、管线路径、线径或断路器规格。',f'''
    <div class="plan-grid services"><div class="drawing">{svgs['03-services.svg']}<div class="notice small">蓝色：功能区需求；橙色：条件/待核。R01文字为重新选址任务，并非所在位置可安装。新图未给出烟道、立管或真实水电点。</div></div><div>
    {table(['点号／用途','候选区域','接口与用电需求'],points_short,'tiny')}
    {card('电气与给排水设计必须补齐','<p>收集设备额定/最大功率与同时使用场景，核入户容量、回路、接地和漏电保护；不能凭本表给所有设备套同一插座或回路。</p><p>每台上下水设备有可操作阀门；电源避开漏水路径。排水按设备要求核高差、防回流及固定方式；禁止默认向雨水管排污。</p>')}
    <p class="caption">C03仅收纳；H02灯位随桌位；L02需保温、上下水及全天通行。H03无固定水路；各电器给水/排水详见第09页，完整15点见CSV。</p>
    </div></div>'''))

    equip_short=[[r[0]+' '+r[1],r[2],r[3],r[4]+'；'+r[5],r[6]] for r in EQUIPMENT]
    pages.append(page('04','设备候选与采购前锁定','当前未指定品牌、型号和价格。柜体尺寸须以候选型号安装图为依据，预留值不能用于下单。',f'''
    {table(['设备','位置','规划起点','必须锁定','使用／维修验收'],equip_short,'equipment')}
    <div class="threecol">
    {card('优先配置','<p>全尺寸洗碗机、自动投放洗衣机＋热泵烘干机、满足安装条件的自动上下水机器人。先解决位置、供排水和维修，再选具体型号。</p>')}
    {card('保留余地','<p>厨余机先预留；蒸烤箱先研究中厨600级高柜，无法保留操作台则不锁位。现有空调采暖检查合格保留。</p>')}
    {card('不列为默认','<p>C区新水槽、独立岛台、全屋软水、复杂智能联动。C的发热排汽设备只在开放且满足厂家条件的操作位使用。</p>')}
    </div>'''))

    pages.append(page('05','柜体安装与检修关系','先锁定整机与维修包络，再画柜体。下图是模块关系示意，不表示四组柜体能按图尺寸放入现场。',f'''
    <div class="cabinet-drawing">{cabinet}</div>
    {table(['模块','柜图必须标注','必须能直接完成的动作'],[
    ['J01 水槽柜与洗碗机','净水、存水弯、分类桶、厨余预留的立面/剖面；管线可达位置；门和踢脚避让','关阀、换芯、取桶、拆存水弯；洗碗机不拆台面即可前抽'],
    ['J02 冰箱及蒸烤条件柜','冰箱门铰侧/顶部/背部余量；蒸烤开孔、承重、厂家进出风路径；邻柜电源','冰箱抽屉完全拉出；整机可移出；蒸烤箱独立拆出且不先拆其他整机'],
    ['J03 洗烘叠放柜','整机含管线突出深度；原厂连接件；顶部拆装和前场搬出；阀门电源可达','清绒毛、取水盒（如有）、清洗衣机过滤器；上下两机分别拆出'],
    ['J04 机器人低位柜','坡道与转向前场；抽盘、尘袋/清洁液更换方向；接管限制；离地关系','厨房关门照常出入；不搬其他家具就能清污水盘、换袋、关水、抽出基站']
    ],'compact')}
    <div class="twocol">
    {card('柜体做法服务于少家务','<p>厨房下柜优先抽屉；餐具靠洗碗机和餐桌，食品靠冰箱，清洁耗材靠基站。家具封底或留足机器人完整出入空间，避免半高积灰缝。</p>')}
    {card('表面与日常维护','<p>减少开放格、细密装饰线及复杂吊顶。台面与水槽交接易擦拭且可重新打胶。绒毛过滤器、机器人污水盘仍须清理，维护面不能被装饰板封死。</p>')}
    </div>'''))

    pages.append(page('06','现场放样与使用验收','所有尺寸目标是设计输入，当前未进行现场测量或运行测试。下列场景须逐项记录“结果＋实测值/照片＋整改”。',f'''
    {table(['场景','具体操作','通过条件'],[
    ['通行与书房','在地面放出隔断框、门扇和桌椅；从入户分别走到A/B/D','不穿书房；卧室通道目标1000–1100mm按最窄处记录；开门不互撞'],
    ['四人日常／六人来客','实物或等大样板摆桌椅；延伸到约1800；有人坐及拉椅时端盘经过','主要通道争取1000–1100mm；实际状态可通行，不能仅测收椅状态'],
    ['冰箱与洗碗机','分别全开门、拉出冰箱抽屉；另测常见同时使用组合','不撞桌椅；主要通道仍可使用；不通过调整桌柜后复测'],
    ['中厨关闭','关厨房门，按设计工况运行烟机并烹饪/模拟排烟；专业方检查补风','符合当地燃气/通风要求；排烟与补风有效，门可正常关闭'],
    ['封闭书房','关门、有人办公，开启照明与温控/通风；记录时段、人数和测量数据','专业设计给出的照度、空气交换及温度目标有记录支持；不以“有空调”替代通风'],
 ['清洁机器人','R01完成重新选址后，从基站出发；厨房关门，往返客餐厅及A/B/D干区并完成上下水','不跨受阻门槛、不被桌椅卡住；水路无漏水/回流；湿区不为机器人取消挡水'],
    ['设备维修','按J01–J04实际演示开阀、取盘、换芯/袋、过滤器清理及拆机路径','无需破坏柜体和台面；设备可独立拆出，搬出路径连续'],
    ['漏水与实体控制','在各探测点按厂家方式模拟；验证报警及可选关阀；断网后操作灯/窗帘','各点有效；手动关水可达；自动化失效后仍有实体直接操作'],
    ['湿区与干区','核卫生间防水/挡水、阳台排水及干区高差；执行当地要求的防水验收','防水满足要求；干区减少门槛，未把污水接入雨水管']
    ,['H03咖啡柜','柜前站人，演示取水箱、加豆、前抽废水盘；往返中厨取水及清洗','不搬整机、不遮插座、不侵主通道；无需固定水路，台面滴水可直接擦净']
    ])}
    <div class="threecol">
    {card('设计交付','<p>①实测家具电器尺寸平面图<br/>②附结构与审批依据的拆改图<br/>③负荷、回路与给排水点位图<br/>④型号对应柜体立剖面及检修图</p>')}
    {card('下单前共同复核','<p>设计师、柜体商和设备安装方在同一版图上核对型号、整机包络、开门投影、散热及维修空间；变更设备型号后同步改图。</p>')}
    {card('业主重点观察','<p>餐具能顺手卸入柜，常用电器不占净操作台，基站和滤芯伸手可取；清洁路线连续，收纳围绕实际使用位置。</p>')}
    </div>'''))

    pages.append(page('07','待核验事项与资料交接','每项由负责专业补齐证据后关闭；本册不将概念判断记录为现场验收通过。',f'''
    {table(['编号／负责方','核验内容','应取得证据','影响的交付／当前状态'],[[r[0]+' '+r[1],r[2],r[3],r[4]+'；'+r[5]] for r in CHECKS],'compact')}
    <div class="twocol">
    {card('本地交付文件','<p>方案册.html／方案册-R4.pdf：完整可打印方案。<br/>01–05 SVG：家具、拆改、水电、柜体及咖啡餐边柜。<br/>七份UTF-8 CSV：含电器上下水表，可在表格软件中编辑。<br/>build_package.py：文档生成源文件。</p>')}
    {card('下一版必须补齐的输入','<p>带净尺寸/门窗/标高的测绘图、结构与用途核查、燃气条件、阳台和排水资料、入户用电容量、候选设备安装图。收到后才能锁定开口、桌柜和水电标高。</p>')}
    </div>'''))

    pages.append(page('08','新图核对：数值、门窗与落位修订','参考图：IMG20260907-094631119.jpg，1170×874像素。以图上N箭头为准，上北下南；数值识读不等于现场实测。',f'''
    <div class="twocol"><div>
    {table(['空间','新图面积 / ㎡','对方案的影响'],NEW_AREAS,'compact')}
    <p class="caption">11项标签求和为131.3㎡，仅为标签算术合计；不据此计算套内面积、公摊或得房率。176㎡仍来自任务描述。新旧图部分面积和外围尺寸不同，不可混用。</p>
    {card('书房的方向成立，围合边界仍需测量','<p>原餐厅14.4㎡；A入口在上方靠右，B入口在右侧下段。隔断要同时保留通往两门的路径及下方入口过渡。新图仍未画餐厅直接外窗，玻璃借光和独立通风需求不变。</p>')}
    {card('更正上一版A窗方向','<p>A窗在南侧偏东，即图中下沿右段，R1画在上沿有误，已修正。B、C东侧及D南侧是外凸窗轮廓；先测窗台高度、进深和开启方式，再定窗侧柜，不能把外凸区默认计入柜深。</p>','accent')}
    </div><div>
    {table(['尺寸线对应区域','图注 / mm','使用边界'],NEW_SPANS,'compact')}
    {card('现状与R4采用方案','<p>现状C房门在北侧偏西，厨房门在西墙南端，阳台B门在厨房东侧南段。R4已采用C西侧非承重墙宽开口；原C北门洞保留、门扇取消。中厨连接口保留可关闭分隔，C/D隔墙及东侧外墙窗不动。</p>')}
    {card('R01旧点撤销，保持门厅畅通','<p>旧基站候选点靠近C与厨房入口交汇处，撤销其固定落位。重新寻找厨房关门仍可达的室内位置，并同时满足合法供排水和前场。阳台B洗烘先核门扇、端部窗及检修，不仅看面积。</p>','accent')}
    {card('C餐桌继续借用客厅','<p>条件算例：以图注进深2998减600深柜、850桌宽，两侧合计仅余1548，且尚未扣墙厚及施工影响。不能据此认定六人桌椅已放得下；维持独立餐桌借客厅、无岛台的方向。</p>')}
    </div></div>'''))
    pages.append(page('09','咖啡餐边柜与电器上下水','已确认：水箱式咖啡机，手动加水、倒废水。H03仅接电；其余设备按给水和排水分别核对，未定型号不预埋接口。',f'''
    <div class="twocol"><div>
    <div class="coffee-drawing">{coffee}</div>
    {card('落位：客厅西墙北段、沙发北侧','<p>作为餐厅/客厅共用餐边柜，服务咖啡与杯具收纳，独立于C的≥1200mm净备餐面。柜体以封闭抽屉/柜门为主，设备在开放台面运行；不做把整机闷住的电器格。</p><p>先把入户门、玄关转弯、柜前站人和沙发一起放样，主通道争取1000–1100mm。标注的是候选墙段，未确认1600–1800mm整柜已能放下；不足时缩柜或重排沙发。</p>')}
    {card('加水、废水与日常清洁','<p>中厨取水 → 咖啡机水箱；废水盘取出 → 中厨水槽处理；杯具回中厨清洗。H03不设水槽、给水管或排水管。水质按咖啡机要求选用，不默认所有净水都适用。</p><p>水箱上抽/侧抽、豆仓开盖与废水盘前抽均按型号留空；台面用易擦拭耐水材料，设置可取接水托盘。电源可达，避开加水滴洒和蒸汽路径。</p>','accent')}
    {card('只留所需设备','<p>咖啡机＋磨豆机作为基础，其他设备按实际清单增加固定插座并核负荷。暂不增加直饮机或柜内净水器，也不把自动上下水机器人塞进无水路的咖啡柜。</p>')}
    </div><div>
    {table(['设备','固定给水','排水/废水处理','位置与锁定条件'],WATER_NEEDS,'compact')}
    <div class="notice small">需要水路的设备：先确认可接入系统、阀门、电源和检修，再定柜。手动水箱设备：另留加水/取箱和倒废水空间。烘干机、空调即使无给水，也不能遗漏冷凝水处理。</div>
    </div></div>'''))
    css='''
    *{box-sizing:border-box}body{margin:0;background:#e6e9e3;color:#233d36;font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;font-size:12px;line-height:1.6}
    nav{max-width:1480px;margin:18px auto;display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:0 20px}nav a{color:#287361;text-decoration:none}button{background:#233d36;color:white;border:0;padding:10px 20px;border-radius:5px;cursor:pointer;font:inherit}
    .page{width:420mm;min-height:297mm;margin:20px auto;padding:12mm 15mm 14mm;background:#fffef9;position:relative;box-shadow:0 4px 24px #233d3610;break-after:page}header{display:flex;justify-content:space-between;border-top:3px solid #233d36;padding-top:9px;font-size:11px;color:#69786c;letter-spacing:.04em}.eyebrow{font-weight:700}h1{font-size:30px;line-height:1.2;margin:18px 0 8px;font-weight:600}h1 b{font-size:24px;color:#999f81;margin-right:18px;font-weight:400}.subtitle{font-size:13px;color:#6b7769;margin:0 0 20px}h3{font-size:16px;margin:0 0 7px}p{margin:0 0 8px}.card{border-top:1px solid #d6ddd0;padding:13px 0 6px;margin-top:12px}.card p:last-child{margin-bottom:0}.accent{background:#eff4eb;border:0;padding:15px 17px}.notice{background:#f3e9d9;border-left:3px solid #ac6537;padding:12px 16px;margin-top:18px;font-size:13px}.notice.small{font-size:12px}.caption{font-size:11px;color:#778070;line-height:1.65;margin-top:12px}.overview-grid{display:grid;grid-template-columns:1.05fr 1fr;gap:32px}.source-panel{padding:18px;background:#f4f3eb;align-self:start}.source{display:block;width:100%;height:520px;object-fit:contain;image-rendering:auto}.statrow{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:6px 0 18px}.statrow div{background:#eef1e7;padding:14px}.statrow strong{font-family:Georgia,serif;font-size:42px;display:block;line-height:1.2}.statrow span{font-size:12px}.plan-grid{display:grid;grid-template-columns:43% 1fr;gap:28px}.drawing{background:#f8f8f0;padding:4px 10px;align-self:start}.drawing svg{width:100%;height:785px;display:block}.legend{font-size:11px;margin-bottom:14px;display:flex;align-items:center;gap:8px}.dot{width:9px;height:9px;border-radius:50%;display:inline-block}.green{background:#287361}.blue{background:#427f9a}.amber{background:#ac6537}table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:12px}th{text-align:left;background:#e8ede2;font-weight:600;border-top:1px solid #b9c5b5;padding:10px 11px}td{vertical-align:top;border-bottom:1px solid #dee4d8;padding:10px 11px;overflow-wrap:anywhere}tr{break-inside:avoid}tbody tr:nth-child(even){background:#fafaf4}.compact{font-size:11.5px}.compact td,.compact th{padding:8px 10px}.tiny{font-size:11px}.tiny td,.tiny th{padding:7px 9px}.tiny th:first-child{width:23%}.tiny th:nth-child(2){width:24%}.equipment{font-size:11.5px}.equipment th:nth-child(1){width:13%}.equipment th:nth-child(2){width:17%}.equipment th:nth-child(3){width:20%}.equipment th:nth-child(4){width:29%}.equipment th:nth-child(5){width:21%}.twocol{display:grid;grid-template-columns:1fr 1fr;gap:28px}.threecol{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}.cabinet-drawing{background:#f6f6ee;margin-bottom:18px;padding:8px 12px}.cabinet-drawing svg{width:100%;height:380px;display:block}.services .drawing svg{height:715px}footer{position:absolute;bottom:7mm;left:15mm;right:15mm;display:flex;justify-content:space-between;border-top:1px solid #d8dfd1;padding-top:7px;font-size:10px;color:#7d8574}
    .coffee-drawing{background:#f6f6ee;padding:10px}.coffee-drawing svg{display:block;width:100%;height:330px}
    @page{size:A3 landscape;margin:0}@media print{body{background:white}nav{display:none}.page{margin:0;box-shadow:none;width:420mm;height:297mm;min-height:0;overflow:hidden;print-color-adjust:exact;-webkit-print-color-adjust:exact}.page:last-child{break-after:auto}}
    @media screen and (max-width:1000px){.page{width:96%;min-height:0;padding:24px;margin:16px auto}.overview-grid,.plan-grid{grid-template-columns:1fr}.source{height:auto;max-height:500px}.drawing svg{height:auto;max-height:800px}.threecol,.twocol{grid-template-columns:1fr}footer{position:static;margin-top:30px;gap:12px}.statrow strong{font-size:32px}h1{font-size:25px}table{font-size:11px}th,td{padding:7px 6px}.cabinet-drawing{overflow-x:auto}.cabinet-drawing svg{min-width:800px}.legend{flex-wrap:wrap}header{gap:15px}}
    '''
    document='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>丽水嘉园176㎡｜三卧＋独立书房＋开放餐厨方案册 R4</title><style>'+css+'</style></head><body><nav aria-label="方案册导航"><button type="button" onclick="window.print()">打印 / 另存PDF</button>'+''.join(f'<a href="#p{n:02d}">{n:02d} {name}</a>' for n,name in enumerate(['方案','家具','拆改','水电','设备','柜体','验收','待核验','新图核对','咖啡与水路']))+'</nav><main>'+''.join(pages)+'</main></body></html>'
    (OUT/'方案册.html').write_text(document,encoding='utf-8')
    write_csv('家具尺寸表.csv',['编号','家具或空间','尺寸目标_mm','尺寸性质','锁定条件'],DIMENSIONS)
    write_csv('设备预留表.csv',['编号','设备','候选位置','规划起点_非下单尺寸','型号安装图需锁定','水电及检修条件','验收动作','候选品牌型号','安装图版本','最终柜体尺寸_mm'],[r+['待选型','待提供','待实测及选型'] for r in EQUIPMENT])
    write_csv('水电点位表.csv',['点号','候选区域','用途','给排水要求','电气及控制要求','检修及限制','水平定位_mm','标高_mm','回路及保护','状态'],[r+['待实测','待设备/柜图锁定','待负荷计算','概念预留'] for r in POINTS])
    write_csv('现场核验表.csv',['编号','建议负责方','待核内容','证据或通过记录','影响交付','状态','实测值或结论','证据链接或图号','签认人','日期'],[r+['','','',''] for r in CHECKS])
    write_csv('新图面积标注.csv',['空间','新图面积_平方米','设计影响'],NEW_AREAS)
    write_csv('新图尺寸标注.csv',['尺寸线对应区域','图注_mm_非实测净尺寸','使用边界'],NEW_SPANS)
    write_csv('电器上下水表.csv',['设备','固定给水需求','排水或废水处理','位置与锁定条件'],WATER_NEEDS)
    (OUT/'README.md').write_text('''# 丽水嘉园176㎡ · 概念深化包

已更新为R4版10页A3横向方案册。采用方案：打开C西侧非承重隔墙，以宽开口与客厅形成共享餐区；保留粗线承重部分、梁柱、C/D隔墙及C东侧外墙窗。原C北门洞保留、取消门扇，中厨保持可关闭。A/B/D保留卧室，原餐厅部分隔书房；C配置冰箱、食品收纳与干备餐台，餐桌在两区交界借位。无C区新增水槽、无独立岛台。

- 打开 `方案册.html` 可离线阅读并打印；本版PDF为 `方案册-R4.pdf`，原 `方案册.pdf` 为历史版本。若PDF受本机企业文件保护，请按组织允许的方式阅读，详见文件保护说明及verification.json。
- `01-furniture.svg`：家具、功能关系与通行概念。
- `02-alterations-review.svg`：已采用M02西侧宽开口的拟拆线与保留边界；具体开口尺寸尚待现场标定，不是已核验施工图。
- `03-services.svg`：功能点位；精确位置、标高和回路尚待锁定。
- `04-cabinet-access.svg`：设备安装与检修关系。
- `05-coffee-sideboard.svg`：H03水箱式咖啡餐边柜，手动加水、倒废水，仅接电。
- 七份CSV用UTF-8 BOM编码，可在Excel中编辑，尺寸单位mm；新图面积表单位为㎡。新增电器上下水表分别列出给水、排水及水箱处理。

## 依据与边界

R4依据用户方案、新图 `IMG20260907-094631119.jpg`（1170×874像素）、粗细墙图例，以及采用C西侧宽开口联通的决定。粗线承重墙保留，M02落实所标非承重段开口边界，M03落实可关闭的中厨分隔；端部、梁柱、管线及净开口宽度待现场标定。旧图 `standard_ef6b1946-6bcb-4410-b852-cf986e432b70.png.533x400.jpg` 保留归档，数值不混用。176㎡来自任务描述，面积标签合计131.3㎡不用于测算套内、公摊或得房率。SVG为非比例图，保留端部和家具均未经过实测尺寸校核。

R2将餐厅13.9㎡更新为新图14.4㎡，纠正R1误画在北侧的A窗（应为南侧偏东），标出B/C东侧及D南侧外凸窗。C现门位于北侧偏西，厨房门在西墙南端；C西墙朝客厅开放仍须拆改核验。由于门外交汇空间需要保通行，撤销R1厨房门外机器人候选点；R01仅为室内重新选址任务，图中文字不代表可安装点位。阳台B经中厨出入，仍不默认安排全屋机器人基站。洗烘还须核狭长净宽、门扇、端部窗、保温防冻、承载、合规排污和搬出条件。

R3新增H03咖啡餐边柜，优先客厅西墙北段、沙发北侧，宽1600–1800、深550–600、高850–900mm为规划起点，需与玄关、柜前站人和沙发共同放样。用户已确认水箱式咖啡机、手动加水和倒废水，H03仅接电，不预留固定上下水或水槽；中厨负责取水、清洗和废水处理。C的净备餐面与咖啡设备分开。所有电器按给水/排水分别核查，不能因只有电源位置就认定可安装。

本包未完成现场结构、用途、燃气或设备运行核验，也不是施工、采购或拆墙依据。`现场核验表.csv`列出应补资料及负责专业，全部保持待核验状态。最终施工图须由负责专业在实测及相应核验完成后出具。

## 更新与生成

使用Python标准库运行 `python deliverables/build_package.py` 重建HTML、SVG及CSV（会覆盖同名生成文件；若已人工更新CSV，请先保存副本或同步修改源数据）。PDF及检查由 `python deliverables/render_verify.py` 生成，需要本机Playwright、可用Chromium/Edge与PyMuPDF。通过 `FURNISH_BROWSER` 可指定浏览器路径。
''',encoding='utf-8')
    print(json.dumps({'pages':len(pages),'equipment':len(EQUIPMENT),'points':len(POINTS),'checks':len(CHECKS),'out':str(OUT)},ensure_ascii=False))

if __name__=='__main__':
    main()
