import re
import time
from html.parser import HTMLParser

from playwright.sync_api import Playwright, sync_playwright, expect


def extra_userinfo(html_code: str):
    username_match = re.search(r'<div class="([^"]+)">\s*([^<>]+?)\s*</div>',
                               html_code)
    if username_match:
        class_id = username_match.group(1)
        username = username_match.group(2).strip()
    else:
        class_id = ''
        username = ''

    # 提取最后一条消息（<pre>中的文本）
    message_match = re.search(r'<pre[^>]*>(.*?)</pre>', html_code, re.DOTALL)
    last_message = message_match.group(1).strip() if message_match else ''

    user_info = {
        'username': username,
        'class_id': class_id,
        'last_message': last_message
    }
    return user_info


class StrictMessageParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.messages = []
        self.current_time = None
        self.justify_context = None
        self.in_pre = False
        self.current_msg = None
        self._buffer = ""
        self.in_msg_block = False  # 在有效的消息体（聊天内容）结构内
        self.in_msg_container = False  # 外层消息块

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # 判断左右 sender
        if tag == "div" and "style" in attrs_dict:
            style = attrs_dict["style"]
            if "justify-content: space-between" in style:
                self.justify_context = "对方"
            elif "justify-content: right" in style:
                self.justify_context = "自己"

        # 识别消息内容块
        if tag == "div" and "data-e2e" in attrs_dict and attrs_dict[
                "data-e2e"] == "msg-item-content":
            self.in_msg_block = True

        # <pre> 文本消息
        if tag == "pre":
            self.in_pre = True
            self.current_msg = {
                "sender": self.justify_context,
                "time": self.current_time,
                "type": "text",
                "content": ""
            }

        # 图片消息
        if tag == "img" and "src" in attrs_dict:
            src = attrs_dict["src"]
            if src.startswith("data:image/") and self.in_msg_block:
                base64_data = src.split(",", 1)[1] if "," in src else ""
                self.messages.append({
                    "sender": self.justify_context,
                    "time": self.current_time,
                    "type": "image",
                    "content": base64_data
                })

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False
            if self.current_msg:
                self.messages.append(self.current_msg)
                self.current_msg = None
        elif tag == "div":
            # 结束时间段判断
            if re.match(r"^(昨天|\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}",
                        self._buffer):
                self.current_time = self._buffer.strip()
            self._buffer = ""
            self.in_msg_block = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        self._buffer += text
        if self.in_pre and self.current_msg:
            self.current_msg["content"] += text

    def close(self):
        super().close()
        if self.current_msg:
            self.messages.append(self.current_msg)


def extra_chat_history(msg_contianer_code):
    parser = StrictMessageParser()
    parser.feed(msg_contianer_code)
    parser.close()
    return parser.messages


def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    # page.goto("https://www.douyin.com/?recommend=1")

    cookies = [
        {
            # "url": f"{page.url}",
            "name": "sid_tt",
            "value": "4cb87bd6e82d1ae2855dbed498d4389c",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
        },
        {
            # "url": f"{page.url}",
            "name": "ttwid",
            "value":
            "1%7CRmUDO-ssFCO0QoeMyfT76yHbbZXb5WJmBPw7Zkb5OiA%7C1750930284%7Cff411d4d907331bc389329be29e1d62105a78f710a09431d14f04b9505492b6d",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": True,
            "secure": False,
        },
        # {
        #     # "url": f"{page.url}",
        #     "name": "sessionid",
        #     "value": "4cb87bd6e82d1ae2855dbed498d4389c",
        #     "domain": ".douyin.com",
        #     "path": "/",
        #     "httpOnly": True,
        #     "secure": True,
        # },
        {
            # "url": f"{page.url}",
            "name": "sessionid_ss",
            "value": "4cb87bd6e82d1ae2855dbed498d4389c",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
        },
        # {
        #     # "url": f"{page.url}",
        #     "name": "uid_tt",
        #     "value": "673b01676f8538cff2a5646c6e5edd3b",
        #     "domain": ".douyin.com",
        #     "path": "/",
        #     "httpOnly": True,
        #     "secure": True,
        # },
        {
            # "url": f"{page.url}",
            "name": "uid_tt_ss",
            "value": "673b01676f8538cff2a5646c6e5edd3b",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
        },
        {
            "name": "enter_pc_once",
            "value": "1",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": False,
            "secure": True,
        },
        {
            "name": "passport_fe_beating_status",
            "value": "true",
            "domain": ".douyin.com",
            "path": "/",
            "httpOnly": False,
            "secure": False,
        }
    ]
    page.context.add_cookies(cookies)

    print(page.context.cookies())
    page.goto("https://www.douyin.com/?recommend=1")
    time.sleep(6)
    page.hover(
        'xpath=//div[@data-e2e="something-button" and .//p[text()="私信"]]')
    # ele_test = page.locator('xpath=//div[@data-e2e="something-button" and .//p[text()="私信"]]')
    # print(ele_test.text_content())
    # ele_test_html = ele_test.evaluate("el => el.outerHTML")
    # print(ele_test_html)
    # page.locator("div").filter(has_text=re.compile(r"^私信$")).nth(3).click(
    #     button="right")

    # page.hover("text=More information")
    ele_fans_list = page.locator('xpath=//div[@data-e2e="conversation-item"]')

    # page.wait_for_timeout(30000)
    time.sleep(3)
    print(f"ele_fans_list count:{ele_fans_list.count()}")

    for i in range(ele_fans_list.count()):
        ele_html = ele_fans_list.nth(i).evaluate("el => el.outerHTML")
        # 已读消息联系人
        if 'x-semi-prop="count"' not in ele_html:
            ele_fans_list.nth(i).click()
            break
    
    user_info_list = []
    for i in range(ele_fans_list.count()):
        ele_html = ele_fans_list.nth(i).evaluate("el => el.outerHTML")

        # 已读消息联系人
        if 'x-semi-prop="count"' not in ele_html:
            user_info = extra_userinfo(ele_html)
            ele_fans_list.nth(i).click()
            msg_contianer = page.locator('xpath=//div[@id="messageContent"]')
            time.sleep(3)
            msg_contianer_code = msg_contianer.evaluate("el => el.outerHTML")
            print(f"msg_contianer_code:{msg_contianer_code}")

            msg_history = extra_chat_history(msg_contianer_code)
            user_info["msg_history"] = msg_history
            user_info_list.append(user_info)

    print(user_info_list)
    page.wait_for_timeout(3000)
    # ---------------------
    context.close()
    browser.close()

    return user_info_list

with sync_playwright() as playwright:
    run(playwright)
