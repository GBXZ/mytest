from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechatpy import parse_message,create_reply
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.utils import check_signature
from wechatpy import WeChatClient
from cartest.models import Carinfo
'''
自定义微信公众号菜单，具体可参照wechatpy文档
'''
client = WeChatClient('wx65ecd82cb1ce0559','9c5acf854e9fe944657c775ced596e81')
client.menu.create(
        {
        'button':[
                {
                'type':'click',
                'name':'汽车查询',
                'key':'car_find'
                },
        {
                'type':'view',
                'name':'车辆订单',
		'url':'http://119.29.160.42/cartest/index/'
        }
        ]
        }
)
'''
首先进行连接验证,验证正确返回echostr
'''
WECHAT_TOKEN = 'slh201008'
@csrf_exempt
def weixin(request):
	if request.method == 'GET':
		signature = request.GET.get('signature','')
		timestamp = request.GET.get('timestamp','')
		nonce = request.GET.get('nonce','')
		echo_str = request.GET.get('echostr','')
		try:
			check_signature(WECHAT_TOKEN,signature,timestamp,nonce)
		except InvalidSignatureException:
			echo_str = 'error'
		response = HttpResponse(echo_str,content_type='text/plain')
		return response
	elif request.method == 'POST':
		msg = parse_message(request.body)
		if msg.type =="text":
			if Carinfo.objects.filter(car_number=msg.content):
				car_msg = Carinfo.objects.filter(car_number=msg.content)
				for p in car_msg:
					car_state = p.car_state
				if car_state == 'dj':
					car_state = "待检测"
					reply = create_reply(car_state,msg)
				if car_state == 'jc':
					car_state = "检测中"
					reply = create_reply(car_state,msg)
				if car_state == 'yj':
					car_state = "检测完毕"
					reply = create_reply(car_state,msg)
			else:
				reply = create_reply('您输入的车辆不存在',msg)
		elif msg.type == 'image':
			reply = create_reply('B',msg)
		elif msg.type == 'voice':
			reply = create_reply('C',msg)
		else:
			reply = create_reply('D',msg)
		response = HttpResponse(reply.render(),content_type='application/xml')
		return response
	else:
		logger.info('----------------')

# Create your views here.
