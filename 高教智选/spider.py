from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pymysql
import time
import re

def crawl_courses():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,2000')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--disable-images')
    options.add_argument('--enable-javascript')
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://higher.smartedu.cn/courses")
    
    courses = []
    seen_links = set()
    page_num = 1
    prev_total = 0
    fail_count = 0
    
    while len(courses) < 500:
        print(f"=== 第 {page_num} 页 ===")
        page_num += 1
        
        try:
            time.sleep(4)
            
            course_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/course/"]')
            print(f"找到 {len(course_elements)} 个课程链接")
            
            new_count = 0
            for idx, element in enumerate(course_elements):
                try:
                    href = element.get_attribute('href')
                    if not href:
                        continue
                    link = href
                    
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                    time.sleep(0.5)
                    
                    title = ""
                    school = ""
                    teacher = ""
                    students = ""
                    
                    title = driver.execute_script("return arguments[0].querySelector('div.font-bold')?.textContent || '';", element).strip()
                    
                    if not title:
                        title = driver.execute_script("return arguments[0].querySelector('.font-bold')?.textContent || '';", element).strip()
                    
                    if not title:
                        all_divs = driver.execute_script("return Array.from(arguments[0].querySelectorAll('div')).map(d => d.textContent.trim()).filter(t => t && t.length > 3 && !t.includes('累计选课') && !t.includes('智慧树') && !t.includes('爱课程'));", element)
                        if all_divs:
                            title = all_divs[0]
                    
                    info_spans = driver.execute_script("return Array.from(arguments[0].querySelectorAll('span')).map(s => s.textContent.trim()).filter(t => t && t !== '一流课程');", element)
                    if len(info_spans) >= 1:
                        school = info_spans[0]
                    if len(info_spans) >= 2:
                        teacher = info_spans[1]
                    
                    all_texts = driver.execute_script("return Array.from(arguments[0].querySelectorAll('p, span')).map(e => e.textContent.trim());", element)
                    for text in all_texts:
                        if '累计选课' in text:
                            match = re.search(r'累计选课\s*([\d万+]+)', text)
                            students = match.group(1) if match else ""
                            break
                    
                    if title:
                        new_count += 1
                        course = {
                            'link': link,
                            'title': title,
                            'school': school,
                            'teacher': teacher,
                            'students': students
                        }
                        courses.append(course)
                        print(f"已爬取 {len(courses)}/500: {title}")
                        
                        if len(courses) >= 500:
                            break
                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    continue
            
            print(f"本页新增 {new_count} 条数据，累计 {len(courses)} 条")
            
            if len(courses) >= 500:
                break
            
            if new_count == 0:
                fail_count += 1
                print(f"没有新增数据，第 {fail_count} 次")
                if fail_count >= 3:
                    print("连续3次没有新增数据，结束爬取")
                    break
            else:
                fail_count = 0
            
            if len(courses) == prev_total:
                print("数据没有增加")
            prev_total = len(courses)
            
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                load_more_button = None
                try:
                    load_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "加载更多")]'))
                    )
                except TimeoutException:
                    pass
                
                if not load_more_button:
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, 'button')
                        for btn in buttons:
                            btn_text = btn.text.strip()
                            if '加载更多' in btn_text:
                                load_more_button = btn
                                break
                    except:
                        pass
                
                if load_more_button:
                    print("找到加载更多按钮，点击中...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                    time.sleep(2)
                    driver.execute_script("arguments[0].click();", load_more_button)
                    time.sleep(6)
                else:
                    print("没有找到加载更多按钮")
                    fail_count += 1
                    if fail_count >= 3:
                        break
                    
            except Exception as e:
                print(f"加载更多失败: {e}")
                fail_count += 1
                if fail_count >= 3:
                    break
            
        except Exception as e:
            print(f"发生错误: {e}")
            break
    
    driver.quit()
    return courses

def save_to_database(courses):
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='xhq',
            database='nocourse',
            charset='utf8mb4',
            port=3306
        )
        
        cursor = conn.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS course")
        
        cursor.execute("""
            CREATE TABLE course (
                id INT AUTO_INCREMENT PRIMARY KEY,
                link VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                school VARCHAR(100),
                teacher VARCHAR(100),
                students VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        insert_sql = """
            INSERT IGNORE INTO course (link, title, school, teacher, students)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        data = [(course['link'], course['title'], course['school'], course['teacher'], course['students']) for course in courses]
        
        cursor.executemany(insert_sql, data)
        conn.commit()
        
        print(f"成功插入 {cursor.rowcount} 条记录")
        
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("开始爬取课程数据...")
    courses = crawl_courses()
    print(f"爬取完成，共获取 {len(courses)} 条课程数据")
    
    print("开始保存到数据库...")
    save_to_database(courses)
    print("任务完成！")