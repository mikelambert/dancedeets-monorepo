# -*-*- encoding: utf-8 -*-*-

import re

from ..nlp import re_flatten

prefectures = [
    u'愛知県',
    u'秋田県',
    u'青森県',
    u'千葉県',
    u'愛媛県',
    u'福井県',
    u'福岡県',
    u'福島県',
    u'岐阜県',
    u'群馬県',
    u'広島県',
    u'北海道',
    u'兵庫県',
    u'茨城県',
    u'石川県',
    u'岩手県',
    u'香川県',
    u'鹿児島県',
    u'神奈川県',
    u'高知県',
    u'熊本県',
    u'京都府',
    u'三重県',
    u'宮城県',
    u'宮崎県',
    u'長野県',
    u'長崎県',
    u'奈良県',
    u'新潟県',
    u'大分県',
    u'岡山県',
    u'沖縄県',
    u'大阪府',
    u'佐賀県',
    u'埼玉県',
    u'滋賀県',
    u'島根県',
    u'静岡県',
    u'栃木県',
    u'徳島県',
    u'東京都',
    u'鳥取県',
    u'富山県',
    u'和歌山県',
    u'山形県',
    u'山口県',
    u'山梨県',
]

cities = [
    u'名古屋市',
    u'豊橋市',
    u'岡崎市',
    u'一宮市',
    u'瀬戸市',
    u'半田市',
    u'春日井市',
    u'豊川市',
    u'津島市',
    u'碧南市',
    u'刈谷市',
    u'豊田市',
    u'安城市',
    u'西尾市',
    u'蒲郡市',
    u'犬山市',
    u'常滑市',
    u'江南市',
    u'小牧市',
    u'稲沢市',
    u'東海市',
    u'大府市',
    u'知多市',
    u'知立市',
    u'尾張旭市',
    u'高浜市',
    u'岩倉市',
    u'豊明市',
    u'日進市',
    u'田原市',
    u'愛西市',
    u'清須市',
    u'新城市',
    u'北名古屋市',
    u'弥富市',
    u'みよし市',
    u'あま市',
    u'秋田市',
    u'大館市',
    u'鹿角市',
    u'大仙市',
    u'潟上市',
    u'北秋田市',
    u'男鹿市',
    u'由利本荘市',
    u'湯沢市',
    u'仙北市',
    u'横手市',
    u'にかほ市',
    u'能代市',
    u'八戸市',
    u'黒石市',
    u'三沢市',
    u'むつ市',
    u'十和田市',
    u'つがる市',
    u'五所川原市',
    u'青森市',
    u'平川市',
    u'弘前市',
    u'千葉市',
    u'銚子市',
    u'市川市',
    u'船橋市',
    u'館山市',
    u'木更津市',
    u'松戸市',
    u'野田市',
    u'茂原市',
    u'成田市',
    u'佐倉市',
    u'東金市',
    u'習志野市',
    u'柏市',
    u'勝浦市',
    u'市原市',
    u'流山市',
    u'八千代市',
    u'我孫子市',
    u'鎌ヶ谷市',
    u'君津市',
    u'富津市',
    u'浦安市',
    u'四街道市',
    u'袖ヶ浦市',
    u'八街市',
    u'印西市',
    u'白井市',
    u'冨里市',
    u'鴨川市',
    u'旭市',
    u'いすみ市',
    u'匝瑳市',
    u'南房総市',
    u'香取市',
    u'山武市',
    u'松山市',
    u'新居浜市',
    u'四国中央市',
    u'西予市',
    u'東温市',
    u'西条市',
    u'大洲市',
    u'今治市',
    u'八幡浜市',
    u'伊予市',
    u'宇和島市',
    u'福井市',
    u'敦賀市',
    u'小浜市',
    u'大野市',
    u'勝山市',
    u'鯖江市',
    u'あわら市',
    u'越前市',
    u'坂井市',
    u'福岡市',
    u'久留米市',
    u'大牟田市',
    u'直方市',
    u'田川市',
    u'柳川市',
    u'八女市',
    u'筑後市',
    u'大川市',
    u'行橋市',
    u'豊前市',
    u'中間市',
    u'北九州市',
    u'小郡市',
    u'筑紫野市',
    u'春日市',
    u'大野城市',
    u'宗像市',
    u'太宰府市',
    u'古賀市',
    u'福津市',
    u'うきは市',
    u'宮若市',
    u'朝倉市',
    u'飯塚市',
    u'嘉麻市',
    u'みやま市',
    u'糸島市',
    u'会津若松市',
    u'福島市',
    u'郡山市',
    u'須賀川市',
    u'相馬市',
    u'いわき市',
    u'田村市',
    u'白河市',
    u'二本松市',
    u'南相馬市',
    u'伊達市',
    u'喜多方市',
    u'本宮市',
    u'岐阜市',
    u'大垣市',
    u'高山市',
    u'多治見市',
    u'関市',
    u'中津川市',
    u'美濃市',
    u'瑞浪市',
    u'羽島市',
    u'美濃加茂市',
    u'土岐市',
    u'各務原市',
    u'可児市',
    u'山県市',
    u'瑞穂市',
    u'飛騨市',
    u'本巣市',
    u'郡上市',
    u'下呂市',
    u'恵那市',
    u'海津市',
    u'前橋市',
    u'高崎市',
    u'桐生市',
    u'伊勢崎市',
    u'太田市',
    u'沼田市',
    u'館林市',
    u'藤岡市',
    u'渋川市',
    u'安中市',
    u'富岡市',
    u'みどり市',
    u'広島市',
    u'尾道市',
    u'呉市',
    u'福山市',
    u'三原市',
    u'府中市',
    u'三次市',
    u'庄原市',
    u'大竹市',
    u'竹原市',
    u'東広島市',
    u'廿日市市',
    u'安芸高田市',
    u'江田島市',
    u'札幌市',
    u'函館市',
    u'小樽市',
    u'旭川市',
    u'室蘭市',
    u'帯広市',
    u'夕張市',
    u'岩見沢市',
    u'網走市',
    u'留萌市',
    u'苫小牧市',
    u'稚内市',
    u'美唄市',
    u'芦別市',
    u'江別市',
    u'赤平市',
    u'紋別市',
    u'三笠市',
    u'根室市',
    u'千歳市',
    u'滝川市',
    u'砂川市',
    u'歌志内市',
    u'深川市',
    u'富良野市',
    u'登別市',
    u'恵庭市',
    u'伊達市',
    u'北広島市',
    u'石狩市',
    u'士別市',
    u'釧路市',
    u'北斗市',
    u'北見市',
    u'名寄市',
    u'神戸市',
    u'姫路市',
    u'尼崎市',
    u'明石市',
    u'西宮市',
    u'芦屋市',
    u'伊丹市',
    u'相生市',
    u'豊岡市',
    u'加古川市',
    u'赤穂市',
    u'宝塚市',
    u'三木市',
    u'高砂市',
    u'川西市',
    u'小野市',
    u'三田市',
    u'加西市',
    u'篠山市',
    u'養父市',
    u'丹波市',
    u'南あわじ市',
    u'朝来市',
    u'淡路市',
    u'宍粟市',
    u'西脇市',
    u'たつの市',
    u'洲本市',
    u'加東市',
    u'水戸市',
    u'日立市',
    u'土浦市',
    u'結城市',
    u'龍ヶ崎市',
    u'下妻市',
    u'常総市',
    u'常陸太田市',
    u'高萩市',
    u'北茨城市',
    u'取手市',
    u'牛久市',
    u'つくば市',
    u'ひたちなか市',
    u'鹿嶋市',
    u'潮来市',
    u'守谷市',
    u'常陸大宮市',
    u'那珂市',
    u'坂東市',
    u'稲敷市',
    u'筑西市',
    u'かすみがうら市',
    u'神栖市',
    u'行方市',
    u'古河市',
    u'石岡市',
    u'桜川市',
    u'鉾田市',
    u'笠間市',
    u'つくばみらい市',
    u'小美玉市',
    u'金沢市',
    u'野々市市',
    u'七尾市',
    u'小松市',
    u'珠洲市',
    u'羽咋市',
    u'かほく市',
    u'白山市',
    u'能美市',
    u'加賀市',
    u'輪島市',
    u'盛岡市',
    u'釜石市',
    u'大船渡市',
    u'陸前高田市',
    u'北上市',
    u'宮古市',
    u'八幡平市',
    u'一関市',
    u'遠野市',
    u'花巻市',
    u'二戸市',
    u'奥州市',
    u'久慈市',
    u'滝沢市',
    u'高松市',
    u'丸亀市',
    u'坂出市',
    u'善通寺市',
    u'さぬき市',
    u'東かがわ市',
    u'三豊市',
    u'観音寺市',
    u'鹿児島市',
    u'鹿屋市',
    u'枕崎市',
    u'阿久根市',
    u'出水市',
    u'指宿市',
    u'南さつま市',
    u'西之表市',
    u'垂水市',
    u'薩摩川内市',
    u'日置市',
    u'曽於市',
    u'いちき串木野市',
    u'霧島市',
    u'志布志市',
    u'奄美市',
    u'南九州市',
    u'伊佐市',
    u'姶良市',
    u'横浜市',
    u'横須賀市',
    u'川崎市',
    u'平塚市',
    u'鎌倉市',
    u'藤沢市',
    u'小田原市',
    u'茅ヶ崎市',
    u'逗子市',
    u'相模原市',
    u'三浦市',
    u'秦野市',
    u'厚木市',
    u'大和市',
    u'伊勢原市',
    u'海老名市',
    u'座間市',
    u'南足柄市',
    u'綾瀬市',
    u'高知市',
    u'宿毛市',
    u'安芸市',
    u'土佐清水市',
    u'須崎市',
    u'土佐市',
    u'室戸市',
    u'南国市',
    u'四万十市',
    u'香美市',
    u'香南市',
    u'熊本市',
    u'八代市',
    u'人吉市',
    u'荒尾市',
    u'水俣市',
    u'玉名市',
    u'山鹿市',
    u'菊池市',
    u'宇土市',
    u'上天草市',
    u'宇城市',
    u'阿蘇市',
    u'合志市',
    u'天草市',
    u'京都市',
    u'福知山市',
    u'舞鶴市',
    u'綾部市',
    u'宇治市',
    u'宮津市',
    u'亀岡市',
    u'城陽市',
    u'向日市',
    u'長岡京市',
    u'八幡市',
    u'京田辺市',
    u'京丹後市',
    u'南丹市',
    u'木津川市',
    u'四日市市',
    u'松阪市',
    u'桑名市',
    u'鈴鹿市',
    u'名張市',
    u'尾鷲市',
    u'亀山市',
    u'鳥羽市',
    u'いなべ市',
    u'志摩市',
    u'伊賀市',
    u'伊勢市',
    u'熊野市',
    u'津市',
    u'仙台市',
    u'石巻市',
    u'塩竈市',
    u'白石市',
    u'名取市',
    u'角田市',
    u'多賀城市',
    u'岩沼市',
    u'登米市',
    u'栗原市',
    u'東松島市',
    u'気仙沼市',
    u'大崎市',
    u'宮崎市',
    u'都城市',
    u'延岡市',
    u'日南市',
    u'小林市',
    u'日向市',
    u'串間市',
    u'西都市',
    u'えびの市',
    u'松本市',
    u'岡谷市',
    u'諏訪市',
    u'須坂市',
    u'小諸市',
    u'駒ヶ根市',
    u'大町市',
    u'飯山市',
    u'飯田市',
    u'茅野市',
    u'塩尻市',
    u'長野市',
    u'千曲市',
    u'東御市',
    u'中野市',
    u'佐久市',
    u'安曇野市',
    u'上田市',
    u'伊那市',
    u'長崎市',
    u'佐世保市',
    u'島原市',
    u'大村市',
    u'対馬市',
    u'壱岐市',
    u'五島市',
    u'諫早市',
    u'西海市',
    u'平戸市',
    u'雲仙市',
    u'松浦市',
    u'南島原市',
    u'奈良市',
    u'大和高田市',
    u'大和郡山市',
    u'天理市',
    u'橿原市',
    u'桜井市',
    u'五條市',
    u'御所市',
    u'生駒市',
    u'香芝市',
    u'葛城市',
    u'宇陀市',
    u'新潟市',
    u'長岡市',
    u'柏崎市',
    u'新発田市',
    u'小千谷市',
    u'加茂市',
    u'見附市',
    u'村上市',
    u'妙高市',
    u'上越市',
    u'佐渡市',
    u'阿賀野市',
    u'魚沼市',
    u'南魚沼市',
    u'糸魚川市',
    u'十日町市',
    u'三条市',
    u'胎内市',
    u'五泉市',
    u'燕市',
    u'大分市',
    u'別府市',
    u'中津市',
    u'日田市',
    u'佐伯市',
    u'臼杵市',
    u'津久見市',
    u'竹田市',
    u'豊後高田市',
    u'宇佐市',
    u'豊後大野市',
    u'杵築市',
    u'由布市',
    u'国東市',
    u'岡山市',
    u'倉敷市',
    u'津山市',
    u'玉野市',
    u'笠岡市',
    u'井原市',
    u'総社市',
    u'高梁市',
    u'新見市',
    u'備前市',
    u'瀬戸内市',
    u'赤磐市',
    u'真庭市',
    u'美作市',
    u'浅口市',
    u'那覇市',
    u'石垣市',
    u'宜野湾市',
    u'浦添市',
    u'名護市',
    u'糸満市',
    u'沖縄市',
    u'豊見城市',
    u'うるま市',
    u'宮古島市',
    u'南城市',
    u'大阪市',
    u'堺市',
    u'岸和田市',
    u'豊中市',
    u'池田市',
    u'吹田市',
    u'泉大津市',
    u'高槻市',
    u'貝塚市',
    u'守口市',
    u'枚方市',
    u'茨木市',
    u'八尾市',
    u'泉佐野市',
    u'富田林市',
    u'寝屋川市',
    u'河内長野市',
    u'松原市',
    u'大東市',
    u'和泉市',
    u'箕面市',
    u'柏原市',
    u'羽曳野市',
    u'門真市',
    u'摂津市',
    u'高石市',
    u'藤井寺市',
    u'東大阪市',
    u'泉南市',
    u'四条畷市',
    u'交野市',
    u'大阪狭山市',
    u'阪南市',
    u'鳥栖市',
    u'伊万里市',
    u'鹿島市',
    u'多久市',
    u'唐津市',
    u'小城市',
    u'佐賀市',
    u'嬉野市',
    u'武雄市',
    u'神埼市',
    u'川越市',
    u'川口市',
    u'行田市',
    u'秩父市',
    u'所沢市',
    u'飯能市',
    u'加須市',
    u'東松山市',
    u'狭山市',
    u'羽生市',
    u'鴻巣市',
    u'上尾市',
    u'草加市',
    u'越谷市',
    u'蕨市',
    u'戸田市',
    u'入間市',
    u'朝霞市',
    u'志木市',
    u'和光市',
    u'新座市',
    u'桶川市',
    u'久喜市',
    u'北本市',
    u'八潮市',
    u'富士見市',
    u'三郷市',
    u'蓮田市',
    u'坂戸市',
    u'幸手市',
    u'鶴ヶ島市',
    u'日高市',
    u'吉川市',
    u'さいたま市',
    u'熊谷市',
    u'春日部市',
    u'ふじみ野市',
    u'深谷市',
    u'本庄市',
    u'大津市',
    u'彦根市',
    u'近江八幡市',
    u'草津市',
    u'守山市',
    u'栗東市',
    u'甲賀市',
    u'野洲市',
    u'湖南市',
    u'高島市',
    u'東近江市',
    u'米原市',
    u'長浜市',
    u'松江市',
    u'出雲市',
    u'益田市',
    u'安来市',
    u'江津市',
    u'雲南市',
    u'浜田市',
    u'大田市',
    u'静岡市',
    u'浜松市',
    u'沼津市',
    u'熱海市',
    u'三島市',
    u'富士宮市',
    u'伊東市',
    u'島田市',
    u'磐田市',
    u'焼津市',
    u'掛川市',
    u'藤枝市',
    u'御殿場市',
    u'袋井市',
    u'富士市',
    u'下田市',
    u'裾野市',
    u'湖西市',
    u'伊豆市',
    u'御前崎市',
    u'菊川市',
    u'伊豆の国市',
    u'牧之原市',
    u'宇都宮市',
    u'足利市',
    u'栃木市',
    u'鹿沼市',
    u'小山市',
    u'真岡市',
    u'大田原市',
    u'矢板市',
    u'那須塩原市',
    u'佐野市',
    u'さくら市',
    u'那須烏山市',
    u'下野市',
    u'日光市',
    u'徳島市',
    u'鳴門市',
    u'小松島市',
    u'阿南市',
    u'吉野川市',
    u'美馬市',
    u'阿波市',
    u'三好市',
    u'八王子市',
    u'立川市',
    u'武蔵野市',
    u'三鷹市',
    u'青梅市',
    u'府中市',
    u'昭島市',
    u'調布市',
    u'町田市',
    u'小金井市',
    u'小平市',
    u'日野市',
    u'東村山市',
    u'国分寺市',
    u'国立市',
    u'福生市',
    u'狛江市',
    u'東大和市',
    u'清瀬市',
    u'東久留米市',
    u'武蔵村山市',
    u'多摩市',
    u'稲城市',
    u'羽村市',
    u'あきる野市',
    u'西東京市',
    u'足立区',
    u'荒川区',
    u'文京区',
    u'千代田区',
    u'中央区',
    u'江戸川区',
    u'板橋区',
    u'葛飾区',
    u'北区',
    u'江東区',
    u'目黒区',
    u'港区',
    u'中野区',
    u'練馬区',
    u'大田区',
    u'世田谷区',
    u'渋谷区',
    u'品川区',
    u'新宿区',
    u'杉並区',
    u'墨田区',
    u'台東区',
    u'豊島区',
    u'鳥取市',
    u'米子市',
    u'倉吉市',
    u'境港市',
    u'富山市',
    u'魚津市',
    u'氷見市',
    u'滑川市',
    u'砺波市',
    u'小矢部市',
    u'南砺市',
    u'高岡市',
    u'射水市',
    u'黒部市',
    u'和歌山市',
    u'海南市',
    u'田辺市',
    u'御坊市',
    u'有田市',
    u'新宮市',
    u'紀の川市',
    u'橋本市',
    u'岩出市',
    u'山形市',
    u'米沢市',
    u'新庄市',
    u'寒河江市',
    u'上山市',
    u'村山市',
    u'長井市',
    u'天童市',
    u'東根市',
    u'尾花沢市',
    u'南陽市',
    u'鶴岡市',
    u'酒田市',
    u'宇部市',
    u'防府市',
    u'下松市',
    u'美祢市',
    u'周南市',
    u'光市',
    u'下関市',
    u'柳井市',
    u'萩市',
    u'長門市',
    u'山陽小野田市',
    u'山口市',
    u'岩国市',
    u'甲府市',
    u'富士吉田市',
    u'都留市',
    u'大月市',
    u'韮崎市',
    u'南アルプス市',
    u'甲斐市',
    u'笛吹市',
    u'北杜市',
    u'上野原市',
    u'山梨市',
    u'甲州市',
    u'中央市',
]

prefectures_re_text = re_flatten.construct_regex(prefectures)
cities_re_text = re_flatten.construct_regex(cities)
address_re_text = ur'%s?%s\S{4,}' % (prefectures_re_text, cities_re_text)
address_re = re.compile(address_re_text)


def find_addresses(s):
    return address_re.findall(s)
