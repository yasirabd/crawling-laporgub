import scrapy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
import time
import re
from laporgub.items import LaporgubItem
from datetime import datetime


class LaporSpider(scrapy.Spider):
    name = 'lapor'
    allowed_domains = ['laporgub.jatengprov.go.id']
    start_urls = ['http://laporgub.jatengprov.go.id/']
    custom_settings = {
        # specifies exported fields and order
        # 'DOWNLOADER_MIDDLEWARES': {'scrapy_selenium.SeleniumMiddleware': 800},
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': (ChromeDriverManager().install()),
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless']
    }

    def __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.stop_datetime = datetime.strptime("01-10-2020", "%d-%m-%Y")
        self.list_sektor = ['KATEGORI LAIN-LAIN']
        # self.list_sektor = ['INFRASTRUKTUR', 'KESEHATAN', 'ENERGI', 'PENDIDIKAN', 'KEPEGAWAIAN',
        #                     'PERTANIAN', 'PEMBANGUNAN DAERAH', 'PERMADES DAN KEPENDUDUKAN', 'KEUANGAN DAN ASET ', 'BENCANA ',
        #                     'EKONOMI DAN INDUSTRI', 'SOSIAL MASYARAKAT', 'LINGKUNGAN', 'PARIWISATA DAN BUDAYA ', 'KATEGORI LAIN-LAIN',
        #                     'Forkominda', 'Kabupaten Kota', 'SABERPUNGLI', 'LAPOR SP4N']


    def start_requests(self):
        yield SeleniumRequest(
            url = "https://laporgub.jatengprov.go.id/",
            wait_time = 3,
            callback = self.parse,
        )


    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(5)

        # lakukan tiap 1 sektor
        # sektor = self.list_sektor[0]
        for sektor in self.list_sektor:
            self.driver.find_element_by_xpath("//select[@id='sektor']/option[text()='"+sektor+"']").click()

            while True:
                # get url item
                element = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "paginate_info")))
                try:
                    selector = Selector(text=self.driver.page_source)

                    # exclude_item = ['72704', '72720', '72708', '72703', '72700']
                    # exclude_item = ['72777', '72768', '72761', '72720', '72708']
                    # exclude_item = ['72802', '72794', '72785', '72777', '72768']
                    # exclude_item = ['72835', '72832', '72822', '72820', '72841']
                    exclude_item = ['72873', '72865', '72860', '72841', '72835']


                    for href in selector.css('a::attr(href)'):
                        if "main/detail" in href.extract():
                            if any(exclude in href.extract() for exclude in exclude_item):
                                continue

                            # yield scrapy.Request(
                            #     url=href.extract(),
                            #     callback=self.parse_laporan,
                            #     meta={'sektor':sektor}
                            # )
                            yield SeleniumRequest(
                                url = href.extract(),
                                callback = self.parse_laporan,
                                wait_time = 1,
                                meta = {'sektor': sektor}
                            )

                    time.sleep(2)
                    next = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, ">")))
                    next.click()

                except:
                    break

                time.sleep(2)

        self.driver.quit()

    def cleaning_text(self, string):
        # hilangkan \n\t pada text
        string = ' '.join([s.strip() for s in string.split()])
        return string

    def parse_laporan(self, response):
        item = LaporgubItem()


        extract_date = response.xpath('//div[@class="box-head clearfix"]/span').extract_first()
        list_date = re.findall(r'(\d+-\d+-\d+ \d+:\d+ \w+)', extract_date)

        date = list_date[0].replace("WIB","").strip()
        # berhenti ambil data jika sampai batas waktu
        # if datetime.strptime(date, "%d-%m-%Y %H:%M") < self.stop_datetime:
        #     self.driver.close()
        #     raise CloseSpider("Datetime sudah melebihi")

        item['sektor'] = response.meta['sektor']
        item['posting_date'] = self.cleaning_text(list_date[0])

        table_isi = response.xpath('//div[@class="box-isi"]/table//tr')
        for isi in table_isi:
            colname = isi.xpath('td[1]//text()').extract_first().strip()

            if colname == 'Jenis':
                laporan_jenis = isi.xpath('td[3]//text()').extract_first()
                item['laporan_jenis'] = self.cleaning_text(laporan_jenis)

            if colname == 'Melalui':
                laporan_melalui = isi.xpath('td[3]//text()').extract_first()
                item['laporan_melalui'] = self.cleaning_text(laporan_melalui)

            if colname == 'Lokasi':
                laporan_lokasi = isi.xpath('td[3]//text()').extract_first()
                item['laporan_lokasi'] = self.cleaning_text(laporan_lokasi)

            if colname == 'Lampiran':
                lampiran = isi.xpath('td[3]').extract_first()
                if 'a href' in lampiran:
                    laporan_lampiran = isi.xpath('td[3]/p/a/@href').extract_first()
                else:
                    laporan_lampiran = isi.xpath('td[3]/p/text()').extract_first()
                item['laporan_lampiran'] = self.cleaning_text(laporan_lampiran)

            if colname == 'Laporan':
                laporan = isi.xpath('td[3]//text()').extract_first()
                item['laporan'] = self.cleaning_text(laporan)

        # respon komentar
        komentar = response.xpath('//div[@id="komentar"]/ul')
        list_komentar = komentar.xpath('//li[re:test(@class, "media label-\w+")]')
        for idx, k in enumerate(list_komentar):
            if idx == 0:
                item['respon1_perespon'] = self.cleaning_text(k.css('h4::text').get())
                item['respon1_date'] = self.cleaning_text(k.css('div.meta::text').get())
                item['respon1_keterangan'] = self.cleaning_text(k.css('p::text').get())
            if idx == 1:
                item['respon2_perespon'] = self.cleaning_text(k.css('h4::text').get())
                item['respon2_date'] = self.cleaning_text(k.css('div.meta::text').get())
                item['respon2_keterangan'] = self.cleaning_text(k.css('p::text').get())
            if idx == 2:
                item['respon3_perespon'] = self.cleaning_text(k.css('h4::text').get())
                item['respon3_date'] = self.cleaning_text(k.css('div.meta::text').get())
                item['respon3_keterangan'] = self.cleaning_text(k.css('p::text').get())
            if idx == 3:
                item['respon4_perespon'] = self.cleaning_text(k.css('h4::text').get())
                item['respon4_date'] = self.cleaning_text(k.css('div.meta::text').get())
                item['respon4_keterangan'] = self.cleaning_text(k.css('p::text').get())

        return item
