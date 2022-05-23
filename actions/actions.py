from typing import Any, Text, Dict, List
from difflib import SequenceMatcher
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

cred = credentials.Certificate('actions/firebase-sdk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
def remove_accents(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s

def getToHop(text,nameToHop):
    lastText = remove_accents(text).lower()
    print(lastText)
    listText = list(lastText.split(","))
    with open('actions/data.json', encoding='utf-8') as fh:
        data = json.load(fh)
    with open('actions/tohopmon.json', encoding='utf-8') as fh:
        toHop = json.load(fh)

    listMaToHop = []
    listMajor = []


    for th in toHop:
        if all(x in remove_accents(th['toHop'].lower())  for x in listText):
            print(th['maToHop'])
            listMaToHop.append(th['maToHop'])
    for m in data:
        if any(x in m[nameToHop]  for x in listMaToHop):
            if m not in listMajor:
                listMajor.append(m)

    print(str(listMajor))
    print(len(listMajor))
    return listMajor

def showInformationMajor(data):
    name_major = data['ten_nganh'] + '\n'

    tuition_major = 'Học phí [1 kì học] : ' + data['hoc_phi'] + 'VNĐ \n'
    return name_major + tuition_major

class ActionUniversityInformation(Action):

    def name(self) -> Text:
        return "action_university_information"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Trường Đại học Duy Tân thành lập ngày 11/11/1994 tại trrung tâm của thành phố Đà Nẵng. Đây là trường Đại học Tư thục được đánh giá là ngôi trường đầu tiên lớn nhất, đào tạo nhiều ngành nghề, lĩnh vực nhất tại miền Trung.",
            buttons=[
                {
                    "type": "postback",
                    "title": "Ngành Học",
                    "payload": "Ngành Học"
                }, ]
        )

        return []


class ActionAllMajors(Action):

    def name(self) -> Text:
        return "action_all_majors"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # send payload to Facebook Messenger
        dispatcher.utter_message(
            text="ĐẠI HỌC DUY TÂN CÓ 5 TRƯỜNG & 2 VIỆN ĐÀO TẠO, sau khi xem xong nếu có thắc mắt hoặc bất kì câu hỏi nào có thể liên hệ với chúng tôi!",
            buttons=[
                {
                    "type": "web_url",
                    "url": "https://duytan.edu.vn/tuyen-sinh/Page/EnrollArticleViewDetail.aspx?id=854",
                    "title": "Bấm vào để xem tất cả các ngành học",
                    "webview_height_ratio": "full"
                }, ]
        )

        return []


class ActionMajor(Action):

    def name(self) -> Text:
        return "action_major"

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def showInformation(self, data):
        begin_text = "Thông tin ngành học này là:\n"
        name_major = data['ten_nganh'] + '\n'

        tuition_major = 'Học phí [1 kì học] : ' + data['hoc_phi'] + 'VNĐ \n'
        return begin_text + name_major + tuition_major

    def showConfirm(self, dispatcher, data):
        message = 'Có các ngành trùng tên với ngành bạn muốn tìm kiếm được mình liệt kê bên dưới, nếu đúng bạn hãy bấm vào ngành mà bạn muốn hỏi nhé, cảm ơn bạn <3'
        dispatcher.utter_message(
            text=message,
        )

        for a in data:
            dispatcher.utter_message(
                text=a['ten_nganh'],
                buttons=[{
                    "type": "postback",
                    "title": 'Xem Thông Tin' + a['ten_nganh'],
                    "payload": a['ten_nganh']
                }]
            )

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # It will return array of entities
        text = tracker.latest_message['text']
        with open('actions/data.json', encoding='utf-8') as fh:
            data = json.load(fh)

        low_priority_list = []
        high_priority_list = []

        for a in data:
            name_major = a['ten_nganh']
            same_percentage = SequenceMatcher(None, str(name_major), str(text)).ratio()
            if same_percentage > 0.55:
                if same_percentage >= 0.85:
                    high_priority_list.append(a)
                else:
                    low_priority_list.append(a)

        if len(high_priority_list) > 0:
            if len(high_priority_list) == 1:
                high_priority_list[0]['time'] = datetime.datetime.now()
                db.collection("ReportData").add(high_priority_list[0])
                dispatcher.utter_message(
                    text=str(self.showInformation(high_priority_list[0])),
                    buttons=[
                        {
                            "type": "web_url",
                            "url": high_priority_list[0]["link"],
                            "title": "Xem chi tiết",
                            "webview_height_ratio": "full"
                        }, ]
                )
            else:
                self.showConfirm(dispatcher, high_priority_list)

        else:
            if len(low_priority_list) > 0:
                self.showConfirm(dispatcher, low_priority_list)

        if len(high_priority_list) == 0 and len(low_priority_list) == 0:
            dispatcher.utter_message(
                text = "Hệ thống DTAbot không có ngành tương tự giống ngành của bạn muốn tìm hiểu, nếu bạn đang viết tắt hoặc viết sai tên ngành bạn vui lòng sửa lại nhé!Admin cảm ơn",
            )
        return []


class AskCombinationOfSubjects(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # send payload to Facebook Messenger
        dispatcher.utter_message(
            text="Để xem các ngành phù hợp bằng tổ hợp môn xét tuyển thi THPT hoặc Học bạ bạn có thể nhắn tin theo cách sau:\n"
                 "Ví dụ bạn muốn xét tuyển theo học bạ với tổ hợp môn : Toán Lý và Hóa Trước tiên bạn bấm vào 2 lựa chọn dưới và sau đó :\n"
                 "Bạn hãy nhắn theo cách sau : Toán,Lý,Hóa",
            buttons=[
                {
                    "type": "postback",
                    "title": 'Tổ hợp môn thi THPT',
                    "payload": 'Xét Tuyển Theo môn thi THPT'
                },
                {
                    "type": "postback",
                    "title": 'Tổ hợp môn theo Học Bạ',
                    "payload": 'Xét Tuyển Theo Học Bạ'
                }
            ]
        )

        return []


class AskCombinationOfSubjectsDetailHB(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjectsDetailHB"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # send payload to Facebook Messenger
        dispatcher.utter_message(
            text="Để xem các ngành phù hợp bằng tổ hợp môn xét tuyển theo Học bạ bạn có thể nhắn tin theo cách sau:\n"
                 "Ví dụ bạn muốn xét tuyển theo học bạ với tổ hợp môn : Toán Lý và Hóa\n"
                 "Bạn hãy nhắn theo cách sau : Toán,Lý,Hóa\n"
                 "[chú ý : cách nhau bằng dấu ,]",
        )

        return []


class AskCombinationOfSubjectsDetailTHPT(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjectsDetailTHPT"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # send payload to Facebook Messenger
        dispatcher.utter_message(
            text="Để xem các ngành phù hợp bằng tổ hợp môn xét tuyển theo môn thi THPT bạn có thể nhắn tin theo cách sau:\n"
                 "Ví dụ bạn muốn xét tuyển theo học bạ với tổ hợp môn : Toán Lý và Hóa\n"
                 "Bạn hãy nhắn theo cách sau : Toán,Lý,Hóa\n"
                 "[chú ý : cách nhau bằng dấu ,]",
        )

        return []


class AskCombinationOfSubjectsDetail(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjectsDetail"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        def get_latest_custom_action() -> Text:
            for e in reversed(tracker.events):

                if e['event'] == 'action':
                    if e['name'] != 'action_listen':
                        return e['name']
            return None

        lastActionName = get_latest_custom_action()
        print(str(tracker.events))
        # send payload to Facebook Messenger
        dispatcher.utter_message(
            text= "Hiện tại trường Đại Học Duy Tân có 2 cách xét tuyển theo tổ hợp môn bên dưới, bạn hãy lựa chọn để xem tổ hợp môn phù hợp nhé <3 :",
            buttons=[
                {
                    "type": "postback",
                    "title": 'Học bạ',
                    "payload": 'Học bạ'
                },
                {
                    "type": "postback",
                    "title": 'THPT',
                    "payload": 'THPT'
                } ]
        )

        return []



class AskCombinationOfSubjectsDetailConfirmHB(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjectsDetailConfirmHB"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        def get_latest_text_action() -> Text:
            for e in reversed(tracker.events):

                if e['event'] == 'user':
                    if e['text'] != tracker.latest_message['text']:
                        return e['text']
            return None
        listMajor = getToHop(get_latest_text_action(),'to_hop_xet_tuyen_hoc_ba')
        countListMajor = len(listMajor)

        if countListMajor != 0:
            dispatcher.utter_message(
                text = f'Hiện tại có {countListMajor} ngành học phù hợp với tổ hợp môn mà bạn gửi, chúng tôi sẽ tổng hợp phí bên dưới :',
            )

            for m in listMajor:
                dispatcher.utter_message(
                    text = showInformationMajor(m)
                )
        else:
            dispatcher.utter_message(
                text = 'Hiện không ngành học nào phù hợp với tổ hợp môn trên!',
            )

        return []

class AskCombinationOfSubjectsDetailConfirmTHPT(Action):

    def name(self) -> Text:
        return "AskCombinationOfSubjectsDetailConfirmTHPT"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        def get_latest_text_action() -> Text:
            for e in reversed(tracker.events):

                if e['event'] == 'user':
                    if e['text'] != tracker.latest_message['text']:
                        return e['text']
            return None
        listMajor = getToHop(get_latest_text_action(),'to_hop_xet_tuyen_THPT')
        countListMajor = len(listMajor)

        if countListMajor != 0:
            dispatcher.utter_message(
                text = f'Hiện tại có {countListMajor} ngành học phù hợp với tổ hợp môn mà bạn gửi, chúng tôi sẽ tổng hợp phí bên dưới :',
            )

            for m in listMajor:
                dispatcher.utter_message(
                    text = showInformationMajor(m)
                )
        else:
            dispatcher.utter_message(
                text = 'Hiện không ngành học nào phù hợp với tổ hợp môn trên!',
            )

        return []
