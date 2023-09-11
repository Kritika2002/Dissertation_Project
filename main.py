from bs4 import BeautifulSoup
import requests
import time

def find_main_title():
    html_text = requests.get('https://www.soompi.com/').text
    #print(html_text)
    soup = BeautifulSoup(html_text,'lxml')

    soompi_title = soup.find('h1',class_ = 'featured-meta-title')

    title = soompi_title.find('a').text
    post_link = soompi_title.a['href']
    with open('title/text.txt','w') as f:
        f.write(f'The title of the main post in Soompi is: {title} \n')
        f.write(post_link)
    print ('File saved')


if __name__ == '__main__':
    while True:
        find_main_title()
        time.wait = 10
        print(f'Time to wait {time.wait} minutes')
        time.sleep(time.wait * 60)