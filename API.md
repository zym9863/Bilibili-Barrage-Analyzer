# API示例

from bilibili_api import * 

v = video.Video("BV1P24y1a7Lt") # 初始化视频对象 

sync(ass.make_ass_file_danmakus_protobuf( 
obj=v, # 生成弹幕文件的对象 
page=0, # 哪一个分 P (从 0 开始) 
out="protobuf.ass" # 输出文件地址 
)) 

sync(ass.make_ass_file_danmakus_protobuf( 
obj=v, # 生成弹幕文件的对象 
page=0, # 哪一个分 P (从 0 开始) 
out="xml.ass" # 输出文件地址 
)) 

test.ass 即为弹幕文件 

make_ass_file_danmakus_protobuf 代表从 protobuf 格式的新接口中抓取弹幕制成 ass 
make_ass_file_danmakus_xml 代表从旧的 xml 接口中抓取弹幕制成 ass


# API文档

async def make_ass_file_danmakus_protobuf() 
生成视频弹幕文件 

弹幕数据来源于 protobuf 接口 

编码默认采用 utf-8 

name type description 
obj Union[Video,Episode,CheeseVideo] 对象 
page int, optional 分 P 号. Defaults to 0. 
out str, optional 输出文件. Defaults to "test.ass" 
cid int | None, optional cid. Defaults to None. 
date datetime.date, optional 获取时间. Defaults to None. 
font_name str, optional 字体. Defaults to "Simsun". 
font_size float, optional 字体大小. Defaults to 25.0. 
alpha float, optional 透明度(0-1). Defaults to 1. 
fly_time float, optional 滚动弹幕持续时间. Defaults to 7. 
static_time float, optional 静态弹幕持续时间. Defaults to 5. 
async def make_ass_file_danmakus_xml() 
生成视频弹幕文件 

弹幕数据来源于 xml 接口 

编码默认采用 utf-8 

name type description 
obj Union[Video,Episode,Cheese] 对象 
page int, optional 分 P 号. Defaults to 0. 
out str, optional 输出文件. Defaults to "test.ass". 
cid int | None, optional cid. Defaults to None. 
font_name str, optional 字体. Defaults to "Simsun". 
font_size float, optional 字体大小. Defaults to 25.0. 
alpha float, optional 透明度(0-1). Defaults to 1. 
fly_time float, optional 滚动弹幕持续时间. Defaults to 7. 
static_time float, optional 静态弹幕持续时间. Defaults to 5.