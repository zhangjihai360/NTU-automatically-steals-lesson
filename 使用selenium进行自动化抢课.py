import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys
import re


class Spider:
    def __init__(self):

        # 打开浏览器并设置浏览器为全屏
        self.driver = webdriver.Edge()
        self.driver.maximize_window()
        self.driver.get('https://tdjw.ntu.edu.cn/')

        self.log_in()

        time.sleep(100)

        # 关闭浏览器
        self.driver.close()

    def restart(self):
        """对网站崩溃所做的处理"""

        # 关闭浏览器
        self.driver.close()

        # 打开浏览器并设置浏览器为全屏
        self.driver = webdriver.Edge()
        self.driver.maximize_window()
        self.driver.get('https://tdjw.ntu.edu.cn/')

        self.log_in()

        time.sleep(100)

        # 关闭浏览器
        self.driver.close()

    def get_info(self):
        """获取用户的基本信息"""
        self.username = 'username'
        self.password = 'password'


        """
        self.username = input('请输入你的学号：')
        self.password = input('请输入你的密码：')
        """


    def log_in(self):
        """实现自动化登录"""

        #获取用户信息
        self.get_info()

        #输入学号
        username_input = self.driver.find_element(By.ID, "username")
        username_input.clear()
        username_input.send_keys(self.username)

        #输入密码
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(self.password)

        #勾选7天免登录
        free_log_in_button = self.driver.find_element(By.ID, "rememberMe")
        free_log_in_button.click()

        #点击登录按钮
        log_in_button = self.driver.find_element(By.ID, "login_submit")
        log_in_button.click()

        #进入自主抢课界面
        self.enter_elective_course()

    def enter_elective_course(self):
        """从主界面进入自主抢课界面"""

        # 防止请求超时
        try:
            # 等待新页面加载完成
            self.driver.implicitly_wait(60)

        except:
            self.restart()

        #保存主窗口句柄
        self.main_window = self.driver.window_handles[0]

        #找到选课按钮并点击
        course_select_father_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((
                        By.XPATH, "// *[ @ id = 'cdNav'] / ul / li[3]")))
        course_select_father_button.click()

        #找到自主选课按钮并点击
        independent_course_selection = self.driver.find_element(By.XPATH, '//*[@id="cdNav"]/ul/li[3]/ul/li[3]/a')
        independent_course_selection.click()

        #防止请求超时
        try:
            #获取课程信息
            self.rob_lesson_message()

        except:
            # 获取所有窗口句柄
            all_windows = self.driver.window_handles

            # 关闭所有非主窗口
            for window in all_windows:
                if window != self.main_window:
                    self.driver.switch_to.window(window)  # 切换到该窗口
                    self.driver.close()  # 关闭该窗口

            # 切换回主窗口
            self.driver.switch_to.window(self.main_window)

            #重新进入选课界面
            self.enter_elective_course()

    def rob_lesson_message(self):
        """获取课程信息"""

        # 等待新页面加载完成，并将操作目标切换到新页面
        time.sleep(2)
        self.driver.implicitly_wait(60)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        #点击查询按钮
        query_button = self.driver.find_element(By.XPATH,
                            '// *[ @ id = "searchBox"] / div / div[1] / div / div / div / div / span / button[1]')
        query_button.click()
        self.driver.implicitly_wait(100)

        #展开页面
        while True:
            try:
                expand_page_button = self.driver.find_element(By.XPATH, '//*[@id="more"]/font/a')
                expand_page_button.click()
                self.driver.implicitly_wait(10)
            except:
                break

        # 获取所有匹配的课程元素
        elements = self.driver.find_elements(By.XPATH,
                                '//*[@id="contentBox"]/div[2]//div[contains(@class, "panel panel-info")]')

        # 遍历找到的所有元素
        for element in elements:
            #点击该元素以展开课程信息
            element.click()
            self.driver.implicitly_wait(10)
            time.sleep(1)

            # 查找当前元素下的子孙节点中class值为kcgs的元素
            kcgs_element = element.find_element(By.CLASS_NAME, 'kcgs')

            #获得kch_id
            kch_id = element.find_element(By.CLASS_NAME, 'kch_id').text

            #检查课程人数是否已满
            try:
                num = element.find_element(By.CLASS_NAME, 'full')
                if num.text == "已满":
                    continue

            except:
                pass

            # 检查文本内容是否为"艺术审美与鉴赏类"
            if kcgs_element.text == "艺术审美与鉴赏类":


                # 获取课程节点的id属性
                lesson_element = kcgs_element.find_element(By.XPATH, './..')  # 使用'./..'返回父节点
                lesson_element_id = lesson_element.get_attribute('id')

                self.rob_lesson(lesson_element_id, kch_id)

        print('不好意思，课程已被选完')

        # 结束程序运行
        sys.exit()

    def rob_lesson(self, lesson_element_id, kch_id):
        """点击抢课按钮并确定是否成功"""

        rob_lesson_button_id = 'btn-xk-' + re.sub(r'^tr_', '', lesson_element_id)
        print(kch_id)
        rob_lesson_button = self.driver.find_element(By.ID, rob_lesson_button_id)
        rob_lesson_button.click()

        #获取课程状态
        course_status_xpath = f"//*[@id='zt_txt_{kch_id}']/b"
        course_status = self.driver.find_element(By.XPATH, course_status_xpath).text

        #检查是否选课成功
        if course_status == '已选':
            print('恭喜你，选课成功！')

            # 关闭浏览器
            self.driver.close()

            #结束程序运行
            sys.exit()

        else:
            self.rob_lesson(lesson_element_id, kch_id)

if __name__ == '__main__':
    Spider()
