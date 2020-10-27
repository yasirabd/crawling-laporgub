# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LaporgubItem(scrapy.Item):
    sektor = scrapy.Field()
    posting_date = scrapy.Field()
    laporan_jenis = scrapy.Field()
    laporan_melalui = scrapy.Field()
    laporan_lokasi = scrapy.Field()
    laporan_lampiran = scrapy.Field()
    laporan = scrapy.Field()

    respon1_date = scrapy.Field()
    respon1_perespon = scrapy.Field()
    respon1_keterangan = scrapy.Field()

    respon2_date = scrapy.Field()
    respon2_perespon = scrapy.Field()
    respon2_keterangan = scrapy.Field()

    respon3_date = scrapy.Field()
    respon3_perespon = scrapy.Field()
    respon3_keterangan = scrapy.Field()

    respon4_date = scrapy.Field()
    respon4_perespon = scrapy.Field()
    respon4_keterangan = scrapy.Field()
